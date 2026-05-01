"""
Entrada principal para demonstrar luz de área e sombras suaves.

Este arquivo espelha a cena simples de `main.py`, mas substitui a
PointLight por uma `AreaLight` retangular, conforme os slides 14 a 23.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.cli import (
  add_gamma_fix_argument,
  add_image_size_arguments,
  add_light_sampling_argument,
  add_sampling_arguments,
  add_seed_argument,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLight, AreaLightSamplingMode
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Plane, Sphere


def render(width: int = 400,
           height: int = 300,
           spp: int = 1,
           sampling_mode: str = SamplingMode.JITTERED.value,
           light_sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
           seed: int | None = None,
           gamma_fix: bool = False):
  """Renderiza a cena com uma luz de área sobre a esfera e o plano."""
  W, H = int(width), int(height)
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
  # `light_sampling_mode` permite comparar regular, uniform e stratified.
  scene.lights.append(
    AreaLight(
      p=glm.vec3(-1.0, 5.0, 4.0),
      e_u=glm.vec3(2.0, 0.0, 0.0),
      e_v=glm.vec3(0.0, 0.0, 2.0),
      power=glm.vec3(150.0),
      samples_u=4,
      samples_v=4,
      sampling_mode=light_sampling_mode,
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


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render the area-light demo scene with separate film and light sampling controls.',
    examples=[
      'python -m ray_tracing_2.main_area_light --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.main_area_light --width 800 --height 600 --spp 1 --sampling_mode stratified --light_sampling_mode regular --seed 42',
    ],
  )
  add_image_size_arguments(parser, width_default=400, height_default=300)
  add_sampling_arguments(parser, spp_default=1)
  add_light_sampling_argument(parser, help_text='Sampling mode for the area light')
  add_seed_argument(parser)
  add_gamma_fix_argument(parser)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  render(width=args.width, height=args.height, spp=args.spp, sampling_mode=args.sampling_mode, light_sampling_mode=args.light_sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)