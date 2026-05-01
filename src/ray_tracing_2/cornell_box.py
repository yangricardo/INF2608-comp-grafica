"""
Entrada principal: monta uma cena simples (esfera + luz) e executa o
loop de renderização usando a implementação de traçado de raios do projeto.

Este arquivo demonstra o fluxo básico descrito no README: construir uma
`Camera`, popular uma `Scene` com `Shape` e `Material`, e iterar sobre os
pixels gerando raios com `Camera.generate_ray` para avaliar cor via
`Scene.trace_ray`.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.cli import (
  CommonRenderOptions,
  add_block_material_arguments,
  add_common_render_arguments,
  add_light_sampling_argument,
  add_max_depth_argument,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, AreaLight, AreaLightSamplingMode, PointLight
from ray_tracing_2.material import PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Rotate, Sphere, Translate



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



def render(width: int = 800,
           height: int = 600,
           spp: int = 1,
           sampling_mode: str = SamplingMode.JITTERED.value,
           light_sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
           seed: int | None = None,
           gamma_fix: bool = False,
           max_depth: int = 10,
           small_block_material: str = 'opaque',
           large_block_material: str = 'opaque'):
  """Renderiza a cena de exemplo e salva `render_final.png`.

  O procedimento segue o pipeline principal:
  1. Cria `Camera` com parâmetros de pinhole.
  2. Monta `Scene` com objetos e luzes.
  3. Para cada pixel, gera um raio primário e avalia a cor com
     `Scene.trace_ray`.
  """
  render_options = CommonRenderOptions(
    width=width,
    height=height,
    spp=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )
  # Slide 4, p. 24-29: define a resolução do filme e a câmera pinhole da cena.
  W, H = render_options.width, render_options.height
  # Cria a câmera (proj1-exemplo.pdf)
  cam = Camera(eye=glm.vec3(2.775, 3.200, 12.775), center=glm.vec3(2.775, 2.775, 2.775), up=glm.vec3(0, 1, 0), fov=50, width=W, height=H, focal_distance=1.0)
  
  # Cria cena com luz ambiente
  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3), max_depth=max_depth)
  
  white_phong_material = PhongMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  red_phong_material = PhongMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  reflexive_red_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  green_phong_material = PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  reflexive_green_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  reflexive_white_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  transparent_mat = TransparentMaterial(ior=1.5, attenuation=glm.vec3(1))
  small_block_surface = _build_block_material(small_block_material)
  large_block_surface = _build_block_material(large_block_material)

  # Cria objetos da cena: paredes, blocos e luz pontual.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=reflexive_white_phong_material)
  left_wall = Box(p_min=glm.vec3(-0.1, -0.1, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green_phong_material)
  right_wall = Box(p_min=glm.vec3(5.55, -0.1, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red_phong_material)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white_phong_material)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white_phong_material)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])

  # Blocos instanciados conforme proj1-exemplo.pdf
  small_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 1.65, 0.30), material=transparent_mat)
  small_block = Rotate(angle_deg=-18.0, x=0, y=1, z=0, shape=small_block)
  small_block = Translate(3.40, 1.2, 5.65, small_block)
  large_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 3.30, 1.65), material=red_phong_material)
  large_block = Rotate(angle_deg=22.5, x=0, y=1, z=0, shape=large_block)
  large_block = Translate(0.65, 0.0, 1.30, large_block)
  scene.objects.extend([small_block, large_block])
  red_sphere = Sphere(center=glm.vec3(2.5, 0.5, 5.0), radius=0.6, material=green_phong_material)
  scene.objects.append(red_sphere)
  
  # Luminária: proj1-exemplo.pdf — Sphere(vec3(2.775,5.55,2.775), 0.1)
  # Aqui a esfera visível da luminária usa PhongMaterial com componente ambiente
  # alta para funcionar como marcador emissivo aparente; a iluminação efetiva da
  # cena continua vindo das luzes explícitas adicionadas logo abaixo.
  lamp_material = PhongMaterial(
    diffuse=glm.vec3(0.0),   # Não precisa de cor difusa (não recebe luz de outros objetos)
    specular=glm.vec3(1),  # Sem brilho especular
    shininess=0,             # Sem rugosidade
    ambient=glm.vec3(1.0)    # Brilho constante máximo (cor branca pura)
  )
  lamp_sphere = Sphere(center=glm.vec3(2.775, 5.55, 2.775), radius=0.1, material=lamp_material)
  scene.objects.append(lamp_sphere)
  # Luz de área atrás da câmera para iluminar a cena pela direção do observador.
  camera_fill_light = AreaLight(
    p=glm.vec3(1.25, 1.95, 13.45),
    e_u=glm.vec3(3.05, 0.0, 0.0),
    e_v=glm.vec3(0.0, 2.35, 0.0),
    power=glm.vec3(80.0, 80.0, 80.0),
    samples_u=2,
    samples_v=2,
    sampling_mode=light_sampling_mode,
    seed=seed,
  )
  scene.lights.append(camera_fill_light)
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5, 2.775), power=glm.vec3(0.7, 0.7, 0.7)))  
  # # 5.tracado_de_raios2.pdf - p.35: area light no teto, centralizada entre as paredes laterais.
  # # Inset de ~10% em cada lado do volume útil do box: x/z de 0.555 até 5.0.
  # area_light_origin = glm.vec3(0.555, 5.54, 0.555)
  # area_light_e_u = glm.vec3(4.44, 0.0, 0.0)
  # area_light_e_v = glm.vec3(0.0, 0.0, 4.44)
  # scene.lights.append(
  #   AreaLight(
  #     p=area_light_origin,
  #     e_u=area_light_e_u,
  #     e_v=area_light_e_v,
  #     power=glm.vec3(0.7, 0.7, 0.7),
  #     samples_u=2,
  #     samples_v=2,
  #     seed=seed,
  #   )
  # )

  # Fonte de luz conforme proj1-exemplo.pdf
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5.55, 2.775), power=glm.vec3(0.7, 0.7, 0.7)))  
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  r.render(scene=scene, cam=cam, **render_options.to_render_kwargs(name='cornell_box'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render the Cornell-like scene with separate film and area-light sampling controls.',
    examples=[
      'python -m ray_tracing_2.cornell_box --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.cornell_box --width 800 --height 600 --spp 1 --sampling_mode stratified --light_sampling_mode regular --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  add_light_sampling_argument(parser, help_text='Sampling mode for area lights in the scene')
  add_max_depth_argument(parser, default=4)
  add_block_material_arguments(parser, small_default='opaque', large_default='opaque')
  return parser


if __name__ == "__main__":
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(
    **common_options.to_entrypoint_kwargs(),
    light_sampling_mode=args.light_sampling_mode,
    max_depth=args.max_depth,
    small_block_material=args.small_block_material,
    large_block_material=args.large_block_material,
  )