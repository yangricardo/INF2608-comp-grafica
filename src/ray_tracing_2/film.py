from __future__ import annotations

from PIL import Image
import glm
import numpy as np

from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene

class Film:
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self.resolution = (width, height)
    # Slide 4, p. 24-28: buffer 2D de pixels que armazena a imagem final da renderização.
    self.image = np.zeros((height, width, 3))

  def set_pixel(self, i: int, j: int, color: glm.vec3):
    # Slide 4, p. 24-28: grava a cor calculada no pixel (i, j), já limitada ao intervalo válido.
    self.image[j, i] = glm.clamp(color, 0, 1)

  def get_sample(self, i, j):
    """Retorna as coordenadas normalizadas (0 a 1) para o pixel (i, j)"""
    # Slide 4, p. 25-29: amostragem no centro do pixel para disparar um raio primário.
    return (i + 0.5) / self.width, (j + 0.5) / self.height
  
  def render(self, scene: Scene, camera: Camera, filename: str, gamma_fix: bool = False) -> None:
    # Slide 4, p. 24-29: percorre todos os pixels e pede um raio para cada amostra.
    print("Renderizando a cena...")    
    for j in range(self.height):
      for i in range(self.width):
        # Slide 4, p. 25-29: converte o pixel em coordenadas normalizadas da tela.
        xn, yn = self.get_sample(i, j)
        # Slide 4, p. 29 e p. 35: gera o raio primário e consulta a cena.
        ray = camera.generate_ray(xn, yn)
        color = scene.trace_ray(ray)
        # Slide 4, p. 24-28: escreve o resultado no buffer de imagem.
        self.set_pixel(i, j, color)
    # Correção gama opcional para aproximar a resposta visual exibida na tela.
    if gamma_fix:
      img_data = np.power(self.image, 1/2.2)
    else:
      img_data = self.image
    # Converte para uint8 e salva a imagem usando PIL.
    img_data = np.clip(img_data * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_data)
    img.save(filename)
    print(f"Imagem salva em {filename}")