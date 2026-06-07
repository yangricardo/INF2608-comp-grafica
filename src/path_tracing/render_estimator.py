from __future__ import annotations

from dataclasses import dataclass
import os
from time import perf_counter
from typing import Any

from .film import Film
from .render_snapshot import RenderSnapshot


def _print_log_block(title: str, lines: list[str]) -> None:
  print('\n' + '=' * 70)
  print(title)
  print('=' * 70)
  for line in lines:
    print(f'  - {line}')
  print('=' * 70 + '\n')


def _format_seconds_and_minutes(seconds: float) -> str:
  value_seconds = max(0.0, float(seconds))
  return f'{value_seconds:.3f}s ({value_seconds / 60.0:.3f} min)'


@dataclass(slots=True)
class EstimatorOptions:
  calibrate: bool = True
  calibrate_only: bool = False
  calibrate_grid: int = 16
  calibrate_max_seconds: float = 5.0


class RayCountEstimator:
  """Estimador de raios (ray tracing) ou caminhos (path tracing).

  Quando path_tracing_mode=True:
  - A unidade primária é o **caminho** (sample completo: câmera → bounces → luz)
  - total_paths = W × H × SPP; bounces são detalhes internos
  - Throughput em caminhos/segundo (medido via integrator.Li)
  - estimate_total_rays() retorna total_paths (sem bounces) para que
    tempo = total_paths / throughput seja correto

  Quando path_tracing_mode=False (padrão — ray tracing Whitted):
  - Comportamento original: primários + recursivos + shadow rays
  """

  DEFAULT_THROUGHPUT_RAYS_PER_SECOND = 35_000
  DEFAULT_THROUGHPUT_PATHS_PER_SECOND = 5_000  # path tracing sem calibração

  def __init__(
    self,
    width: int,
    height: int,
    samples_per_pixel: int,
    max_depth: int,
    num_objects: int = 0,
    num_lights: int = 0,
    throughput_rays_per_second: float | None = None,
    avg_intersections_per_ray: float | None = None,
    measured_intersection_throughput: float | None = None,
    shadow_samples_per_hit: int | None = None,
    primary_hit_ratio: float = 0.70,
    recursive_surface_ratio: float = 0.05,
    path_tracing_mode: bool = False,
    min_depth: int = 1,
  ):
    self.width = width
    self.height = height
    self.samples_per_pixel = samples_per_pixel
    self.max_depth = max_depth
    self.min_depth = max(1, int(min_depth))
    self.num_objects = num_objects
    self.num_lights = num_lights
    self.path_tracing_mode = bool(path_tracing_mode)
    default_tp = (
      self.DEFAULT_THROUGHPUT_PATHS_PER_SECOND if self.path_tracing_mode
      else self.DEFAULT_THROUGHPUT_RAYS_PER_SECOND
    )
    self.throughput_rays_per_second = float(throughput_rays_per_second) if throughput_rays_per_second else default_tp
    self.avg_intersections_per_ray = float(avg_intersections_per_ray) if avg_intersections_per_ray is not None else None
    self.measured_intersection_throughput = float(measured_intersection_throughput) if measured_intersection_throughput is not None else None
    self.shadow_samples_per_hit = int(shadow_samples_per_hit) if shadow_samples_per_hit is not None else 0
    self.primary_hit_ratio = max(0.0, min(1.0, float(primary_hit_ratio)))
    self.recursive_surface_ratio = max(0.0, min(1.0, float(recursive_surface_ratio)))

  def estimate_primary_rays(self) -> int:
    """Raios primários (ray tracing) ou caminhos totais (path tracing)."""
    return self.width * self.height * self.samples_per_pixel

  def estimate_secondary_rays(self) -> int:
    """Raios secundários (ray tracing) ou bounces totais (path tracing, informativo).

    Path tracing: cada caminho gera avg_path_length bounces internamente.
    Esse valor é informativo — NÃO entra no cálculo de tempo quando
    path_tracing_mode=True (os bounces já estão embutidos no throughput medido).
    """
    if self.path_tracing_mode:
      # Comprimento médio do caminho: (min_depth + max_depth) / 2
      avg_path_length = (self.min_depth + self.max_depth) / 2.0
      bounces_per_path = max(0.0, avg_path_length - 1.0)  # 1 primário + N bounces
      return int(float(self.estimate_primary_rays()) * bounces_per_path)

    # Ray tracing: decaimento exponencial por profundidade
    if self.max_depth <= 0 or self.recursive_surface_ratio <= 0.0:
      return 0
    primary = float(self.estimate_primary_rays())
    continuation_factors = [1.0, 0.60, 0.40, 0.25, 0.15]
    prev = primary * self.primary_hit_ratio * self.recursive_surface_ratio
    secondary = 0.0
    for depth in range(1, self.max_depth + 1):
      factor = continuation_factors[min(depth - 1, len(continuation_factors) - 1)]
      depth_rays = prev * factor
      secondary += depth_rays
      prev = depth_rays * self.recursive_surface_ratio
    return int(secondary)

  def estimate_shadow_rays(self) -> int:
    if self.shadow_samples_per_hit <= 0:
      return 0
    primary = float(self.estimate_primary_rays())
    secondary = float(self.estimate_secondary_rays())
    shadable = (primary + secondary) * self.primary_hit_ratio
    return int(shadable * float(self.shadow_samples_per_hit))

  def estimate_total_rays(self) -> int:
    """Total de trabalho para estimativa de tempo.

    Path tracing: apenas caminhos (throughput medido já inclui bounces).
    Ray tracing: primários + recursivos + shadow.
    """
    if self.path_tracing_mode:
      return self.estimate_primary_rays()  # = total_paths; bounces já no throughput
    return self.estimate_primary_rays() + self.estimate_secondary_rays() + self.estimate_shadow_rays()

  def estimate_render_time_seconds(self) -> float:
    total = self.estimate_total_rays()
    return total / self.throughput_rays_per_second

  def format_time(self, seconds: float) -> str:
    if seconds < 0:
      return 'N/A'
    return _format_seconds_and_minutes(seconds)

  def format_ray_count(self, ray_count: int) -> str:
    if ray_count >= 1_000_000_000:
      return f'{ray_count / 1_000_000_000:.2f}B'
    if ray_count >= 1_000_000:
      return f'{ray_count / 1_000_000:.2f}M'
    if ray_count >= 1_000:
      return f'{ray_count / 1_000:.2f}K'
    return str(ray_count)

  def estimate_total_intersection_tests(self) -> int:
    total_rays = float(self.estimate_total_rays())
    if self.avg_intersections_per_ray is not None and self.avg_intersections_per_ray > 0.0:
      avg = float(self.avg_intersections_per_ray)
    else:
      avg = max(1.0, float(self.num_objects))
    return int(total_rays * avg)

  def estimate_render_time_by_intersections_seconds(self) -> float | None:
    if self.measured_intersection_throughput is None or self.measured_intersection_throughput <= 0.0:
      return None
    total_tests = self.estimate_total_intersection_tests()
    return float(total_tests) / float(self.measured_intersection_throughput)

  def print_estimate(self, title: str = 'ESTIMATIVA DE TRAÇADO DE RAIOS') -> None:
    primary = self.estimate_primary_rays()
    secondary = self.estimate_secondary_rays()
    shadow = self.estimate_shadow_rays()
    total = self.estimate_total_rays()
    estimated_time = self.estimate_render_time_seconds()

    if self.path_tracing_mode:
      avg_path_length = (self.min_depth + self.max_depth) / 2.0
      lines = [
        f'Resolução: {self.width}x{self.height} pixels',
        f'Amostras por pixel (SPP): {self.samples_per_pixel}',
        f'Profundidade: min={self.min_depth}, max={self.max_depth} (méd.≈{avg_path_length:.1f} bounces)',
        f'Objetos: {self.num_objects}',
        f'Luzes (NEE/MIS em scene.lights): {self.num_lights}',
        f'Caminhos totais: {self.format_ray_count(primary)} caminhos',
        f'Bounces estimados: {self.format_ray_count(secondary)} (informativo; já no throughput)',
        f'Shadow rays: {self.format_ray_count(shadow)} raios',
        f'Throughput: {self.format_ray_count(int(self.throughput_rays_per_second))} caminhos/segundo',
        f'Tempo estimado: {self.format_time(estimated_time)}',
      ]
    else:
      lines = [
        f'Resolução: {self.width}x{self.height} pixels',
        f'Amostras por pixel: {self.samples_per_pixel}',
        f'Profundidade máxima: {self.max_depth}',
        f'Objetos: {self.num_objects}',
        f'Luzes: {self.num_lights}',
        f'Raios primários: {self.format_ray_count(primary)} raios',
        f'Raios secundários (recursivos): {self.format_ray_count(secondary)} raios',
        f'Shadow rays: {self.format_ray_count(shadow)} raios',
        f'Total de raios: {self.format_ray_count(total)} raios',
        f'Throughput: {self.format_ray_count(int(self.throughput_rays_per_second))} raios/segundo',
        f'Tempo estimado (por raios): {self.format_time(estimated_time)}',
      ]
      time_by_intersections = self.estimate_render_time_by_intersections_seconds()
      if time_by_intersections is not None:
        lines.append(f'Tempo estimado (por interseções): {self.format_time(time_by_intersections)}')
    _print_log_block(title, lines)

  def to_dict(self) -> dict:
    primary = self.estimate_primary_rays()
    secondary = self.estimate_secondary_rays()
    shadow = self.estimate_shadow_rays()
    total = self.estimate_total_rays()
    estimated_time = self.estimate_render_time_seconds()

    data: dict[str, Any] = {
      'path_tracing_mode': self.path_tracing_mode,
      'primary_rays': primary,
      'secondary_rays': secondary,
      'shadow_rays': shadow,
      'total_rays': total,
      'estimated_time_seconds': estimated_time,
      'estimated_time_minutes': estimated_time / 60.0,
      'formatted_time': self.format_time(estimated_time),
      'throughput_rays_per_second': int(self.throughput_rays_per_second),
      'primary_hit_ratio': float(self.primary_hit_ratio),
      'recursive_surface_ratio': float(self.recursive_surface_ratio),
      'shadow_samples_per_hit': int(self.shadow_samples_per_hit),
    }

    est_tests = self.estimate_total_intersection_tests()
    data['estimated_intersection_tests'] = est_tests
    if self.measured_intersection_throughput is not None:
      data['measured_intersection_throughput'] = float(self.measured_intersection_throughput)
      time_by_tests = self.estimate_render_time_by_intersections_seconds()
      data['estimated_time_by_intersections_seconds'] = time_by_tests
      data['estimated_time_by_intersections_minutes'] = (time_by_tests / 60.0) if time_by_tests is not None else None
    if self.avg_intersections_per_ray is not None:
      data['avg_intersections_per_ray'] = float(self.avg_intersections_per_ray)

    return data


class RenderEstimator:
  """Orquestra estimativa/calibração usando contexto de `Render` e da cena."""

  def __init__(
    self,
    render: Any,
    scene: Any,
    cam: Any,
    *,
    width: int,
    height: int,
    name: str,
    samples_per_pixel: int,
    sampling_mode: str,
    seed: int | None,
    gamma_fix: bool,
    options: EstimatorOptions | None = None,
    integrator: Any = None,
    command_line: str | None = None,
  ):
    self.render = render
    self.scene = scene
    self.cam = cam
    self.width = int(width)
    self.height = int(height)
    self.name = str(name)
    self.samples_per_pixel = int(samples_per_pixel)
    self.sampling_mode = str(sampling_mode)
    self.seed = seed
    self.gamma_fix = bool(gamma_fix)
    self.options = options or EstimatorOptions()
    self.integrator = integrator
    self.command_line = command_line
    self.calibration_info: dict[str, Any] | None = None

  def _reset_run_state(self) -> None:
    # Reinicia estado interno para uma nova execução.
    self.calibration_info = None

    shadow_samples_per_hit = self._compute_shadow_samples_per_hit()
    recursive_surface_ratio = self._compute_recursive_surface_ratio()
    path_tracing_mode = self.integrator is not None
    min_depth = getattr(self.integrator, 'min_depth', 1) if self.integrator is not None else 1

    self.ray_counter = RayCountEstimator(
      width=self.width,
      height=self.height,
      samples_per_pixel=self.samples_per_pixel,
      max_depth=getattr(self.scene, 'max_depth', 3),
      min_depth=min_depth,
      num_objects=len(getattr(self.scene, 'objects', [])),
      num_lights=len(getattr(self.scene, 'lights', [])),
      shadow_samples_per_hit=shadow_samples_per_hit,
      recursive_surface_ratio=recursive_surface_ratio,
      path_tracing_mode=path_tracing_mode,
    )

  @staticmethod
  def _extract_material(obj: Any):
    current = obj
    while current is not None:
      material = getattr(current, 'material', None)
      if material is not None:
        return material
      current = getattr(current, 'shape', None)
    return None

  def _compute_shadow_samples_per_hit(self) -> int:
    total = 0
    for light in getattr(self.scene, 'lights', []):
      su = getattr(light, 'samples_u', None)
      sv = getattr(light, 'samples_v', None)
      if su is not None and sv is not None:
        total += int(su) * int(sv)
      else:
        total += 1
    return total

  def _compute_recursive_surface_ratio(self) -> float:
    total_materials = 0
    recursive_materials = 0
    # Tipos de material/BSDF que geram raio secundário (path tracing ou ray tracer)
    _RECURSIVE_KEYWORDS = (
      'reflective', 'transparent',          # legacy ray_tracing_2 material names
      'lambertian', 'dielectric', 'ggx',    # BSDF types — todo BSDF não-emissivo continua
      'microfacet', 'cooktorrance', 'glass',
    )
    for obj in getattr(self.scene, 'objects', []):
      material = self._extract_material(obj)
      if material is None:
        continue
      total_materials += 1
      material_name = type(material).__name__.lower()
      if any(k in material_name for k in _RECURSIVE_KEYWORDS):
        recursive_materials += 1
    if total_materials == 0:
      return 0.0
    return float(recursive_materials) / float(total_materials)

  def print_initial_estimate(self) -> None:
    self.ray_counter.print_estimate()

  def maybe_calibrate(self, film: Film) -> None:
    if not self.options.calibrate:
      return

    print('Executando calibração rápida para estimativa de throughput...')
    try:
      self.scene.reset_profile_stats()
    except Exception:
      pass

    cal_start = perf_counter()
    nx = min(int(self.options.calibrate_grid), max(1, int(self.width)))
    ny = min(int(self.options.calibrate_grid), max(1, int(self.height)))
    if nx > 1:
      xs = [int(round(k * (self.width - 1) / (nx - 1))) for k in range(nx)]
    else:
      xs = [0]
    if ny > 1:
      ys = [int(round(k * (self.height - 1) / (ny - 1))) for k in range(ny)]
    else:
      ys = [0]

    samples_tested = 0
    integrator_samples = 0  # raios efetivos contados pelo integrador (path tracing)
    integrator_available = self.integrator is not None and hasattr(self.integrator, 'Li')

    for j in ys:
      for i in xs:
        samples = film.get_samples_for_pixel(i, j)
        for xn, yn in samples:
          ray = self.cam.generate_ray(xn, yn)
          if integrator_available:
            # Calibração com custo real: integrador executa todos os bounces.
            # Mede throughput em "samples completos/segundo" (inclui BSDF + interseções).
            self.integrator.Li(ray, self.scene)  # type: ignore[union-attr]
            integrator_samples += 1
          else:
            self.scene.trace_ray(ray)
          samples_tested += 1
          if perf_counter() - cal_start > float(self.options.calibrate_max_seconds):
            break
        if perf_counter() - cal_start > float(self.options.calibrate_max_seconds):
          break
      if perf_counter() - cal_start > float(self.options.calibrate_max_seconds):
        break

    cal_elapsed = perf_counter() - cal_start
    try:
      stats = self.scene.profile_stats()
    except Exception:
      stats = {}
    rays_traced = int(stats.get('rays_traced', 0))
    intersection_tests = int(stats.get('intersection_tests', 0))
    shadow_rays = int(stats.get('shadow_rays', 0))

    if integrator_available and integrator_samples > 0 and cal_elapsed > 0:
      # Throughput em "samples completos por segundo" — cada sample inclui N bounces.
      # Convertemos para "pixels/segundo" e depois para tempo total de render estimado.
      samples_per_second = integrator_samples / cal_elapsed
      total_pixels = self.width * self.height * self.samples_per_pixel
      estimated_render_seconds = total_pixels / samples_per_second
      measured_throughput = samples_per_second  # unidade: samples/s (não raios primários/s)
      calibration_mode = 'integrator_Li'
    else:
      measured_throughput = ((rays_traced + shadow_rays) / cal_elapsed) if cal_elapsed > 0 else 0.0
      estimated_render_seconds = None
      calibration_mode = 'scene_trace_ray'
    self.calibration_info = {
      'calibration_mode': calibration_mode,
      'calibration_elapsed_seconds': cal_elapsed,
      'calibration_samples_tested': samples_tested,
      'calibration_rays_traced': rays_traced,
      'calibration_intersection_tests': intersection_tests,
      'calibration_shadow_rays': shadow_rays,
      'measured_throughput_rays_per_second': measured_throughput,
    }

    log_lines = [
      f'modo: {calibration_mode}',
      f'samples_tested: {samples_tested}',
      f'rays_traced: {rays_traced}',
      f'intersection_tests: {intersection_tests}',
      f'shadow_rays: {shadow_rays}',
      f'elapsed: {_format_seconds_and_minutes(cal_elapsed)}',
    ]
    if integrator_available:
      log_lines.append(f'throughput (samples completos/s): {measured_throughput:.0f} samples/segundo')
      if estimated_render_seconds is not None:
        log_lines.append(f'tempo estimado direto: {_format_seconds_and_minutes(estimated_render_seconds)}')
    else:
      log_lines.append(f'measured_throughput (rays + shadow_rays): {measured_throughput:.0f} raios/segundo')
    _print_log_block('RESULTADO DA CALIBRACAO', log_lines)

    if integrator_available and integrator_samples > 0 and cal_elapsed > 0:
      # Path tracing: throughput em caminhos/segundo (paths/s).
      # estimate_total_rays() no modo path_tracing_mode retorna total_paths,
      # então tempo = total_paths / paths_per_second — sem conversão extra.
      if measured_throughput > 0.0:
        self.ray_counter.throughput_rays_per_second = measured_throughput
    elif measured_throughput > 0.0:
      self.ray_counter.throughput_rays_per_second = measured_throughput

    shadow_samples_per_hit = max(1, int(self.ray_counter.shadow_samples_per_hit))
    if rays_traced > 0:
      calibrated_hit_ratio = float(shadow_rays) / float(rays_traced * shadow_samples_per_hit)
      self.ray_counter.primary_hit_ratio = max(0.05, min(0.98, calibrated_hit_ratio))

    if intersection_tests > 0 and cal_elapsed > 0.0:
      self.ray_counter.measured_intersection_throughput = float(intersection_tests) / float(cal_elapsed)
      if not integrator_available and rays_traced > 0:
        # Só computa avg_intersections_per_ray no modo ray-tracer: o integrador chama
        # compute_intersection() diretamente sem incrementar rays_traced, então
        # rays_traced=0 e a divisão produziria um valor absurdo (25K+).
        denom = float(rays_traced + shadow_rays) if (rays_traced + shadow_rays) > 0 else float(max(1, rays_traced))
        self.ray_counter.avg_intersections_per_ray = float(intersection_tests) / denom

    self.ray_counter.print_estimate('ESTIMATIVA DE TRAÇADO DE RAIOS')

  def should_skip_render(self) -> bool:
    return bool(self.options.calibrate and self.options.calibrate_only)

  def estimation_dict(self) -> dict[str, Any]:
    payload = self.ray_counter.to_dict()
    if self.calibration_info is not None:
      payload['calibration'] = self.calibration_info
    return payload

  def _write_snapshot_files(self, snapshot: RenderSnapshot, *, image_name: str | None = None) -> tuple[str, str]:
    result = self.render.last_result or {}
    properties_json_path = result.get('properties_json_path')
    properties_md_path = result.get('properties_md_path')
    if properties_json_path is None or properties_md_path is None:
      raise RuntimeError('Render.last_result missing output paths; call render.render_core first')

    os.makedirs(os.path.dirname(properties_json_path), exist_ok=True)
    with open(properties_json_path, 'w', encoding='utf-8') as f:
      f.write(snapshot.to_json(indent=2, ensure_ascii=False))

    md_text = snapshot.to_markdown(
      image_name=image_name,
      properties_json_name=os.path.basename(properties_json_path),
    )
    os.makedirs(os.path.dirname(properties_md_path), exist_ok=True)
    with open(properties_md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    return properties_json_path, properties_md_path

  def run(self) -> str:
    self._reset_run_state()

    film = Film(
      width=self.width,
      height=self.height,
      samples_per_pixel=self.samples_per_pixel,
      sampling_mode=self.sampling_mode,
      seed=self.seed,
    )
    if not self.options.calibrate:
      self.print_initial_estimate()
    self.maybe_calibrate(film)

    if self.should_skip_render():
      result = self.render._build_output_paths(self.name)
      self.render.last_result = {
        **result,
        'name': self.name,
        'gamma_fix': self.gamma_fix,
      }
      snapshot = RenderSnapshot.from_runtime(
        scene=self.scene,
        cam=self.cam,
        width=self.width,
        height=self.height,
        name=self.name,
        samples_per_pixel=self.samples_per_pixel,
        sampling_mode=self.sampling_mode,
        seed=self.seed,
        gamma_fix=self.gamma_fix,
        render_time_seconds=None,
        render_estimator=self,
        command_line=self.command_line,
      )
      properties_json_path, properties_md_path = self._write_snapshot_files(snapshot, image_name=None)
      _print_log_block(
        'CALIBRACAO CONCLUIDA',
        [
          f'propriedades: {properties_json_path}',
          f'resumo: {properties_md_path}',
        ],
      )
      return str(self.render.last_result['sim_dir'])

    core = self.render.render_core(
      scene=self.scene,
      cam=self.cam,
      width=self.width,
      height=self.height,
      name=self.name,
      samples_per_pixel=self.samples_per_pixel,
      sampling_mode=self.sampling_mode,
      seed=self.seed,
      gamma_fix=self.gamma_fix,
      integrator=self.integrator,
    )
    self.render.last_result = core

    snapshot = RenderSnapshot.from_runtime(
      scene=self.scene,
      cam=self.cam,
      width=self.width,
      height=self.height,
      name=str(core.get('name', 'scene')),
      samples_per_pixel=int(core.get('effective_samples_per_pixel', self.samples_per_pixel)),
      sampling_mode=self.sampling_mode,
      seed=self.seed,
      gamma_fix=bool(core.get('gamma_fix', False)),
      render_time_seconds=float(core.get('render_time_seconds', 0.0)),
      render_estimator=self,
      command_line=self.command_line,
    )
    properties_json_path, properties_md_path = self._write_snapshot_files(
      snapshot,
      image_name=os.path.basename(str(core['img_path'])),
    )

    est_payload = self.estimation_dict()
    est_seconds = float(est_payload.get('estimated_time_seconds', 0.0) or 0.0)
    real_seconds = float(core.get('render_time_seconds', 0.0) or 0.0)
    comparison_lines = [
      f'estimado (raios): {_format_seconds_and_minutes(est_seconds)}',
      f'real: {_format_seconds_and_minutes(real_seconds)}',
    ]
    if est_seconds > 0.0 and real_seconds > 0.0:
      ratio = real_seconds / est_seconds
      delta = real_seconds - est_seconds
      rel_err = abs(delta) / max(1e-9, real_seconds)
      comparison_lines.extend([
        f'fator real/estimado: {ratio:.2f}x',
        f'erro absoluto: {_format_seconds_and_minutes(abs(delta))}',
        f'erro relativo: {rel_err:.2%}',
      ])
    _print_log_block('COMPARATIVO ESTIMATIVA X RENDER REAL', comparison_lines)
    _print_log_block(
      'ARTEFATOS DO SNAPSHOT',
      [
        f'propriedades: {properties_json_path}',
        f'resumo: {properties_md_path}',
      ],
    )

    return str(core['sim_dir'])


def run_render_with_estimation(
  *,
  render: Any,
  scene: Any,
  cam: Any,
  width: int,
  height: int,
  name: str,
  samples_per_pixel: int,
  sampling_mode: str,
  seed: int | None,
  gamma_fix: bool,
  estimator_options: EstimatorOptions | None = None,
  integrator: Any = None,
  command_line: str | None = None,
) -> str:
  estimator = RenderEstimator(
    render=render,
    scene=scene,
    cam=cam,
    width=width,
    height=height,
    name=name,
    samples_per_pixel=samples_per_pixel,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
    options=estimator_options,
    integrator=integrator,
    command_line=command_line,
  )
  return estimator.run()
