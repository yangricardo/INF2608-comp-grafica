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
from ray_tracing_2.film import Film


def render():
  """Renderiza a cena de exemplo e salva `render_final.png`.

  O procedimento segue o pipeline principal:
  1. Cria `Camera` com parâmetros de pinhole.
  2. Monta `Scene` com objetos e luzes.
  3. Para cada pixel, gera um raio primário e avalia a cor com
     `Scene.trace_ray`.
  """
  # Slide 4, p. 24-29: define a resolução do filme e a câmera pinhole da cena.
  W, H = 400, 300
  film = Film(width=W, height=H)
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
  # scene.lights.append(PointLight(pos=glm.vec3(0, 5, 0), power=glm.vec3(150.0)))
  scene.lights.append(PointLight(pos=glm.vec3(-5, 0, 0), power=glm.vec3(150.0)))

  # Slide 4, p. 24-29: o Film percorre os pixels e pede ao Camera um raio por amostra.
  film.render(scene=scene, camera=cam, filename="render_ray_tracing_2.png", gamma_fix=True)

if __name__ == "__main__":
    render()