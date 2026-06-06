"""Path Tracer unidirecional com amostragem de BSDF (Etapa 02).

Referências:
- Slide 7 "Integração de Monte Carlo" (MC basics, importance sampling)
- Slide 8 "Traçado de Caminhos" (LTE, path integral, throughput)
- Slide 9 "Traçado de Caminhos II" (extensões: NEE, MIS, RR)
- PBRT 4e §13.1–13.4 "Light Transport I"
- Kajiya, "The Rendering Equation", SIGGRAPH 1986
"""

from __future__ import annotations
from path_tracing.ray import Ray
from path_tracing.scene import Scene
from pyglm import glm
import random

from .base import Integrator, Sampler
from ..onb import ONB
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF


class PathIntegrator(Integrator):
  """Path Tracer unidirecional com amostragem de BSDF.
  
  Estimador básico: apenas amostragem BSDF, sem NEE (next event estimation).
  Respeitando min_depth obrigatório = 4.
  
  Referência: PBRT 4e §13.3 "A Simple Path Tracer"
  """
  
  def __init__(
    self,
    min_depth: int = 4,
    max_depth: int = 8,
    mode: str = "bsdf_only",
    seed: int | None = None,
  ):
    """Inicializa path tracer.
    
    Args:
      min_depth: profundidade mínima antes de qualquer terminação (exigência: 4)
      max_depth: profundidade máxima do caminho
      mode: "bsdf_only" (Etapa 02) ou estendido em etapas posteriores
      seed: seed do RNG
    """
    self.min_depth = max(1, int(min_depth))
    self.max_depth = max(self.min_depth, int(max_depth))
    self.mode = mode
    self.seed = seed
    
    # RNG global (por amostra)
    self.rng = random.Random(seed)
  
  def Li(
    self,
    ray: Ray,  # Ray
    scene: Scene,  # Scene
    sampler: Sampler | None = None,  # Sampler | None
    depth: int = 1,
  ) -> glm.vec3:
    """Estima radiância ao longo do raio via path tracing.
    
    Pseudocódigo (PBRT 4e §13.3):
      β ← (1,1,1),  L ← (0,0,0)
      para profundidade = 1, 2, ..., max_depth:
        hit ← scene.intersect(ray)
        se !hit: L += β * background; terminar
        se hit.emissivo E (profundidade ≥ min_depth OU profundidade == 1):
          L += β * Le; terminar
        wo = -ray.d (frame local)
        (wi, pdf, f) ← bsdf.sample(wo, u)
        se pdf == 0 ou f == 0: terminar
        β *= f * |cos θ_i| / pdf
        ray ← Ray(offset_point(...), wi_global)
    
    Ref: PBRT 4e §13.3; Slide 8 "Traçado de Caminhos"
    """
    # Ref: PBRT 4e §13.3 A Simple Path Tracer; Slide 8 Traçado de Caminhos
    
    L = glm.vec3(0.0)
    beta = glm.vec3(1.0)
    current_ray = ray
    current_depth = depth
    
    # Loop iterativo de path tracing
    for iter_depth in range(1, self.max_depth + 1):
      # Interseção
      hit = scene.compute_intersection(current_ray)
      
      if hit is None:
        # Nenhuma interseção: fundo
        L += beta * scene.background_color
        break
      
      # Checar se superfície é emissiva
      # Assumindo hit.material possui is_emissive ou Le
      hit_material = hit.material
      is_emissive = (
        hit_material is not None
        and isinstance(hit_material, EmissiveBSDF)
      )
      
      if is_emissive:
        # Terminar em emissivo (apenas em primário ou se ≥ min_depth)
        if iter_depth == 1 or iter_depth >= self.min_depth:
          le_val = getattr(hit_material, 'Le', glm.vec3(0.0))
          L += beta * le_val
        break
      
      # Se profundidade < min_depth obrigatória, não termina aqui
      if iter_depth >= self.max_depth:
        break
      
      # Amostragem BSDF
      if hit_material is None:
        # Default: Lambertiana branca
        bsdf = LambertianBSDF(glm.vec3(0.5))
      elif hasattr(hit_material, 'sample'):
        # É um BSDF com sample()
        bsdf = hit_material
      else:
        # Material antigo sem sample() — usar Lambertiana
        bsdf = LambertianBSDF(glm.vec3(0.5))
      
      # Construir ONB local (normal como z)
      onb = ONB(hit.normal)
      wo_global = -current_ray.d
      wo_local = onb.global_to_local(wo_global)
      
      # Amostra BSDF
      u_sample = (self.rng.random(), self.rng.random())
      sample_result = bsdf.sample(wo_local, glm.vec2(u_sample[0], u_sample[1]))  # type: ignore[union-attr]
      
      if sample_result is None or sample_result['pdf'] == 0.0:
        break
      
      wi_local = sample_result['wi']
      pdf = sample_result['pdf']
      f = sample_result['f']
      
      # Verificar cosseno em frame local (normal = z)
      cos_theta = wi_local.z
      if cos_theta <= 0.0:
        # Wi aponta para baixo; inválido
        break
      
      # Acumular throughput
      # β *= f * |cos θ_i| / pdf
      beta *= f * cos_theta / pdf
      
      # Verificar se beta ficou muito pequeno (evita infinitos)
      if glm.length(beta) < 1e-6:
        break
      
      # Novo raio em frame global
      wi_global = onb.local_to_global(wi_local)
      wi_global = glm.normalize(wi_global)
      
      # Offset point para evitar shadow acne
      offset_origin = scene.offset_point(hit.pos, hit.normal, wi_global)
      current_ray = type(current_ray)(offset_origin, wi_global)
      current_depth = iter_depth + 1
    
    return L
