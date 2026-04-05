from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Optional, Any

import glm

from ray_tracing_2_antialiasing.film import Film


class Render:
  def __init__(self, out_root: str = 'outputs'):
    self.out_root = out_root

  def explain_properties_md(self, props: dict) -> str:
    """Gera o texto Markdown com as propriedades da simulação.

    Comentário (PT): reutiliza o formato usado em `generate_scene.py` e
    `random_scene.py` para manter consistência de saída.
    """
    def vec_to_list(v):
      try:
        return [float(v.x), float(v.y), float(v.z)]
      except Exception:
        return v

    lines = []
    lines.append('# Propriedades da Simulação')
    lines.append('')
    lines.append('![Imagem da Simulação](render.png)')
    lines.append('')
    lines.append('## Objetos (detalhado)')
    lines.append('')
    objs: list[dict[str, Any]] | None = props.get('objects') if isinstance(props, dict) else None
    if objs:
      for i, o in enumerate(objs):
        o: dict[str, Any] = o
        lines.append(f'### Objeto {i+1}: {o.get("type", "Unknown")}')
        if 'center' in o:
          lines.append(f'- **center**: {vec_to_list(o.get("center"))}')
        if 'pos' in o:
          lines.append(f'- **pos**: {vec_to_list(o.get("pos"))}')
        if 'normal' in o:
          lines.append(f'- **normal**: {vec_to_list(o.get("normal"))}')
        if 'radius' in o:
          lines.append(f'- **radius**: {o.get("radius")}')
        mat = o.get('material')
        if mat:
          lines.append('- **material**:')
          if isinstance(mat, dict):
            for k, v in mat.items():
              lines.append(f'  - **{k}**: {v}')
          else:
            try:
              amb = vec_to_list(getattr(mat, 'm_amb', getattr(mat, 'ambient', None)))
              dif = vec_to_list(getattr(mat, 'm_dif', getattr(mat, 'diffuse', None)))
              spe = vec_to_list(getattr(mat, 'm_spe', getattr(mat, 'specular', None)))
              shi = getattr(mat, 'shi', getattr(mat, 'shininess', None))
              lines.append(f'  - **ambient**: {amb}')
              lines.append(f'  - **diffuse**: {dif}')
              lines.append(f'  - **specular**: {spe}')
              lines.append(f'  - **shininess**: {shi}')
            except Exception:
              lines.append('  - (material details unavailable)')
        lines.append('')
    else:
      lines.append('- (Nenhum objeto detalhado fornecido)')
      lines.append('')

    lines.append('## Luzes (detalhado)')
    lines.append('')
    lights: list[dict[str, Any]] | None = props.get('lights') if isinstance(props, dict) else None
    if lights:
      for i, L in enumerate(lights):
        L: dict[str, Any] = L
        lines.append(f'- **Light {i+1}**:')
        if 'pos' in L:
          lines.append(f'  - pos: {vec_to_list(L.get("pos"))}')
        if 'power' in L:
          lines.append(f'  - power: {vec_to_list(L.get("power"))}')
        lines.append('')
    else:
      lines.append('- (Nenhuma luz detalhada fornecida)')
      lines.append('')

    lines.append('## Debug (raw JSON)')
    lines.append('')
    lines.append('```json')
    lines.append(json.dumps(props, indent=2, ensure_ascii=False))
    lines.append('```')
    lines.append('')
    lines.append('> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.')
    return '\n'.join(lines)

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

    # Cria o Film com parâmetros de AA e renderiza para o arquivo de saída
    film = Film(width=width, height=height, samples_per_pixel=samples_per_pixel, sampling_mode=sampling_mode, seed=seed)
    film.render(scene=scene, camera=cam, filename=img_path, gamma_fix=gamma_fix)

    # Gera o markdown de propriedades e grava
    def glm_to_list(v):
      try:
        return [float(v.x), float(v.y), float(v.z)]
      except Exception:
        return v

    objects_list: list[dict[str, Any]] = []
    for o in scene.objects:
      entry: dict[str, Any] = {'type': type(o).__name__}
      if hasattr(o, 'center'):
        entry['center'] = glm_to_list(getattr(o, 'center'))
      if hasattr(o, 'pos'):
        entry['pos'] = glm_to_list(getattr(o, 'pos'))
      if hasattr(o, 'normal'):
        entry['normal'] = glm_to_list(getattr(o, 'normal'))
      if hasattr(o, 'radius'):
        entry['radius'] = float(getattr(o, 'radius'))
      mat = getattr(o, 'material', None)
      if mat is not None:
        m: dict[str, Any] = {}
        if hasattr(mat, 'm_amb'):
          m['ambient'] = glm_to_list(mat.m_amb)
        if hasattr(mat, 'm_dif'):
          m['diffuse'] = glm_to_list(mat.m_dif)
        if hasattr(mat, 'm_spe'):
          m['specular'] = glm_to_list(mat.m_spe)
        if hasattr(mat, 'shi'):
          m['shininess'] = float(mat.shi)
        entry['material'] = m
      objects_list.append(entry)

    lights_list: list[dict[str, Any]] = []
    for L in scene.lights:
      lentry: dict[str, Any] = {}
      if hasattr(L, 'pos'):
        lentry['pos'] = glm_to_list(getattr(L, 'pos'))
      if hasattr(L, 'power'):
        lentry['power'] = glm_to_list(getattr(L, 'power'))
      lights_list.append(lentry)

    props = {'objects': objects_list, 'lights': lights_list}

    md_text = self.explain_properties_md(props)
    md_path = os.path.join(sim_dir, 'properties.md')
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    return sim_dir
