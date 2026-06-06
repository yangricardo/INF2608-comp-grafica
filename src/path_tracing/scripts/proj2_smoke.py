#!/usr/bin/env python3
"""Smoke test da Etapa 01: Renderiza esfera com normal-as-color (ray-cast).

Uso:
  python -m path_tracing.scripts.proj2_smoke --out out/proj2/smoke
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from pyglm import glm
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.scene import Scene
from path_tracing.camera import Camera
from path_tracing.shape import Sphere
from path_tracing.bsdf.lambertian import LambertianBSDF


def render_smoke_test(width: int, height: int, out_root: str = 'out/proj2/smoke') -> str:
  """Renderiza esfera com normal-as-color (ray-cast primário, sem integrador).

  Cor = (n + 1) / 2 mapeia normal em [-1,1]^3 para [0,1]^3.
  Ref: Etapa 01 boilerplate smoke test; PBRT 4e para.1.1 Ray Casting.
  """
  scene = Scene()
  scene.objects.append(Sphere(
    center=glm.vec3(0, 0, 0),
    radius=1.0,
    material=LambertianBSDF(glm.vec3(1.0)),
  ))

  camera = Camera(
    eye=glm.vec3(0, 0, 3),
    center=glm.vec3(0, 0, 0),
    up=glm.vec3(0, 1, 0),
    fov=60.0,
    width=width,
    height=height,
    focal_distance=1.0,
  )

  pixels: list[int] = []
  for j in range(height):
    for i in range(width):
      xn = (i + 0.5) / width
      yn = (j + 0.5) / height
      hit = scene.compute_intersection(camera.generate_ray(xn, yn))
      if hit is not None:
        c = (hit.normal + glm.vec3(1.0)) * 0.5
      else:
        c = glm.vec3(0.1)
      pixels += [
        int(min(255, max(0, round(c.x * 255)))),
        int(min(255, max(0, round(c.y * 255)))),
        int(min(255, max(0, round(c.z * 255)))),
      ]
    if (j + 1) % max(1, height // 4) == 0:
      print(f'  Renderizacao: {(j + 1) / height * 100:.0f}%')

  img = Image.frombytes('RGB', (width, height), bytes(pixels))

  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  out_dir = Path(out_root) / f'proj2_smoke_{timestamp}'
  out_dir.mkdir(parents=True, exist_ok=True)
  out_path = out_dir / 'render.png'
  img.save(str(out_path))

  print(f'Smoke test renderizado: {out_path}')
  return str(out_dir)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Smoke test da Etapa 01 — esfera com normal-as-color (ray-cast primario)',
  )
  parser.add_argument('--width', type=int, default=256, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=256, help='Altura da imagem')
  parser.add_argument('--out', type=str, default='out/proj2/smoke', help='Diretorio raiz de saida')
  args = parser.parse_args()
  render_smoke_test(args.width, args.height, args.out)
