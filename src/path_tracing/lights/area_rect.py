"""Luz de área retangular planar.

Referências:
- PBRT 4e §12.4 "Area Lights"
- PBRT 4e §12.6 "Light Sampling"
- PBRT 4e §13.1.1 "Area Light Sample Integral"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

from .base import Light

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


class RectAreaLight(Light):
  """Luz retangular planar em 3D.

  Geometria: paralelogramo definido por corner (canto) e dois edges (arestas).
  Emissão: constante Le por qualquer direção (hemisfério outward).
  Amostragem: uniforme por área, depois conversão para ângulo sólido.
  """

  def __init__(
    self,
    corner: glm.vec3,
    edge_u: glm.vec3,
    edge_v: glm.vec3,
    Le: glm.vec3,
  ):
    """Inicializa luz retangular.

    Args:
      corner: ponto de canto (v0)
      edge_u: primeira aresta (v1 - v0)
      edge_v: segunda aresta (v3 - v0)
      Le: radiância emitida (constante)
    """
    self.corner = glm.vec3(corner)
    self.edge_u = glm.vec3(edge_u)
    self.edge_v = glm.vec3(edge_v)
    self.Le = glm.vec3(Le)

    # Normal: cross(edge_u, edge_v), normalizada
    cross_prod = glm.cross(self.edge_u, self.edge_v)
    self.normal = glm.normalize(cross_prod)

    # Área do paralelogramo
    self.area = glm.length(cross_prod)

    # Centro para referência
    self.center = self.corner + 0.5 * self.edge_u + 0.5 * self.edge_v

  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra ponto uniforme na superfície da luz.

    Ref: PBRT 4e §12.6; §13.1.1 (conversão pdf_area → pdf_solid_angle)
    """
    # Ref: PBRT 4e §12.6 "Light Sampling"; §13.1.1 "Area Light Sample Integral"

    # Amostra paramétricas [0,1]² para posição no retângulo
    u_pos = u.x  # coordenada em edge_u
    v_pos = u.y  # coordenada em edge_v

    # Ponto na superfície
    p_on_light = self.corner + u_pos * self.edge_u + v_pos * self.edge_v

    # Direção de ref_point para p_on_light
    l_vec = p_on_light - ref_point
    distance = glm.length(l_vec)

    if distance < 1e-6:
      # Ponto muito perto; amostra inválida
      return None

    wi = l_vec / distance

    # Cossenos
    cos_at_ref = glm.dot(wi, self.normal)  # ângulo em ref_point
    cos_at_light = -cos_at_ref  # ângulo na luz (normal aponta para fora)

    if cos_at_light <= 0.0:
      # Ref_point está no lado não-emissor da luz
      return None

    # Conversão pdf_area → pdf_solid_angle
    # pdf_area = 1/area
    # pdf_solid_angle = pdf_area * distance² / |cos_at_light|
    pdf_solid_angle = 1.0 / self.area * distance * distance / cos_at_light

    return {
      'p_on_light': p_on_light,
      'wi': wi,
      'Li': self.Le,
      'pdf_solid_angle': pdf_solid_angle,
      'distance': distance,
      'cos_at_light': cos_at_light,
    }

  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """PDF em ângulo sólido para direção wi a partir de ref_point.

    Interseciona o raio (ref_point, wi) com o plano da luz para obter
    a distância e calcular a conversão área → ângulo sólido.

    Ref: PBRT 4e §13.1.1; Veach & Guibas SIGGRAPH 1995 eq. 9.
    """
    # Interseção com o plano da luz via equação paramétrica:
    # p(t) = ref_point + t * wi;  dot(p(t) - corner, normal) = 0
    denom = glm.dot(wi, self.normal)
    # Emissão unilateral: só o lado emissor conta (mesmo critério de sample_Li,
    # onde cos_at_light = -dot(wi, normal) > 0  ⟺  denom < 0). Raio paralelo ao
    # plano ou atingindo o verso não-emissor → PDF 0 (consistência do MIS).
    if denom > -1e-6:
      return 0.0

    t = glm.dot(self.corner - ref_point, self.normal) / denom
    if t <= 1e-4:
      return 0.0  # Interseção atrás ou muito perto

    p_hit = ref_point + t * wi

    # Verificar se o ponto está dentro do paralelogramo
    # Projetar (p_hit - corner) nas arestas e checar [0, 1]
    d = p_hit - self.corner
    len_u = glm.length(self.edge_u)
    len_v = glm.length(self.edge_v)
    if len_u < 1e-9 or len_v < 1e-9:
      return 0.0
    u_coord = glm.dot(d, self.edge_u) / (len_u * len_u)
    v_coord = glm.dot(d, self.edge_v) / (len_v * len_v)
    if not (0.0 <= u_coord <= 1.0 and 0.0 <= v_coord <= 1.0):
      return 0.0  # Fora do retângulo

    cos_at_light = -denom  # denom < 0 garantido acima ⇒ = |denom|
    # pdf_area = 1/area; conversão: pdf_solid_angle = pdf_area * t² / cos_at_light
    return (t * t) / (self.area * cos_at_light)
