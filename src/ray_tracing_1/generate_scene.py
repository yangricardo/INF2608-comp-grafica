"""Generate a scene from a JSON specification and write outputs similar to
`random_scene.py` (renders image + properties.md in an output folder).

Usage:
  python src/generate_scene.py --input inputs/example_scene.json

The JSON schema (flexible) supports:
  - "spheres": [ {"center": [x,y,z], "radius": r, "material": {..}} ]
  - "plane": {"y": number, "material": {...} }
  - "lights": [ {"pos": [x,y,z], "power": [r,g,b]} ]
  - optional: "camera": {"eye": [x,y,z], "center": [x,y,z], "up": [x,y,z], "fov": number}

If a field is missing reasonable defaults are used.
"""
from __future__ import annotations


import os
import json
import argparse
from datetime import datetime
import numpy as np
from PIL import Image
import glm
from ray_tracing_1.camera import Camera
from ray_tracing_1.scene import Scene
from ray_tracing_1.shape import Sphere, Plane
from ray_tracing_1.material import PhongMaterial
from ray_tracing_1.light import PointLight


def render_scene(scene: Scene, cam: Camera, W: int, H: int, out_path: str):
  img = np.zeros((H, W, 3), dtype=np.uint8)
  for j in range(H):
    for i in range(W):
      xn, yn = (i + 0.5) / W, (j + 0.5) / H
      ray = cam.generate_ray(xn, yn)
      color = glm.clamp(scene.trace_ray(ray), 0, 1)
      img[j, i] = (color * 255)
  Image.fromarray(img).save(out_path)


def _material_from_spec(spec: dict) -> PhongMaterial:
  if spec is None:
    # default neutral gray
    return PhongMaterial(glm.vec3(0.02), glm.vec3(0.6), glm.vec3(0.3), 10)
  amb = spec.get('ambient', [0.02, 0.02, 0.02])
  dif = spec.get('diffuse', [0.6, 0.6, 0.6])
  spe = spec.get('specular', [0.3, 0.3, 0.3])
  shi = spec.get('shininess', 10)
  return PhongMaterial(ambient=glm.vec3(*amb), diffuse=glm.vec3(*dif), specular=glm.vec3(*spe), shininess=shi)


def build_scene_from_json(spec: dict) -> tuple[Scene, dict]:
  scene = Scene()
  props = {'spheres': [], 'plane': None, 'lights': []}

  # Plane
  plane_spec = spec.get('plane')
  if plane_spec:
    plane_y = plane_spec.get('y', -1.0)
    mat = _material_from_spec(plane_spec.get('material'))
    scene.objects.append(Plane(pos=glm.vec3(0, plane_y, 0), normal=glm.vec3(0, 1, 0), material=mat))
    props['plane'] = {'y': float(plane_y), 'material': plane_spec.get('material', {})}

  # Spheres
  for s in spec.get('spheres', []):
    center = s.get('center', [0.0, 0.0, 0.0])
    radius = s.get('radius', 1.0)
    mat = _material_from_spec(s.get('material'))
    scene.objects.append(Sphere(center=glm.vec3(*center), radius=radius, material=mat))
    props['spheres'].append({'center': center, 'radius': radius, 'material': s.get('material', {})})

  # Lights
  for L in spec.get('lights', []):
    pos = L.get('pos', [5,5,5])
    power = L.get('power', [150,150,150])
    scene.lights.append(PointLight(pos=glm.vec3(*pos), power=glm.vec3(*power)))
    props['lights'].append({'pos': pos, 'power': power})

  return scene, props


def explain_properties_md(props: dict) -> str:
  lines = []
  lines.append('# Propriedades da Simulação')
  lines.append('')
  lines.append('![Imagem da Simulação](render.png)')
  lines.append('')
  lines.append('## Valores usados (numéricos)')
  lines.append('')
  lines.append('```json')
  lines.append(json.dumps(props, indent=2, ensure_ascii=False))
  lines.append('```')
  lines.append('')
  lines.append('## O que significa cada valor (explicação para leigos)')
  lines.append('')
  lines.append('- **Spheres**: lista de esferas; cada uma tem `center` (posição [x,y,z]) e `radius` (tamanho).')
  lines.append('- **Plane - `y`**: altura do piso; valores menores colocam o piso mais abaixo.')
  lines.append('- **Material - `ambient`**: iluminação ambiente (suave).')
  lines.append('- **Material - `diffuse`**: cor principal sob luz direta.')
  lines.append('- **Material - `specular`**: cor/intensidade do brilho (pequenos reflexos).')
  lines.append('- **Material - `shininess`**: controla quão pequeno/afiado é o brilho especular.')
  lines.append('- **Lights - `pos`**: posição da fonte; **power**: intensidade por canal (R,G,B).')
  lines.append('')
  lines.append('> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.')
  return '\n'.join(lines)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', '-i', required=True, help='Path to JSON scene specification')
  parser.add_argument('--outdir', '-o', default='outputs', help='Root outputs directory')
  parser.add_argument('--name', '-n', default='scene', help='Base name for the simulation folder')
  parser.add_argument('--width', type=int, default=400)
  parser.add_argument('--height', type=int, default=300)
  args = parser.parse_args()

  with open(args.input, 'r', encoding='utf-8') as f:
    spec = json.load(f)

  scene, props = build_scene_from_json(spec)

  ts = datetime.now().strftime('%Y%m%d_%H%M%S')
  sim_dir = os.path.join(os.getcwd(), args.outdir, f'{args.name}_{ts}')
  os.makedirs(sim_dir, exist_ok=True)

  cam_spec = spec.get('camera') or {}
  eye = cam_spec.get('eye', [0,0,5])
  center = cam_spec.get('center', [0,0,0])
  up = cam_spec.get('up', [0,1,0])
  fov = cam_spec.get('fov', 45)
  cam = Camera(eye=glm.vec3(*eye), center=glm.vec3(*center), up=glm.vec3(*up), fov=fov, width=args.width, height=args.height)

  img_path = os.path.join(sim_dir, 'render.png')
  md_path = os.path.join(sim_dir, 'properties.md')

  render_scene(scene, cam, args.width, args.height, img_path)
  md_text = explain_properties_md(props)
  with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_text)

  print(f'Wrote scene -> {sim_dir}')


if __name__ == '__main__':
  main()
