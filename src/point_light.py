import glm

class PointLight:
  def __init__(self, pos, power):
      self.pos = glm.vec3(pos)
      self.power = glm.vec3(power)