"""
Entrada principal para demonstrar instanciação de caixas (Box) em uma cena
estilo Cornell Box, semelhante à imagem do slide 27.

A cena usa duas caixas instanciadas a partir da mesma geometria-base, com
paredes coloridas e uma luz de área no teto para produzir sombras suaves.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Instance, Plane


def _transform(tx: float, ty: float, tz: float, sx: float, sy: float, sz: float, ry_deg: float = 0.0) -> glm.mat4:
  ry = glm.radians(ry_deg)
  c = glm.cos(ry)
  s = glm.sin(ry)

  m = glm.mat4(1.0)
  m[0][0] = c * sx
  m[0][2] = -s * sx
  m[1][1] = sy
  m[2][0] = s * sz
  m[2][2] = c * sz
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
    center=glm.vec3(2.775,2.775, 2.775),
    up=glm.vec3(0, 1, 0),
    fov=50.0,
    width=W,
    height=H,
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
  light_gray = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.6),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  dark_gray = PhongMaterial(
    ambient=glm.vec3(0.05),
    diffuse=glm.vec3(0.3),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  gray = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  scene = Scene()

  # Cornell-like room: floor, ceiling, back wall and side walls.
  floor = Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=white)
  left_wall = Plane(pos=glm.vec3(-2.0, 0, 0), normal=glm.vec3(1, 0, 0), material=green)
  right_wall = Plane(pos=glm.vec3(2.0, 0, 0), normal=glm.vec3(-1, 0, 0), material=red)
  back_wall = Plane(pos=glm.vec3(0, 0, -4.0), normal=glm.vec3(0, 0, 1), material=light_gray)
  top_wall = Plane(pos=glm.vec3(0, 3.0, 0), normal=glm.vec3(0, -1, 0), material=dark_gray)
  scene.objects.append(floor)
  scene.objects.append(left_wall)
  scene.objects.append(right_wall)
  scene.objects.append(back_wall)
  scene.objects.append(top_wall)

  # Base box reused through instancing to demonstrate the slide concept.
  base_box = Box(
    p_min=glm.vec3(-0.5, -0.5, -0.5),
    p_max=glm.vec3(0.5, 0.5, 0.5),
    material=gray,
  )

  tall_box = Instance(base_box, _transform(-0.65, -0.05, -2.2, 0.75, 1.55, 0.75, ry_deg=25.0))
  short_box = Instance(base_box, _transform(0.65, -0.6, -1.7, 1.0, 0.7, 1.0, ry_deg=-35.0))

  scene.objects.append(tall_box)
  scene.objects.append(short_box)

  # Area light on the ceiling, slightly forward, to create soft shadows.
  scene.lights.append(
    AreaLight(
      p=glm.vec3(-0.75, 2.95, -2.9),
      e_u=glm.vec3(1.5, 0.0, 0.0),
      e_v=glm.vec3(0.0, 0.0, 1.2),
      power=glm.vec3(50.0),
      samples_u=6,
      samples_v=6,
      seed=seed,
    )
  )

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