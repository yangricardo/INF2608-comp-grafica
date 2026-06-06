"""Interface base para luzes no path tracing.

Referência:
- PBRT 4e §12 "Light Sources"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


class Light:
  """Interface base para todas as luzes.
  
  Luzes amostram sua emissão em um ponto de referência e retornam
  PDF em ângulo sólido (para conversão de área).
  """
  
  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra um ponto na superfície da luz.
    
    Args:
      ref_point: ponto de referência na cena de onde a luz é vista
      u: variáveis aleatórias 2D uniformes em [0,1)²
    
    Returns:
      Dict com:
        - 'p_on_light': ponto amostrado na superfície da luz
        - 'wi': direção normalizada de ref_point para p_on_light
        - 'Li': radiância Le emitida
        - 'pdf_solid_angle': PDF em ângulo sólido (para importância)
        - 'distance': distância de ref_point a p_on_light
        - 'cos_at_light': cosseno do ângulo entre normal luz e -wi
      Retorna None se amostra for inválida.
    """
    raise NotImplementedError("Light subclasses must implement sample_Li()")
  
  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """Calcula PDF em ângulo sólido (para MIS).
    
    Args:
      ref_point: ponto de referência
      wi: direção normalizada
    
    Returns:
      PDF dessa direção em ângulo sólido
    """
    raise NotImplementedError("Light subclasses must implement pdf_Li()")
