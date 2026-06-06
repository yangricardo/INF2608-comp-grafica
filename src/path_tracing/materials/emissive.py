"""Material emissivo para fontes de luz.

Referências:
- PBRT 4e §4.4 "Light Emission"
- Slide 5: emissão local sem depender de iluminação incidente
"""

from __future__ import annotations

from pyglm import glm
from typing import TYPE_CHECKING

from .base import Material

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene
  from ..ray import Ray


class EmissiveMaterial(Material):
  """Material que emite luz própria.
  
  PBRT 4e, cap. 4.4: quando um raio atinge superfície emissiva,
  contribuição observada vem da radiância emitida localmente, sem
  depender de iluminação incidente.
  
  Campo shadow_passthrough: permite "dupla identidade" (painel visível
  + AreaLight coincidente sem ocluir shadow rays).
  """
  
  def __init__(self, emission: glm.vec3, shadow_passthrough: bool = True):
    """Inicializa material emissivo.
    
    Args:
      emission: radiância emitida (RGB)
      shadow_passthrough: se True, transparente para shadow rays (padrão)
    """
    self.emission = glm.vec3(emission)
    self.shadow_passthrough = bool(shadow_passthrough)
  
  def eval(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
    depth: int = 0,
    max_depth: int | None = None,
  ) -> glm.vec3:
    """Retorna radiância emitida.
    
    PBRT 4e, cap. 12.4: sem dependência de iluminação incidente.
    """
    return glm.vec3(self.emission)
  
  def shadow_transmittance(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
  ) -> glm.vec3:
    """Transparência para shadow rays (dupla identidade).
    
    Permite que AreaLight coincidente com painel emissivo não
    ocua shadow rays da câmera.
    """
    if self.shadow_passthrough:
      return glm.vec3(1.0)
    return glm.vec3(0.0)
