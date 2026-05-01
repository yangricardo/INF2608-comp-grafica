from __future__ import annotations

import os
from datetime import datetime
from time import perf_counter
from typing import Optional

from ray_tracing_2.film import Film
from ray_tracing_2.film import describe_sampling_configuration
from ray_tracing_2.film import effective_samples_per_pixel_for_mode
from ray_tracing_2.render_snapshot import RenderSnapshot


def _ensure_parent_dir(path: str) -> None:
  parent = os.path.dirname(path)
  if parent:
    os.makedirs(parent, exist_ok=True)


class Render:
  def __init__(self, out_root: str = 'outputs'):
    self.out_root = out_root

  def render(self,
             scene,
             cam,
             width: int,
             height: int,
             name: str = 'scene',
             samples_per_pixel: int = 16,
             sampling_mode: str = 'jittered',
             seed: Optional[int] = None,
             gamma_fix: bool = False) -> str:
    """Renderiza a cena, salva `render.png` e `properties.md` em uma pasta timestamp.

    Retorna o caminho da pasta criada.
    """
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    sim_dir = os.path.join(os.getcwd(), self.out_root, f'{name}_{ts}')
    os.makedirs(sim_dir, exist_ok=True)

    img_path = os.path.join(sim_dir, 'render.png')
    properties_json_path = os.path.join(sim_dir, 'properties.json')
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

    # Cria o Film com parâmetros de AA e renderiza para o arquivo de saída
    film = Film(
      width=width,
      height=height,
      samples_per_pixel=effective_samples_per_pixel,
      sampling_mode=sampling_mode,
      seed=seed,
    )
    render_start = perf_counter()
    film.render(scene=scene, camera=cam, filename=img_path, gamma_fix=gamma_fix)
    render_time_seconds = perf_counter() - render_start

    snapshot = RenderSnapshot.from_runtime(
      scene=scene,
      cam=cam,
      width=width,
      height=height,
      name=name,
      samples_per_pixel=effective_samples_per_pixel,
      sampling_mode=sampling_mode,
      seed=seed,
      gamma_fix=gamma_fix,
      render_time_seconds=render_time_seconds,
    )

    _ensure_parent_dir(properties_json_path)
    with open(properties_json_path, 'w', encoding='utf-8') as f:
      f.write(snapshot.to_json(indent=2, ensure_ascii=False))

    md_text = snapshot.to_markdown(
      image_name=os.path.basename(img_path),
      properties_json_name=os.path.basename(properties_json_path),
    )
    md_path = os.path.join(sim_dir, 'properties.md')
    _ensure_parent_dir(md_path)
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    render_time_minutes = render_time_seconds / 60.0
    print(
      f'Render finalizado em {render_time_seconds:.3f}s '
      f'({render_time_minutes:.3f} min)\n'
      f'  imagem: {img_path}\n'
      f'  resumo: {md_path}\n'
      f'  propriedades: {properties_json_path}'
    )

    return sim_dir
