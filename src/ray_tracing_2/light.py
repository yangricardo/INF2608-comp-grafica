from __future__ import annotations

from pyglm import glm
import math
import random
from typing import TYPE_CHECKING

from ray_tracing_2.ray import Ray

if TYPE_CHECKING:
  from ray_tracing_2.hit import Hit
  from ray_tracing_2.scene import Scene

class Light:
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    self.power = glm.vec3(power)
    self.pos = glm.vec3(pos)

  def radiance(self, scene: "Scene", hit: "Hit"):
    """Calcula a radiância incidente e a direção da luz no ponto de impacto"""
    raise NotImplementedError("Light subclasses must implement radiance()")


class PointLight(Light):
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    super().__init__(pos, power)

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Calcula a radiância incidente e a direção da luz no ponto de impacto"""
    # Slide 4, p. 40: a direção da luz vai do ponto atingido até a posição da fonte.
    l_vec = self.pos - hit.pos
    # Slide 4, p. 40: a intensidade cai com o quadrado da distância.
    dist = glm.distance(self.pos, hit.pos)
    l = glm.normalize(l_vec)

    # Slide 4, p. 38-39 e p. 51-52: lança um shadow ray para testar visibilidade.
    # O epsilon evita que o próprio ponto de impacto seja reintersectado.
    shadow_origin = hit.pos + hit.normal * 0.001
    shadow_ray = Ray(shadow_origin, l)
    shadow_hit = scene.compute_intersection(shadow_ray)

    # Slide 4, p. 38-39: se algo estiver entre o ponto e a luz, o ponto fica em sombra.
    if shadow_hit and shadow_hit.t < dist:
      return glm.vec3(0), l

    # Slide 4, p. 40: potência dividida por r^2 fornece a radiância recebida.
    li = self.power / (dist ** 2)
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
    seed: int | None = None,
  ):
    super().__init__(p, power)
    self.p = glm.vec3(p)
    self.e_u = glm.vec3(e_u)
    self.e_v = glm.vec3(e_v)
    self.samples_u = max(1, int(samples_u))
    self.samples_v = max(1, int(samples_v))
    self.rng = random.Random(seed)
    self.area = glm.length(glm.cross(self.e_u, self.e_v))

  def _sample_position(self, iu: int, iv: int) -> glm.vec3:
    u = (iu + self.rng.random()) / self.samples_u
    v = (iv + self.rng.random()) / self.samples_v
    return self.p + u * self.e_u + v * self.e_v

  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Amostra múltiplos pontos na superfície da luz para produzir penumbra."""
    samples: list[tuple[glm.vec3, glm.vec3]] = []
    sample_count = self.samples_u * self.samples_v
    if sample_count <= 0:
      return samples

    shadow_origin = hit.pos + hit.normal * 0.001
    for iu in range(self.samples_u):
      for iv in range(self.samples_v):
        pos = self._sample_position(iu, iv)
        l_vec = pos - hit.pos
        dist = glm.distance(pos, hit.pos)
        if dist <= 0.0:
          continue
        l = glm.normalize(l_vec)

        shadow_ray = Ray(shadow_origin, l)
        shadow_hit = scene.compute_intersection(shadow_ray)
        if shadow_hit and shadow_hit.t < dist:
          samples.append((glm.vec3(0), l))
          continue

        li = (self.power / float(sample_count)) / (dist ** 2)
        samples.append((li, l))

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
      if li == glm.vec3(0):
        continue
      li_sum += li
      l_sum += l
      valid += 1

    if valid == 0:
      return glm.vec3(0), glm.vec3(0, 0, 1)

    return li_sum, glm.normalize(l_sum)