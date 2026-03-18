import glm
import numpy as np

class Film:
  def __init__(self, width, height):
    self.resolution = (width, height)
    self.image = np.zeros((height, width, 3)) # Buffer de pixels

  def set_pixel(self, i, j, color):
    self.image[j, i] = glm.clamp(color, 0, 1)