"""Luz de área representada por malha de triângulos (poliedro).

Referências:
- PBRT 4e §12.4 "Area Lights"
- PBRT 4e §12.6 "Light Sampling"
- PBRT 4e §6.5 "Triangle Sampling"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

from .base import Light
from ..sampling import uniform_triangle
from ..triangle_bvh import TriangleBVH
from ..ray import Ray
from ..hit import Hit

if TYPE_CHECKING:
  from ..scene import Scene


class _BvhTriangle:
  """Wrapper para que dict de triângulo seja compatível com TriangleBVH.

  O BVH espera objetos com atributos .v0, .v1, .v2 (glm.vec3) E com o método
  ``intersect(ray, hit)`` (mesmo contrato da classe ``Triangle`` em ``shape.py``).
  Este wrapper pré-computa ``e1``, ``e2`` e ``normal`` no construtor para
  acelerar o teste de Möller-Trumbore que é invocado na travessia do BVH.
  """
  __slots__ = ('v0', 'v1', 'v2', 'e1', 'e2', 'normal', 'area')
  def __init__(self, v0: glm.vec3, v1: glm.vec3, v2: glm.vec3,
               normal: glm.vec3, area: float):
    self.v0 = glm.vec3(v0)
    self.v1 = glm.vec3(v1)
    self.v2 = glm.vec3(v2)
    # Pré-computação: arestas do triângulo para Möller-Trumbore.
    # Ref: PBRT 4e §3.6.2 / Slide 4, p. 35 — otimização clássica do algoritmo.
    self.e1 = self.v1 - self.v0
    self.e2 = self.v2 - self.v0
    self.normal = glm.vec3(normal)
    self.area = area

  def intersect(self, ray: 'Ray', hit: 'Hit') -> bool:
    """Möller-Trumbore aplicado a este triângulo (mesma lógica de ``Triangle.intersect``).

    Ref: PBRT 4e §3.6.2 "Ray–Triangle Intersection"; Slide 4, p. 35 e p. 47-48.
    Atualiza ``hit.t``, ``hit.pos`` e ``hit.normal`` apenas quando o hit for mais
    próximo que o ``hit.t`` corrente. Não atribui ``hit.material`` — a luz de
    malha não carrega material; a atribuição de material é feita por outras
    instâncias (``Triangle``/``TriangleMesh``) consultadas via
    ``Scene.compute_intersection``.
    """
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
    hit.set_face_normal(ray, self.normal)
    return True


class TriangleMeshLight(Light):
  """Luz de área representada por malha de triângulos com distribuição uniforme.

  Geometria: conjunto de triângulos (poliedro).
  Emissão: constante Le por qualquer direção (hemisfério outward).
  Amostragem: escolhe triângulo por área, depois ponto uniforme no triângulo.

  A avaliação de ``pdf_Li`` usa um BVH interno (``TriangleBVH``) para
  acelerar a interseção raio-malha, substituindo o loop linear O(N).

  Ref: PBRT 4e §6.5 "Triangle Sampling" e §12.4 "Area Lights".
  """

  def __init__(
    self,
    vertices: list[glm.vec3],
    faces: list[tuple[int, int, int]],
    Le: glm.vec3,
  ):
    """Inicializa luz de malha triangular.

    Args:
      vertices: lista de vértices 3D
      faces: lista de tuplas (i0, i1, i2) indexando vertices
      Le: radiância emitida (constante)
    """
    self.vertices = [glm.vec3(v) for v in vertices]
    self.faces = [tuple(face) for face in faces]
    self.Le = glm.vec3(Le)

    # Pré-calcular normais e áreas de cada triângulo
    self.triangles: list[_BvhTriangle] = []
    total_area = 0.0

    for i0, i1, i2 in self.faces:
      v0 = self.vertices[i0]
      v1 = self.vertices[i1]
      v2 = self.vertices[i2]

      e1 = v1 - v0
      e2 = v2 - v0
      cross = glm.cross(e1, e2)
      area = 0.5 * glm.length(cross)

      if area < 1e-8:
        continue

      normal = glm.normalize(cross)
      tri = _BvhTriangle(v0, v1, v2, normal, area)
      self.triangles.append(tri)
      total_area += area

    self.total_area = total_area

    if len(self.triangles) == 0:
      raise ValueError("TriangleMeshLight: no valid triangles")

    # BVH interno para pdf_Li O(log N)
    self._bvh = TriangleBVH(self.triangles, leaf_size=4)

    # Áreas cumulativas para amostragem por CDF
    self.cdf = []
    cumsum = 0.0
    for tri in self.triangles:
      cumsum += tri.area
      self.cdf.append(cumsum / total_area)

  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra ponto uniforme por área na malha.

    Etapa 1: escolhe triângulo com probabilidade ∝ área (CDF sobre u.x).
    Etapa 2: amostra ponto uniforme no triângulo via baricêntricas (PBRT §6.5).

    Ref: PBRT 4e §6.5 "Triangle Meshes" (uniform triangle sampling).
    """
    u_tri = u.x
    tri_idx = len(self.triangles) - 1
    cdf_prev = 0.0
    for i, cdf_val in enumerate(self.cdf):
      if u_tri <= cdf_val:
        tri_idx = i
        break
      cdf_prev = cdf_val

    tri = self.triangles[tri_idx]
    v0, v1, v2 = tri.v0, tri.v1, tri.v2
    normal = tri.normal
    area = tri.area

    bucket = self.cdf[tri_idx] - cdf_prev
    u1 = (u_tri - cdf_prev) / bucket if bucket > 1e-12 else u.y

    b0, b1, b2 = uniform_triangle(u1, u.y)
    p_on_light = b0 * v0 + b1 * v1 + b2 * v2

    l_vec = p_on_light - ref_point
    distance = glm.length(l_vec)

    if distance < 1e-6:
      return None

    wi = l_vec / distance

    cos_at_ref = glm.dot(wi, normal)
    cos_at_light = -cos_at_ref

    if cos_at_light <= 0.0:
      return None

    pdf_solid_angle = 1.0 / self.total_area * distance * distance / cos_at_light

    return {
      'p_on_light': p_on_light,
      'wi': wi,
      'Li': self.Le,
      'pdf_solid_angle': pdf_solid_angle,
      'distance': distance,
      'cos_at_light': cos_at_light,
    }

  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """PDF em ângulo sólido para direção wi.

    Usa BVH interno para interseção O(log N) em vez de loop linear O(N).
    """
    # Construir raio para interseção com a malha
    ray = Ray(ref_point, wi)
    hit = Hit()

    if not self._bvh.intersect(ray, hit):
      return 0.0

    # hit.geo_normal é a normal geométrica outward (nunca invertida por set_face_normal).
    # cos_at_light = -dot(wi, geo_normal): positivo apenas quando o raio vem do lado
    # emissor (hemisfério outward). Hits de face traseira dão cos_at_light ≤ 0 → PDF 0,
    # garantindo consistência com sample_Li que rejeita cos_at_light ≤ 0.
    cos_at_light = -glm.dot(wi, hit.geo_normal)
    if cos_at_light <= 0.0:
      return 0.0

    # pdf_area = 1 / total_area
    # pdf_solid_angle = pdf_area * t² / cos_at_light
    return (hit.t * hit.t) / (self.total_area * cos_at_light)