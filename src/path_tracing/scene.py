from __future__ import annotations

from pyglm import glm
from .hit import Hit
from .light import AmbientLight, Light
from .ray import Ray
from .shape import Shape

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
    # Perfil de execução (instrumentação leve para calibração/diagnóstico)
    # Contadores: `rays_traced` inclui primários e secundários (cada chamada a trace_ray),
    # `shadow_rays` conta chamadas explícitas de shadow-ray em transmittance(),
    # `intersection_tests` conta testes de interseção por primitiva.
    self._profile_stats = {
      'rays_traced': 0,
      'shadow_rays': 0,
      'intersection_tests': 0,
    }

  def compute_intersection(self, ray: Ray):
    # Slide 4, p. 35 e p. 47-48: percorre os objetos e guarda apenas o hit mais
    # próximo, isto é, o menor t positivo compatível com a geometria visível.
    # TODO(accel): substituir este loop linear por um agregador global de cena
    # quando houver muitas primitivas heterogêneas e/ou múltiplas malhas BVH.
    closest_hit = Hit()
    found = False
    for obj in self.objects:
      # Conta um teste de interseção por primitiva testada (instrumentação)
      try:
        self._profile_stats['intersection_tests'] += 1
      except Exception:
        pass
      if obj.intersect(ray, closest_hit):
        found = True
    return closest_hit if found else None

  def offset_point(self, pos: glm.vec3, normal: glm.vec3, direction: glm.vec3) -> glm.vec3:
    # O pequeno deslocamento ao longo da normal separa numericamente o novo raio
    # da superfície que o gerou, evitando auto-interseção em sombra, reflexão e
    # refração. Sem isso surgem artefatos clássicos de shadow acne. Em termos
    # geométricos, é uma perturbação controlada em torno da solução ideal t=0.
    reference_normal = glm.normalize(glm.vec3(normal))
    sign = 1.0 if glm.dot(direction, reference_normal) >= 0.0 else -1.0
    return glm.vec3(pos) + reference_normal * (self.ray_epsilon * sign)

  def can_spawn_ray(self, depth: int, max_depth: int | None = None) -> bool:
    # Slide 5, p. 26-34: o segundo conjunto de slides estende o traçador local
    # do Slide 4 para um traçador recursivo. Este limite mantém a aproximação
    # finita e controla o custo das cadeias de reflexão/refração.
    allowed_depth = self.max_depth if max_depth is None else max_depth
    return depth < allowed_depth

  def transmittance(self,
                    pos: glm.vec3,
                    normal: glm.vec3,
                    direction: glm.vec3,
                    max_distance: float,
                    max_steps: int = 16) -> glm.vec3:
    # Slide 5, p. 35: este método generaliza o shadow ray binário do Slide 4.
    # Em vez de responder apenas "livre" ou "bloqueado", ele acumula o
    # throughput ao longo do segmento até a luz: materiais opacos zeram a
    # energia, enquanto interfaces transparentes delegam a Beer-Lambert para
    # `shadow_transmittance()`. O resultado é um produto discreto de fatores de
    # transmitância, análogo a T = Π_k a_k^{s_k} para um meio homogêneo por trecho.
    # TODO(transmittance): expor um critério de parada baseado em profundidade
    # óptica acumulada, além de `max_steps`, para cenas com muitos transparentes.
    if max_distance <= 0.0:
      return glm.vec3(0.0)

    throughput = glm.vec3(1.0)
    dir_norm = glm.normalize(glm.vec3(direction))
    origin = self.offset_point(pos, normal, dir_norm)
    # Subtrai ray_epsilon para compensar o offset inicial da origem:
    # sem isso, objetos que estão exatamente na posição da luz (como o teto na y=5.55
    # quando a luz também está em y=5.55) aparecem dentro do alcance máximo e
    # bloqueiam todos os raios de sombra.
    remaining = float(max_distance) - self.ray_epsilon

    for _ in range(max_steps):
      # Conta um shadow-ray gerado (instrumentação)
      try:
        self._profile_stats['shadow_rays'] += 1
      except Exception:
        pass
      shadow_ray = Ray(origin, dir_norm)
      shadow_hit = self.compute_intersection(shadow_ray)
      # Usa remaining - ray_epsilon para dar margem de tolerância acumulada:
      # cada offset_point adiciona um epsilon, então objetos na fronteira da luz
      # (t ≈ remaining) não devem bloquear o raio.
      if shadow_hit is None or shadow_hit.t >= remaining - self.ray_epsilon:
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

  def reset_profile_stats(self) -> None:
    """Zera os contadores de perfil da cena."""
    for k in self._profile_stats:
      self._profile_stats[k] = 0

  def profile_stats(self) -> dict:
    """Retorna uma cópia dos contadores atuais de perfil."""
    return dict(self._profile_stats)

  def trace_ray(self, ray: Ray, depth: int = 0, max_depth: int | None = None):
    # Slide 4, p. 35 e p. 55: o núcleo do traçador local é encontrar o hit e
    # delegar a cor ao material. Slide 5 reaproveita esse mesmo ponto de entrada
    # para raios secundários, mudando apenas depth/max_depth.
    # Conta uma chamada a trace_ray (inclui primários e secundários)
    try:
      self._profile_stats['rays_traced'] += 1
    except Exception:
      pass
    hit = self.compute_intersection(ray)
    if hit and hit.material:
      return hit.material.eval(self, hit, ray, depth=depth, max_depth=max_depth)
    # Slide 4, p. 35: sem hit, o raio retorna a cor de fundo da cena.
    return self.background_color