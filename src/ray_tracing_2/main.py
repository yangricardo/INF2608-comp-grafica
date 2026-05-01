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
  add_common_render_arguments,
  build_parser,
)
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Plane, Rotate, Sphere, Translate



def render(width: int = 800,
           height: int = 600,
           spp: int = 1,
           sampling_mode: str = SamplingMode.JITTERED.value,
           seed: int | None = None,
           gamma_fix: bool = False):
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
  # Cria a câmera
  cam = Camera(eye=glm.vec3(2.7750, 2.775, 2.775), center=glm.vec3(2.775, 3.200, 12.775), up=glm.vec3(0, 1, 0), fov=50, width=W, height=H)
  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3))
  # Slide 4, p. 41-49: materiais Phong para o objeto principal e para o chão.
  mat_red = PhongMaterial(ambient=glm.vec3(0.1, 0, 0), diffuse=glm.vec3(0.7, 0, 0), specular=glm.vec3(1, 1, 1), shininess=50.0)
  mat_gray = PhongMaterial(ambient=glm.vec3(0.1), diffuse=glm.vec3(0.5), specular=glm.vec3(1), shininess=10.0)

  # Slide 4, p. 35-40: reúne objetos, luzes e o ambiente que o traçador precisa avaliar.
  
  # Slide 4, p. 11-18: adiciona um plano e uma esfera para exercitar interseções.
  front_wall = Box(
    p_min=glm.vec3(-0.10, -0.10, -0.10),
    p_max=glm.vec3(5.65, 5.65, 0.0),
    material=mat_gray,
  )
  front_wall = Translate(3.40,1.2,3.65, front_wall)
  front_wall = Rotate(angle_deg=-18.0, x=0, y=1, z=0, shape=front_wall)
  scene.objects.append(front_wall)
  scene.objects.append(Sphere(center=glm.vec3(2.775, 3.200, 12.775), radius=1, material=mat_red))
  scene.objects.append(Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=mat_gray))

  # Slide 4, p. 40: luz pontual usada no cálculo de difusa, especular e sombra.
  # scene.lights.append(PointLight(pos=glm.vec3(2.775,5.55,2.775), power=glm.vec3(0.7, 0.7, 0.7)))
  scene.lights.append(PointLight(pos=glm.vec3(2.775,5.55,2.775), power=glm.vec3(150.0)))
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  r.render(scene=scene, cam=cam, **render_options.to_render_kwargs(name='main_scene'))


def build_cli_parser() -> argparse.ArgumentParser:
  parser = build_parser(
    'Render the baseline Slide 4 scene.',
    examples=[
      'python -m ray_tracing_2.main --width 800 --height 600 --spp 1',
      'python -m ray_tracing_2.main --width 800 --height 600 --spp 1 --sampling_mode stratified --seed 42',
    ],
  )
  add_common_render_arguments(parser, width_default=800, height_default=600, spp_default=1)
  return parser


if __name__ == "__main__":
  parser = build_cli_parser()
  args = parser.parse_args()
  common_options = CommonRenderOptions.from_namespace(args)
  render(**common_options.to_entrypoint_kwargs())