"""Gera várias cenas aleatórias e grava cada simulação em uma pasta em
`outputs/` contendo a imagem renderizada e um arquivo Markdown com as
propriedades e explicações em linguagem leiga.

Veja `src/random.py` (anterior) — este arquivo evita colisão com o módulo
`random` da biblioteca padrão renomeando o script.
"""
from __future__ import annotations


import os
import json
import numpy as np
from PIL import Image
import glm
import random
from datetime import datetime
from ray_tracing_2.ray import Ray
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Sphere, Plane
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.light import PointLight


def render_scene(scene: Scene, cam: Camera, W: int, H: int, out_path: str, samples_per_pixel: int = 16, sampling_mode: str = 'jittered', seed: int | None = None, gamma_fix: bool = False):
  # Usa a classe Render para criar pastas e markdown
  from ray_tracing_2.render import Render
  r = Render()
  base = os.path.splitext(os.path.basename(out_path))[0]
  r.render(scene=scene, cam=cam, width=W, height=H, name=base, props=None, samples_per_pixel=samples_per_pixel, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)


def build_random_scene(rng: random.Random):
  # Gera parâmetros geométricos aleatórios para produzir variações da mesma cena-base.
  sx = rng.uniform(-2.0, 2.0)
  sy = rng.uniform(-0.5, 1.5)
  sr = rng.uniform(0.3, 1.5)
  plane_y = rng.uniform(-2.0, 0.0)

  def rand_color(scale=1.0):
    return glm.vec3(rng.random() * scale, rng.random() * scale, rng.random() * scale)

  # Slide 4, p. 41-49: materiais com componentes ambiente, difuso e especular.
  mat_sphere = PhongMaterial(
    ambient=glm.vec3(rng.uniform(0.0, 0.15), rng.uniform(0.0, 0.15), rng.uniform(0.0, 0.15)),
    diffuse=rand_color(1.0),
    specular=rand_color(1.0),
    shininess=rng.uniform(5, 200)
  )

  mat_plane = PhongMaterial(
    ambient=glm.vec3(rng.uniform(0.0, 0.1), rng.uniform(0.0, 0.1), rng.uniform(0.0, 0.1)),
    diffuse=glm.vec3(rng.uniform(0.2, 0.9), rng.uniform(0.2, 0.9), rng.uniform(0.2, 0.9)),
    specular=glm.vec3(rng.uniform(0.0, 0.5), rng.uniform(0.0, 0.5), rng.uniform(0.0, 0.5)),
    shininess=rng.uniform(1, 50)
  )

  scene = Scene()
  # Slide 4, p. 11-18 e p. 40: plano, esfera e luzes formam a cena usada no teste visual.
  scene.objects.append(Plane(pos=glm.vec3(0, plane_y, 0), normal=glm.vec3(0, 1, 0), material=mat_plane))
  scene.objects.append(Sphere(center=glm.vec3(sx, sy, 0), radius=sr, material=mat_sphere))

  lights = []
  n_lights = rng.randint(1, 3)
  for i in range(n_lights):
    lx = rng.uniform(-6.0, 6.0)
    ly = rng.uniform(2.0, 7.0)
    lz = rng.uniform(-4.0, 6.0)
    p = glm.vec3(rng.uniform(40, 300), rng.uniform(40, 300), rng.uniform(40, 300))
    scene.lights.append(PointLight(pos=glm.vec3(lx, ly, lz), power=p))
    lights.append({"pos": [lx, ly, lz], "power": [float(p.x), float(p.y), float(p.z)]})

  # Guarda os valores numéricos usados para explicar a cena no Markdown de saída.
  props = {
    "sphere": {"center": [float(sx), float(sy), 0.0], "radius": float(sr)},
    "plane": {"y": float(plane_y), "normal": [0.0, 1.0, 0.0]},
    "material_sphere": {
      "ambient": [float(mat_sphere.m_amb.x), float(mat_sphere.m_amb.y), float(mat_sphere.m_amb.z)],
      "diffuse": [float(mat_sphere.m_dif.x), float(mat_sphere.m_dif.y), float(mat_sphere.m_dif.z)],
      "specular": [float(mat_sphere.m_spe.x), float(mat_sphere.m_spe.y), float(mat_sphere.m_spe.z)],
      "shininess": float(mat_sphere.shi)
    },
    "material_plane": {
      "ambient": [float(mat_plane.m_amb.x), float(mat_plane.m_amb.y), float(mat_plane.m_amb.z)],
      "diffuse": [float(mat_plane.m_dif.x), float(mat_plane.m_dif.y), float(mat_plane.m_dif.z)],
      "specular": [float(mat_plane.m_spe.x), float(mat_plane.m_spe.y), float(mat_plane.m_spe.z)],
      "shininess": float(mat_plane.shi)
    },
    "lights": lights
  }

  return scene, props


def explain_properties_md(props: dict) -> str:
  lines = []
  lines.append('# Propriedades da Simulação')
  # O caminho relativo permite renderizar a imagem no próprio diretório da simulação.
  lines.append('![Imagem da Simulação](render.png)')
  lines.append('')
  lines.append('## Valores usados (numéricos)')
  lines.append('')
  lines.append('```json')
  lines.append(json.dumps(props, indent=2))
  lines.append('```')
  lines.append('')
  lines.append('## O que significa cada valor (explicação para leigos)')
  lines.append('')
  lines.append('- **Esfera - `center`**: posição da esfera no espaço 3D. Ex.: `[x, y, z]` — move a esfera para a esquerda/direita, para cima/baixo ou para frente/trás.')
  lines.append('- **Esfera - `radius`**: tamanho da esfera; quanto maior, mais volumosa ela aparece na imagem.')
  lines.append('- **Plano - `y`**: altura do piso. Valores menores (mais negativos) colocam o plano mais abaixo; valores próximos de zero posicionam o piso próximo da origem.')
  lines.append('- **Material - `ambient`**: cor que representa a iluminação ambiente geral — pequena quantidade que ilumina objetos mesmo quando não recebem luz direta. É um componente suave e difuso.')
  lines.append('- **Material - `diffuse`**: cor principal do objeto sob luz direta. Controla a aparência básica (por exemplo, azul, verde, vermelho).')
  lines.append('- **Material - `specular`**: cor e intensidade dos brilhos (reflexos pequenos). Valores maiores tornam o brilho mais aparente.')
  lines.append('- **Material - `shininess`**: controla o tamanho e nitidez do brilho especular. Valores altos produzem brilhos pequenos e intensos (superfícies muito brilhantes); valores baixos produzem brilhos largos e suaves (superfícies foscas).')
  lines.append('- **Luzes - `pos`**: posição da fonte de luz no espaço; deslocar a luz muda a direção das sombras e onde aparecem os brilhos.')
  lines.append('- **Luzes - `power`**: intensidade da luz por canal (R,G,B). Valores maiores tornam a cena mais iluminada; diferenças entre R/G/B podem dar tons coloridos à iluminação.')
  lines.append('')
  lines.append('> Dica: experimente aumentar o `power` de uma luz para ver sombras mais claras, ou aumentar `shininess` da esfera para ver reflexos mais nítidos.')
  return '\n'.join(lines)


def main(n_sim: int = 5, W: int = 400, H: int = 300):
  # Mantém todas as simulações em uma pasta de saída previsível.
  out_root = os.path.join(os.getcwd(), 'outputs')
  os.makedirs(out_root, exist_ok=True)
  rng = random.Random()
  rng.seed()

  # Slide 4, p. 14 e p. 29: câmera fixa para comparar variações de geometria.
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45, width=W, height=H)

  for i in range(n_sim):
    scene, props = build_random_scene(rng)
    # Timestamp evita sobrescrever uma simulação anterior.
    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    sim_dir = os.path.join(out_root, f'sim_{ts}')
    os.makedirs(sim_dir, exist_ok=True)
    img_path = os.path.join(sim_dir, 'render.png')
    md_path = os.path.join(sim_dir, 'properties.md')

    # Renderiza e registra a explicação textual da cena em paralelo à imagem.
    render_scene(scene, cam, W, H, img_path)
    md_text = explain_properties_md(props)
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    print(f'Wrote simulation {i:03d} -> {sim_dir}')


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--n_sim', type=int, default=5)
  parser.add_argument('--width', type=int, default=400)
  parser.add_argument('--height', type=int, default=300)
  parser.add_argument('--spp', type=int, default=16, help='Samples per pixel (AA)')
  parser.add_argument('--sampling_mode', choices=['jittered', 'stratified'], default='jittered')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  # Chamamos main com parâmetros e passamos AA para o render via render_scene
  out_root = os.path.join(os.getcwd(), 'outputs')
  os.makedirs(out_root, exist_ok=True)
  rng = random.Random()
  rng.seed(args.seed)

  W, H = args.width, args.height
  for i in range(args.n_sim):
    scene, props = build_random_scene(rng)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    sim_dir = os.path.join(out_root, f'sim_{ts}')
    os.makedirs(sim_dir, exist_ok=True)
    img_path = os.path.join(sim_dir, 'render.png')
    md_path = os.path.join(sim_dir, 'properties.md')
    render_scene(scene, cam=Camera(eye=glm.vec3(0,0,5), center=glm.vec3(0,0,0), up=glm.vec3(0,1,0), fov=45, width=W, height=H), W=W, H=H, out_path=img_path, samples_per_pixel=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)
    md_text = explain_properties_md(props)
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)
    print(f'Wrote simulation {i:03d} -> {sim_dir}')
