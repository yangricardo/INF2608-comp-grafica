"""
Entrada principal para demonstrar instanciação de objetos com `Instance`.

Este arquivo replica a cena simples de `main.py`, mas transforma a esfera
unitária em um elipsoide por meio de uma matriz de escala não uniforme.
Isso mostra, na prática, a ideia dos slides 9 a 13 sobre instanciação.
"""

from __future__ import annotations

import argparse

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
from ray_tracing_2.shape import Instance, Plane, Sphere


def render(width: int = 400,
           height: int = 300,
           spp: int = 1,
           sampling_mode: str = SamplingMode.JITTERED.value,
           seed: int | None = None,
           gamma_fix: bool = False):
  """Renderiza um elipsoide instanciado a partir de uma esfera unitária."""
  render_options = CommonRenderOptions(
    width=width,
    height=height,
    spp=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )
  W, H = render_options.width, render_options.height
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
  base_sphere = Sphere(center=glm.vec3(0, 0, 0), radius=1.0, material=mat_red)
  scale_matrix = glm.scale(glm.mat4(1.0), glm.vec3(0.5, 0.95, 0.5))
  ellipsoid = Instance(base_sphere, scale_matrix)

  scene.objects.append(ellipsoid)
  scene.objects.append(Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=mat_gray))
  scene.lights.append(PointLight(pos=glm.vec3(0, 5, 0), power=glm.vec3(150.0)))

  r = Render()
  r.render(scene=scene, cam=cam, **render_options.to_render_kwargs(name='main_ellipse'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render the instanced ellipsoid demo scene.',
    examples=[
      'python -m ray_tracing_2.main_ellipse --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.main_ellipse --width 800 --height 600 --spp 1 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=400, height_default=300, spp_default=1)
  return parser


if __name__ == "__main__":
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())