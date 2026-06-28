"""BSDF Espelho: reflexão especular pura (delta distribution).

Implementa reflexão perfeita sem refração — ideal para demonstrar
comportamento delta puro em contraste com DielectricBSDF (refração + reflexão).

Referências:
- PBRT 4e §9.2 "Specular Reflection and Transmission"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

from .base import BSDF

if TYPE_CHECKING:
  pass


class MirrorBSDF(BSDF):
  """BSDF para superfícies espelhadas (reflexão especular pura).

  Delta distribution: reflete 100% da radiância incidente na direção
  especular, sem absorção ou transmissão. Oposto de DielectricBSDF,
  que permite tanto reflexão quanto refração.
  """

  def __init__(self):
    """Inicializa BSDF de espelho (sem parâmetros)."""
    pass

  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Retorna glm.vec3(0) — delta distribution."""
    return glm.vec3(0.0)

  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """Retorna 0.0 — delta distribution."""
    return 0.0

  def is_specular(self) -> bool:
    """True — espelho é delta (reflexão especular pura)."""
    return True

  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra reflexão especular perfeitamente especular.

    No frame da normal geométrica (z = normal outward):
      wi = vec3(-wo.x, -wo.y, wo.z) — reflexão plana
      f = 1.0 (refletância total)
      pdf = 1.0 (delta)

    Args:
      wo: direção outgoing (frame local)
      u: variáveis aleatórias (ignoradas para delta)

    Returns:
      {wi, pdf, f, transmitted} ou None se raio paralelo
    """
    cos_i = abs(wo.z)
    if cos_i < 1e-6:
      return None  # Raio quase paralelo à superfície

    # Reflexão especular no frame local: inverte x,y mantém z
    wi = glm.vec3(-wo.x, -wo.y, wo.z)
    return {
      'wi': glm.normalize(wi),
      'pdf': 1.0,
      'f': glm.vec3(1.0),  # Refletância total
      'transmitted': False,  # Reflexão (não transmissão)
    }
