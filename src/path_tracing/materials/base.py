"""Interface base para materiais em ray tracing e path tracing.

Referências:
- Slide 4-5: materiais de ray tracing (Phong, reflexão, refração)
- PBRT 4e §5 "Color and Radiometry", §9 "Materials"
"""

from __future__ import annotations

from pyglm import glm
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene
  from ..ray import Ray


class Material(ABC):
  """Interface base para todos os materiais.
  
  Todo material implementa:
  - eval(): avaliação local + recursiva (ray tracing clássico)
  - shadow_transmittance(): transmitância para raios de sombra (para TR e path tracing)
  """
  
  @abstractmethod
  def eval(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
    depth: int = 0,
    max_depth: int | None = None,
  ) -> glm.vec3:
    """Avalia contribuição de luz no ponto de impacto.
    
    Slide 4-5: pode incluir iluminação direta (Phong) + recursão
    (reflexão especular, refração) até atingir profundidade máxima.
    
    Args:
      scene: cena com luzes e geometria
      hit: ponto de impacto
      ray: raio incidente
      depth: profundidade de recursão atual
      max_depth: profundidade máxima permitida
    
    Returns:
      Vetor de radiância/cor RGB no ponto
    """
    raise NotImplementedError("Material.eval() must be implemented")
  
  def shadow_transmittance(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
  ) -> glm.vec3:
    """Transmitância para raios de sombra.
    
    Slide 5, p.35: Light.SampleRadiance só continua enquanto
    hit.material.IsTransparent(). Materiais opacos retornam vec3(0).
    
    Args:
      scene: cena
      hit: ponto onde o raio de sombra passa
      ray: raio de sombra (teste de visibilidade)
    
    Returns:
      Fator de transmitância [0,1]³ (1=transparente, 0=bloqueado)
    """
    return glm.vec3(0.0)
