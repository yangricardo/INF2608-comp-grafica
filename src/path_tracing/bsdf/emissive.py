"""BSDF Emissiva (marcadora de superfícies que emitem luz).

Referência:
- PBRT 4e §4.4 "Light Emission"
"""

from __future__ import annotations
from pyglm import glm

from .base import BSDF


class EmissiveBSDF(BSDF):
  """BSDF terminal para superfícies emissivas.
  
  Não participa da BRDF (eval=0, pdf=0). Serve apenas para marcar
  superfícies que emitem Le (radiância) e, no path tracing, para
  terminação de caminhos em primário (depth=1) ou após NEE.
  """
  
  def __init__(self, Le: glm.vec3):
    """Inicializa BSDF emissiva.
    
    Args:
      Le: radiância emitida (típ. branca ou colorida)
    """
    self.Le = glm.vec3(Le)
    self.is_emissive = True
  
  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Retorna zero (não reflete, apenas emite)."""
    return glm.vec3(0.0)
  
  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict | None:
    """Retorna None (não é amostrada como BSDF)."""
    return None
  
  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """Retorna zero (não é amostrada como BSDF)."""
    return 0.0
