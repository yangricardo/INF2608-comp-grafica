from __future__ import annotations

import glm
import numpy as np

class Film:
  def __init__(self, width: int, height: int):
    self.resolution = (width, height)
    self.image = np.zeros((height, width, 3)) # Buffer de pixels

  def set_pixel(self, i: int, j: int, color: glm.vec3):
    self.image[j, i] = glm.clamp(color, 0, 1)