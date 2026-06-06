from __future__ import annotations

import os
from datetime import datetime
from time import perf_counter
from typing import Optional

from .film import Film
from .film import describe_sampling_configuration
from .film import effective_samples_per_pixel_for_mode


def _ensure_parent_dir(path: str) -> None:
  parent = os.path.dirname(path)
  if parent:
    os.makedirs(parent, exist_ok=True)


def _print_log_block(title: str, lines: list[str]) -> None:
  print('\n' + '=' * 70)
  print(title)
  print('=' * 70)
  for line in lines:
    print(f'  - {line}')
  print('=' * 70 + '\n')


class Render:
  def __init__(self, out_root: str = 'outputs'):
    self.out_root = out_root
    self.last_result: dict | None = None

  def _build_output_paths(self, name: str) -> dict[str, str]:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    sim_dir = os.path.join(os.getcwd(), self.out_root, f'{name}_{ts}')
    os.makedirs(sim_dir, exist_ok=True)
    return {
      'sim_dir': sim_dir,
      'img_path': os.path.join(sim_dir, 'render.png'),
      'properties_json_path': os.path.join(sim_dir, 'properties.json'),
      'properties_md_path': os.path.join(sim_dir, 'properties.md'),
    }

  def render_core(self,
                  scene,
                  cam,
                  width: int,
                  height: int,
                  name: str = 'scene',
                  samples_per_pixel: int = 16,
                  sampling_mode: str = 'jittered',
                  seed: Optional[int] = None,
                  gamma_fix: bool = False,
                  integrator=None) -> dict:
    paths = self._build_output_paths(name)

    requested_samples_per_pixel = max(1, int(samples_per_pixel))
    effective_samples_per_pixel = effective_samples_per_pixel_for_mode(
      requested_samples_per_pixel,
      sampling_mode,
    )
    seed_text = 'aleatória' if seed is None else str(seed)
    gamma_text = 'ligada' if gamma_fix else 'desligada'

    print(
      f"Iniciando render '{name}'\n"
      f"  resolução: {width}x{height}\n"
      f"  filme: {describe_sampling_configuration(requested_samples_per_pixel, sampling_mode)}\n"
      f"  seed: {seed_text}\n"
      f"  correção gama: {gamma_text}"
    )

    film = Film(
      width=width,
      height=height,
      samples_per_pixel=effective_samples_per_pixel,
      sampling_mode=sampling_mode,
      seed=seed,
    )

    render_start = perf_counter()
    film.render(scene=scene, camera=cam, filename=paths['img_path'], gamma_fix=gamma_fix, integrator=integrator)
    render_time_seconds = perf_counter() - render_start

    render_time_minutes = render_time_seconds / 60.0
    _print_log_block(
      'RENDER FINALIZADO',
      [
        f'tempo: {render_time_seconds:.3f}s ({render_time_minutes:.3f} min)',
        f'imagem: {paths["img_path"]}',
      ],
    )

    result = {
      **paths,
      'render_time_seconds': render_time_seconds,
      'render_time_minutes': render_time_minutes,
      'requested_samples_per_pixel': requested_samples_per_pixel,
      'effective_samples_per_pixel': effective_samples_per_pixel,
      'sampling_mode': sampling_mode,
      'seed': seed,
      'gamma_fix': gamma_fix,
      'name': name,
      'width': width,
      'height': height,
    }
    self.last_result = result
    return result

  def render(self,
             scene,
             cam,
             width: int,
             height: int,
             name: str = 'scene',
             samples_per_pixel: int = 16,
             sampling_mode: str = 'jittered',
             seed: Optional[int] = None,
             gamma_fix: bool = False,
             integrator=None) -> str:
    """Wrapper de compatibilidade: renderiza e retorna o diretório de saída."""
    result = self.render_core(
      scene=scene,
      cam=cam,
      width=width,
      height=height,
      name=name,
      samples_per_pixel=samples_per_pixel,
      sampling_mode=sampling_mode,
      seed=seed,
      gamma_fix=gamma_fix,
      integrator=integrator,
    )
    return str(result['sim_dir'])
