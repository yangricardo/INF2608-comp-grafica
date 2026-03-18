import glm

class Light:
  def __init__(self, power):
    self.power = glm.vec3(power)

class PointLight(Light):
  def __init__(self, pos, power):
    super().__init__(power)
    self.pos = glm.vec3(pos)