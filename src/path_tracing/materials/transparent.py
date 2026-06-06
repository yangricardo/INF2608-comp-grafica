"""Material dielétrico com refração, Fresnel-Schlick e Lei de Beer.

Referências:
- Slide 5, p.29-34: PhongDieletrics.Eval
- Snell (p.31-32), Fresnel (p.26), Beer-Lambert (p.33)
- PBRT 4e §9.4 "Dielectric Materials"
"""

from __future__ import annotations

from pyglm import glm
from typing import TYPE_CHECKING

from .phong import PhongMaterial

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene
  from ..ray import Ray


def _vec3(value: float | glm.vec3) -> glm.vec3:
  return glm.vec3(value)


class TransparentMaterial(PhongMaterial):
  """Material dielétrico com refração, Fresnel e absorção volumétrica.
  
  Slide 5, p.29-34: incrementa Phong com óptica de dielétricos:
  - Reflexão angular (Fresnel-Schlick)
  - Mudança de meio (Lei de Snell)
  - Reflexão interna total (TIR)
  - Absorção volumétrica (Lei de Beer)
  
  Fluxo:
  1. Calcular R (Fresnel-Schlick) em ângulo de visão
  2. Computar direção refratada (Snell ou TIR)
  3. Aplicar Lei de Beer ao sair do material
  """
  
  def __init__(
    self,
    ambient: glm.vec3 = glm.vec3(0.0),
    diffuse: glm.vec3 = glm.vec3(0.0),
    specular: glm.vec3 = glm.vec3(0.0),
    shininess: float = 1.0,
    ior: float = 1.5,
    attenuation: glm.vec3 | None = None,
    transmission: float | glm.vec3 | None = None,
    reflection_tint: float | glm.vec3 | None = None,
    opacity: float = 0.0,
  ):
    """Inicializa material dielétrico.
    
    Args:
      ambient, diffuse, specular, shininess: Phong base
      ior: índice de refração (η), default 1.5 (vidro)
      attenuation: constante Lei de Beer a(λ) [0-1]³, default 1 (incolor)
      transmission: compatibilidade retroativa (usa attenuation)
      reflection_tint, opacity: não usados (compatibilidade)
    """
    super().__init__(
      ambient=ambient,
      diffuse=diffuse,
      specular=specular,
      shininess=shininess,
    )
    
    # Slide 5, p.30: η (índice de refração)
    self.ior = max(1.0, float(ior))
    
    # Slide 5, p.33: Lei de Beer: I(s) = I0 * a^s
    if attenuation is not None:
      self.attenuation = glm.vec3(attenuation)
    elif transmission is not None:
      # Compatibilidade retroativa
      self.attenuation = _vec3(transmission)
    else:
      self.attenuation = glm.vec3(1.0)
  
  def shadow_transmittance(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
  ) -> glm.vec3:
    """Transmitância para shadow rays com Lei de Beer.
    
    Slide 5, p.35: Light.SampleRadiance enquanto IsTransparent():
    if IsBackfacing(): I = I * a^||p - hit.p||
    
    Só atenua ao SAIR do material (backfacing = face de saída).
    """
    if hit.backfacing:
      # Lei de Beer: I(s) = I0 * a^s, s = distância percorrida = hit.t
      s = hit.t
      return glm.vec3(
        self.attenuation.x ** s,
        self.attenuation.y ** s,
        self.attenuation.z ** s,
      )
    # Entrando (front_face): sem atenuação ainda
    return glm.vec3(1.0)
  
  def eval(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
    depth: int = 0,
    max_depth: int | None = None,
  ) -> glm.vec3:
    """Avaliação com refração, Fresnel e Lei de Beer.
    
    Slide 5, p.29-34: encadeia reflexão angular (Schlick) +
    refração (Snell) + absorção (Beer).
    """
    from ..ray import Ray as RayClass
    
    p = hit.pos
    n = hit.normal
    v = glm.normalize(ray.o - p)
    
    # Slide 5, p.30: R0 = ((η-1)/(η+1))^2 para ηi=1 ou ηt=1
    r0_scalar = ((self.ior - 1.0) / (self.ior + 1.0)) ** 2
    R0 = glm.vec3(r0_scalar)
    
    # Slide 5, p.26-27: R = R0 + (1 - R0)(1 - v̂·n̂)^5 (Schlick)
    cos_theta = max(0.0, float(glm.dot(v, n)))
    R = R0 + (glm.vec3(1.0) - R0) * ((1.0 - cos_theta) ** 5)
    
    # Reflexão especular recursiva
    c = glm.vec3(0.0)
    if scene.can_spawn_ray(depth, max_depth):
      reflected_dir = glm.normalize(glm.vec3(glm.reflect(-v, n)))
      reflected_origin = scene.offset_point(p, hit.geo_normal, reflected_dir)
      c = R * scene.trace_ray(
        RayClass(reflected_origin, reflected_dir),
        depth=depth + 1,
        max_depth=max_depth,
      )
    
    # Lei de Beer: atenuação volumétrica
    # Slide 5, p.34: if backfacing, I = a^||o-p||; else I = 1
    if hit.backfacing:
      s = float(glm.length(ray.o - p))
      I = glm.vec3(
        self.attenuation.x ** s,
        self.attenuation.y ** s,
        self.attenuation.z ** s,
      )
      ratio = self.ior / 1.0  # Saindo: η/1
    else:
      I = glm.vec3(1.0)
      ratio = 1.0 / self.ior  # Entrando: 1/η
    
    # Refração (Lei de Snell)
    if scene.can_spawn_ray(depth, max_depth):
      incident = glm.normalize(ray.d)
      refracted = glm.vec3(glm.refract(incident, n, float(ratio)))
      
      # Slide 5, p.34: se refracted não-nulo (sem TIR)
      if float(glm.dot(refracted, refracted)) > 0.5:
        refracted_origin = scene.offset_point(p, hit.geo_normal, glm.vec3(refracted))
        c += (glm.vec3(1.0) - R) * scene.trace_ray(
          RayClass(refracted_origin, glm.vec3(refracted)),
          depth=depth + 1,
          max_depth=max_depth,
        )
    
    # Slide 5, p.34: return I * c
    return I * c
