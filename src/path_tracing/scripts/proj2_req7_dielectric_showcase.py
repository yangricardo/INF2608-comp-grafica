#!/usr/bin/env python3
"""Showcase multi-material dielétrico: quatro esferas com variações de IOR e absorção.

Renderiza a cena cornell_dielectric_multi, que instancia quatro DielectricBSDF distintos
numa mesma Cornell Box, comparando visualmente:
  - Vidro incolor (IOR=1.5): alta reflectância Fresnel em ângulos rasantes
  - Vidro âmbar (IOR=1.5, σ=(0.2,0.6,1.2)): coloração por Beer-Lambert
  - Água incolor (IOR=1.33): refração suave, menos Fresnel
  - Água azul-esverdeada (IOR=1.33, σ=(0.30,0.05,0.10)): coloração por Beer-Lambert

Uso:
  python -m path_tracing.scripts.proj2_req7_dielectric_showcase --spp 32 --depth 8 --mode mis
  python -m path_tracing.scripts.proj2_req7_dielectric_showcase --spp 64 --depth 8 --mode mis --seed 42
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes import build_proj2_cornell_dielectric_multi_scene

_ARGV = ' '.join(sys.argv)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Showcase multi-material dielétrico: 4 esferas com variações de IOR e absorção',
  )
  parser.add_argument('--spp', type=int, default=32, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=8, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador')
  parser.add_argument('--use-rr', type=lambda x: x.lower() in ('true', '1', 'yes'), default=False,
                      help='Usar Russian Roulette (true|false, default: false)')
  parser.add_argument('--rr-min-depth', type=int, default=None,
                      help='Profundidade mínima para RR (default: min_depth)')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/req7_dielectric_showcase',
                      help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração')

  args = parser.parse_args()

  print('=' * 70)
  print(f'SHOWCASE DIELÉTRICO — 4 esferas multi-material (modo={args.mode})')
  print('=' * 70)
  print(f'  modo: {args.mode}')
  print(f'  use_rr: {args.use_rr}')
  print(f'  spp: {args.spp}')
  print(f'  depth (máx): {args.depth}')
  print(f'  seed: {args.seed}')
  print(f'  resolução: {args.width}x{args.height}')
  print(f'  saída: {args.out}')
  print('=' * 70)

  scene, camera = build_proj2_cornell_dielectric_multi_scene()

  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=args.mode,
    seed=args.seed,
    use_rr=args.use_rr,
    rr_min_depth=args.rr_min_depth,
  )

  rr_suffix = '_rr' if args.use_rr else '_no_rr'
  name = f'proj2_req7_dielectric_showcase_{args.mode}{rr_suffix}'
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
