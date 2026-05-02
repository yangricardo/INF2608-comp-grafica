from __future__ import annotations

import argparse
from pyglm import glm
from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.proj1_scene_common import (
  add_req4_sampling_lights,
  add_req4_sampling_objects,
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
  scene = build_proj1_scene(ambient=glm.vec3(0.015, 0.015, 0.015), max_depth=2)
  build_cornell_room(scene)
  add_req4_sampling_objects(scene)
  add_req4_sampling_lights(scene)

  renderer = Render()
  renderer.render(scene=scene, cam=camera, **render_options.to_render_kwargs(name='proj1_req4_sampling'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render requirement-4 scene to compare single-sample and multi-sample behavior with the same camera framing.',
    examples=[
      'python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 1 --sampling_mode center',
      'python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 4 --sampling_mode jittered --seed 42',
      'python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())
