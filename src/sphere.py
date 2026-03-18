import glm

from src.hit import Hit
from src.ray import Ray


class Sphere:
  def __init__(self, center, radius, material):
    self.center = glm.vec3(center)
    self.radius = radius
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    oc = ray.o - self.center
    a = glm.dot(ray.d, ray.d)
    b = 2.0 * glm.dot(ray.d, oc)
    c = glm.dot(oc, oc) - self.radius**2
    delta = b**2 - 4*a*c
    if delta >= 0:
        t = (-b - glm.sqrt(delta)) / (2.0 * a)
        if 0.001 < t < hit.t:
            hit.t = t
            hit.pos = ray.o + t * ray.d
            hit.normal = (hit.pos - self.center) / self.radius
            hit.material = self.material
            return True
    return False