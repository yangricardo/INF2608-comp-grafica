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
      hit.set_face_normal(ray, (hit.pos - self.center) / self.radius)
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
            hit.set_face_normal(ray, self.normal)
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
    # Slabs: calcula os intervalos de entrada/saída do raio em cada eixo e
    # intersecta esses intervalos para obter a primeira face visível da caixa.
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

    use_near = t_near > 0.001
    t_candidate = t_near if use_near else t_far
    if t_candidate >= hit.t:
      return False

    hit.t = t_candidate
    hit.pos = ray.o + t_candidate * ray.d
    outward_normal = near_normal if use_near else far_normal
    hit.set_face_normal(ray, outward_normal)
    hit.material = self.material
    return True


class Triangle(Shape):
  # Slide 4, p. 35 e p. 47-48: a primitiva participa do mesmo fluxo de closest hit das demais.
  def __init__(self, v0: glm.vec3, v1: glm.vec3, v2: glm.vec3, material: Material):
    self.v0 = glm.vec3(v0)
    self.v1 = glm.vec3(v1)
    self.v2 = glm.vec3(v2)
    self.e1 = self.v1 - self.v0
    self.e2 = self.v2 - self.v0
    normal = glm.cross(self.e1, self.e2)
    if glm.dot(normal, normal) <= 1e-12:
      raise ValueError('Triangle vertices are degenerate or collinear')
    self.geo_normal = glm.normalize(normal)
    self.material = material

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 35 e p. 47-48: Möller-Trumbore testa a primitiva e devolve o hit local.
    eps = 1e-6
    pvec = glm.cross(ray.d, self.e2)
    det = glm.dot(self.e1, pvec)
    if abs(det) < eps:
      return False

    inv_det = 1.0 / det
    tvec = ray.o - self.v0
    u = glm.dot(tvec, pvec) * inv_det
    if u < 0.0 or u > 1.0:
      return False

    qvec = glm.cross(tvec, self.e1)
    v = glm.dot(ray.d, qvec) * inv_det
    if v < 0.0 or (u + v) > 1.0:
      return False

    t_candidate = glm.dot(self.e2, qvec) * inv_det
    if t_candidate <= 0.001 or t_candidate >= hit.t:
      return False

    hit.t = t_candidate
    hit.pos = ray.o + t_candidate * ray.d
    hit.set_face_normal(ray, self.geo_normal)
    hit.material = self.material
    return True


class TriangleMesh(Shape):
  def __init__(
    self,
    triangles: list[Triangle],
    material: Material,
    vertices: list[glm.vec3] | None = None,
    faces: list[tuple[int, int, int]] | None = None,
    name: str | None = None,
  ):
    self.triangles = list(triangles)
    self.material = material
    self.vertices = [glm.vec3(v) for v in vertices] if vertices is not None else []
    self.faces = [tuple(face) for face in faces] if faces is not None else []
    self.name = name

  @classmethod
  def from_vertices_faces(
    cls,
    vertices: list[glm.vec3],
    faces: list[tuple[int, int, int]],
    material: Material,
    name: str | None = None,
  ):
    triangles = [Triangle(vertices[i0], vertices[i1], vertices[i2], material) for i0, i1, i2 in faces]
    return cls(triangles=triangles, material=material, vertices=vertices, faces=faces, name=name)

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 35 e p. 47-48: a malha apenas percorre os triângulos e conserva o hit mais próximo.
    found = False
    for triangle in self.triangles:
      if triangle.intersect(ray, hit):
        found = True
    return found
  
class Instance(Shape):
  def __init__(self, shape: Shape, matrix: glm.mat4):
    self.shape = shape
    self.m = glm.mat4(matrix)
    self.m_inv = glm.inverse(self.m)
    # Slide 5, p. 12-13: a normal não pode usar a mesma matriz do ponto quando
    # há escala não uniforme. A inversa transposta preserva perpendicularidade.
    self.m_inv_t = glm.transpose(self.m_inv)

  def intersect(self, ray: Ray, hit: Hit):
    # Slide 4, p. 44-46:
    # 1. Transforma o raio do mundo para o espaço local da instância usando a inversa da matriz.
    # 2. Realiza o teste de interseção no espaço local.
    # 3. Se houver hit, transforma a posição e a normal de volta para o mundo.
    # 4. Converte a posição encontrada para o parâmetro t do raio original no espaço global.
    # Esse desacoplamento permite reutilizar primitivas simples como esfera, plano
    # e box em cenas mais ricas sem reescrever a matemática de interseção.
    local_o = glm.vec3(self.m_inv * glm.vec4(ray.o.x, ray.o.y, ray.o.z, 1.0))
    local_d = glm.vec3(self.m_inv * glm.vec4(ray.d.x, ray.d.y, ray.d.z, 0.0))
    local_ray = Ray(local_o, local_d)
    local_hit = Hit()

    # 2. Calcula interseção raio-objeto no espaço local
    if not self.shape.intersect(local_ray, local_hit):
      return False

    # 3. Transforma ponto e normal da interseção para o espaço global
    world_pos = glm.vec3(self.m * glm.vec4(local_hit.pos.x, local_hit.pos.y, local_hit.pos.z, 1.0))
    world_outward_normal = glm.normalize(glm.vec3(self.m_inv_t * glm.vec4(local_hit.geo_normal.x, local_hit.geo_normal.y, local_hit.geo_normal.z, 0.0)))

    # 4. Converte o ponto encontrado em um t paramétrico no espaço global.
    ray_d_len_sq = glm.dot(ray.d, ray.d)
    if ray_d_len_sq <= 1e-12:
      return False

    world_t = glm.dot(world_pos - ray.o, ray.d) / ray_d_len_sq
    if world_t <= 0.001 or world_t >= hit.t:
      return False

    hit.t = world_t
    hit.pos = world_pos
    hit.set_face_normal(ray, world_outward_normal)
    hit.material = local_hit.material
    hit.light = local_hit.light
    return True
  

class Translate(Instance):
    """Especialização de Instance para translação simples."""
    def __init__(self, x: float, y: float, z: float, shape: Shape):
        # Cria uma matriz de translação usando GLM
        matrix = glm.translate(glm.mat4(1.0), glm.vec3(x, y, z))
        super().__init__(shape, matrix)

class Rotate(Instance):
    """Especialização de Instance para rotação em torno de um eixo."""
    def __init__(self, angle_deg: float, x: float, y: float, z: float, shape: Shape):
        # Cria uma matriz de rotação (converte graus para radianos)
        matrix = glm.rotate(glm.mat4(1.0), glm.radians(angle_deg), glm.vec3(x, y, z))
        super().__init__(shape, matrix)