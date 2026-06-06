"""BSDF Lambertiana (difusa perfeita).

Referências:
- Slide 7 "Integração de Monte Carlo" — Método de Malley (hemisfério cosseno)
- Slide 8 "Traçado de Caminhos" — BRDF Lambertiana ρ/π
- PBRT 4e §9.2 "Diffuse Reflection"
- PBRT 4e §A.5 "Sampling Multidimensional Functions"
"""

from __future__ import annotations
import math
from pyglm import glm

from .base import BSDF


class LambertianBSDF(BSDF):
  """BSDF Lambertiana: f_r = ρ/π (constante por direção).
  
  Amostragem via Método de Malley com hemisfério cosseno-ponderado.
  Reduz variância vs. amostragem uniforme sem custo computacional.
  
  Ref: PBRT 4e §A.5 "Sampling a Sphere"; §9.2 "Diffuse Reflection":
    "By incorporating the cosine factor in the light transport equation's
     integrand, cosine-weighted hemisphere sampling improves MSE by a factor
     of 2.34 for this test scene, without additional computational cost."
  """
  
  def __init__(self, rho: glm.vec3):
    """Inicializa BSDF Lambertiana.
    
    Args:
      rho: albedo (reflectância difusa) em [0,1]³ (típ. cor)
    """
    self.rho = glm.clamp(glm.vec3(rho), glm.vec3(0.0), glm.vec3(1.0))
  
  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Retorna ρ/π (constante, frame local).
    
    Ref: PBRT 4e §9.2, Eq. 9.1
    """
    # Ref: PBRT 4e §9.2 Diffuse Reflection
    return self.rho / glm.pi
  
  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict:
    """Amostra hemisfério cosseno-ponderado via Malley.
    
    Método de Malley:
      φ = 2π u.x
      r = sqrt(u.y)
      wi = (r cos φ, r sin φ, sqrt(1 - r²))
    
    Ref: PBRT 4e §A.5 "Malley Method"; Slide 7
    """
    # Ref: PBRT 4e §A.5 Malley Method; Slide 7 "Método de Malley"
    phi = 2.0 * glm.pi * u.x
    r = glm.sqrt(u.y)
    
    x = r * glm.cos(phi)
    y = r * glm.sin(phi)
    z = glm.sqrt(glm.max(0.0, 1.0 - r * r))
    
    wi = glm.normalize(glm.vec3(x, y, z))
    pdf_val = self.pdf(wo, wi)
    f_val = self.eval(wo, wi)
    
    return {
      'wi': wi,
      'pdf': pdf_val,
      'f': f_val,
    }
  
  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """PDF cosseno-ponderado: max(0, wi.z) / π.
    
    Ref: PBRT 4e §9.2 "Diffuse Reflection"
    """
    # Ref: PBRT 4e §9.2 Diffuse Reflection, Eq. 9.2
    # Frame local: normal = z, portanto cosθ_i = wi.z
    cos_theta = glm.max(0.0, wi.z)
    return cos_theta / glm.pi
