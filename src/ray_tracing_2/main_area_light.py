"""
Entrada principal para demonstrar luz de área e sombras suaves.

Este arquivo espelha a cena simples de `main.py`, mas substitui a
PointLight por uma `AreaLight` retangular, conforme os slides 14 a 23.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Plane, Sphere


def render(spp: int = 1, sampling_mode: str = 'jittered', seed: int | None = None, gamma_fix: bool = False):
  """Renderiza a cena com uma luz de área sobre a esfera e o plano."""
  W, H = 400, 300
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45.0, width=W, height=H)

  mat_red = PhongMaterial(
    ambient=glm.vec3(0.1, 0, 0),
    diffuse=glm.vec3(0.7, 0, 0),
    specular=glm.vec3(1, 1, 1),
    shininess=50.0,
  )
  mat_gray = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  scene = Scene()
  scene.objects.append(Sphere(center=glm.vec3(0, 0, 0), radius=1.0, material=mat_red))
  scene.objects.append(Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=mat_gray))

  # Luz de área retangular: origem + dois vetores de aresta.
  # A região cobre um retângulo acima e à frente da esfera para criar penumbra.
  scene.lights.append(
    AreaLight(
      p=glm.vec3(-1.0, 5.0, 4.0),
      e_u=glm.vec3(2.0, 0.0, 0.0),
      e_v=glm.vec3(0.0, 0.0, 2.0),
      power=glm.vec3(150.0),
      samples_u=4,
      samples_v=4,
      seed=seed,
    )
  )

  r = Render()
  r.render(
    scene=scene,
    cam=cam,
    width=W,
    height=H,
    name='main_area_light',
    samples_per_pixel=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  render(spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)