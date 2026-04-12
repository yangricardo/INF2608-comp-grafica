"""
Entrada principal para uma cena de teste inspirada na Cornell Box.

A montagem segue o enunciado com paredes em `Box`, dois blocos instanciados,
uma luminária esférica e uma luz pontual no teto, além de luz ambiente global.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Instance, Sphere


def _translate_rotate_y(tx: float, ty: float, tz: float, ry_deg: float = 0.0) -> glm.mat4:
  ry = glm.radians(ry_deg)
  c = glm.cos(ry)
  s = glm.sin(ry)

  m = glm.mat4(1.0)
  m[0][0] = c
  m[0][2] = -s
  m[1][1] = 1.0
  m[2][0] = s
  m[2][2] = c
  m[3][0] = tx
  m[3][1] = ty
  m[3][2] = tz
  return m


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 25,
  sampling_mode: str = 'jittered',
  seed: int | None = None,
  gamma_fix: bool = False,
):
  """Renderiza uma cena tipo Cornell Box com caixas instanciadas."""
  W, H = width, height
  cam = Camera(
    eye=glm.vec3(2.775, 3.200, 12.775),
    center=glm.vec3(2.775, 2.775, 2.775),
    up=glm.vec3(0, 1, 0),
    fov=50.0,
    width=W,
    height=H,
    focal_distance=1.0,
  )

  white = PhongMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  red = PhongMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  green = PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  gray = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3))

  # Cornell Box literal: front wall, left wall, right wall, ceiling and floor.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white)
  left_wall = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green)
  right_wall = Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])

  lamp = Sphere(center=glm.vec3(2.775, 5.55, 2.775), radius=0.1, material=white)
  scene.objects.append(lamp)

  # Base boxes from the statement, then instanced with translate + rotate.
  small_block_base = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.65, 0.30),
    material=gray,
  )
  large_block_base = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 3.30, 1.65),
    material=gray,
  )

  small_block = Instance(small_block_base, _translate_rotate_y(3.40, 1.2, 3.65, ry_deg=-18.0))
  large_block = Instance(large_block_base, _translate_rotate_y(0.65, 0.0, 1.30, ry_deg=22.5))

  scene.objects.extend([small_block, large_block])

  # Point light on the ceiling, matching the statement.
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5.55, 2.775), power=glm.vec3(150.0, 150.0, 150.0)))

  r = Render()
  r.render(
    scene=scene,
    cam=cam,
    width=W,
    height=H,
    name='main_box',
    samples_per_pixel=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--width', type=int, default=800, help='Image width in pixels')
  parser.add_argument('--height', type=int, default=600, help='Image height in pixels')
  parser.add_argument('--spp', type=int, default=25, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  render(width=args.width, height=args.height, spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)