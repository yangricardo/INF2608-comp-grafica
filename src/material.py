import glm
from ray import Ray
from hit import Hit
from scene import Scene

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
    # Luz Ambiente [cite: 4, 41, 42]
    color = self.m_amb * scene.ambient_light
    v = glm.normalize(ray_origin - hit.pos)
    
    for light in scene.lights:
      # Radiance e Shadow [cite: 4, 36, 39, 52]
      l_vec = light.pos - hit.pos
      dist = glm.distance(light.pos, hit.pos)
      l = glm.normalize(l_vec)
      
      # Shadow Ray para visibilidade [cite: 4, 39, 51]
      shadow_ray = Ray(hit.pos + hit.normal * 0.001, l)
      shadow_hit = scene.compute_intersection(shadow_ray)
      
      if shadow_hit and shadow_hit.t < dist:
        continue # O ponto está em sombra
          
      li = light.power / (dist ** 2)
      
      # Difusa (Lambert) [cite: 4, 32, 49]
      n_dot_l = max(0.0, glm.dot(hit.normal, l))
      color += self.m_dif * li * n_dot_l
      
      # Especular (Phong) [cite: 4, 32, 49]
      r = glm.reflect(-l, hit.normal)
      r_dot_v = max(0.0, glm.dot(r, v))
      color += self.m_spe * li * (r_dot_v ** self.shi)
        
    return color