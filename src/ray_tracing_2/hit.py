from __future__ import annotations

from pyglm import glm
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
  from ray_tracing_2.material import Material
  from ray_tracing_2.light import Light
  from ray_tracing_2.ray import Ray

class Hit:
  def __init__(self, t: float = float('inf')):
    # Slide 4, p. 5-6: o hit guarda a melhor interseção encontrada até o momento.
    self.t = t
    self.pos = glm.vec3(0)
    self.normal = glm.vec3(0)
    self.geo_normal = glm.vec3(0)
    self.material: Optional['Material'] = None
    self.light: Optional['Light'] = None
    self.front_face: bool = True
    self.backfacing: bool = False

  def set_face_normal(self, ray: 'Ray', outward_normal: glm.vec3):
    outward = glm.normalize(glm.vec3(outward_normal))
    self.geo_normal = outward
    self.front_face = glm.dot(ray.d, outward) < 0.0
    self.backfacing = not self.front_face
    self.normal = outward if self.front_face else -outward