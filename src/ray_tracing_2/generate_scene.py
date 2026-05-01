"""Gera uma cena a partir de uma especificação JSON e grava saídas no padrão
de `random_scene.py`.

O arquivo condensa o pipeline básico descrito no Slide 4: primitivas analíticas
(`4.tracado_de_raios.pdf`, pp. 10-18), câmera pinhole (`4.tracado_de_raios.pdf`,
pp. 19-29) e iluminação local com luz pontual (`4.tracado_de_raios.pdf`,
pp. 40-49).

Uso:
  python src/generate_scene.py --input inputs/example_scene.json

Esquema JSON aceito:
  - "spheres": [ {"center": [x,y,z], "radius": r, "material": {..}} ]
  - "plane": {"y": number, "material": {...} }
  - "lights": [ {"pos": [x,y,z], "power": [r,g,b]} ]
  - opcional: "camera": {"eye": [x,y,z], "center": [x,y,z], "up": [x,y,z], "fov": number}

Quando um campo não aparece, o script usa defaults conservadores.
"""
from __future__ import annotations


import os
import json
import argparse
from datetime import datetime

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.cli import (
  CommonRenderOptions,
  add_common_render_arguments,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import PointLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Sphere, Plane


def render_scene(scene: Scene, cam: Camera, out_path: str, render_options: CommonRenderOptions):
  # Usa a classe Render para organizar saída e gerar markdown
  r = Render()
  # out_path aqui é esperado ser o caminho completo do arquivo de imagem; a
  # classe Render cria sua própria pasta timestamp. Interpretamos `out_path`
  # como base nome da cena quando chamamos Render.render.
  # Para compatibilidade com chamada anterior, extraímos um nome simples.
  base = os.path.splitext(os.path.basename(out_path))[0]
  r.render(scene=scene, cam=cam, **render_options.to_render_kwargs(name=base))


def _material_from_spec(spec: dict) -> PhongMaterial:
  if spec is None:
    # Slide 4, p. 41-42: defaults neutros garantem contribuição ambiente/difusa mínima.
    return PhongMaterial(glm.vec3(0.02), glm.vec3(0.6), glm.vec3(0.3), 10)
  amb = spec.get('ambient', [0.02, 0.02, 0.02])
  dif = spec.get('diffuse', [0.6, 0.6, 0.6])
  spe = spec.get('specular', [0.3, 0.3, 0.3])
  shi = spec.get('shininess', 10)
  return PhongMaterial(ambient=glm.vec3(*amb), diffuse=glm.vec3(*dif), specular=glm.vec3(*spe), shininess=shi)


def build_scene_from_json(spec: dict) -> tuple[Scene, dict]:
  scene = Scene()
  props = {'spheres': [], 'plane': None, 'lights': []}

  # Slide 4, p. 11-12: um plano definido por altura `y` e normal para o piso da cena.
  plane_spec = spec.get('plane')
  if plane_spec is not None:
    plane_y = plane_spec.get('y', -1.0)
    mat = _material_from_spec(plane_spec.get('material'))
    scene.objects.append(Plane(pos=glm.vec3(0, plane_y, 0), normal=glm.vec3(0, 1, 0), material=mat))
    props['plane'] = {'y': float(plane_y), 'material': plane_spec.get('material', {})}

  # Slide 4, p. 15-18: cada esfera vira um objeto geométrico com centro, raio e material.
  for s in spec.get('spheres', []):
    center = s.get('center', [0.0, 0.0, 0.0])
    radius = s.get('radius', 1.0)
    mat = _material_from_spec(s.get('material'))
    scene.objects.append(Sphere(center=glm.vec3(*center), radius=radius, material=mat))
    props['spheres'].append({'center': center, 'radius': radius, 'material': s.get('material', {})})

  # Slide 4, p. 40: luz pontual armazena posição e potência. Nesta base, a
  # PointLight segue a convenção do enunciado com intensidade constante, sem
  # queda explícita por distância no próprio modelo da fonte.
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
  # Mantém a imagem no mesmo diretório do Markdown para o link relativo funcionar.
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


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Generate and render a scene from a JSON specification.',
    examples=[
      'python -m ray_tracing_2.generate_scene --input inputs/example_scene.json --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.generate_scene --input inputs/example_scene.json --width 800 --height 600 --spp 1 --sampling_mode stratified --seed 42',
    ],
  )
  parser.add_argument('--input', '-i', required=True, help='Path to JSON scene specification')
  parser.add_argument('--outdir', '-o', default='outputs', help='Root outputs directory')
  parser.add_argument('--name', '-n', default='scene', help='Base name for the simulation folder')
  add_common_render_arguments(parser, width_default=400, height_default=300, spp_default=16)
  return parser


def main():
  parser = build_cli_parser()
  args = parser.parse_args()
  render_options = CommonRenderOptions.from_namespace(args)

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
  cam = Camera(eye=glm.vec3(*eye), center=glm.vec3(*center), up=glm.vec3(*up), fov=fov, width=render_options.width, height=render_options.height)

  img_path = os.path.join(sim_dir, 'render.png')
  md_path = os.path.join(sim_dir, 'properties.md')

  # Passa `props` para que Render gere o markdown detalhado
  render_scene(scene, cam, img_path, render_options)

  print(f'Wrote scene -> {sim_dir}')


if __name__ == '__main__':
  main()
