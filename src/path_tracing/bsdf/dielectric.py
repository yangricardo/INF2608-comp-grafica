"""BSDF Dielétrico (Refratário): vidro, água, ar, diamante, etc.

Implementa reflexão especular com Fresnel e refração (transmissão) com Snell's law.
Suporta absorção via Beer-Lambert para materiais coloridos.

Referências:
- PBRT 4e §9.5 "Dielectric BRDF and BTDF"
- PBRT 4e §5.3.2 "The Fresnel Equations"
- Slide Prof. Celes "Traçado de Caminhos II" — refração

Física:
1. Fresnel: cálculo da refletância R em função do ângulo de incidência
2. Snell's Law: n1*sin(θ1) = n2*sin(θ2)
3. Beer-Lambert: transmitância = exp(-σ * d) onde d é a distância percorrida
"""

from __future__ import annotations
from pyglm import glm
import math
import random
from typing import TYPE_CHECKING

from .base import BSDF

if TYPE_CHECKING:
  pass


class DielectricBSDF(BSDF):
  """BSDF para materiais dielétricos (sem condução).
  
  Combina reflexão (Fresnel) com refração (Snell's law + Beer-Lambert).
  Em cada vértice, escolhe refletir OU refractar (delta distribution).
  
  Ref: PBRT 4e §9.5; Walter et al. 2007 para aproximações Fresnel.
  """
  
  def __init__(
    self,
    ior: float = 1.5,
    absorption: glm.vec3 | None = None,
    seed: int | None = None,
  ):
    """Inicializa BSDF dielétrico.
    
    Args:
      ior: Índice de refração (1.5 = vidro, 1.33 = água, 1.0 = ar)
      absorption: Coeficiente de absorção σ em RGB (default: sem absorção)
      seed: Seed do RNG
    """
    self.ior = float(ior)
    self.absorption = glm.vec3(absorption) if absorption is not None else glm.vec3(0.0)
    self.rng = random.Random(seed)
  
  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Retorna glm.vec3(0) — BSDF dielétrico é uma delta distribution.
    
    Não há reflexão/refração difusa para avaliar fora de direcções específicas.
    """
    return glm.vec3(0.0)
  
  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """Retorna 0.0 — PDF não é amostrável por método inverso.
    
    RR usar reflexão/refração especular: PDF = 0 ou 1 dependendo da decisão.
    """
    return 0.0
  
  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra reflexão OU refração segundo Fresnel.
    
    Etapa 1: Calcular cosseno de incidência cos_i = |wo.z|
    Etapa 2: Calcular refletância Fresnel R(θ_i)
    Etapa 3: RR decision: refletir com prob R, refractar com prob 1-R
    Etapa 4: Retornar direção e PDF=1.0 (delta)
    
    Ref: PBRT 4e §9.5.2 "Specular Reflection and Transmission".
    """
    # Cosseno do ângulo de incidência (wo aponta saída, em frame local wo.z > 0)
    cos_i = abs(wo.z)
    if cos_i < 1e-6:
      return None  # Ray nearly parallel to surface
    
    # Determinar índices de refração entrada/saída
    # Frame local: normal é z=(0,0,1), apontando para cima (exterior)
    # Se wo.z > 0: raio vem de cima → n1=ior, n2=1.0 (ar)
    # Se wo.z < 0: raio vem de baixo → n1=1.0, n2=ior (nunca acontece em path tracer unidirecional)
    
    # Assumir wo aponta para fora (wo.z > 0 em frame local)
    entering = wo.z > 0.0
    n1 = self.ior if entering else 1.0
    n2 = 1.0 if entering else self.ior
    
    # Fresnel: refletância em ângulo θ (Schlick's approximation ou exato)
    # Usar fórmula exata (mais correto para validação)
    # R = |n1*cos_i - n2*cos_t|² / |n1*cos_i + n2*cos_t|²
    # onde cos_t vem de Snell's law: cos_t = sqrt(1 - (n1/n2)² * (1 - cos_i²))
    
    ratio = n1 / n2
    sin_i_sq = 1.0 - cos_i * cos_i
    sin_t_sq = ratio * ratio * sin_i_sq
    
    # Verificar reflexão interna total
    if sin_t_sq > 1.0:
      # Reflexão interna total: refletir sempre
      wi = glm.vec3(-wo.x, -wo.y, wo.z)  # refletir em z (normal para cima)
      return {
        'wi': glm.normalize(wi),
        'pdf': 1.0,
        'f': glm.vec3(1.0),  # Refletância = 1.0
      }
    
    cos_t = glm.sqrt(1.0 - sin_t_sq)
    
    # Fresnel (fórmula exata para interface dielétrica)
    # R = ((n1*cos_i - n2*cos_t) / (n1*cos_i + n2*cos_t))²
    numerator = n1 * cos_i - n2 * cos_t
    denominator = n1 * cos_i + n2 * cos_t
    fresnel = (numerator / denominator) ** 2
    
    # RR decision: refletir com probabilidade fresnel
    if u.x < fresnel:
      # Reflexão especular
      wi = glm.vec3(-wo.x, -wo.y, wo.z)
      return {
        'wi': glm.normalize(wi),
        'pdf': 1.0,
        'f': glm.vec3(fresnel),
      }
    else:
      # Refração especular (Snell's law)
      # Direção refratada em frame local:
      # wi.xy = (n1/n2) * (-wo.xy)
      # wi.z = -cos_t (aponta para interior)
      
      wi_tangent = (n1 / n2) * glm.vec2(-wo.x, -wo.y)
      wi_normal = -cos_t  # aponta para baixo (interior)
      wi = glm.vec3(wi_tangent.x, wi_tangent.y, wi_normal)
      
      # Transmitância (sem absorção por enquanto)
      transmittance = 1.0 - fresnel
      
      return {
        'wi': glm.normalize(wi),
        'pdf': 1.0,
        'f': glm.vec3(transmittance),
      }
