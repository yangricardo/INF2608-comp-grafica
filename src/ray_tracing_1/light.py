from __future__ import annotations

import glm

from ray_tracing_1.ray import Ray
from ray_tracing_1.hit import Hit
from ray_tracing_1.scene import Scene

class Light:
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    self.power = glm.vec3(power)
    self.pos = pos

class PointLight(Light):
  def __init__(self, pos: glm.vec3, power: glm.vec3):
    super().__init__(pos, power)

  def sample_radiance(self, scene: Scene, hit: Hit):
    """Calcula a radiância incidente e a direção da luz no ponto de impacto"""
    l_vec = self.pos - hit.pos
    dist = glm.distance(self.pos, hit.pos)
    l = glm.normalize(l_vec)
    
    # Teste de visibilidade (Shadow Ray)
    # Epsilon de 0.001 para evitar shadow acne
    shadow_ray = Ray(hit.pos + hit.normal * 0.001, l)
    shadow_hit = scene.compute_intersection(shadow_ray)
    
    # Se houver algo bloqueando o caminho até a luz
    if shadow_hit and shadow_hit.t < dist:
        return glm.vec3(0), l
        
    # Radiância com decaimento Li = P / r^2
    li = self.power / (dist ** 2)
    return li, l