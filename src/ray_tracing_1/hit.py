from __future__ import annotations

import glm
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
  from ray_tracing_1.material import Material
  from ray_tracing_1.light import Light

class Hit:
  def __init__(self, t: float = float('inf')):
    # Slide 4, p. 5-6: o hit guarda a melhor interseção encontrada até o momento.
    self.t = t
    self.pos = glm.vec3(0)
    self.normal = glm.vec3(0)
    self.material: Optional['Material'] = None
    self.light: Optional['Light'] = None
    self.backfacing: bool = False