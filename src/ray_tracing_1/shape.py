import glm

from .hit import Hit
from .ray import Ray
from .material import Material

class Shape:
  def intersect(self, ray: Ray, hit: Hit):
    raise NotImplementedError("Shape subclasses must implement intersect()")

class Sphere(Shape):
  def __init__(self, center: glm.vec3, radius: float, material: Material):
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
      sqrt_d = glm.sqrt(delta)
      t1 = (-b - sqrt_d) / (2.0 * a)
      t2 = (-b + sqrt_d) / (2.0 * a)

      t_candidate = None
      if t1 > 0.001:
        t_candidate = t1
      elif t2 > 0.001:
        t_candidate = t2

      if t_candidate is not None and t_candidate < hit.t:
        hit.t = t_candidate
        hit.pos = ray.o + t_candidate * ray.d
        hit.normal = (hit.pos - self.center) / self.radius
        hit.material = self.material
        return True
    return False


class Plane(Shape):
  def __init__(self, pos: glm.vec3, normal: glm.vec3, material: Material):
    self.pos = glm.vec3(pos)
    self.normal = glm.normalize(glm.vec3(normal))
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    denom = glm.dot(self.normal, ray.d)
    if abs(denom) > 1e-6:
        t = glm.dot(self.pos - ray.o, self.normal) / denom
        if 0.001 < t < hit.t:
            hit.t = t
            hit.pos = ray.o + t * ray.d
            hit.normal = self.normal
            hit.material = self.material
            return True
    return False
  
class Instance(Shape):
  def __init__(self, shape: Shape, matrix: glm.mat4):
    self.shape = shape
    self.m = glm.mat4(matrix)
    self.m_inv = glm.inverse(self.m)
    self.m_inv_t = glm.transpose(self.m_inv) # Para transformar a normal corretamente

  def intersect(self, ray: Ray, hit: Hit):
    # Transforma o raio para o espaço local do objeto
    local_o = glm.vec3(self.m_inv * glm.vec4(ray.o.x, ray.o.y, ray.o.z, 1.0))
    local_d = glm.vec3(self.m_inv * glm.vec4(ray.d.x, ray.d.y, ray.d.z, 0.0))
    local_ray = Ray(local_o, local_d)

    if self.shape.intersect(local_ray, hit):
      # Transforma o ponto e a normal de volta para o espaço do mundo
      hit.pos = glm.vec3(self.m * glm.vec4(hit.pos.x, hit.pos.y, hit.pos.z, 1.0))
      hit.normal = glm.normalize(glm.vec3(self.m_inv_t * glm.vec4(hit.normal.x, hit.normal.y, hit.normal.z, 0.0)))
      return True
    return False