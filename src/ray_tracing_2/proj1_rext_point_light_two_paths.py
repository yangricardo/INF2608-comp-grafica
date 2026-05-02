from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.proj1_rext_point_light_luminaire import add_point_light_luminaire
from ray_tracing_2.proj1_scene_common import (
  add_rext_area_light_objects,
  build_proj1_camera,
  build_proj1_scene,
  green_wall_material,
  red_wall_material,
  white_wall_material,
)
from ray_tracing_2.render_estimator import run_render_with_estimation
from ray_tracing_2.render import Render
from ray_tracing_2.shape import Box


def build_cornell_room_with_ceiling_cutout(
  scene,
  *,
  opening_center: glm.vec3 = glm.vec3(2.775, 5.55, 2.775),
  opening_radius: float = 0.16,
) -> None:
  white = white_wall_material()
  red = red_wall_material()
  green = green_wall_material()

  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white)
  left_wall = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green)
  right_wall = Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white)

  x0 = max(0.0, opening_center.x - opening_radius)
  x1 = min(5.55, opening_center.x + opening_radius)
  z0 = max(0.0, opening_center.z - opening_radius)
  z1 = min(5.55, opening_center.z + opening_radius)
  y0 = 5.55
  y1 = 5.65

  ceiling_parts = [
    Box(p_min=glm.vec3(0.0, y0, 0.0), p_max=glm.vec3(x0, y1, 5.55), material=white),
    Box(p_min=glm.vec3(x1, y0, 0.0), p_max=glm.vec3(5.55, y1, 5.55), material=white),
    Box(p_min=glm.vec3(x0, y0, 0.0), p_max=glm.vec3(x1, y1, z0), material=white),
    Box(p_min=glm.vec3(x0, y0, z1), p_max=glm.vec3(x1, y1, 5.55), material=white),
  ]

  scene.objects.extend([front_wall, left_wall, right_wall, floor, *ceiling_parts])


def render_variant(
  *,
  variant: str,
  width: int,
  height: int,
  spp: int,
  sampling_mode: str,
  seed: int | None,
  gamma_fix: bool,
  calibrate: bool,
  calibrate_only: bool,
  calibrate_grid: int,
  calibrate_max_seconds: float,
) -> None:
  render_options = CommonRenderOptions(
    width=width,
    height=height,
    spp=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
    calibrate=calibrate,
    calibrate_only=calibrate_only,
    calibrate_grid=calibrate_grid,
    calibrate_max_seconds=calibrate_max_seconds,
  )
  camera = build_proj1_camera(render_options.width, render_options.height)
  scene = build_proj1_scene(ambient=glm.vec3(0.02, 0.02, 0.02), max_depth=3)

  if variant == 'ceiling_cutout':
    build_cornell_room_with_ceiling_cutout(scene)
    add_point_light_luminaire(scene, pos=glm.vec3(2.775, 5.55, 2.775))
  else:
    from ray_tracing_2.proj1_scene_common import build_cornell_room
    build_cornell_room(scene)
    add_point_light_luminaire(scene, pos=glm.vec3(2.775, 5.40, 2.775))

  add_rext_area_light_objects(scene)

  renderer = Render()
  run_render_with_estimation(
    render=renderer,
    scene=scene,
    cam=camera,
    width=render_options.width,
    height=render_options.height,
    name=f'proj1_rext_point_light_{variant}',
    samples_per_pixel=render_options.spp,
    sampling_mode=render_options.sampling_mode,
    seed=render_options.seed,
    gamma_fix=render_options.gamma_fix,
    estimator_options=render_options.to_estimator_options(),
  )


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 1,
  sampling_mode: str = SamplingMode.JITTERED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
  calibrate: bool = True,
  calibrate_only: bool = False,
  calibrate_grid: int = 16,
  calibrate_max_seconds: float = 5.0,
  variant: str = 'both',
):
  variants = ['lowered', 'ceiling_cutout'] if variant == 'both' else [variant]
  for item in variants:
    render_variant(
      variant=item,
      width=width,
      height=height,
      spp=spp,
      sampling_mode=sampling_mode,
      seed=seed,
      gamma_fix=gamma_fix,
      calibrate=calibrate,
      calibrate_only=calibrate_only,
      calibrate_grid=calibrate_grid,
      calibrate_max_seconds=calibrate_max_seconds,
    )


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render both remediation paths for the point-light luminaire example.',
    examples=[
      'python -m ray_tracing_2.proj1_rext_point_light_two_paths --width 800 --height 600 --spp 1 --variant both',
      'python -m ray_tracing_2.proj1_rext_point_light_two_paths --width 800 --height 600 --spp 1 --variant lowered',
      'python -m ray_tracing_2.proj1_rext_point_light_two_paths --width 800 --height 600 --spp 1 --variant ceiling_cutout',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  parser.add_argument(
    '--variant',
    choices=['both', 'lowered', 'ceiling_cutout'],
    default='both',
    help='Choose which remediation path to render.',
  )
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(
    **common_options.to_entrypoint_kwargs(include_calibration=True),
    variant=args.variant,
  )