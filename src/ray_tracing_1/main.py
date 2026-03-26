"""
Entrada principal: monta uma cena simples (esfera + luz) e executa o
loop de renderização usando a implementação de traçado de raios do projeto.

Este arquivo demonstra o fluxo básico descrito no README: construir uma
`Camera`, popular uma `Scene` com `Shape` e `Material`, e iterar sobre os
pixels gerando raios com `Camera.generate_ray` para avaliar cor via
`Scene.trace_ray`.
"""

import numpy as np
from PIL import Image
import glm
from .ray import Ray
from .camera import Camera
from .scene import Scene
from .shape import Sphere
from .material import PhongMaterial
from .light import PointLight


def render():
  """Renderiza a cena de exemplo e salva `render_final.png`.

  O procedimento segue o pipeline principal:
  1. Cria `Camera` com parâmetros de pinhole.
  2. Monta `Scene` com objetos e luzes.
  3. Para cada pixel, gera um raio primário e avalia a cor com
     `Scene.trace_ray`.
  """
  # Resolução de saída
  W, H = 400, 300

  # Câmera: olho posicionado em (0,0,5), olhando para origem
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45, width=W, height=H)

  # Monta a cena: um objeto (esfera) com material Phong e uma luz pontual
  scene = Scene()
  mat_red = PhongMaterial(ambient=glm.vec3(0.1, 0, 0),
                         diffuse=glm.vec3(0.7, 0, 0),
                         specular=glm.vec3(1, 1, 1),
                         shininess=50)
  scene.objects.append(Sphere(center=glm.vec3(0, 0, 0), radius=1.0, material=mat_red))
  scene.lights.append(PointLight(pos=glm.vec3(5, 5, 5), power=glm.vec3(150, 150, 150)))

  # Loop de render: amostragem central do pixel e conversão para uint8
  img = np.zeros((H, W, 3), dtype=np.uint8)
  for j in range(H):
    for i in range(W):
      # Coordenadas normalizadas do centro do pixel
      xn, yn = (i + 0.5) / W, (j + 0.5) / H
      ray = cam.generate_ray(xn=xn, yn=yn)
      # Avalia a cor via Scene.trace_ray e limita valores entre 0 e 1
      color = glm.clamp(scene.trace_ray(ray=ray), 0, 1)
      img[j, i] = (color * 255)

  # Salva o resultado em disco
  Image.fromarray(img).save("render_final.png")
  print("Renderização concluída. Imagem salva como 'render_final.png'.")

if __name__ == "__main__":
    render()