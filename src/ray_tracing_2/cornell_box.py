"""
Entrada principal: monta uma cena simples (esfera + luz) e executa o
loop de renderização usando a implementação de traçado de raios do projeto.

Este arquivo demonstra o fluxo básico descrito no README: construir uma
`Camera`, popular uma `Scene` com `Shape` e `Material`, e iterar sobre os
pixels gerando raios com `Camera.generate_ray` para avaliar cor via
`Scene.trace_ray`.
"""

from __future__ import annotations

from pyglm import glm
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Plane, Rotate, Sphere, Translate
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.film import Film, SamplingMode
from ray_tracing_2.render import Render
import argparse



def render(spp: int = 1, sampling_mode: str = 'jittered', seed: int | None = None, gamma_fix: bool = False):
  """Renderiza a cena de exemplo e salva `render_final.png`.

  O procedimento segue o pipeline principal:
  1. Cria `Camera` com parâmetros de pinhole.
  2. Monta `Scene` com objetos e luzes.
  3. Para cada pixel, gera um raio primário e avalia a cor com
     `Scene.trace_ray`.
  """
  # Slide 4, p. 24-29: define a resolução do filme e a câmera pinhole da cena.
  W, H = 800, 600
  # Cria a câmera (proj1-exemplo.pdf)
  cam = Camera(eye=glm.vec3(2.775, 3.200, 12.775), center=glm.vec3(2.775, 2.775, 2.775), up=glm.vec3(0, 1, 0), fov=50, width=W, height=H, focal_distance=1.0)
  
  # Cria cena com luz ambiente
  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3))
  
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
  green_phong_material = PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  gray_phong_material = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  # Cria objetos da cena: paredes, blocos e luz pontual.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white_phong_material)
  left_wall = Box(p_min=glm.vec3(-0.1, -0.1, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green_phong_material)
  right_wall = Box(p_min=glm.vec3(5.55, -0.1, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red_phong_material)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white_phong_material)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white_phong_material)
  lamp = Sphere(center=glm.vec3(2.775, 5.55, 2.775), radius=0.1, material=white_phong_material)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor, lamp])

  # Blocos instanciados conforme proj1-exemplo.pdf
  small_block_base = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 1.65, 0.30), material=gray_phong_material)
  small_block = Translate(3.40, 1.2, 3.65, Rotate(-18.0, 0, 1, 0, small_block_base))
  large_block_base = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 3.30, 1.65), material=gray_phong_material)
  large_block = Translate(0.65, 0.0, 1.30, Rotate(22.5, 0, 1, 0, large_block_base))
  scene.objects.extend([small_block, large_block])

  # Fonte de luz conforme proj1-exemplo.pdf (power escalado para compensar r² no PointLight)
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5.55, 2.775), power=glm.vec3(150.0, 150.0, 150.0)))
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  r.render(scene=scene, cam=cam, width=W, height=H, name='cornell_box', samples_per_pixel=spp, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  render(spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)