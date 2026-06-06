"""Luz de área representada por malha de triângulos (poliedro).

Referências:
- PBRT 4e §12.4 "Area Lights"
- PBRT 4e §12.6 "Light Sampling"
- PBRT 4e §6.5 "Triangle Sampling"
"""

from __future__ import annotations
from pyglm import glm
import random
from typing import TYPE_CHECKING

from .base import Light
from ..sampling import uniform_triangle

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


class TriangleMeshLight(Light):
  """Luz de área representada por malha de triângulos com distribuição uniforme.
  
  Geometria: conjunto de triângulos (poliedro).
  Emissão: constante Le por qualquer direção (hemisfério outward).
  Amostragem: escolhe triângulo por área, depois ponto uniforme no triângulo.
  
  Ref: PBRT 4e §6.5 "Triangle Sampling" e §12.4 "Area Lights".
  """
  
  def __init__(
    self,
    vertices: list[glm.vec3],
    faces: list[tuple[int, int, int]],
    Le: glm.vec3,
    seed: int | None = None,
  ):
    """Inicializa luz de malha triangular.
    
    Args:
      vertices: lista de vértices 3D
      faces: lista de tuplas (i0, i1, i2) indexando vertices
      Le: radiância emitida (constante)
      seed: seed do RNG
    """
    self.vertices = [glm.vec3(v) for v in vertices]
    self.faces = [tuple(face) for face in faces]
    self.Le = glm.vec3(Le)
    
    # Pré-calcular normais e áreas de cada triângulo
    self.triangles = []  # lista de dict {'v0', 'v1', 'v2', 'normal', 'area'}
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
        # Triângulo degenerado; pular
        continue
      
      normal = glm.normalize(cross)
      
      self.triangles.append({
        'v0': v0,
        'v1': v1,
        'v2': v2,
        'normal': normal,
        'area': area,
      })
      total_area += area
    
    self.total_area = total_area
    
    if len(self.triangles) == 0:
      raise ValueError("TriangleMeshLight: no valid triangles")
    
    # Áreas cumulativas para amostragem por CDF
    self.cdf = []
    cumsum = 0.0
    for tri in self.triangles:
      cumsum += tri['area']
      self.cdf.append(cumsum / total_area)
    
    # RNG
    self.rng = random.Random(seed)
  
  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra ponto uniforme por área na malha.

    Etapa 1: escolhe triângulo com probabilidade ∝ área (CDF sobre u.x).
    Etapa 2: amostra ponto uniforme no triângulo via baricêntricas (PBRT §6.5).

    Como a interface fornece só 2 dimensões aleatórias (u.x, u.y), reaproveitamos
    u.x: após localizar o triângulo na CDF, remapeamos u.x para [0,1) dentro do
    seu intervalo, obtendo uma dimensão fresca e independente de u.y. Isso evita
    a degeneração anterior (usar u.y para as duas baricêntricas, colapsando as
    amostras em uma curva 1D dentro do triângulo).

    Ref: PBRT 4e §6.5 "Triangle Meshes" (uniform triangle sampling).
    """
    # Etapa 1: escolher triângulo via CDF, guardando o limite inferior do bucket.
    u_tri = u.x
    tri_idx = len(self.triangles) - 1
    cdf_prev = 0.0
    for i, cdf_val in enumerate(self.cdf):
      if u_tri <= cdf_val:
        tri_idx = i
        break
      cdf_prev = cdf_val

    tri = self.triangles[tri_idx]
    v0, v1, v2 = tri['v0'], tri['v1'], tri['v2']
    normal = tri['normal']
    area = tri['area']

    # Remapear u.x dentro do bucket do triângulo → uniforme fresco em [0,1).
    bucket = self.cdf[tri_idx] - cdf_prev
    u1 = (u_tri - cdf_prev) / bucket if bucket > 1e-12 else u.y

    # Etapa 2: ponto uniforme por área via baricêntricas (helper compartilhado).
    b0, b1, b2 = uniform_triangle(u1, u.y)
    p_on_light = b0 * v0 + b1 * v1 + b2 * v2

    # Direção e distância
    l_vec = p_on_light - ref_point
    distance = glm.length(l_vec)
    
    if distance < 1e-6:
      return None
    
    wi = l_vec / distance
    
    # Cossenos
    cos_at_ref = glm.dot(wi, normal)
    cos_at_light = -cos_at_ref
    
    if cos_at_light <= 0.0:
      # Ponto no lado não-emissor
      return None
    
    # PDF em ângulo sólido
    # pdf_area = 1 / total_area  (escolhemos triângulo com prob area/total_area, depois ponto uniforme no tri)
    # pdf_solid_angle = pdf_area * distance² / |cos_at_light|
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
    
    Interseciona raio com malha, calcula conversão área → ângulo sólido.
    """
    # Para cada triângulo, testar interseção
    closest_t = float('inf')
    closest_tri_idx = -1
    
    for tri_idx, tri in enumerate(self.triangles):
      v0, v1, v2 = tri['v0'], tri['v1'], tri['v2']

      # Emissão unilateral: só o lado emissor conta (cos_at_light = -dot(wi,n) > 0).
      # Triângulo de verso não pode ser amostrado por sample_Li → PDF 0 (MIS).
      if glm.dot(wi, tri['normal']) > -1e-9:
        continue

      # Möller-Trumbore triangle intersection
      e1 = v1 - v0
      e2 = v2 - v0
      pvec = glm.cross(wi, e2)
      det = glm.dot(e1, pvec)

      if abs(det) < 1e-6:
        continue
      
      inv_det = 1.0 / det
      tvec = ref_point - v0
      u = glm.dot(tvec, pvec) * inv_det
      
      if u < 0.0 or u > 1.0:
        continue
      
      qvec = glm.cross(tvec, e1)
      v = glm.dot(wi, qvec) * inv_det
      
      if v < 0.0 or (u + v) > 1.0:
        continue
      
      t = glm.dot(e2, qvec) * inv_det
      
      if t > 1e-4 and t < closest_t:
        closest_t = t
        closest_tri_idx = tri_idx
    
    if closest_tri_idx < 0:
      return 0.0
    
    tri = self.triangles[closest_tri_idx]
    cos_at_light = abs(glm.dot(wi, tri['normal']))
    
    # pdf_area = 1 / total_area
    # pdf_solid_angle = pdf_area * t² / cos_at_light
    return (closest_t * closest_t) / (self.total_area * cos_at_light)
  
  # Métodos legados para compatibilidade
  def radiance(self, scene: "Scene", hit: "Hit"):
    return glm.vec3(0.0), glm.vec3(0, 0, 1)
