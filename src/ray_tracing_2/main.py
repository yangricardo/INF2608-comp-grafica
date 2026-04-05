"""
Entrada principal: monta uma cena simples (esfera + luz) e executa o
loop de renderização usando a implementação de traçado de raios do projeto.

Este arquivo demonstra o fluxo básico descrito no README: construir uma
`Camera`, popular uma `Scene` com `Shape` e `Material`, e iterar sobre os
pixels gerando raios com `Camera.generate_ray` para avaliar cor via
`Scene.trace_ray`.
"""

from __future__ import annotations

import glm
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Plane, Sphere
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.light import PointLight
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
  W, H = 400, 300
  # Cria a câmera
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45.0, width=W, height=H)

  # Slide 4, p. 41-49: materiais Phong para o objeto principal e para o chão.
  mat_red = PhongMaterial(ambient=glm.vec3(0.1, 0, 0), diffuse=glm.vec3(0.7, 0, 0), specular=glm.vec3(1, 1, 1), shininess=50.0)
  mat_gray = PhongMaterial(ambient=glm.vec3(0.1), diffuse=glm.vec3(0.5), specular=glm.vec3(0.0), shininess=1.0)

  # Slide 4, p. 35-40: reúne objetos, luzes e o ambiente que o traçador precisa avaliar.
  scene = Scene()

  # Slide 4, p. 11-18: adiciona um plano e uma esfera para exercitar interseções.
  scene.objects.append(Sphere(center=glm.vec3(0, 0, 0), radius=1.0, material=mat_red))
  scene.objects.append(Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=mat_gray))

  # Slide 4, p. 40: luz pontual usada no cálculo de difusa, especular e sombra.
  scene.lights.append(PointLight(pos=glm.vec3(0, 5, 0), power=glm.vec3(150.0)))
  # scene.lights.append(PointLight(pos=glm.vec3(-5, 0, 0), power=glm.vec3(150.0)))
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  props = {
    'objects': len(scene.objects),
    'lights': len(scene.lights)
  }
  r.render(scene=scene, cam=cam, width=W, height=H, name='main_scene', props=props, samples_per_pixel=spp, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  render(spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)