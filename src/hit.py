import glm
from typing import Optional
from material import Material
from light import Light
class Hit:
  def __init__(self, t=float('inf')):
    self.t = t
    self.pos = glm.vec3(0)
    self.normal = glm.vec3(0)
    self.material: Optional[Material] = None
    self.light: Optional[Light] = None