from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Optional, Any

from pyglm import glm

from ray_tracing_2.film import Film


class Render:
  def __init__(self, out_root: str = 'outputs'):
    self.out_root = out_root

  def _serialize_material(self, material) -> dict[str, Any]:
    info: dict[str, Any] = {'type': type(material).__name__}

    def vec_to_list(v):
      try:
        return [float(v.x), float(v.y), float(v.z)]
      except Exception:
        return v

    if hasattr(material, 'm_amb'):
      info['ambient'] = vec_to_list(material.m_amb)
    if hasattr(material, 'm_dif'):
      info['diffuse'] = vec_to_list(material.m_dif)
    if hasattr(material, 'm_spe'):
      info['specular'] = vec_to_list(material.m_spe)
    if hasattr(material, 'shi'):
      info['shininess'] = float(material.shi)
    if hasattr(material, 'reflectivity'):
      info['reflectivity'] = vec_to_list(material.reflectivity)
    if hasattr(material, 'transmission'):
      info['transmission'] = vec_to_list(material.transmission)
    if hasattr(material, 'reflection_tint'):
      info['reflection_tint'] = vec_to_list(material.reflection_tint)
    if hasattr(material, 'ior'):
      info['ior'] = float(material.ior)
    if hasattr(material, 'opacity'):
      info['opacity'] = float(material.opacity)
    return info

  def _shape_chain(self, obj) -> list[str]:
    chain: list[str] = []
    current = obj
    while current is not None:
      chain.append(type(current).__name__)
      current = getattr(current, 'shape', None)
    return chain

  def _extract_material(self, obj):
    current = obj
    while current is not None:
      material = getattr(current, 'material', None)
      if material is not None:
        return material
      current = getattr(current, 'shape', None)
    return None

  def _extract_attr(self, obj, attr_name: str):
    current = obj
    while current is not None:
      if hasattr(current, attr_name):
        return getattr(current, attr_name)
      current = getattr(current, 'shape', None)
    return None

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

    render_settings: dict[str, Any] | None = props.get('render') if isinstance(props, dict) else None
    if render_settings:
      lines.append('## Render')
      lines.append('')
      for key, value in render_settings.items():
        lines.append(f'- **{key}**: {value}')
      lines.append('')

    scene_settings: dict[str, Any] | None = props.get('scene') if isinstance(props, dict) else None
    if scene_settings:
      lines.append('## Scene')
      lines.append('')
      for key, value in scene_settings.items():
        lines.append(f'- **{key}**: {value}')
      lines.append('')

    camera_settings: dict[str, Any] | None = props.get('camera') if isinstance(props, dict) else None
    if camera_settings:
      lines.append('## Camera')
      lines.append('')
      for key, value in camera_settings.items():
        lines.append(f'- **{key}**: {value}')
      lines.append('')

    lines.append('## Objetos (detalhado)')
    lines.append('')
    objs: list[dict[str, Any]] | None = props.get('objects') if isinstance(props, dict) else None
    if objs:
      for i, o in enumerate(objs):
        o: dict[str, Any] = o
        lines.append(f'### Objeto {i+1}: {o.get("type", "Unknown")}')
        if 'shape_chain' in o:
          lines.append(f'- **shape_chain**: {o.get("shape_chain")}')
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
      if hasattr(o, 'p_min'):
        entry['p_min'] = glm_to_list(getattr(o, 'p_min'))
      if hasattr(o, 'p_max'):
        entry['p_max'] = glm_to_list(getattr(o, 'p_max'))
      vertices = self._extract_attr(o, 'vertices')
      if vertices is not None:
        entry['vertex_count'] = len(vertices)
      faces = self._extract_attr(o, 'faces')
      if faces is not None:
        entry['face_count'] = len(faces)
      triangles = self._extract_attr(o, 'triangles')
      if triangles is not None:
        entry['triangle_count'] = len(triangles)
      accelerator = self._extract_attr(o, 'accelerator')
      if accelerator is not None:
        entry['accelerator'] = accelerator
      bvh_leaf_size = self._extract_attr(o, 'bvh_leaf_size')
      if bvh_leaf_size is not None:
        entry['bvh_leaf_size'] = bvh_leaf_size
      bvh_node_count = self._extract_attr(o, 'bvh_node_count')
      if bvh_node_count is not None:
        entry['bvh_node_count'] = bvh_node_count
      bvh_leaf_count = self._extract_attr(o, 'bvh_leaf_count')
      if bvh_leaf_count is not None:
        entry['bvh_leaf_count'] = bvh_leaf_count
      bvh_max_depth = self._extract_attr(o, 'bvh_max_depth')
      if bvh_max_depth is not None:
        entry['bvh_max_depth'] = bvh_max_depth
      shape_chain = self._shape_chain(o)
      if len(shape_chain) > 1:
        entry['shape_chain'] = shape_chain
      mat = self._extract_material(o)
      if mat is not None:
        entry['material'] = self._serialize_material(mat)
      objects_list.append(entry)

    lights_list: list[dict[str, Any]] = []
    for L in scene.lights:
      lentry: dict[str, Any] = {}
      if hasattr(L, 'pos'):
        lentry['pos'] = glm_to_list(getattr(L, 'pos'))
      if hasattr(L, 'power'):
        lentry['power'] = glm_to_list(getattr(L, 'power'))
      lights_list.append(lentry)

    render_settings: dict[str, Any] = {
      'name': name,
      'width': width,
      'height': height,
      'samples_per_pixel': samples_per_pixel,
      'sampling_mode': sampling_mode,
      'seed': seed,
      'gamma_fix': gamma_fix,
    }

    scene_settings: dict[str, Any] = {}
    if hasattr(scene, 'ambient_light'):
      scene_settings['ambient_light'] = glm_to_list(scene.ambient_light)
    if hasattr(scene, 'background_color'):
      scene_settings['background_color'] = glm_to_list(scene.background_color)
    if hasattr(scene, 'max_depth'):
      scene_settings['max_depth'] = int(scene.max_depth)
    if hasattr(scene, 'ray_epsilon'):
      scene_settings['ray_epsilon'] = float(scene.ray_epsilon)

    camera_settings: dict[str, Any] = {}
    if hasattr(cam, 'eye'):
      camera_settings['eye'] = glm_to_list(cam.eye)
    if hasattr(cam, 'center'):
      camera_settings['center'] = glm_to_list(cam.center)
    if hasattr(cam, 'up'):
      camera_settings['up'] = glm_to_list(cam.up)
    if hasattr(cam, 'angle'):
      camera_settings['fov'] = float(cam.angle)
    if hasattr(cam, 'focal_distance'):
      camera_settings['focal_distance'] = float(cam.focal_distance)
    if hasattr(cam, 'aspect'):
      camera_settings['aspect'] = float(cam.aspect)

    props = {
      'render': render_settings,
      'scene': scene_settings,
      'camera': camera_settings,
      'objects': objects_list,
      'lights': lights_list,
    }

    md_text = self.explain_properties_md(props)
    md_path = os.path.join(sim_dir, 'properties.md')
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    return sim_dir
