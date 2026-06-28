#!/usr/bin/env python3
"""Showcase combinada: Wall Lights + Dielétrico Multi-Material.

Renderiza a cena cornell_combined_showcase, que reúne:
  - 3 fontes de luz (RectAreaLight teto + 2 TriangleMeshLight hexagonais nas paredes)
  - 4 DielectricBSDF: 2 esferas no piso (IOR=1.5, incolor e âmbar) e 2 suspensas
    (IOR=1.33, água incolor e azul-esverdeada)
  - 2 caixas Lambertianas rotacionadas + esfera difusa azul

Uso:
  python -m path_tracing.scripts.proj2_showcase_combined --spp 32 --depth 12 --mode mis
  python -m path_tracing.scripts.proj2_showcase_combined --spp 64 --depth 12 --mode mis --use-rr true
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes import build_proj2_cornell_combined_showcase_scene

_ARGV = ' '.join(sys.argv)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Showcase combinada: Wall Lights + Dielétrico Multi-Material',
  )
  parser.add_argument('--spp', type=int, default=64, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=12, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador')
  parser.add_argument('--use-rr', type=lambda x: x.lower() in ('true', '1', 'yes'), default=False,
                      help='Usar Russian Roulette (true|false, default: false)')
  parser.add_argument('--rr-min-depth', type=int, default=None)
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/showcase_combined',
                      help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração')

  args = parser.parse_args()

  print('=' * 70)
  print(f'SHOWCASE COMBINADA — Wall Lights + Dielétrico Multi (modo={args.mode})')
  print('=' * 70)
  print(f'  modo: {args.mode}  use_rr: {args.use_rr}')
  print(f'  spp: {args.spp}  depth: {args.depth}  seed: {args.seed}')
  print(f'  resolução: {args.width}x{args.height}  saída: {args.out}')
  print('=' * 70)

  scene, camera = build_proj2_cornell_combined_showcase_scene()

  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=args.mode,
    seed=args.seed,
    use_rr=args.use_rr,
    rr_min_depth=args.rr_min_depth,
  )

  rr_suffix = '_rr' if args.use_rr else '_no_rr'
  name = f'proj2_showcase_combined_{args.mode}{rr_suffix}'
  out_path = run_render_with_estimation(
    render=Render(out_root=args.out),
    scene=scene,
    cam=camera,
    width=args.width,
    height=args.height,
    name=name,
    samples_per_pixel=args.spp,
    sampling_mode='stratified',
    seed=args.seed,
    gamma_fix=args.gamma,
    estimator_options=EstimatorOptions(calibrate=not args.no_calibrate, calibrate_only=False),
    integrator=integrator,
    command_line=_ARGV,
  )

  print(f'Renderização concluída: {out_path}')
