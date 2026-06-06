"""Interface base para integradores de renderização.

Referência:
- PBRT 4e §13 "Light Transport I: Surface Reflection"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
  from ..ray import Ray
  from ..scene import Scene


class Sampler:
  """Sampler simples para gerar números aleatórios 1D e 2D."""
    
  def __init__(self, seed: int | None = None):
    self.rng = random.Random(seed)
  
  def next_float(self) -> float:
    """Próximo número 1D uniforme em [0,1)."""
    return self.rng.random()
  
  def next_2d(self) -> tuple[float, float]:
    """Próximo par 2D uniforme em [0,1)²."""
    return (self.rng.random(), self.rng.random())


class Integrator:
  """Interface base para integradores."""
  
  def Li(self, ray: Ray, scene: Scene, sampler: Sampler, depth: int = 0) -> glm.vec3:
    """Estima radiância incidente (Li) ao longo do raio.
    
    Args:
      ray: raio primário ou secundário
      scene: cena (primitivas + luzes)
      sampler: gerador de números aleatórios
      depth: profundidade do caminho (1 = primário)
    
    Returns:
      Cor (radiância) estimada
    """
    raise NotImplementedError("Integrator subclasses must implement Li()")
