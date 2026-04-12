from __future__ import annotations

from pyglm import glm
from ray_tracing_2.hit import Hit
from ray_tracing_2.light import AmbientLight, Light
from ray_tracing_2.ray import Ray
from ray_tracing_2.shape import Shape

class Scene:
  def __init__(self,
               ambient_light: glm.vec3 | AmbientLight = glm.vec3(1,1,1),
               max_depth: int = 4,
               ray_epsilon: float = 0.001):
    self.objects: list[Shape] = []
    self.lights: list[Light] = []
    if isinstance(ambient_light, AmbientLight):
      self.ambient_light = glm.vec3(ambient_light.color)
    else:
      self.ambient_light = glm.vec3(ambient_light)
    self.background_color = glm.vec3(0.02, 0.02, 0.05)
    self.max_depth = max(0, int(max_depth))
    self.ray_epsilon = float(ray_epsilon)

  def compute_intersection(self, ray: Ray):
    # Slide 4, p. 35 e p. 47-48: percorre os objetos e guarda apenas o hit mais próximo.
    closest_hit = Hit()
    found = False
    for obj in self.objects:
      if obj.intersect(ray, closest_hit):
        found = True
    return closest_hit if found else None

  def offset_point(self, pos: glm.vec3, normal: glm.vec3, direction: glm.vec3) -> glm.vec3:
    reference_normal = glm.normalize(glm.vec3(normal))
    sign = 1.0 if glm.dot(direction, reference_normal) >= 0.0 else -1.0
    return glm.vec3(pos) + reference_normal * (self.ray_epsilon * sign)

  def can_spawn_ray(self, depth: int, max_depth: int | None = None) -> bool:
    allowed_depth = self.max_depth if max_depth is None else max_depth
    return depth < allowed_depth

  def transmittance(self,
                    pos: glm.vec3,
                    normal: glm.vec3,
                    direction: glm.vec3,
                    max_distance: float,
                    max_steps: int = 16) -> glm.vec3:
    # 5.tracado_de_raios2.pdf - p.35: Light.SampleRadiance com suporte a materiais transparentes.
    # Implementa o loop:
    #   while hits.material.IsTransparent() do
    #     if hits.IsBackfacing() then I = I * hits.material.a^||p-hits.p||
    #     ray = Ray(hits.p, l̂); hits = scene.ComputeIntersection(ray)
    # A verificação de backfacing e a Lei de Beer (p.33) ficam em
    # TransparentMaterial.shadow_transmittance(), que retorna:
    #   • vec3(1.0) ao entrar (front_face) — sem atenuação ainda
    #   • a^hit.t  ao sair  (backfacing) — Lei de Beer pela espessura percorrida
    #   • vec3(0.0) para materiais opacos — bloqueia o raio
    if max_distance <= 0.0:
      return glm.vec3(0.0)

    throughput = glm.vec3(1.0)
    dir_norm = glm.normalize(glm.vec3(direction))
    origin = self.offset_point(pos, normal, dir_norm)
    remaining = float(max_distance)

    for _ in range(max_steps):
      shadow_ray = Ray(origin, dir_norm)
      shadow_hit = self.compute_intersection(shadow_ray)
      if shadow_hit is None or shadow_hit.t >= remaining:
        return throughput

      if shadow_hit.material is None:
        return glm.vec3(0.0)

      # p.35: delega o cálculo de atenuação ao material
      # TransparentMaterial retorna != 0; Material opaco retorna vec3(0)
      attenuation = shadow_hit.material.shadow_transmittance(self, shadow_hit, shadow_ray)
      if attenuation.x <= 0.0 and attenuation.y <= 0.0 and attenuation.z <= 0.0:
        return glm.vec3(0.0)

      throughput *= attenuation
      if glm.dot(throughput, throughput) <= 1e-8:
        return glm.vec3(0.0)

      remaining -= shadow_hit.t
      if remaining <= self.ray_epsilon:
        return throughput

      exit_normal = shadow_hit.geo_normal if glm.dot(shadow_hit.geo_normal, shadow_hit.geo_normal) > 0.0 else shadow_hit.normal
      origin = self.offset_point(shadow_hit.pos, exit_normal, dir_norm)

    return throughput

  def trace_ray(self, ray: Ray, depth: int = 0, max_depth: int | None = None):
    # Slide 4, p. 35 e p. 55: se houver interseção visível, delega o cálculo de cor ao material.
    hit = self.compute_intersection(ray)    
    if hit and hit.material:
      return hit.material.eval(self, hit, ray, depth=depth, max_depth=max_depth)
    # Slide 4, p. 35: sem hit, o raio retorna a cor de fundo da cena.
    return self.background_color