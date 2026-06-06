"""Interface base para BSDFs (Bidirectional Scattering Distribution Functions).

Referência:
- PBRT 4e §9 "Reflection Models"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..scene import Scene


class BSDF:
  """Interface base para todas as BSDFs.
  
  Todas as operações são em frame local onde a normal é z=(0,0,1).
  As direções (wo, wi) devem estar normalizadas.
  """
  
  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Avalia o valor BSDF f_r(wo, wi) em frame local.
    
    Args:
      wo: direção de saída normalizada (para onde veio a luz)
      wi: direção de entrada normalizada (para onde vai a luz)
    
    Returns:
      Valor f_r (radiância/radiância incidente)
    """
    raise NotImplementedError("BSDF subclasses must implement eval()")
  
  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra direção wi segundo distribuição da BSDF.
    
    Args:
      wo: direção de saída normalizada
      u: variáveis aleatórias 2D uniformes em [0,1)²
    
    Returns:
      Dict com:
        - 'wi': direção de entrada amostrada (normalizada)
        - 'pdf': PDF dessa direção
        - 'f': valor f_r(wo, wi)
      Retorna None ou dict com pdf=0 se amostra for inválida.
    """
    raise NotImplementedError("BSDF subclasses must implement sample()")
  
  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """Calcula PDF de wi dado wo (para MIS).
    
    Args:
      wo: direção de saída normalizada
      wi: direção de entrada normalizada
    
    Returns:
      Probabilidade (PDF) dessa direção
    """
    raise NotImplementedError("BSDF subclasses must implement pdf()")
