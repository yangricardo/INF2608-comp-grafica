"""
Entrada principal para uma cena de teste inspirada na Cornell Box.

A montagem segue o enunciado com paredes em `Box`, dois blocos instanciados,
uma luminária esférica e uma luz pontual no teto, além de luz ambiente global.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.cli import (
  CommonRenderOptions,
  add_block_material_arguments,
  add_common_render_arguments,
  add_max_depth_argument,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.material import PhongMaterial, ReflectiveMaterial, TransparentMaterial
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


def _build_block_material(kind: str):
  if kind == 'reflective':
    return ReflectiveMaterial(
      ambient=glm.vec3(0.03),
      diffuse=glm.vec3(0.25),
      specular=glm.vec3(0.05),
      shininess=32.0,
      reflectivity=glm.vec3(0.55),
    )
  if kind == 'transparent':
    # 5.tracado_de_raios2.pdf - p.36: cena com vidro (a = (0.8, 0.9, 0.8))
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


def render(
  width: int = 800,
  height: int = 600,
  spp: int = 25,
  sampling_mode: str = SamplingMode.JITTERED.value,
  seed: int | None = None,
  gamma_fix: bool = False,
  light_power: float = 0.7,   # proj1-exemplo.pdf: PointLight(vec3(0.7,0.7,0.7), ...)
  light_y: float = 5.55,     # proj1-exemplo.pdf: posição y da luz = 5.55
  max_depth: int = 4,
  small_block_material: str = 'opaque',
  large_block_material: str = 'opaque',
):
  """Renderiza uma cena tipo Cornell Box com caixas instanciadas."""
  render_options = CommonRenderOptions(
    width=width,
    height=height,
    spp=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )
  W, H = render_options.width, render_options.height
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
  gray = _build_block_material('opaque')

  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3), max_depth=max_depth)

  # Slide 4, pp. 11-12, e proj1-exemplo.pdf: a sala é montada por cinco caixas
  # alinhadas aos eixos, reutilizando a mesma primitiva analítica do método de slabs.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white)
  left_wall = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green)
  right_wall = Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])

  # Slide 4, pp. 15-18, e proj1-exemplo.pdf: a luminária é representada por uma
  # esfera pequena. O centro foi rebaixado para y=5.45 para caber por completo
  # no interior da sala sem interceptar numericamente o teto em y=5.55.
  lamp_mat = TransparentMaterial(ior=1.5, attenuation=glm.vec3(1.0))
  lamp_sphere = Sphere(center=glm.vec3(2.775, 5.45, 2.775), radius=0.1, material=lamp_mat)
  scene.objects.append(lamp_sphere)

  # Slide 5, pp. 9-13: os blocos base são instanciados por transformações afins
  # em vez de redefinir a interseção de cada caixa já posicionada no mundo.
  small_block_base = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.65, 0.30),
    material=_build_block_material(small_block_material),
  )
  large_block_base = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 3.30, 1.65),
    material=_build_block_material(large_block_material),
  )

  small_block = Instance(small_block_base, _translate_rotate_y(3.40, 1.2, 3.65, ry_deg=-18.0))
  large_block = Instance(large_block_base, _translate_rotate_y(0.65, 0.0, 1.30, ry_deg=22.5))

  scene.objects.extend([small_block, large_block])

  # Slide 4, pp. 40-41, e proj1-exemplo.pdf: luz pontual no teto para manter a
  # convenção de iluminação direta usada no enunciado base.
  scene.lights.append(PointLight(pos=glm.vec3(2.775, light_y, 2.775), power=glm.vec3(light_power, light_power, light_power)))

  r = Render()
  r.render(scene=scene, cam=cam, **render_options.to_render_kwargs(name='main_box'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render the Cornell box statement scene with instanced blocks.',
    examples=[
      'python -m ray_tracing_2.main_box --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.main_box --width 800 --height 600 --spp 1 --sampling_mode stratified --seed 42 --max_depth 4',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=25)
  parser.add_argument('--light_power', type=float, default=0.7, help='Point light power (proj1-exemplo.pdf: 0.7)')
  parser.add_argument('--light_y', type=float, default=5.55, help='Y position of the point light (proj1-exemplo.pdf: 5.55)')
  add_max_depth_argument(parser, default=4)
  add_block_material_arguments(parser, small_default='opaque', large_default='opaque')
  return parser


if __name__ == '__main__':
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(
    **common_options.to_entrypoint_kwargs(),
    light_power=args.light_power,
    light_y=args.light_y,
    max_depth=args.max_depth,
    small_block_material=args.small_block_material,
    large_block_material=args.large_block_material,
  )