"""Luz pontual para ray tracing e path tracing.

Referências:
- Slide 4, pp. 40-41: PointLight(Intensity, Position)
- PBRT 4e §12.1 "Point Lights"
"""

from __future__ import annotations

import math

from pyglm import glm
from typing import TYPE_CHECKING

from .base import Light

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


def _is_black(color: glm.vec3) -> bool:
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0


class PointLight(Light):
  """Luz pontual com emissão isotrópica.

  Interface legada: radiance(), sample_radiance()
  Interface nova (path tracing): sample_Li(), pdf_Li()

  Slide 4, pp. 40-41: a convenção do projeto usa intensidade constante
  sem decaimento 1/r². Apenas a transmitância geométrica/volumétrica
  reduz a energia entregue.

  Como é uma distribuição delta (PBRT 4e §12.1.1), o integrador deve
  usar peso MIS = 1.0 incondicionalmente. Para sinalizar isso, a
  flag ``is_delta = True`` é setada na classe e ``pdf_solid_angle``
  devolve ``math.inf`` (o integrador do path_tracer curto-circuita
  o cálculo MIS nesse caso).
  """

  is_delta: bool = True

  def __init__(self, pos: glm.vec3, power: glm.vec3):
    """Inicializa luz pontual.

    Args:
      pos: posição da fonte (world space)
      power: intensidade/radiância (convenção projeto, sem 1/r²)
    """
    self.pos = glm.vec3(pos)
    self.power = glm.vec3(power)

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Interface legada: calcula radiância incidente e direção da luz.

    Slide 4, pp. 40-41: l = normalize(x_luz - x_hit)

    Returns:
      (radiância_incidente, direção_normalizada)
    """
    l_vec = self.pos - hit.pos
    dist = glm.length(l_vec)
    if dist <= 0.0:
      return glm.vec3(0.0), glm.vec3(0, 0, 1)
    l = glm.normalize(l_vec)

    transmittance = scene.transmittance(hit.pos, hit.geo_normal, l, dist)
    if _is_black(transmittance):
      return glm.vec3(0.0), l

    # Slide 4, pp. 40-41: intensidade constante (sem 1/r²)
    li = self.power * transmittance
    return li, l

  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Interface legada: amostra múltiplos pontos para penumbra.

    PointLight é pontual, então retorna sempre um único ponto.
    """
    return [self.radiance(scene, hit)]

  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Interface nova (path tracing): amostra direção de luz.

    Para PointLight, há apenas um ponto; retorna diretamente.

    Args:
      ref_point: ponto de referência na cena
      u: variáveis aleatórias 2D (ignoradas para luz pontual)

    Returns:
      Dict com pontos de luz ou None se inválido.

    Note:
      ``pdf_solid_angle`` devolve ``math.inf`` (delta distribution).
      O integrador deve usar peso MIS = 1.0 incondicionalmente.
    """
    wi_vec = self.pos - ref_point
    distance = glm.length(wi_vec)
    if distance <= 0.0:
      return None

    wi = glm.normalize(wi_vec)

    return {
      'p_on_light': glm.vec3(self.pos),
      'wi': wi,
      'Li': glm.vec3(self.power),
      'pdf_solid_angle': math.inf,  # delta: PDF = +inf por convenção
      'distance': distance,
      'cos_at_light': 1.0,  # pontual é omnidirecional
    }

  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """Retorna PDF para direção de luz.

    PointLight é uma delta function; não tem PDF contínuo.
    """
    return 0.0
