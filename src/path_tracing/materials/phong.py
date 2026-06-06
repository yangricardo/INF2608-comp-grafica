"""Material Phong com iluminação direta (não-recursivo).

Referências:
- Slide 4-5, p.27: PhongMaterial.Eval
- PBRT 4e §5.6.1 "The Phong Model"
"""

from __future__ import annotations

from pyglm import glm
from typing import TYPE_CHECKING

from .base import Material

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene
  from ..ray import Ray


def _is_black(color: glm.vec3) -> bool:
  return color.x <= 0.0 and color.y <= 0.0 and color.z <= 0.0


class PhongMaterial(Material):
  """Material Phong com componentes ambiente, difusa e especular.
  
  Slide 4-5, p.27: síntese física:
  c = c_amb + Σ(k_d L_i max(0, n·l) + k_s L_i max(0, r·v)^s)
  
  Componentes não-recursivas: apenas iluminação direta sem reflexão
  especular nem refração. Materiais avançados (Reflective, Transparent)
  herdam e adicionam recursão.
  """
  
  def __init__(
    self,
    ambient: glm.vec3,
    diffuse: glm.vec3,
    specular: glm.vec3,
    shininess: float,
  ):
    """Inicializa material Phong.
    
    Args:
      ambient: coeficiente de luz ambiente (RGB)
      diffuse: coeficiente difuso (RGB)
      specular: coeficiente especular (RGB)
      shininess: expoente de brilho (maior = mais especular)
    """
    self.m_amb = glm.vec3(ambient)
    self.m_dif = glm.vec3(diffuse)
    self.m_spe = glm.vec3(specular)
    self.shi = float(shininess)
  
  def direct_lighting(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
  ) -> glm.vec3:
    """Calcula iluminação direta (ambiente + pontos de luz).
    
    Slide 4-5, p.27: esta é a parcela local herdada. Materiais
    recursivos (Reflective, Transparent) a reutilizam como termo base
    antes de somar reflexão/refração.
    
    Returns:
      Cor RGB da iluminação direta
    """
    color = self.m_amb * scene.ambient_light
    v = glm.normalize(ray.o - hit.pos)
    
    for light in scene.lights:
      samples = light.sample_radiance(scene, hit)
      
      for li, l in samples:
        if _is_black(li):
          continue
        
        # Slide 4-5, p.27: c += m_dif * Li * (n̂ · l̂)
        n_dot_l = max(0.0, glm.dot(hit.normal, l))
        color += self.m_dif * li * n_dot_l
        
        # Slide 4-5, p.27: r̂ = reflect(-l̂, n̂); c += m_spe * max(0, r̂·v̂)^shi
        r = glm.reflect(-l, hit.normal)
        r_dot_v = max(0.0, glm.dot(r, v))
        color += self.m_spe * li * (r_dot_v ** self.shi)
    
    return color
  
  def eval(
    self,
    scene: "Scene",
    hit: "Hit",
    ray: "Ray",
    depth: int = 0,
    max_depth: int | None = None,
  ) -> glm.vec3:
    """Avaliação pura Phong (sem recursão).
    
    Slide 4-5, p.27: avaliação local do modelo Phong. Materiais
    recursivos herdam e adicionam reflexão/refração antes de retornar.
    """
    return self.direct_lighting(scene, hit, ray)
