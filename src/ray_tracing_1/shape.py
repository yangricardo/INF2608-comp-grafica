from __future__ import annotations

import glm
from typing import TYPE_CHECKING

from ray_tracing_1.hit import Hit
from ray_tracing_1.ray import Ray

if TYPE_CHECKING:
  from ray_tracing_1.material import Material

class Shape:
  def intersect(self, ray: Ray, hit: Hit):
    raise NotImplementedError("Shape subclasses must implement intersect()")

class Sphere(Shape):
  def __init__(self, center: glm.vec3, radius: float, material: Material):
    self.center = glm.vec3(center)
    self.radius = radius
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 15-18: interseção esfera-raio é resolvida pela equação quadrática.
    oc = ray.o - self.center
    a = glm.dot(ray.d, ray.d)
    b = 2.0 * glm.dot(ray.d, oc)
    c = glm.dot(oc, oc) - self.radius**2
    delta = (b**2) - (4*a*c)
    if delta < 0:
      return False
    
    sqrt_d = glm.sqrt(delta)
    t1 = (-b - sqrt_d) / (2.0 * a)
    t2 = (-b + sqrt_d) / (2.0 * a)

    # Slide 4, p. 15-18: escolhe a primeira raiz positiva; se necessário, usa a segunda.
    t_candidate = None
    if t1 > 0.001:
      t_candidate = t1
    elif t2 > 0.001:
      t_candidate = t2

    if t_candidate is not None and t_candidate < hit.t:
      hit.t = t_candidate
      hit.pos = ray.o + t_candidate * ray.d
      # Slide 4, p. 15-18: normal geométrica aponta do centro para fora.
      hit.normal = (hit.pos - self.center) / self.radius
      # Slide 4, p. 15-18: se o raio atingiu a face interna, inverte a normal para o shading.
      if glm.dot(ray.d, hit.normal) > 0.0:
          hit.normal = -hit.normal # Inverte a normal para o shading funcionar
          hit.backfacing = True
      else:
          hit.normal = hit.normal
          hit.backfacing = False
      hit.material = self.material
      return True
    return False


class Plane(Shape):
  def __init__(self, pos: glm.vec3, normal: glm.vec3, material: Material):
    self.pos = glm.vec3(pos)
    self.normal = glm.normalize(glm.vec3(normal))
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 11-12: plano é resolvido por produto escalar entre normal e direção.
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
    # Slide 4, p. 44-46: transforma o raio para o espaço local antes de testar a geometria.
    local_o = glm.vec3(self.m_inv * glm.vec4(ray.o.x, ray.o.y, ray.o.z, 1.0))
    local_d = glm.vec3(self.m_inv * glm.vec4(ray.d.x, ray.d.y, ray.d.z, 0.0))
    local_ray = Ray(local_o, local_d)
    # Mantém o hit local separado para não misturar `t` do espaço local com o do mundo.
    local_hit = Hit()
    if not self.shape.intersect(local_ray, local_hit):
      return False

    # Slide 4, p. 44-46: reconstrói posição e normal no espaço do mundo.
    world_pos = glm.vec3(self.m * glm.vec4(local_hit.pos.x, local_hit.pos.y, local_hit.pos.z, 1.0))
    world_normal = glm.normalize(glm.vec3(self.m_inv_t * glm.vec4(local_hit.normal.x, local_hit.normal.y, local_hit.normal.z, 0.0)))

    if local_hit.t < hit.t:
      hit.t = float(local_hit.t)
      hit.pos = world_pos
      hit.normal = world_normal
      hit.material = local_hit.material
      hit.backfacing = local_hit.backfacing
      return True

    return False