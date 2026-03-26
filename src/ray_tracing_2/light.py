from __future__ import annotations

import glm
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