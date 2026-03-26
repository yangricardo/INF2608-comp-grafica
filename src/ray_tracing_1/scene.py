from __future__ import annotations

import glm
from ray_tracing_1.hit import Hit
from ray_tracing_1.light import Light
from ray_tracing_1.ray import Ray
from ray_tracing_1.shape import Shape

class Scene:
  def __init__(self, ambient_light: glm.vec3 = glm.vec3(0.1)):
    self.objects: list[Shape] = []
    self.lights: list[Light] = []
    self.ambient_light = ambient_light
    self.background_color = glm.vec3(0.02, 0.02, 0.05)

  def compute_intersection(self, ray: Ray):
    closest_hit = Hit()
    found = False
    for obj in self.objects:
      if obj.intersect(ray, closest_hit):
        found = True
    return closest_hit if found else None

  def trace_ray(self, ray: Ray):
    # [cite: 4, 35, 48, 55]
    hit = self.compute_intersection(ray)    
    if hit and hit.material:
      return hit.material.eval(self, hit, ray.o)
    return self.background_color