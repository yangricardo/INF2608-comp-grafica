from __future__ import annotations

from dataclasses import dataclass

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.material import PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Instance, Sphere


@dataclass(frozen=True)
class Proj1CameraConfig:
  eye: tuple[float, float, float] = (2.775, 3.200, 12.775)
  center: tuple[float, float, float] = (2.775, 2.775, 2.775)
  up: tuple[float, float, float] = (0.0, 1.0, 0.0)
  fov: float = 50.0
  focal_distance: float = 1.0


CANONICAL_CAMERA = Proj1CameraConfig()


def build_proj1_camera(width: int, height: int, config: Proj1CameraConfig = CANONICAL_CAMERA) -> Camera:
  return Camera(
    eye=glm.vec3(*config.eye),
    center=glm.vec3(*config.center),
    up=glm.vec3(*config.up),
    fov=config.fov,
    width=width,
    height=height,
    focal_distance=config.focal_distance,
  )


def _translate_rotate_y(tx: float, ty: float, tz: float, ry_deg: float = 0.0) -> glm.mat4:
  ry = glm.radians(ry_deg)
  c = glm.cos(ry)
  s = glm.sin(ry)

  matrix = glm.mat4(1.0)
  matrix[0][0] = c
  matrix[0][2] = -s
  matrix[1][1] = 1.0
  matrix[2][0] = s
  matrix[2][2] = c
  matrix[3][0] = tx
  matrix[3][1] = ty
  matrix[3][2] = tz
  return matrix


def build_block_material(kind: str):
  if kind == 'reflective':
    return ReflectiveMaterial(
      ambient=glm.vec3(0.03),
      diffuse=glm.vec3(0.25),
      specular=glm.vec3(0.05),
      shininess=32.0,
      reflectivity=glm.vec3(0.55),
    )
  if kind == 'transparent':
    return TransparentMaterial(
      ior=1.5,
      attenuation=glm.vec3(0.8, 0.9, 0.8),
    )
  return PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def white_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def red_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def green_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def build_cornell_room(scene: Scene) -> None:
  white = white_wall_material()
  red = red_wall_material()
  green = green_wall_material()

  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white)
  left_wall = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green)
  right_wall = Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])


def build_proj1_scene(*, ambient: glm.vec3 = glm.vec3(0.18, 0.18, 0.18), max_depth: int = 4) -> Scene:
  return Scene(ambient_light=AmbientLight(ambient), max_depth=max_depth)


def add_ceiling_point_light(scene: Scene, *, power: glm.vec3 = glm.vec3(0.8, 0.8, 0.8), y: float = 5.45) -> None:
  scene.lights.append(PointLight(pos=glm.vec3(2.775, y, 2.775), power=power))


def add_req1_geometry_objects(scene: Scene) -> None:
  large_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 3.30, 1.65),
    material=build_block_material('opaque'),
  )
  small_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.65, 0.30),
    material=build_block_material('opaque'),
  )

  scene.objects.extend([
    Instance(large_box, _translate_rotate_y(0.65, 0.0, 1.30, ry_deg=22.5)),
    Instance(small_box, _translate_rotate_y(3.40, 0.0, 3.65, ry_deg=-18.0)),
    Sphere(center=glm.vec3(3.95, 0.65, 4.65), radius=0.65, material=build_block_material('opaque')),
  ])


def add_req2_light_probe_objects(scene: Scene) -> None:
  neutral = PhongMaterial(
    ambient=glm.vec3(0.03),
    diffuse=glm.vec3(0.70),
    specular=glm.vec3(0.15),
    shininess=20.0,
  )
  glossy = PhongMaterial(
    ambient=glm.vec3(0.02),
    diffuse=glm.vec3(0.35),
    specular=glm.vec3(0.55),
    shininess=96.0,
  )

  scene.objects.extend([
    Sphere(center=glm.vec3(1.45, 0.65, 4.10), radius=0.65, material=neutral),
    Sphere(center=glm.vec3(3.95, 0.65, 3.95), radius=0.65, material=glossy),
    Box(
      p_min=glm.vec3(2.25, 0.0, 1.75),
      p_max=glm.vec3(3.20, 1.65, 2.65),
      material=build_block_material('opaque'),
    ),
  ])


def add_req3_phong_objects(scene: Scene) -> None:
  matte_red = PhongMaterial(
    ambient=glm.vec3(0.06, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.10, 0.10),
    specular=glm.vec3(0.05),
    shininess=16.0,
  )
  glossy_blue = PhongMaterial(
    ambient=glm.vec3(0.0, 0.02, 0.07),
    diffuse=glm.vec3(0.20, 0.25, 0.75),
    specular=glm.vec3(0.60),
    shininess=120.0,
  )

  low_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.10, 1.65),
    material=matte_red,
  )
  tall_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.10, 2.30, 1.10),
    material=glossy_blue,
  )

  scene.objects.extend([
    Instance(low_box, _translate_rotate_y(0.85, 0.0, 1.10, ry_deg=18.0)),
    Instance(tall_box, _translate_rotate_y(3.25, 0.0, 2.85, ry_deg=-16.0)),
    Sphere(center=glm.vec3(2.10, 0.62, 4.25), radius=0.62, material=matte_red),
  ])


def add_req2_point_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(1.25, 5.20, 1.35), power=glm.vec3(0.75, 0.68, 0.62)),
    PointLight(pos=glm.vec3(4.35, 4.85, 2.55), power=glm.vec3(0.45, 0.50, 0.65)),
    PointLight(pos=glm.vec3(2.75, 5.45, 4.85), power=glm.vec3(0.35, 0.35, 0.32)),
  ])


def add_req3_phong_shadow_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(2.85, 5.40, 2.35), power=glm.vec3(0.95, 0.95, 0.95)),
    PointLight(pos=glm.vec3(1.35, 3.55, 4.95), power=glm.vec3(0.25, 0.28, 0.32)),
  ])


def add_req4_sampling_objects(scene: Scene) -> None:
  edge_white = PhongMaterial(
    ambient=glm.vec3(0.02),
    diffuse=glm.vec3(0.85),
    specular=glm.vec3(0.02),
    shininess=8.0,
  )
  edge_black = PhongMaterial(
    ambient=glm.vec3(0.0),
    diffuse=glm.vec3(0.03),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  thin_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(2.80, 0.95, 0.12),
    material=edge_black,
  )
  tall_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(0.55, 2.60, 0.55),
    material=edge_white,
  )

  scene.objects.extend([
    Instance(thin_box, _translate_rotate_y(1.05, 0.0, 2.65, ry_deg=-24.0)),
    Instance(tall_box, _translate_rotate_y(3.75, 0.0, 1.85, ry_deg=9.0)),
    Sphere(center=glm.vec3(2.05, 0.45, 4.35), radius=0.45, material=edge_white),
    Sphere(center=glm.vec3(2.75, 0.45, 4.75), radius=0.45, material=edge_black),
  ])


def add_req4_sampling_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(2.75, 5.45, 2.75), power=glm.vec3(0.85, 0.85, 0.85)),
    PointLight(pos=glm.vec3(4.75, 4.35, 4.55), power=glm.vec3(0.20, 0.20, 0.20)),
  ])