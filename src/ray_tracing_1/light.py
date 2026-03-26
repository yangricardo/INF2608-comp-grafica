from __future__ import annotations

import glm

class Light:
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    self.power = glm.vec3(power)
    self.pos = pos

class PointLight(Light):
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    super().__init__(pos, power)