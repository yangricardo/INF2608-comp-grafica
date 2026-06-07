#!/usr/bin/env python3
"""Etapa 07: Dielectric — Refração com Snell's law e reflexão com Fresnel.

Implementa DielectricBSDF: BSDF que simula transparência com refração (vidro, água).
Suporta dois materiais:
  - glass (IOR=1.5): vidro óptico padrão
  - water (IOR=1.33): água com refração mais suave

Características:
  - Fresnel: reflexão especular dependente do ângulo
  - Snell's law: refração com mudança de direção
  - Reflexão interna total: passa direto sem refração em ângulos críticos

Uso:
  python -m path_tracing.scripts.proj2_req7_dielectric --material glass --spp 32 --depth 8
  python -m path_tracing.scripts.proj2_req7_dielectric --material water --spp 32 --depth 8 --use-rr true

Ref: PBRT 4e §9.5 "Dielectric BRDF and BTDF"; §5.3.2 "The Fresnel Equations".
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyglm import glm
from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes import (

_ARGV = ' '.join(sys.argv)
  build_proj2_cornell_glass_scene,
  build_proj2_cornell_water_scene,
)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Etapa 07: Dielectric — Refração e reflexão com Snell e Fresnel',
  )
  parser.add_argument('--material', choices=['glass', 'water'], default='glass',
                      help='Material dielétrico: glass (IOR=1.5) ou water (IOR=1.33)')
  parser.add_argument('--spp', type=int, default=32, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=8, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima (exigência: 4)')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador')
  parser.add_argument('--use-rr', type=lambda x: x.lower() in ('true', '1', 'yes'), default=False,
                      help='Usar Russian Roulette (true|false, default: false)')
  parser.add_argument('--rr-min-depth', type=int, default=None,
                      help='Profundidade mínima para RR (default: min_depth)')
  parser.add_argument('--absorption', type=float, nargs=3, default=[0.0, 0.0, 0.0],
                      metavar=('R', 'G', 'B'),
                      help='Coef. de absorção Beer-Lambert σ (RGB). 0 0 0 = incolor. '
                           'Ex.: 0.2 0.6 1.2 (vidro âmbar); água: 0.30 0.05 0.10 (azul-esverdeado).')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/req7', help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração/estimativa de tempo')

  args = parser.parse_args()

  print('=' * 70)
  print(f'ETAPA 07: Dielectric ({args.material}) — Cornell Box (modo={args.mode})')
  print('=' * 70)
  print(f'Configuração:')
  print(f'  material: {args.material} (IOR={1.5 if args.material == "glass" else 1.33})')
  print(f'  modo: {args.mode}')
  print(f'  use_rr: {args.use_rr}')
  if args.use_rr:
    print(f'  rr_min_depth: {args.rr_min_depth if args.rr_min_depth else args.min_depth}')
  print(f'  spp: {args.spp}')
  print(f'  depth (máx): {args.depth}')
  print(f'  depth (mín): {args.min_depth}')
  print(f'  seed: {args.seed}')
  print(f'  absorção (Beer-Lambert σ): {tuple(args.absorption)}')
  print(f'  resolução: {args.width}x{args.height}')
  print(f'  saída: {args.out}')
  print('=' * 70)

  # Absorção Beer-Lambert (Etapa 07): None se incolor (0,0,0).
  absorption = glm.vec3(*args.absorption)
  has_absorption = any(c > 0.0 for c in args.absorption)
  absorption_arg = absorption if has_absorption else None

  # Selecionar cena
  if args.material == 'glass':
    scene, camera = build_proj2_cornell_glass_scene(absorption=absorption_arg)
  else:  # water
    scene, camera = build_proj2_cornell_water_scene(absorption=absorption_arg)

  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=args.mode,
    seed=args.seed,
    use_rr=args.use_rr,
    rr_min_depth=args.rr_min_depth,
  )

  rr_suffix = '_rr' if args.use_rr else '_no_rr'
  abs_suffix = ''
  if has_absorption:
    r, g, b = args.absorption
    abs_suffix = f'_abs{r:g}-{g:g}-{b:g}'
  name = f'proj2_req7_{args.material}_{args.mode}{rr_suffix}{abs_suffix}'
  out_path = run_render_with_estimation(
    render=Render(out_root=args.out),
    scene=scene,
    cam=camera,
    width=args.width,
    height=args.height,
    name=name,
    samples_per_pixel=args.spp,
    sampling_mode='jittered',
    seed=args.seed,
    gamma_fix=args.gamma,
    estimator_options=EstimatorOptions(calibrate=not args.no_calibrate, calibrate_only=False),
    integrator=integrator,
    command_line=_ARGV,
  )

  print(f'Renderização concluída: {out_path}')
