from __future__ import annotations

from pyglm import glm
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
  from .light import Light
  from .ray import Ray

class Hit:
  def __init__(self, t: float = float('inf')):
    # Slide 4, p. 5-6: o hit guarda a melhor interseção encontrada até o momento.
    # Slide 5, p. 31-35: além da posição e normal, o registro precisa codificar
    # se o raio está entrando ou saindo do meio para orientar Snell e Beer.
    self.t = t
    self.pos = glm.vec3(0)
    self.normal = glm.vec3(0)
    self.geo_normal = glm.vec3(0)
    self.material: Optional[Any] = None  # BSDF no path tracer
    self.light: Optional['Light'] = None
    self.front_face: bool = True
    self.backfacing: bool = False

  def set_face_normal(self, ray: 'Ray', outward_normal: glm.vec3):
    # front_face/backfacing são a versão discreta da orientação do contorno:
    # entrar no meio usa a normal externa; sair do meio inverte a normal para
    # manter os cálculos óticos consistentes com a direção do raio incidente.
    outward = glm.normalize(glm.vec3(outward_normal))
    self.geo_normal = outward
    self.front_face = glm.dot(ray.d, outward) < 0.0
    self.backfacing = not self.front_face
    self.normal = outward if self.front_face else -outward