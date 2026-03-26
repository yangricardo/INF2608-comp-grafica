from __future__ import annotations

import glm
from ray_tracing_1.ray import Ray
from ray_tracing_1.hit import Hit
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ray_tracing_1.scene import Scene

class Material:
  def eval(self, scene: Scene, hit: Hit, ray_origin: glm.vec3):
    raise NotImplementedError("Material subclasses must implement eval()")

class PhongMaterial(Material):
  def __init__(self, ambient: glm.vec3, diffuse: glm.vec3, specular: glm.vec3, shininess: float):
    self.m_amb = glm.vec3(ambient)
    self.m_dif = glm.vec3(diffuse)
    self.m_spe = glm.vec3(specular)
    self.shi = shininess

  def eval(self, scene: Scene, hit: Hit, ray_origin: glm.vec3):
    # Slide 4, p. 41-42: começa pela contribuição ambiente, independente da direção da luz.
    color = self.m_amb * scene.ambient_light
    # Slide 4, p. 32 e p. 49: o vetor de visão vai do ponto atingido até a câmera.
    v = glm.normalize(ray_origin - hit.pos)
    
    for light in scene.lights:
      # Slide 4, p. 38-40: a luz informa visibilidade e radiância já com atenuação.
      li, l = light.radiance(scene, hit)
      
      # Slide 4, p. 38-39: se a radiância chegou zerada, o ponto está em sombra.
      if li == glm.vec3(0): continue
      
      # Slide 4, p. 32 e p. 49: termo difuso de Lambert, proporcional a n·l.
      n_dot_l = max(0.0, glm.dot(hit.normal, l))
      color += self.m_dif * li * n_dot_l
      
      # Slide 4, p. 32 e p. 49: termo especular de Phong, baseado em r·v.
      r = glm.reflect(-l, hit.normal)
      r_dot_v = max(0.0, glm.dot(r, v))
      color += self.m_spe * li * (r_dot_v ** self.shi)
        
    return color