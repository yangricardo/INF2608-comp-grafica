"""Luz de área retangular com múltiplos modos de amostragem (legado).

Referências:
- Slide 5, pp. 14-23: AreaLight com penumbra
- PBRT 4e §12.4 "Area Lights"

Nota:
  ``AreaLight`` é a implementação legada do Projeto 1 (modos REGULAR/UNIFORM/STRATIFIED
  com ``sample_radiance``). A interface nova de path tracing (``sample_Li``/``pdf_Li``)
  delega para ``RectAreaLight`` — a luz moderna.
"""

from __future__ import annotations

from pyglm import glm
import random
from enum import Enum
from typing import TYPE_CHECKING

from .base import Light
from .area_rect import RectAreaLight
from ..sampling import regular_grid_samples_2d, stratified_grid_samples_2d, uniform_samples_2d

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


def _is_black(color: glm.vec3) -> bool:
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0


class AreaLightSamplingMode(Enum):
  """Modos de amostragem para luz de área."""
  REGULAR = 'regular'        # Centro de cada célula
  UNIFORM = 'uniform'        # Aleatório puro sobre área
  STRATIFIED = 'stratified'  # Jitter por célula


class AreaLight(Light):
  """Luz retangular planar com 3 modos de amostragem (legado).

  Slide 5, pp. 14-23: penumbra resulta de diferentes estados de oclusão
  entre subamostras da fonte extensa e ponto de impacto.

  Modos:
  - REGULAR: amostra centro de cada célula (determinístico)
  - UNIFORM: aleatório puro (menos estrutura)
  - STRATIFIED: jitter dentro de cada célula (default, melhor variância)

  A interface ``sample_Li``/``pdf_Li`` (path tracing) delega para um
  ``RectAreaLight`` interno usando ``Le = power / area``.
  """

  def __init__(
    self,
    p: glm.vec3,
    e_u: glm.vec3,
    e_v: glm.vec3,
    power: glm.vec3,
    samples_u: int = 4,
    samples_v: int = 4,
    sampling_mode: str | AreaLightSamplingMode = AreaLightSamplingMode.STRATIFIED,
    seed: int | None = None,
  ):
    """Inicializa luz de área retangular.

    Args:
      p: canto do retângulo (v0)
      e_u: primeira aresta (v1 - v0)
      e_v: segunda aresta (v3 - v0)
      power: intensidade/power (será dividida por n_samples)
      samples_u: número de amostras em u
      samples_v: número de amostras em v
      sampling_mode: REGULAR, UNIFORM, ou STRATIFIED
      seed: seed para RNG (default: None)
    """
    self.p = glm.vec3(p)
    self.e_u = glm.vec3(e_u)
    self.e_v = glm.vec3(e_v)
    self.power = glm.vec3(power)
    self.samples_u = max(1, int(samples_u))
    self.samples_v = max(1, int(samples_v))

    # Parse sampling mode
    if isinstance(sampling_mode, AreaLightSamplingMode):
      self.sampling_mode = sampling_mode
    else:
      mode_str = str(sampling_mode).lower()
      if mode_str == AreaLightSamplingMode.REGULAR.value:
        self.sampling_mode = AreaLightSamplingMode.REGULAR
      elif mode_str == AreaLightSamplingMode.UNIFORM.value:
        self.sampling_mode = AreaLightSamplingMode.UNIFORM
      else:
        self.sampling_mode = AreaLightSamplingMode.STRATIFIED

    self.rng = random.Random(seed)
    self.area = glm.length(glm.cross(self.e_u, self.e_v))

    # Luz moderna delegada para sample_Li/pdf_Li (path tracing NEE/MIS).
    # ``Le = power / area`` para que a energia total emitida (fluxo)
    # seja compatível com a interface legada (power é intensidade total).
    # Ref: PBRT 4e §12.4 "Area Lights" — relação entre power e Le.
    self._rect_light = RectAreaLight(
      corner=self.p,
      edge_u=self.e_u,
      edge_v=self.e_v,
      Le=self.power / self.area if self.area > 1e-12 else glm.vec3(0.0),
    )

  def _sample_position(self, u: float, v: float) -> glm.vec3:
    """Mapeia coordenadas (u,v) ∈ [0,1]² para ponto no retângulo."""
    return self.p + u * self.e_u + v * self.e_v

  def _iter_sample_uvs(self) -> list[tuple[float, float]]:
    """Retorna pares (u, v) ∈ [0,1]² segundo o modo de amostragem."""
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return []

    if self.sampling_mode == AreaLightSamplingMode.UNIFORM:
      return uniform_samples_2d(sample_count, self.rng)

    if self.sampling_mode == AreaLightSamplingMode.REGULAR:
      return regular_grid_samples_2d(self.samples_u, self.samples_v)

    return stratified_grid_samples_2d(self.samples_u, self.samples_v, self.rng)

  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Interface legada: amostra superfície emissiva."""
    samples: list[tuple[glm.vec3, glm.vec3]] = []
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return samples

    emitter_normal = glm.normalize(glm.cross(self.e_u, self.e_v))

    for u, v in self._iter_sample_uvs():
      pos = self._sample_position(u, v)
      l_vec = pos - hit.pos
      dist = glm.length(l_vec)
      if dist <= 0.0:
        continue
      l = glm.normalize(l_vec)

      emission_cosine = max(0.0, float(glm.dot(emitter_normal, -l)))
      if emission_cosine <= 0.0:
        samples.append((glm.vec3(0.0), l))
        continue

      transmittance = scene.transmittance(hit.pos, hit.geo_normal, l, dist)
      if _is_black(transmittance):
        samples.append((glm.vec3(0.0), l))
        continue

      li = (((self.power / float(sample_count)) / (dist ** 2)) * emission_cosine) * transmittance
      samples.append((li, l))

    return samples

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Interface legada: retorna média da luz e direção representativa."""
    samples = self.sample_radiance(scene, hit)
    if not samples:
      return glm.vec3(0), glm.vec3(0, 0, 1)

    li_sum = glm.vec3(0)
    l_sum = glm.vec3(0)
    valid = 0
    for li, l in samples:
      if _is_black(li):
        continue
      li_sum += li
      l_sum += l
      valid += 1

    if valid == 0:
      return glm.vec3(0), glm.vec3(0, 0, 1)

    return li_sum, glm.normalize(l_sum)

  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Interface nova (path tracing): delega para ``RectAreaLight``."""
    return self._rect_light.sample_Li(ref_point, u)

  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """Retorna PDF para direção de luz (delega para ``RectAreaLight``)."""
    return self._rect_light.pdf_Li(ref_point, wi)