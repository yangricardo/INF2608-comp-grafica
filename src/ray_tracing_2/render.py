from __future__ import annotations

import os
from datetime import datetime
from time import perf_counter
from typing import Optional

from ray_tracing_2.film import Film
from ray_tracing_2.render_snapshot import RenderSnapshot


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

    # Cria o Film com parâmetros de AA e renderiza para o arquivo de saída
    film = Film(width=width, height=height, samples_per_pixel=samples_per_pixel, sampling_mode=sampling_mode, seed=seed)
    render_start = perf_counter()
    film.render(scene=scene, camera=cam, filename=img_path, gamma_fix=gamma_fix)
    render_time_seconds = perf_counter() - render_start

    snapshot = RenderSnapshot.from_runtime(
      scene=scene,
      cam=cam,
      width=width,
      height=height,
      name=name,
      samples_per_pixel=samples_per_pixel,
      sampling_mode=sampling_mode,
      seed=seed,
      gamma_fix=gamma_fix,
      render_time_seconds=render_time_seconds,
    )

    with open(properties_json_path, 'w', encoding='utf-8') as f:
      f.write(snapshot.to_json(indent=2, ensure_ascii=False))

    md_text = snapshot.to_markdown(
      image_name=os.path.basename(img_path),
      properties_json_name=os.path.basename(properties_json_path),
    )
    md_path = os.path.join(sim_dir, 'properties.md')
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    render_time_minutes = render_time_seconds / 60.0
    print(
      f'Render finalizado em {render_time_seconds:.3f}s '
      f'({render_time_minutes:.3f} min). Artefatos em {sim_dir}'
    )

    return sim_dir
