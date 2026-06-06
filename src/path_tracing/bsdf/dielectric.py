"""BSDF Dielétrico (Refratário): vidro, água, ar, diamante, etc.

Implementa reflexão especular com Fresnel e refração (transmissão) com Snell's law.
Suporta absorção via Beer-Lambert para materiais coloridos.

Referências:
- PBRT 4e §9.5 "Dielectric BRDF and BTDF"
- PBRT 4e §5.3.2 "The Fresnel Equations"
- Slide Prof. Celes "Traçado de Caminhos II" — refração

Física:
1. Fresnel: cálculo da refletância R em função do ângulo de incidência
2. Snell's Law: n1*sin(θ1) = n2*sin(θ2)
3. Beer-Lambert: transmitância = exp(-σ * d) onde d é a distância percorrida
"""

from __future__ import annotations
from pyglm import glm
import math
import random
from typing import TYPE_CHECKING

from .base import BSDF

if TYPE_CHECKING:
  pass


class DielectricBSDF(BSDF):
  """BSDF para materiais dielétricos (sem condução).
  
  Combina reflexão (Fresnel) com refração (Snell's law + Beer-Lambert).
  Em cada vértice, escolhe refletir OU refractar (delta distribution).
  
  Ref: PBRT 4e §9.5; Walter et al. 2007 para aproximações Fresnel.
  """
  
  def __init__(
    self,
    ior: float = 1.5,
    absorption: glm.vec3 | None = None,
    seed: int | None = None,
  ):
    """Inicializa BSDF dielétrico.
    
    Args:
      ior: Índice de refração (1.5 = vidro, 1.33 = água, 1.0 = ar)
      absorption: Coeficiente de absorção σ em RGB (default: sem absorção)
      seed: Seed do RNG
    """
    self.ior = float(ior)
    self.absorption = glm.vec3(absorption) if absorption is not None else glm.vec3(0.0)
    self.rng = random.Random(seed)
  
  def eval(self, wo: glm.vec3, wi: glm.vec3) -> glm.vec3:
    """Retorna glm.vec3(0) — BSDF dielétrico é uma delta distribution.
    
    Não há reflexão/refração difusa para avaliar fora de direcções específicas.
    """
    return glm.vec3(0.0)
  
  def pdf(self, wo: glm.vec3, wi: glm.vec3) -> float:
    """Retorna 0.0 — delta distribution não tem densidade amostrável.

    A probabilidade de uma direção arbitrária coincidir com a reflexão/refração
    especular é zero, então o integrador trata bounces especulares por
    `is_specular()` (sem NEE, peso MIS = 1.0).
    """
    return 0.0

  def is_specular(self) -> bool:
    """True — dielétrico é uma delta distribution (reflexão/refração especular)."""
    return True

  def sample(self, wo: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra reflexão OU refração segundo Fresnel.

    Convenção de frame (importante): este BSDF é avaliado no frame da **normal
    geométrica** (z = normal outward, NÃO a normal virada para o raio). Assim o
    sinal de `wo.z` codifica o lado do raio:
      - `wo.z > 0`: raio incide do meio externo → ENTRANDO (n_i=1, n_t=ior)
      - `wo.z < 0`: raio vem de dentro do volume → SAINDO  (n_i=ior, n_t=1)

    Etapas:
      1. cos_i = |wo.z|
      2. eta = n_i / n_t (corrige a inversão: entrada usa 1/ior, não ior)
      3. Snell: sin_t² = eta²·(1 - cos_i²); se ≥ 1 → reflexão interna total
      4. Fresnel exato não polarizado: F = ½(r_∥² + r_⊥²)
      5. Decisão estocástica: u.x < F → reflexão; senão refração (PDF=1, delta)

    O integrador, por ser especular, atualiza o throughput por `β *= f / pdf`
    (sem cosseno geométrico); por isso `f` carrega refletância/transmitância pura.

    Ref: PBRT 4e §9.5.2 "Specular Reflection and Transmission";
         §5.3.2 "The Fresnel Equations".
    """
    # Frame da normal geométrica: sinal de wo.z indica entrada/saída.
    cos_i = abs(wo.z)
    if cos_i < 1e-6:
      return None  # Raio quase paralelo à superfície

    entering = wo.z > 0.0
    # eta = n_incidente / n_transmitido
    n_i = 1.0 if entering else self.ior
    n_t = self.ior if entering else 1.0
    eta = n_i / n_t

    # Snell: sin_t² em função de cos_i
    sin_t_sq = eta * eta * (1.0 - cos_i * cos_i)

    # Reflexão interna total: refração impossível, reflete tudo.
    if sin_t_sq >= 1.0:
      wi = glm.vec3(-wo.x, -wo.y, wo.z)  # reflete no plano z (mesmo lado de wo)
      return {
        'wi': glm.normalize(wi),
        'pdf': 1.0,
        'f': glm.vec3(1.0),  # refletância total
      }

    cos_t = glm.sqrt(1.0 - sin_t_sq)

    # Fresnel exato (não polarizado) = média das componentes paralela e perpendicular.
    r_par = (n_t * cos_i - n_i * cos_t) / (n_t * cos_i + n_i * cos_t)
    r_perp = (n_i * cos_i - n_t * cos_t) / (n_i * cos_i + n_t * cos_t)
    fresnel = 0.5 * (r_par * r_par + r_perp * r_perp)

    if u.x < fresnel:
      # Reflexão especular (mesmo lado de wo).
      wi = glm.vec3(-wo.x, -wo.y, wo.z)
      return {
        'wi': glm.normalize(wi),
        'pdf': 1.0,
        'f': glm.vec3(fresnel),
      }

    # Refração especular (Snell, forma vetorial geral válida para entrada e saída):
    #   componente tangencial escala por eta; z vai para o lado OPOSTO a wo.
    # Nota: o fator de radiância 1/eta² da transmissão é omitido porque cancela
    # em objeto fechado (entra+sai); ver docs/proj2/ETAPA_07_DIELECTRIC.md.
    sign_z = 1.0 if wo.z > 0.0 else -1.0
    wi = glm.vec3(-eta * wo.x, -eta * wo.y, -cos_t * sign_z)
    transmittance = 1.0 - fresnel
    return {
      'wi': glm.normalize(wi),
      'pdf': 1.0,
      'f': glm.vec3(transmittance),
    }
