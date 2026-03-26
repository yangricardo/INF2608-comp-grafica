from __future__ import annotations

import glm

class Ray:
  def __init__(self, origin: glm.vec3, direction: glm.vec3):
    # Slide 4, p. 5-6 e p. 25-29: o raio armazena origem e direção para ser testado contra a cena.
    self.o = glm.vec3(origin)
    self.d = glm.vec3(direction)