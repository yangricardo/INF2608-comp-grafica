import glm

class Hit:
  def __init__(self, t=float('inf')):
      self.t = t
      self.pos = glm.vec3(0)
      self.normal = glm.vec3(0)
      self.material = None
      self.light = None