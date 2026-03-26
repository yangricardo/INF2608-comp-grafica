from __future__ import annotations

from PIL import Image
import glm
import numpy as np

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
  
  def save(self, filename: str) -> None:
    img_data = np.clip(self.image * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_data)
    img.save(filename)