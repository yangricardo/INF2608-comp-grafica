"""Path Tracer unidirecional com amostragem de BSDF (Etapa 02) e NEE (Etapa 03).

Modos suportados:
  "bsdf_only" — Etapa 02: apenas amostragem BSDF, sem NEE
  "nee_only"  — Etapa 03: NEE em todas as luzes, suprime Le em hits não-primários
  "mis"       — Etapa 04: MIS combinando BSDF + NEE (power heuristic β=2)

Referências:
- Slide 7 "Integração de Monte Carlo" (MC basics, importance sampling)
- Slide 8 "Traçado de Caminhos" (LTE, path integral, throughput)
- Slide 9 "Traçado de Caminhos II" (NEE, MIS, RR)
- PBRT 4e §13.1–13.4 "Light Transport I"
- Kajiya, "The Rendering Equation", SIGGRAPH 1986, DOI 10.1145/15922.15902
- Veach & Guibas, SIGGRAPH 1995, DOI 10.1145/218380.218498 (MIS)
"""

from __future__ import annotations
from path_tracing.ray import Ray
from path_tracing.scene import Scene
from pyglm import glm
import math
import random

from .base import Integrator, Sampler
from ..onb import ONB
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..mis import power_heuristic


class PathIntegrator(Integrator):
  """Path Tracer unidirecional: BSDF-only, NEE, ou MIS.

  Ref: PBRT 4e §13.3 "A Simple Path Tracer"; §13.4 "A Better Path Tracer".
  """

  VALID_MODES = ('bsdf_only', 'nee_only', 'mis')

  def __init__(
    self,
    min_depth: int = 4,
    max_depth: int = 8,
    mode: str = 'bsdf_only',
    seed: int | None = None,
  ):
    """Inicializa path tracer.

    Args:
      min_depth: profundidade mínima antes de qualquer terminação antecipada (exigência: 4)
      max_depth: profundidade máxima do caminho
      mode: "bsdf_only" | "nee_only" | "mis"
      seed: seed do RNG
    """
    if mode not in self.VALID_MODES:
      raise ValueError(f'mode deve ser um de {self.VALID_MODES}, recebeu {mode!r}')
    self.min_depth = max(1, int(min_depth))
    self.max_depth = max(self.min_depth, int(max_depth))
    self.mode = mode
    self.seed = seed
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
        # PBRT 4e §13.3: sempre acumula Le ao atingir emissivo em qualquer depth.
        # min_depth é restrição de Russian Roulette (Etapa 05), não de coleta de Le.
        # NEE suprime Le em hits não-primários para evitar dupla contagem.
        if self.mode == 'nee_only' and iter_depth > 1:
          break  # Le já foi contado via NEE no vértice anterior
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
      
      # NEE: amostragem direta das luzes em scene.lights (Etapa 03)
      # Ref: PBRT 4e §13.4 "A Better Path Tracer"; Slide 9 (NEE).
      if self.mode in ('nee_only', 'mis'):
        lights = getattr(scene, 'lights', [])
        for light in lights:
          if not hasattr(light, 'sample_Li'):
            continue
          u_light = glm.vec2(self.rng.random(), self.rng.random())
          sample = light.sample_Li(hit.pos, u_light)
          if sample is None:
            continue
          wi_nee = sample['wi']
          Li_nee = sample['Li']
          pdf_nee = sample['pdf_solid_angle']
          if pdf_nee <= 0.0:
            continue
          # Verificar visibilidade (shadow ray)
          shadow_orig = scene.offset_point(hit.pos, hit.normal, wi_nee)
          shadow_ray = type(current_ray)(shadow_orig, wi_nee)
          shadow_hit = scene.compute_intersection(shadow_ray)
          dist_nee = sample['distance']
          # Se existe hit e é mais perto que a luz, é ocluído
          # EXCETO se o hit é EmissiveBSDF (o painel de luz, não um oclusor)
          if shadow_hit is not None and shadow_hit.t < dist_nee - 1e-3:
            # Verificar se hit é emissivo (luz panel é transparente para NEE)
            is_light_panel = (
              shadow_hit.material is not None
              and isinstance(shadow_hit.material, EmissiveBSDF)
            )
            if not is_light_panel:
              continue  # Ocluído por objeto não-emissivo
          # Avaliar BSDF em direção da luz (frame local)
          wi_nee_local = onb.global_to_local(wi_nee)
          cos_nee = max(0.0, wi_nee_local.z)
          if cos_nee <= 0.0:
            continue
          f_nee: glm.vec3 = bsdf.eval(wo_local, wi_nee_local)  # type: ignore[call-arg]
          
          # MIS weight (Etapa 04)
          w_nee = 1.0
          if self.mode == 'mis':
            # Calcular PDF dessa direção via BSDF para MIS
            pdf_bsdf_for_nee = bsdf.pdf(wo_local, wi_nee_local)  # type: ignore[call-arg]
            w_nee = power_heuristic(1, pdf_nee, 1, pdf_bsdf_for_nee, beta=2.0)
          
          L += beta * f_nee * Li_nee * cos_nee / pdf_nee * w_nee

      # Amostra BSDF
      u_sample = (self.rng.random(), self.rng.random())
      sample_result = bsdf.sample(wo_local, glm.vec2(u_sample[0], u_sample[1]))  # type: ignore[union-attr]
      
      if sample_result is None or sample_result['pdf'] == 0.0:
        break
      
      wi_local = sample_result['wi']
      pdf_bsdf = sample_result['pdf']
      f = sample_result['f']
      
      # Verificar cosseno em frame local (normal = z)
      cos_theta = wi_local.z
      if cos_theta <= 0.0:
        # Wi aponta para baixo; inválido
        break
      
      # MIS weight (Etapa 04)
      w_bsdf = 1.0
      if self.mode == 'mis':
        # Calcular PDF dessa direção via luz(es) para MIS
        wi_bsdf_global = onb.local_to_global(wi_local)
        pdf_light_for_bsdf = 0.0
        lights = getattr(scene, 'lights', [])
        for light in lights:
          if not hasattr(light, 'pdf_Li'):
            continue
          pdf_light_for_bsdf += light.pdf_Li(hit.pos, wi_bsdf_global)
        w_bsdf = power_heuristic(1, pdf_bsdf, 1, pdf_light_for_bsdf, beta=2.0)
      
      # Acumular throughput com weight MIS
      # β *= f * |cos θ_i| / pdf * w_bsdf
      beta *= f * cos_theta / pdf_bsdf * w_bsdf
      
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
