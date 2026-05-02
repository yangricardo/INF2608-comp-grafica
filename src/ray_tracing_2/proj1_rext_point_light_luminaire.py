from __future__ import annotations

import argparse
from pyglm import glm
from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import PointLight
from ray_tracing_2.material import EmissiveMaterial
from ray_tracing_2.proj1_scene_common import (
  add_rext_area_light_objects,
  build_cornell_room,
  build_proj1_camera,
  build_proj1_scene,
)
from ray_tracing_2.render import Render
from ray_tracing_2.shape import Sphere


POINT_LUMINAIRE_POS = glm.vec3(2.775, 5.55, 2.775)
POINT_LUMINAIRE_POWER = glm.vec3(0.7, 0.7, 0.7)
POINT_LUMINAIRE_RADIUS = 0.1


def add_point_light_luminaire(
  scene,
  *,
  pos: glm.vec3 = POINT_LUMINAIRE_POS,
  power: glm.vec3 = POINT_LUMINAIRE_POWER,
  radius: float = POINT_LUMINAIRE_RADIUS,
  emission: glm.vec3 = glm.vec3(1.0, 0.98, 0.95),
) -> None:
  # Segue diretamente o exemplo-base do enunciado: PointLight no teto da sala
  # Cornell, com uma esfera pequena coincidente para tornar a luminária visível.
  scene.lights.append(PointLight(pos=glm.vec3(pos), power=glm.vec3(power)))
  scene.objects.append(
    Sphere(
      center=glm.vec3(pos),
      radius=radius,
      material=EmissiveMaterial(emission=emission, shadow_passthrough=True),
    )
  )


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 1,
  sampling_mode: str = SamplingMode.JITTERED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
):
  render_options = CommonRenderOptions(
    width=width,
    height=height,
    spp=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )
  camera = build_proj1_camera(render_options.width, render_options.height)
  scene = build_proj1_scene(ambient=glm.vec3(0.02, 0.02, 0.02), max_depth=3)
  build_cornell_room(scene)
  add_rext_area_light_objects(scene)
  add_point_light_luminaire(scene)

  renderer = Render()
  renderer.render(scene=scene, cam=camera, **render_options.to_render_kwargs(name='proj1_rext_point_light_luminaire'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render extension example: point light with visible spherical luminaire.',
    examples=[
      'python -m ray_tracing_2.proj1_rext_point_light_luminaire --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.proj1_rext_point_light_luminaire --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())