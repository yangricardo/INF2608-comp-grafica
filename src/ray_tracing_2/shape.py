from __future__ import annotations

from pyglm import glm
from typing import TYPE_CHECKING

from ray_tracing_2.hit import Hit
from ray_tracing_2.ray import Ray

if TYPE_CHECKING:
  from ray_tracing_2.material import Material

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


class Box(Shape):
  def __init__(self, p_min: glm.vec3, p_max: glm.vec3, material: Material):
    self.p_min = glm.vec3(
      min(p_min.x, p_max.x),
      min(p_min.y, p_max.y),
      min(p_min.z, p_max.z),
    )
    self.p_max = glm.vec3(
      max(p_min.x, p_max.x),
      max(p_min.y, p_max.y),
      max(p_min.z, p_max.z),
    )
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    # Slabs: calcula os intervalos de entrada/saída do raio em cada eixo.
    t_near = -float('inf')
    t_far = float('inf')
    near_normal = glm.vec3(0)
    far_normal = glm.vec3(0)
    eps = 1e-6

    for axis in range(3):
      origin = ray.o[axis]
      direction = ray.d[axis]
      slab_min = self.p_min[axis]
      slab_max = self.p_max[axis]

      if abs(direction) < eps:
        if origin < slab_min or origin > slab_max:
          return False
        continue

      inv_d = 1.0 / direction
      t1 = (slab_min - origin) * inv_d
      t2 = (slab_max - origin) * inv_d

      if t1 > t2:
        t1, t2 = t2, t1

      if t1 > t_near:
        t_near = t1
        near_normal = glm.vec3(0)
        near_normal[axis] = -1.0 if direction > 0.0 else 1.0

      if t2 < t_far:
        t_far = t2
        far_normal = glm.vec3(0)
        far_normal[axis] = 1.0 if direction > 0.0 else -1.0

      if t_near > t_far:
        return False

    if t_far < 0.001:
      return False

    t_candidate = t_near if t_near > 0.001 else t_far
    if t_candidate >= hit.t:
      return False

    hit.t = t_candidate
    hit.pos = ray.o + t_candidate * ray.d
    hit.normal = near_normal if t_candidate == t_near else far_normal
    hit.material = self.material
    hit.backfacing = glm.dot(ray.d, hit.normal) > 0.0
    if hit.backfacing:
      hit.normal = -hit.normal
    return True
  
class Instance(Shape):
  def __init__(self, shape: Shape, matrix: glm.mat4):
    self.shape = shape
    self.m = glm.mat4(matrix)
    self.m_inv = glm.inverse(self.m)
    # Slide 5.12: A matriz para transformar normais é a inversa transposta
    self.m_inv_t = glm.transpose(self.m_inv) # Para transformar a normal corretamente

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 44-46:
    # 1. Transforma o raio do mundo para o espaço local da instância usando a inversa da matriz.
    # 2. Normaliza a direção do raio local para garantir que o parâmetro t represente distância real (essencial para instâncias com escala).
    # 3. Realiza o teste de interseção no espaço local.
    # 4. Se houver hit, transforma a posição e a normal de volta para o mundo.
    # 5. O parâmetro t é mantido consistente com o espaço global apenas se a direção local for normalizada.
    local_o = glm.vec3(self.m_inv * glm.vec4(ray.o.x, ray.o.y, ray.o.z, 1.0))
    local_d = glm.vec3(self.m_inv * glm.vec4(ray.d.x, ray.d.y, ray.d.z, 0.0))
    local_d = glm.normalize(local_d)  # O Slide 13 indica a normalização da direção local
    local_ray = Ray(local_o, local_d)
    local_hit = Hit()

    # 2. Calcula interseção raio-objeto no espaço local
    if not self.shape.intersect(local_ray, local_hit):
      return False

    # 3. Transforma ponto e normal da interseção para o espaço global
    world_pos = glm.vec3(self.m * glm.vec4(local_hit.pos.x, local_hit.pos.y, local_hit.pos.z, 1.0))
    world_normal = glm.normalize(glm.vec3(self.m_inv_t * glm.vec4(local_hit.normal.x, local_hit.normal.y, local_hit.normal.z, 0.0)))

    # Como a direção local foi normalizada, precisamos calcular a distância real 
    # no espaço global. Caso contrário, objetos escalonados teriam um 't' incorreto.
    world_t = glm.distance(world_pos, ray.o)

    if world_t < hit.t:
      hit.t = world_t
      hit.pos = world_pos
      hit.normal = world_normal
      hit.material = local_hit.material
      hit.backfacing = local_hit.backfacing
      return True

    return False