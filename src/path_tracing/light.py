"""WRAPPER DE COMPATIBILIDADE: re-exporta de lights/

Este arquivo mantém compatibilidade com código que importa de path_tracing.light.
Todas as implementações foram movidas para path_tracing/lights/ (modular).

Referências:
- lights.base.Light: interface base
- lights.point.PointLight: luz pontual
- lights.area.AreaLight: luz retangular com sampling modes
"""

from __future__ import annotations

from pyglm import glm

# Re-exporta interface base
from .lights.base import Light

# Re-exporta implementações específicas (legadas)
from .lights.point import PointLight
from .lights.area import AreaLight, AreaLightSamplingMode

# AmbientLight é standalone (não herda de Light)
class AmbientLight:
  """Luz ambiente global (não uma fonte de luz pontual/area).
  
  Usado em cálculos de iluminação indireta aproximada (Phong.direct_lighting).
  """
  
  def __init__(self, r: float | glm.vec3, g: float | None = None, b: float | None = None):
    if isinstance(r, glm.vec3):
      self.color = glm.vec3(r)
    elif g is None or b is None:
      self.color = glm.vec3(r)
    else:
      self.color = glm.vec3(r, g, b)
  
  def __iter__(self):
    return iter((self.color.x, self.color.y, self.color.z))


def _is_black(color: glm.vec3) -> bool:
  """Retorna True se cor é próxima a preto (todos componentes ≤ 0)."""
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0


__all__ = [
  'Light',
  'PointLight',
  'AreaLight',
  'AreaLightSamplingMode',
  'AmbientLight',
  '_is_black',
]