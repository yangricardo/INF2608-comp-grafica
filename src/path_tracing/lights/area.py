"""Luz de área retangular com múltiplos modos de amostragem.

Referências:
- Slide 5, pp. 14-23: AreaLight com penumbra
- PBRT 4e §12.4 "Area Lights"
"""

from __future__ import annotations

from pyglm import glm
import random
from enum import Enum
from typing import TYPE_CHECKING

from .base import Light
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
  """Luz retangular planar com 3 modos de amostragem.
  
  Slide 5, pp. 14-23: penumbra resulta de diferentes estados de oclusão
  entre subamostras da fonte extensa e ponto de impacto.
  
  Modos:
  - REGULAR: amostra centro de cada célula (determinístico)
  - UNIFORM: aleatório puro (menos estrutura)
  - STRATIFIED: jitter dentro de cada célula (default, melhor variância)
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
  
  def _sample_position(self, u: float, v: float) -> glm.vec3:
    """Mapeia coordenadas (u,v) ∈ [0,1]² para ponto no retângulo.
    
    Slide 5, pp. 14-23: p = p0 + u*e_u + v*e_v
    """
    return self.p + u * self.e_u + v * self.e_v
  
  def _iter_sample_uvs(self) -> list[tuple[float, float]]:
    """Retorna pares (u, v) ∈ [0,1]² segundo o modo de amostragem.
    
    Slide 5, pp. 14-23: o quadrado unitário é mapeado para a superfície
    emissiva via _sample_position(). Os três modos diferem no padrão
    de cobertura dentro dessa célula.
    """
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return []
    
    if self.sampling_mode == AreaLightSamplingMode.UNIFORM:
      return uniform_samples_2d(sample_count, self.rng)
    
    if self.sampling_mode == AreaLightSamplingMode.REGULAR:
      return regular_grid_samples_2d(self.samples_u, self.samples_v)
    
    return stratified_grid_samples_2d(self.samples_u, self.samples_v, self.rng)
  
  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Interface legada: amostra superfície emissiva.
    
    Slide 5, pp. 14-23: aproxima integral da luz de área por soma discreta.
    Cada subamostra pode ter visibilidade diferente → penumbra.
    
    Returns:
      Lista de (radiância_incidente, direção_normalizada)
    """
    samples: list[tuple[glm.vec3, glm.vec3]] = []
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return samples
    
    # Slide 5, pp. 14-23: normal do emissor = normalize(e_u × e_v)
    emitter_normal = glm.normalize(glm.cross(self.e_u, self.e_v))
    
    for u, v in self._iter_sample_uvs():
      pos = self._sample_position(u, v)
      l_vec = pos - hit.pos
      dist = glm.length(l_vec)
      if dist <= 0.0:
        continue
      l = glm.normalize(l_vec)
      
      # PBRT 4e, cap. 12.4: emissão é one-sided (só hemisfério da normal)
      # l aponta de hit→luz, então usamos -l para luz→hit
      emission_cosine = max(0.0, float(glm.dot(emitter_normal, -l)))
      if emission_cosine <= 0.0:
        samples.append((glm.vec3(0.0), l))
        continue
      
      transmittance = scene.transmittance(hit.pos, hit.geo_normal, l, dist)
      if _is_black(transmittance):
        samples.append((glm.vec3(0.0), l))
        continue
      
      # Slide 5, pp. 14-23: decaimento 1/r² + emission_cosine + transmitância
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
    """Interface nova (path tracing): stub (implementado via MIS com many-light).
    
    Para path tracing completo com NEE, chamar sample_radiance() com Hit.
    """
    return None
  
  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """Retorna PDF para direção de luz (stub para path tracing)."""
    return 0.0
