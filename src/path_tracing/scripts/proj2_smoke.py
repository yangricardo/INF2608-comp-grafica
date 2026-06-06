#!/usr/bin/env python3
"""Smoke test da Etapa 01: Renderiza esfera com normal-as-color (ray-cast).

Uso:
  python -m path_tracing.scripts.proj2_smoke --spp 1 --out out/smoke
"""

import sys
import argparse
from pathlib import Path

from pyglm import glm
import numpy as np
from PIL import Image

# Adiciona src ao path se necessário
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.scene import Scene
from path_tracing.camera import Camera
from path_tracing.shape import Sphere
from path_tracing.bsdf.lambertian import LambertianBSDF
from path_tracing.ray import Ray
from path_tracing.film import Film


def render_smoke_test(width: int, height: int, out_dir: str | None = None) -> str:
  """Renderiza esfera com normal-as-color (ray-cast primário).
  
  Referência:
    - Etapa 01: boilerplate + smoke test
    - Técnica: ray-cast com cor = (n+1)/2
  """
  # Cena
  scene = Scene()
  
  # Esfera unitária na origem
  sphere = Sphere(
    center=glm.vec3(0, 0, 0),
    radius=1.0,
    material=LambertianBSDF(glm.vec3(1.0)),  # Material não importa para smoke test
  )
  scene.objects.append(sphere)
  
  # Câmera
  camera = Camera(
    eye=glm.vec3(0, 0, 3),
    center=glm.vec3(0, 0, 0),
    up=glm.vec3(0, 1, 0),
    fov=60.0,
    width=width,
    height=height,
    focal_distance=1.0,
  )
  
  # Renderizar manualmente (ray-cast, sem integrador)
  image = np.zeros((height, width, 3), dtype=np.float32)
  
  for j in range(height):
    for i in range(width):
      xn = (i + 0.5) / width
      yn = (j + 0.5) / height
      
      ray = camera.generate_ray(xn, yn)
      hit = scene.compute_intersection(ray)
      
      if hit is not None:
        # Normal como cor: (n+1)/2
        color = (hit.normal + glm.vec3(1.0)) / 2.0
      else:
        # Fundo cinza escuro
        color = glm.vec3(0.1)
      
      image[j, i] = [color.x, color.y, color.z]
    
    if (j + 1) % 50 == 0:
      print(f"  {(j + 1) / height * 100:.1f}%", file=sys.stderr)
  
  # Salvar PNG
  out_path = Path(out_dir) if out_dir else Path("output_smoke.png")
  out_path.parent.mkdir(parents=True, exist_ok=True)
  
  img_uint8 = (np.clip(image, 0, 1) * 255).astype(np.uint8)
  pil_img = Image.fromarray(img_uint8, 'RGB')
  pil_img.save(str(out_path))
  
  print(f"Smoke test renderizado: {out_path}")
  return str(out_path)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Smoke test da Etapa 01 — renderiza esfera com normal-as-color (ray-cast)',
  )
  parser.add_argument('--width', type=int, default=256, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=256, help='Altura da imagem')
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (não usado em smoke test)')
  parser.add_argument('--out', type=str, default=None, help='Diretório de saída')
  
  args = parser.parse_args()
  
  render_smoke_test(args.width, args.height, args.out)
