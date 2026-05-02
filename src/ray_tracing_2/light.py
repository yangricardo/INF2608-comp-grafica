from __future__ import annotations

from pyglm import glm
import random
from enum import Enum
from typing import TYPE_CHECKING

from ray_tracing_2.sampling import regular_grid_samples_2d, stratified_grid_samples_2d, uniform_samples_2d

if TYPE_CHECKING:
  from ray_tracing_2.hit import Hit
  from ray_tracing_2.scene import Scene


def _is_black(color: glm.vec3) -> bool:
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0

class Light:
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    self.power = glm.vec3(power)
    self.pos = glm.vec3(pos)

  def radiance(self, scene: "Scene", hit: "Hit"):
    """Calcula a radiância incidente e a direção da luz no ponto de impacto"""
    raise NotImplementedError("Light subclasses must implement radiance()")
  
  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Amostra múltiplos pontos na superfície da luz para produzir penumbra."""
    return [self.radiance(scene, hit)]


class AmbientLight:
  def __init__(self, r: float | glm.vec3, g: float | None = None, b: float | None = None):
    if isinstance(r, glm.vec3):
      self.color = glm.vec3(r)
    elif g is None or b is None:
      self.color = glm.vec3(r)
    else:
      self.color = glm.vec3(r, g, b)

  def __iter__(self):
    return iter((self.color.x, self.color.y, self.color.z))


class AreaLightSamplingMode(Enum):
  REGULAR = 'regular'
  UNIFORM = 'uniform'
  STRATIFIED = 'stratified'


class PointLight(Light):
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    super().__init__(pos, power)

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Calcula a radiância incidente e a direção da luz no ponto de impacto"""
    # Slide 4, pp. 40-41: a direção da luz vai do ponto atingido até a posição
    # da fonte; geometricamente, isso é o vetor l = normalize(x_luz - x_hit).
    l_vec = self.pos - hit.pos
    dist = glm.length(l_vec)
    if dist <= 0.0:
      return glm.vec3(0.0), glm.vec3(0, 0, 1)
    l = glm.normalize(l_vec)

    transmittance = scene.transmittance(hit.pos, hit.geo_normal, l, dist)
    if _is_black(transmittance):
      return glm.vec3(0.0), l

    # Slide 4, pp. 40-41, e proj1-exemplo.pdf: a base teórica usual teria
    # decaimento geométrico ~ 1/r^2, mas o enunciado adota a convenção prática
    # PointLight(Intensity, Position) com intensidade efetiva constante. Por
    # isso, esta implementação deliberadamente não divide por r^2; a única
    # redução de energia aqui vem da transmitância geométrica/volumétrica.
    # TODO(light): alinhar a nomenclatura `power`/`intensity`/`radiance` para
    # evitar ambiguidade entre a convenção do enunciado e a radiometria física.
    li = self.power * transmittance
    return li, l


class AreaLight(Light):
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
    super().__init__(p, power)
    self.p = glm.vec3(p)
    self.e_u = glm.vec3(e_u)
    self.e_v = glm.vec3(e_v)
    self.samples_u = max(1, int(samples_u))
    self.samples_v = max(1, int(samples_v))
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
    return self.p + u * self.e_u + v * self.e_v

  def _iter_sample_uvs(self) -> list[tuple[float, float]]:
    """Mapeia o modo público da luz para padrões compartilhados no quadrado unitário.

    Os pares retornados vivem no domínio normalizado ``[0,1]^2`` da
    parametrização do emissor, conforme a discussão de luz de área do Slide 5
    (`5.tracado_de_raios2.pdf`, pp. 14-23). O mapeamento afim para o retângulo
    físico acontece depois, em `_sample_position()`, por meio de
    ``p + u e_u + v e_v``.
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
    """Amostra a superfície emissiva para aproximar a integral da luz de área.

    Slide 5, pp. 14-23: a penumbra surge porque diferentes subamostras da fonte
    extensa veem estados de oclusão diferentes a partir do mesmo ponto sombreado.
    """
    samples: list[tuple[glm.vec3, glm.vec3]] = []
    # Slide 5, pp. 14-23: a luz de área aproxima a integral sobre uma fonte
    # extensa por soma discreta de amostras. Cada subamostra enxerga uma
    # visibilidade ligeiramente diferente, produzindo penumbra nas regiões
    # parcialmente ocluídas. Esta base agora expõe três padrões explícitos:
    # regular (centro de cada célula), uniform (aleatório puro na área toda)
    # e stratified (jitter por célula, padrão anterior e padrão default).
    # A definição geométrica desses padrões foi extraída para `sampling.py`; aqui
    # a classe só converte o par (u, v) do quadrado unitário para um ponto real
    # na superfície emissiva antes de avaliar visibilidade e 1/r^2.
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return samples

    # Slide 5, pp. 14-23: a normal do emissor retangular vem do produto vetorial
    # entre as arestas, n = normalize(e_u x e_v). Isso fixa a orientação física
    # da fonte extensa e entra no termo angular da emissão.
    emitter_normal = glm.normalize(glm.cross(self.e_u, self.e_v))

    for u, v in self._iter_sample_uvs():
      pos = self._sample_position(u, v)
      l_vec = pos - hit.pos
      dist = glm.length(l_vec)
      if dist <= 0.0:
        continue
      l = glm.normalize(l_vec)

      # Os slides pedem a normal da luz de área e discutem o fator angular da
      # radiância recebida; para a regra explícita de emissão em apenas um lado,
      # seguimos PBRT 4e, cap. 12.4 (DiffuseAreaLight): por padrão, a emissão é
      # one-sided e só existe quando a direção de saída está no hemisfério da
      # normal. Como `l` aponta de hit->luz, usamos `-l` para obter luz->hit.
      emission_cosine = max(0.0, float(glm.dot(emitter_normal, -l)))
      if emission_cosine <= 0.0:
        samples.append((glm.vec3(0.0), l))
        continue

      transmittance = scene.transmittance(hit.pos, hit.geo_normal, l, dist)
      if _is_black(transmittance):
        samples.append((glm.vec3(0.0), l))
        continue

      # Slide 5, pp. 14-23: a luz de área é aproximada por integração discreta
      # sobre a superfície emissiva, com queda geométrica em 1/r^2. O fator
      # `emission_cosine` torna a emissão coerente com uma fonte difusa orientada,
      # em linha com PBRT 4e, cap. 12.4.
      li = (((self.power / float(sample_count)) / (dist ** 2)) * emission_cosine) * transmittance
      samples.append((li, l))

    # TODO(light): incorporar fator angular do emissor (coseno da emissão) se
    # a fonte de área deixar de ser usada apenas como aproximador didático.

    return samples

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Mantém a interface base, retornando a média da luz e uma direção representativa."""
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