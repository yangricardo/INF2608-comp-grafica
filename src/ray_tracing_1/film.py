from __future__ import annotations

from PIL import Image
import glm
import numpy as np

from ray_tracing_1.camera import Camera
from ray_tracing_1.scene import Scene

class Film:
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self.resolution = (width, height)
    self.image = np.zeros((height, width, 3)) # Buffer de pixels

  def set_pixel(self, i: int, j: int, color: glm.vec3):
    self.image[j, i] = glm.clamp(color, 0, 1)

  def get_sample(self, i, j):
    """Retorna as coordenadas normalizadas (0 a 1) para o pixel (i, j)"""
    return (i + 0.5) / self.width, (j + 0.5) / self.height
  
  def render(self, scene: Scene, camera: Camera, filename: str) -> None:
    print("Renderizando a cena...")    
    for j in range(self.height):
      for i in range(self.width):
        # Obtém as coordenadas normalizadas via Film (ideal para futuro Antialiasing)
        xn, yn = self.get_sample(i, j)
        # Gera o raio primário e avalia a cor via Scene.trace_ray        
        ray = camera.generate_ray(xn, yn)
        color = scene.trace_ray(ray)
        # Define a cor do pixel no buffer do Film        
        self.set_pixel(i, j, color)
    # Converte o buffer para uint8 e salva a imagem usando PIL
    img_data = np.clip(self.image * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_data)
    img.save(filename)
    print(f"Imagem salva em {filename}")