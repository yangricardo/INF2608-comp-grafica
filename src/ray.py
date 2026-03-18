import glm

class Ray:
  def __init__(self, origin: glm.vec3, direction: glm.vec3):
    self.o = glm.vec3(origin)
    self.d = glm.normalize(glm.vec3(direction))