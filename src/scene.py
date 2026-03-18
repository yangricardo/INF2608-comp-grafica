import glm
from hit import Hit
from src.light import PointLight
from ray import Ray
from shape import Shape

class Scene:
  def __init__(self):
    self.objects: list[Shape] = []
    self.lights: list[PointLight] = []
    self.ambient_light = glm.vec3(0.1)

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
    return glm.vec3(0.02, 0.02, 0.05) # Background