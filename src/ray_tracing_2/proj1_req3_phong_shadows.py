from __future__ import annotations

import argparse

from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.proj1_scene_common import add_req3_phong_objects, add_req3_phong_shadow_lights, build_cornell_room, build_proj1_camera, build_proj1_scene
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
  scene = build_proj1_scene(ambient=(0.02, 0.02, 0.02), max_depth=2)
  build_cornell_room(scene)
  add_req3_phong_objects(scene)
  add_req3_phong_shadow_lights(scene)

  renderer = Render()
  renderer.render(scene=scene, cam=camera, **render_options.to_render_kwargs(name='proj1_req3_phong_shadows'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render requirement-3 scene with direct Phong shading and visible shadows using point lights.',
    examples=[
      'python -m ray_tracing_2.proj1_req3_phong_shadows --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.proj1_req3_phong_shadows --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())
