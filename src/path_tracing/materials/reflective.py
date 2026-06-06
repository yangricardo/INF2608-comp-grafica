"""Material reflexivo com Fresnel-Schlick.

Referências:
- Slide 5, p.26-27: PhongMetal.Eval com reflexão especular recursiva
- PBRT 4e §9.3 "Conductor Materials"
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


class ReflectiveMaterial(PhongMaterial):
  """Material metálico com reflexão especular e Fresnel-Schlick.
  
  Slide 5, p.26-27: Fresnel-Schlick aproxima reflexão angular:
  R(θ,λ) = R0(λ) + (1 - R0(λ))(1 - cos θ)^5
  
  O material redistribui energia entre iluminação local (1-R) e
  raio refletido recursivo (R), preservando narrativa incremental
  do Slide 5.
  """
  
  def __init__(
    self,
    ambient: glm.vec3,
    diffuse: glm.vec3,
    specular: glm.vec3,
    shininess: float,
    reflectivity: float | glm.vec3 = 0.5,
  ):
    """Inicializa material reflexivo.
    
    Args:
      ambient, diffuse, specular, shininess: parâmetros Phong base
      reflectivity: R0 (reflectância à incidência normal) [0-1]
    """
    super().__init__(
      ambient=ambient,
      diffuse=diffuse,
      specular=specular,
      shininess=shininess,
    )
    self.reflectivity = _vec3(reflectivity)
  
  def eval(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
    depth: int = 0,
    max_depth: int | None = None,
  ) -> glm.vec3:
    """Avaliação com Fresnel-Schlick + reflexão recursiva.
    
    Slide 5, p.26-27: PhongMetal.Eval
    c = (1 - R) * PhongMaterial.Eval() + R * TraceRay(raio_refletido)
    
    Onde R = R0 + (1 - R0)(1 - v̂·n̂)^5
    """
    from ..ray import Ray as RayClass
    
    p = hit.pos
    n = hit.normal
    v = glm.normalize(ray.o - p)
    
    # Slide 5, p.26-27: R = R0 + (1 - R0)(1 - v̂·n̂)^5 (Schlick)
    cos_theta = max(0.0, float(glm.dot(v, n)))
    schlick_factor = (1.0 - cos_theta) ** 5
    R = self.reflectivity + (glm.vec3(1.0) - self.reflectivity) * schlick_factor
    
    # Slide 5, p.27: c = (1 - R) * Phong + R * refletido
    c = (glm.vec3(1.0) - R) * self.direct_lighting(scene, hit, ray)
    
    if scene.can_spawn_ray(depth, max_depth):
      reflected_dir = glm.normalize(glm.vec3(glm.reflect(-v, n)))
      reflected_origin = scene.offset_point(p, hit.geo_normal, reflected_dir)
      reflected_color = scene.trace_ray(
        RayClass(reflected_origin, reflected_dir),
        depth=depth + 1,
        max_depth=max_depth,
      )
      c += R * reflected_color
    
    return c
