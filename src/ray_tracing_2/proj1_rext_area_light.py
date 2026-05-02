from __future__ import annotations

import argparse
from pyglm import glm
from ray_tracing_2.cli import (
  CommonRenderOptions,
  add_common_render_arguments,
  add_light_sampling_argument,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLightSamplingMode
from ray_tracing_2.proj1_scene_common import (
  add_rext_area_light,
  add_rext_area_light_emissive_panel,
  add_rext_area_light_objects,
  build_cornell_room,
  build_proj1_camera,
  build_proj1_scene,
)
from ray_tracing_2.render_estimator import run_render_with_estimation
from ray_tracing_2.render import Render


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 1,
  sampling_mode: str = SamplingMode.JITTERED.value,
  light_sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
  calibrate: bool = False,
  calibrate_only: bool = False,
  calibrate_grid: int = 16,
  calibrate_max_seconds: float = 5.0,
):
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
  build_cornell_room(scene)
  add_rext_area_light_objects(scene)
  # Estratégia de "dupla identidade": os slides cobrem a luz de área como fonte
  # amostrada e o shading local de Phong como resposta do material. Como a
  # arquitetura do projeto não acopla forma emissiva e fonte física na mesma
  # entidade, adicionamos explicitamente uma geometria emissiva visível e uma
  # AreaLight coincidente para iluminar os demais objetos.
  add_rext_area_light_emissive_panel(scene)
  add_rext_area_light(scene, sampling_mode=light_sampling_mode, seed=seed, samples_u=4, samples_v=4)

  renderer = Render()
  run_render_with_estimation(
    render=renderer,
    scene=scene,
    cam=camera,
    width=render_options.width,
    height=render_options.height,
    name='proj1_rext_area_light',
    samples_per_pixel=render_options.spp,
    sampling_mode=render_options.sampling_mode,
    seed=render_options.seed,
    gamma_fix=render_options.gamma_fix,
    estimator_options=render_options.to_estimator_options(),
  )


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render extension requirement: rectangular area light with selectable sampling distribution.',
    examples=[
      'python -m ray_tracing_2.proj1_rext_area_light --width 800 --height 600 --spp 1 --light_sampling_mode regular',
      'python -m ray_tracing_2.proj1_rext_area_light --width 800 --height 600 --spp 1 --light_sampling_mode uniform --seed 42',
      'python -m ray_tracing_2.proj1_rext_area_light --width 800 --height 600 --spp 1 --light_sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  add_light_sampling_argument(parser, default=AreaLightSamplingMode.STRATIFIED.value)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(
    **common_options.to_entrypoint_kwargs(include_calibration=True),
    light_sampling_mode=args.light_sampling_mode,
  )
