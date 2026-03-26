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
    # Luz Ambiente [cite: 4, 41, 42] $c = m_{amb} * l_{amb}$
    color = self.m_amb * scene.ambient_light
    v = glm.normalize(ray_origin - hit.pos)
    
    for light in scene.lights:
      # luz agora resolve a visibilidade e o decaimento
      li, l = light.radiance(scene, hit)
      
      if li == glm.vec3(0): continue # Ponto em sombra
      
      # Difusa (Lambert) [cite: 4, 32, 49]
      n_dot_l = max(0.0, glm.dot(hit.normal, l))
      color += self.m_dif * li * n_dot_l
      
      # Especular (Phong) [cite: 4, 32, 49]
      r = glm.reflect(-l, hit.normal)
      r_dot_v = max(0.0, glm.dot(r, v))
      color += self.m_spe * li * (r_dot_v ** self.shi)
        
    return color