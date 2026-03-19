import glm

class Light:
  def __init__(self, power: glm.vec3):
    self.power = glm.vec3(power)

class PointLight(Light):
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    super().__init__(power)
    self.pos = glm.vec3(pos)