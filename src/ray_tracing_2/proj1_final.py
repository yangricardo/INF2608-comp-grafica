from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.cli import (
  CommonRenderOptions,
  add_common_render_arguments,
  add_light_sampling_argument,
  add_max_depth_argument,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLight, AreaLightSamplingMode, PointLight
from ray_tracing_2.material import EmissiveMaterial, PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.proj1_scene_common import build_proj1_camera, build_proj1_scene
from ray_tracing_2.render import Render
from ray_tracing_2.render_estimator import run_render_with_estimation
from ray_tracing_2.shape import Box, Instance, Sphere, Translate, Rotate, TriangleMesh


def _build_room(scene) -> None:
  mirror = ReflectiveMaterial(
    ambient=glm.vec3(0.05),
    diffuse=glm.vec3(0.30),
    specular=glm.vec3(0.35),
    shininess=96.0,
    reflectivity=glm.vec3(0.70),
  )
  left_diffuse = PhongMaterial(
    ambient=glm.vec3(0.03, 0.05, 0.03),
    diffuse=glm.vec3(0.12, 0.72, 0.15),
    specular=glm.vec3(0.03),
    shininess=6.0,
  )
  right_specular = PhongMaterial(
    ambient=glm.vec3(0.05, 0.02, 0.02),
    diffuse=glm.vec3(0.55, 0.12, 0.12),
    specular=glm.vec3(0.95),
    shininess=180.0,
  )
  floor = PhongMaterial(
    ambient=glm.vec3(0.03),
    diffuse=glm.vec3(0.68),
    specular=glm.vec3(0.08),
    shininess=18.0,
  )

  scene.objects.extend([
    # Parede de fundo espelhada.
    Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=mirror),
    Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=left_diffuse),
    Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=right_specular),
    # Teto espelhado.
    Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=mirror),
    Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=floor),
  ])


def _add_original_blocks(scene) -> None:
  small_glass = TransparentMaterial(ior=1.5, attenuation=glm.vec3(0.86, 0.92, 0.98))
  large_mirror = ReflectiveMaterial(
    ambient=glm.vec3(0.04),
    diffuse=glm.vec3(0.25),
    specular=glm.vec3(0.25),
    shininess=80.0,
    reflectivity=glm.vec3(0.72),
  )

  small_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 1.65, 0.30), material=small_glass)
  small_block = Rotate(angle_deg=-18.0, x=0, y=1, z=0, shape=small_block)
  small_block = Translate(3.40, 1.2, 5.65, small_block)

  large_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 3.30, 1.65), material=large_mirror)
  large_block = Rotate(angle_deg=22.5, x=0, y=1, z=0, shape=large_block)
  large_block = Translate(0.65, 0.0, 1.30, large_block)

  scene.objects.extend([small_block, large_block])


def _add_diamond_pyramid(scene) -> None:
  center = glm.vec3(2.45, 1.05, 4.25)
  half = 0.55
  equator = [
    glm.vec3(center.x - half, center.y, center.z),
    glm.vec3(center.x, center.y, center.z + half),
    glm.vec3(center.x + half, center.y, center.z),
    glm.vec3(center.x, center.y, center.z - half),
  ]
  top = glm.vec3(center.x, center.y + 0.95, center.z)
  bottom = glm.vec3(center.x, center.y - 0.95, center.z)

  top_material = ReflectiveMaterial(
    ambient=glm.vec3(0.03),
    diffuse=glm.vec3(0.18),
    specular=glm.vec3(0.30),
    shininess=120.0,
    reflectivity=glm.vec3(0.80),
  )
  bottom_material = TransparentMaterial(
    ior=1.52,
    attenuation=glm.vec3(0.90, 0.95, 0.98),
  )

  top_vertices = [*equator, top]
  top_faces = [
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4),
  ]
  bottom_vertices = [*equator, bottom]
  bottom_faces = [
    (1, 0, 4),
    (2, 1, 4),
    (3, 2, 4),
    (0, 3, 4),
  ]

  scene.objects.extend([
    TriangleMesh.from_vertices_faces(top_vertices, top_faces, top_material, name='diamond_top_reflective'),
    TriangleMesh.from_vertices_faces(bottom_vertices, bottom_faces, bottom_material, name='diamond_bottom_transparent'),
  ])


def _add_transparent_ellipse(scene) -> None:
  glass = TransparentMaterial(ior=1.48, attenuation=glm.vec3(0.93, 0.97, 1.0))
  sphere = Sphere(center=glm.vec3(4.25, 1.05, 3.55), radius=1.0, material=glass)
  matrix = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
  matrix = glm.scale(matrix, glm.vec3(0.55, 1.10, 0.42))
  scene.objects.append(Instance(sphere, matrix))


def _add_triangle_ceiling_lights(scene) -> None:
  light_positions = [
    glm.vec3(2.775, 5.48, 1.40),
    glm.vec3(1.55, 5.48, 3.95),
    glm.vec3(4.00, 5.48, 3.95),
  ]
  light_powers = [
    glm.vec3(0.65, 0.65, 0.62),
    glm.vec3(0.55, 0.62, 0.72),
    glm.vec3(0.72, 0.60, 0.55),
  ]
  for pos, power in zip(light_positions, light_powers):
    scene.lights.append(PointLight(pos=pos, power=power))
    scene.objects.append(
      Sphere(
        center=pos,
        radius=0.09,
        material=EmissiveMaterial(emission=glm.vec3(1.0, 0.98, 0.95), shadow_passthrough=True),
      )
    )


def _add_back_camera_area_light(
  scene,
  *,
  light_sampling_mode: str,
  seed: int | None,
) -> None:
  scene.lights.append(
    AreaLight(
      p=glm.vec3(1.20, 1.95, 13.45),
      e_u=glm.vec3(3.10, 0.0, 0.0),
      e_v=glm.vec3(0.0, 2.35, 0.0),
      power=glm.vec3(85.0, 85.0, 85.0),
      samples_u=3,
      samples_v=3,
      sampling_mode=light_sampling_mode,
      seed=seed,
    )
  )


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 1,
  sampling_mode: str = SamplingMode.JITTERED.value,
  light_sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
  calibrate: bool = True,
  calibrate_only: bool = False,
  calibrate_grid: int = 16,
  calibrate_max_seconds: float = 5.0,
  max_depth: int = 8,
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
  scene = build_proj1_scene(ambient=glm.vec3(0.02, 0.02, 0.02), max_depth=max_depth)

  _build_room(scene)
  _add_original_blocks(scene)
  _add_diamond_pyramid(scene)
  _add_transparent_ellipse(scene)
  _add_triangle_ceiling_lights(scene)
  _add_back_camera_area_light(
    scene,
    light_sampling_mode=light_sampling_mode,
    seed=seed,
  )

  renderer = Render()
  run_render_with_estimation(
    render=renderer,
    scene=scene,
    cam=camera,
    width=render_options.width,
    height=render_options.height,
    name='proj1_final',
    samples_per_pixel=render_options.spp,
    sampling_mode=render_options.sampling_mode,
    seed=render_options.seed,
    gamma_fix=render_options.gamma_fix,
    estimator_options=render_options.to_estimator_options(),
  )


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render final project scene combining reflective, refractive and area-light effects.',
    examples=[
      'python -m ray_tracing_2.proj1_final --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.proj1_final --width 800 --height 600 --spp 4 --sampling_mode stratified --light_sampling_mode stratified --seed 42',
      'python -m ray_tracing_2.proj1_final --calibrate-only',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  add_light_sampling_argument(parser, help_text='Sampling mode for the back-camera area light')
  add_max_depth_argument(parser, default=8)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(
    **common_options.to_entrypoint_kwargs(include_calibration=True),
    light_sampling_mode=args.light_sampling_mode,
    max_depth=args.max_depth,
  )