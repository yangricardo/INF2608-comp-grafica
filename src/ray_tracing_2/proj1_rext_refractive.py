from __future__ import annotations

import argparse
from pyglm import glm
from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.proj1_scene_common import (
  add_rext_refractive_objects,
  add_rext_reflective_refractive_lights,
  build_cornell_room,
  build_proj1_camera,
  build_proj1_scene,
)
from ray_tracing_2.render import Render


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
  scene = build_proj1_scene(ambient=glm.vec3(0.03, 0.03, 0.03), max_depth=8)
  build_cornell_room(scene)
  add_rext_refractive_objects(scene)
  add_rext_reflective_refractive_lights(scene)

  renderer = Render()
  renderer.render(scene=scene, cam=camera, **render_options.to_render_kwargs(name='proj1_rext_refractive'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render extension requirement: refractive objects (TransparentMaterial with Snell refraction and Beer-Lambert attenuation).',
    examples=[
      'python -m ray_tracing_2.proj1_rext_refractive --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.proj1_rext_refractive --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())
