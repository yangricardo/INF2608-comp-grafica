from __future__ import annotations

from pyglm import glm
from .hit import Hit
from typing import TYPE_CHECKING
from .ray import Ray

if TYPE_CHECKING:
  from .scene import Scene


def _vec3(value: float | glm.vec3) -> glm.vec3:
  return glm.vec3(value)


def _is_black(color: glm.vec3) -> bool:
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0


class Material:
  # Interface base para todos os materiais de traçado de raios.
  def eval(self,
           scene: Scene,
           hit: Hit,
           ray: Ray,
           depth: int = 0,
           max_depth: int | None = None):
    raise NotImplementedError("Material subclasses must implement eval()")

  def shadow_transmittance(self, scene: 'Scene', hit: Hit, ray: Ray) -> glm.vec3:
    # 5.tracado_de_raios2.pdf - p.35: Light.SampleRadiance
    # Material opaco bloqueia o raio de sombra completamente — loop só continua
    # enquanto hits.material.IsTransparent(); qualquer opaco interrompe.
    return glm.vec3(0.0)


class EmissiveMaterial(Material):
  # Material emissivo local: aparece brilhante sem depender de luz incidente.
  # No modo padrão, é transparente para shadow rays para permitir a estratégia
  # de dupla identidade (painel visível + AreaLight sobreposta).
  # Os slides-base do projeto separam materiais de fontes de luz e não definem
  # um "Phong emissivo" explícito. Para esta extensão, seguimos a ideia de
  # emissão própria discutida em PBRT 4e, cap. 4.4 (Light Emission): quando um
  # raio primário atinge uma superfície emissiva, ela pode devolver radiância
  # emitida localmente sem depender de iluminação incidente.
  def __init__(self, emission: glm.vec3, shadow_passthrough: bool = True):
    self.emission = glm.vec3(emission)
    self.shadow_passthrough = bool(shadow_passthrough)

  def eval(self,
           scene: 'Scene',
           hit: Hit,
           ray: Ray,
           depth: int = 0,
           max_depth: int | None = None):
    # PBRT 4e, cap. 12.4 (Area Lights): quando um raio intersecta uma superfície
    # emissiva, a contribuição observada pode vir diretamente da radiância
    # emitida por ela. Aqui modelamos a versão mais simples: emissão constante.
    return glm.vec3(self.emission)

  def shadow_transmittance(self, scene: 'Scene', hit: Hit, ray: Ray) -> glm.vec3:
    # Esta escolha não vem diretamente dos slides: ela é um artifício de
    # engenharia para manter a "dupla identidade". O painel é visível para a
    # câmera, mas não deve ocluir a AreaLight coincidente ao lançar shadow rays.
    if self.shadow_passthrough:
      return glm.vec3(1.0)
    return glm.vec3(0.0)


class PhongMaterial(Material):
  # 5.tracado_de_raios2.pdf - p.27: PhongMaterial.Eval.
  # Sintese fisica: c = c_amb + k_d L_i max(0, n·l) + k_s L_i max(0, r·v)^s.
  def __init__(self, ambient: glm.vec3, diffuse: glm.vec3, specular: glm.vec3, shininess: float):
    self.m_amb = glm.vec3(ambient)
    self.m_dif = glm.vec3(diffuse)
    self.m_spe = glm.vec3(specular)
    self.shi = shininess

  def direct_lighting(self, scene: 'Scene', hit: Hit, ray: Ray) -> glm.vec3:
    # 5.tracado_de_raios2.pdf - p.27: esta é a parcela local herdada do Slide 4.
    # Os materiais avançados continuam usando esse termo como contribuição não
    # recursiva antes de somar reflexão e/ou refração.
    # c = 0; v̂ = normalize(o − hit.p)
    color = self.m_amb * scene.ambient_light  # componente ambiente
    v = glm.normalize(ray.o - hit.pos)  # p.27: v̂ = normalize(o − p)

    for light in scene.lights:
      # p.27: para cada fonte de luz ls: Li, l̂ = ls.Radiance(scene, hit.p)
      samples = light.sample_radiance(scene, hit)

      for li, l in samples:
        if _is_black(li):
          continue

        # p.27: c += m_dif * Li * n̂ · l̂
        n_dot_l = max(0.0, glm.dot(hit.normal, l))
        color += self.m_dif * li * n_dot_l

        # p.27: r̂ = reflect(−l̂, n̂); c += m_spe * max(0, r̂·v̂)^shi
        r = glm.reflect(-l, hit.normal)
        r_dot_v = max(0.0, glm.dot(r, v))
        color += self.m_spe * li * (r_dot_v ** self.shi)

    return color

  def eval(self,
           scene: 'Scene',
           hit: Hit,
           ray: Ray,
           depth: int = 0,
           max_depth: int | None = None):
    # 5.tracado_de_raios2.pdf - p.27: esta é a avaliação local pura do modelo de
    # Phong. Os materiais recursivos do Slide 5 a reutilizam como termo base
    # não-recursivo antes de acrescentar reflexão e/ou refração.
    return self.direct_lighting(scene, hit, ray)


class ReflectiveMaterial(PhongMaterial):
  # 5.tracado_de_raios2.pdf - p.26-27: PhongMetal.Eval
  # Reflexão com Fresnel-Schlick: R(θ,λ) = R0(λ) + (1 − R0(λ))(1 − cos θ)^5
  # R0(λ): reflectância à incidência normal (p.26). O material não substitui
  # Phong; ele redistribui energia entre a resposta local (1 - R) e o raio
  # refletido recursivo R, preservando a narrativa incremental do Slide 5.
  # Em álgebra vetorial, cos θ = v·n com vetores normalizados.

  def __init__(self,
               ambient: glm.vec3,
               diffuse: glm.vec3,
               specular: glm.vec3,
               shininess: float,
               reflectivity: float | glm.vec3 = 0.5):
    super().__init__(ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess)
    # R0(λ): reflectância à incidência normal — parâmetro do material (5.tracado_de_raios2.pdf - p.26)
    self.reflectivity = _vec3(reflectivity)

  def eval(self,
           scene: 'Scene',
           hit: Hit,
           ray: Ray,
           depth: int = 0,
           max_depth: int | None = None):
    # 5.tracado_de_raios2.pdf - p.27: PhongMetal.Eval
    p = hit.pos
    n = hit.normal
    # p.27: v̂ = normalize(o − p)
    v = glm.normalize(ray.o - p)

    # p.26-27: R = R0 + (1 − R0)(1 − v̂ · n̂)^5  (Schlick com ângulo de visão)
    cos_theta = max(0.0, float(glm.dot(v, n)))
    schlick_factor = (1.0 - cos_theta) ** 5
    # R0 per-channel para metais coloridos (vec3)
    R = self.reflectivity + (glm.vec3(1.0) - self.reflectivity) * schlick_factor

    # p.27: c = (1 − R) PhongMaterial.Eval(scene, hit, o)
    # A iluminação direta continua existindo; apenas passa a ser ponderada pelo
    # complemento da refletância angular calculada por Schlick. Esse rateio é
    # uma aproximação útil para o projeto, mas não equivale a um modelo BRDF
    # energeticamente rigoroso como os discutidos em um renderer fisicamente
    # completo.
    c = (glm.vec3(1.0) - R) * self.direct_lighting(scene, hit, ray)

    if scene.can_spawn_ray(depth, max_depth):
      # p.27: r̂ = normalize(reflect(−v̂, n̂)); ray = Ray(p, r̂); c += R * scene.TraceRay(ray)
      reflected_dir = glm.normalize(glm.vec3(glm.reflect(-v, n)))
      reflected_origin = scene.offset_point(p, hit.geo_normal, reflected_dir)
      reflected_color = scene.trace_ray(Ray(reflected_origin, reflected_dir), depth=depth + 1, max_depth=max_depth)
      c += R * reflected_color

    # TODO(material): investigar compensação energética explícita entre Phong
    # local e reflexão recursiva, ou migrar para um modelo microfacet quando o
    # escopo deixar de ser estritamente didático.

    return c


class TransparentMaterial(PhongMaterial):
  # 5.tracado_de_raios2.pdf - p.29-34: PhongDieletrics.Eval
  # Refração com Lei de Snell (p.31-32) + Fresnel-Schlick (p.26) + Lei de Beer (p.33).
  # Aqui o Slide 5 incrementa o pipeline de Phong com ótica de dielétricos:
  # reflexão angular, mudança de meio, TIR e absorção volumétrica.

  def __init__(self,
               ambient: glm.vec3 = glm.vec3(0.0),
               diffuse: glm.vec3 = glm.vec3(0.0),
               specular: glm.vec3 = glm.vec3(0.0),
               shininess: float = 1.0,
               ior: float = 1.5,
               attenuation: glm.vec3 | None = None,
               # parâmetros legados mantidos para compatibilidade retroativa
               transmission: float | glm.vec3 | None = None,
               reflection_tint: float | glm.vec3 | None = None,
               opacity: float = 0.0):
    super().__init__(ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess)
    # η: índice de refração (5.tracado_de_raios2.pdf - p.30)
    self.ior = max(1.0, float(ior))
    # a(λ): constante de atenuação de Beer — I(s) = I0 * a^s  (p.33)
    # slide p.36: exemplo com a = (0.8, 0.9, 0.8) para vidro corado
    if attenuation is not None:
      self.attenuation = glm.vec3(attenuation)
    elif transmission is not None:
      # compatibilidade retroativa: transmission usado como atenuação
      self.attenuation = _vec3(transmission)
    else:
      self.attenuation = glm.vec3(1.0)  # sem atenuação (vidro incolor)

  def shadow_transmittance(self, scene: 'Scene', hit: Hit, ray: Ray) -> glm.vec3:
    # 5.tracado_de_raios2.pdf - p.35: Light.SampleRadiance
    # while hits.material.IsTransparent() do
    #   if hits.IsBackfacing() then I = I * hits.material.a^||p-hits.p||
    # Só atenua pela Lei de Beer ao SAIR do material (backfacing = face de saída).
    # Isso distingue a absorção volumétrica em raios de sombra do cálculo de
    # refração recursiva feito em eval().
    if hit.backfacing:
      # Lei de Beer: I(s) = I0 * a(λ)^s, s = distância percorrida no material = hit.t
      # (5.tracado_de_raios2.pdf - p.33)
      s = hit.t
      return glm.vec3(
        self.attenuation.x ** s,
        self.attenuation.y ** s,
        self.attenuation.z ** s,
      )
    # Entrando no material (front_face): sem atenuação ainda — será computada na saída
    # TODO(material): se houver meios heterogêneos, trocar este modelo por uma
    # integração explícita de profundidade óptica ao longo do segmento interno.
    return glm.vec3(1.0)

  def eval(self,
           scene: 'Scene',
           hit: Hit,
           ray: Ray,
           depth: int = 0,
           max_depth: int | None = None):
    # 5.tracado_de_raios2.pdf - p.34: PhongDieletrics.Eval
    # A lógica abaixo encadeia três decisões físicas: quanto reflete (Schlick),
    # como refrata ao cruzar a interface (Snell) e quanto absorve ao percorrer
    # o volume (Beer-Lambert), sempre respeitando entrada/saída do meio.
    # p = hit.p; n̂ = hit.n̂; v̂ = normalize(o − p)
    p = hit.pos
    n = hit.normal
    v = glm.normalize(ray.o - p)  # p.34: v̂ = normalize(o − p)

    # p.30: R0(λ) = ((η−1)/(η+1))^2  (para ηi=1 ou ηt=1)
    r0_scalar = ((self.ior - 1.0) / (self.ior + 1.0)) ** 2
    R0 = glm.vec3(r0_scalar)

    # p.26-27: R = R0 + (1 − R0)(1 − v̂ · n̂)^5  (Schlick)
    cos_theta = max(0.0, float(glm.dot(v, n)))
    R = R0 + (glm.vec3(1.0) - R0) * ((1.0 - cos_theta) ** 5)

    # p.34: r̂ = normalize(reflect(−v̂, n̂)); ray = Ray(p, r̂); c = R * scene.TraceRay(ray)
    reflected_dir = glm.normalize(glm.vec3(glm.reflect(-v, n)))
    c = glm.vec3(0.0)
    if scene.can_spawn_ray(depth, max_depth):
      reflected_origin = scene.offset_point(p, hit.geo_normal, reflected_dir)
      c = R * scene.trace_ray(Ray(reflected_origin, reflected_dir), depth=depth + 1, max_depth=max_depth)

    # p.34: if hit.IsBackfacing() then I = a^||o−p||; ratio = η/1
    #        else I = 1; ratio = 1/η
    # front_face/backfacing, calculados em Hit.set_face_normal(), determinam se
    # o raio cruza ar->vidro ou vidro->ar e, portanto, qual razão ηi/ηt usar.
    if hit.backfacing:
      # Lei de Beer (p.33): I = a^s onde s = ||o−p|| = distância percorrida no material
      s = float(glm.length(ray.o - p))
      I = glm.vec3(
        self.attenuation.x ** s,
        self.attenuation.y ** s,
        self.attenuation.z ** s,
      )
      # p.31-32 / p.34: ratio = η/1 (saindo do material: ηi = η, ηt = 1)
      ratio = self.ior / 1.0
    else:
      I = glm.vec3(1.0)  # p.34: I = 1 (entrando no material)
      # p.31-32 / p.34: ratio = 1/η (entrando: ηi = 1, ηt = η)
      ratio = 1.0 / self.ior

    if scene.can_spawn_ray(depth, max_depth):
      # p.32: glm::refract(d̂, n̂, ηi/ηt) — retorna vec3(0) em reflexão interna total
      # p.34: r̂ = normalize(−v̂, n̂, ratio)  →  glm.refract(incident, n̂, ratio)
      incident = glm.normalize(ray.d)  # d̂: direção do raio incidente (de ray.o para hit.pos)
      refracted = glm.vec3(glm.refract(incident, n, float(ratio)))
      if float(glm.dot(refracted, refracted)) > 0.5:  # p.34: if r̂ (não-nulo = sem TIR)
        # p.34: ray = Ray(p, r̂); c += (1 − R) * scene.TraceRay(ray)
        refracted_origin = scene.offset_point(p, hit.geo_normal, glm.vec3(refracted))
        c += (glm.vec3(1.0) - R) * scene.trace_ray(Ray(refracted_origin, glm.vec3(refracted)), depth=depth + 1, max_depth=max_depth)

      # TODO(material): substituir o limiar heurístico `dot(refracted, refracted) > 0.5`
      # por um teste explícito de TIR baseado no radicando da fórmula vetorial de Snell.

    # p.34: return I * c
    return I * c