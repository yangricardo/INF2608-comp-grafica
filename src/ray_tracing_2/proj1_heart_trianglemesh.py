from __future__ import annotations

import argparse
import math

from pyglm import glm

from ray_tracing_2.cli import CommonRenderOptions, add_common_render_arguments, build_parser
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.material import EmissiveMaterial, ReflectiveMaterial
from ray_tracing_2.proj1_scene_common import add_req2_point_lights, build_cornell_room, build_proj1_camera, build_proj1_scene
from ray_tracing_2.render import Render
from ray_tracing_2.render_estimator import run_render_with_estimation
from ray_tracing_2.shape import Sphere, TriangleMesh


LIGHT_POSITIONS = [
  glm.vec3(1.25, 5.20, 1.35),
  glm.vec3(4.35, 4.85, 2.55),
  glm.vec3(2.75, 5.45, 4.85),
]


def _heart_curve_point(t: float, scale: float) -> glm.vec2:
  x = 16.0 * math.sin(t) ** 3
  y = 13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t) - math.cos(4.0 * t)
  return glm.vec2(x * scale, y * scale)


def _build_heart_mesh(
  *,
  center: glm.vec3,
  scale: float = 0.055,
  thickness: float = 0.70,
  segments: int = 36,
) -> tuple[list[glm.vec3], list[tuple[int, int, int]]]:
  front: list[glm.vec3] = []
  back: list[glm.vec3] = []
  for i in range(segments):
    t = (2.0 * math.pi * i) / segments
    p = _heart_curve_point(t, scale)
    front.append(glm.vec3(center.x + p.x, center.y + p.y, center.z + thickness * 0.5))
    back.append(glm.vec3(center.x + p.x, center.y + p.y, center.z - thickness * 0.5))

  front_center = glm.vec3(center.x, center.y, center.z + thickness * 0.5)
  back_center = glm.vec3(center.x, center.y, center.z - thickness * 0.5)

  vertices: list[glm.vec3] = [*front, *back, front_center, back_center]
  faces: list[tuple[int, int, int]] = []
  back_offset = segments
  front_center_idx = segments * 2
  back_center_idx = segments * 2 + 1

  for i in range(segments):
    j = (i + 1) % segments
    # Face frontal.
    faces.append((front_center_idx, j, i))
    # Face traseira.
    faces.append((back_center_idx, back_offset + i, back_offset + j))
    # Faces laterais para fechar o volume.
    faces.append((i, j, back_offset + j))
    faces.append((i, back_offset + j, back_offset + i))

  return vertices, faces


def _rotate_vertices_y(vertices: list[glm.vec3], center: glm.vec3, angle_deg: float) -> list[glm.vec3]:
  angle = math.radians(angle_deg)
  c = math.cos(angle)
  s = math.sin(angle)
  rotated: list[glm.vec3] = []
  for v in vertices:
    local = v - center
    x = local.x * c + local.z * s
    z = -local.x * s + local.z * c
    rotated.append(glm.vec3(center.x + x, v.y, center.z + z))
  return rotated


def _add_visible_point_luminaires(scene) -> None:
  luminaire = EmissiveMaterial(emission=glm.vec3(1.0, 0.95, 0.90), shadow_passthrough=True)
  for pos in LIGHT_POSITIONS:
    scene.objects.append(Sphere(center=pos, radius=0.07, material=luminaire))


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 4,
  sampling_mode: str = SamplingMode.JITTERED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
  calibrate: bool = True,
  calibrate_only: bool = False,
  calibrate_grid: int = 16,
  calibrate_max_seconds: float = 5.0,
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

  scene = build_proj1_scene(ambient=glm.vec3(0.03, 0.03, 0.03), max_depth=4)
  camera = build_proj1_camera(render_options.width, render_options.height)

  build_cornell_room(scene)
  add_req2_point_lights(scene)
  _add_visible_point_luminaires(scene)

  heart_material = ReflectiveMaterial(
    ambient=glm.vec3(0.07, 0.01, 0.02),
    diffuse=glm.vec3(0.30, 0.05, 0.10),
    specular=glm.vec3(0.65),
    shininess=140.0,
    reflectivity=glm.vec3(0.62, 0.55, 0.58),
  )
  heart_center = glm.vec3(2.775, 2.90, 2.775)
  vertices, faces = _build_heart_mesh(center=heart_center, scale=0.055, thickness=0.70, segments=36)
  vertices = _rotate_vertices_y(vertices, center=heart_center, angle_deg=24.0)
  heart_mesh = TriangleMesh.from_vertices_faces(
    vertices,
    faces,
    heart_material,
    name='floating_heart',
    accelerator='bvh',
  )
  scene.objects.append(heart_mesh)

  renderer = Render()
  run_render_with_estimation(
    render=renderer,
    scene=scene,
    cam=camera,
    width=render_options.width,
    height=render_options.height,
    name='proj1_heart_trianglemesh',
    samples_per_pixel=render_options.spp,
    sampling_mode=render_options.sampling_mode,
    seed=render_options.seed,
    gamma_fix=render_options.gamma_fix,
    estimator_options=render_options.to_estimator_options(),
  )


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render Cornell Box with a centered floating heart modeled as TriangleMesh and lit by three point lights.',
    examples=[
      'python -m ray_tracing_2.proj1_heart_trianglemesh --width 800 --height 600 --spp 4',
      'python -m ray_tracing_2.proj1_heart_trianglemesh --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42',
      'python -m ray_tracing_2.proj1_heart_trianglemesh --calibrate-only',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=4)
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs(include_calibration=True))
