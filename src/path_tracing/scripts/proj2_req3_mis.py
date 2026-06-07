#!/usr/bin/env python3
"""Etapa 04: Multiple Importance Sampling (MIS) — Cornell Box com pesos MIS.

Combina amostragem direta (NEE) e indireta (BSDF) com pesos power heuristic β=2.
Resultado: convergência ainda mais rápida, fireflies drasticamente reduzidas.

Uso:
  python -m path_tracing.scripts.proj2_req3_mis --spp 32 --depth 6 --out out/proj2/req3
  python -m path_tracing.scripts.proj2_req3_mis --spp 32 --depth 6 --mode nee_only  # comparação
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes import build_proj2_cornell_basic_scene


_ARGV = ' '.join(sys.argv)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Etapa 04: MIS — Cornell Box com pesos power heuristic (β=2)',
  )
  parser.add_argument('--spp', type=int, default=32, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=6, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima (exigência: 4)')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador (mis=Etapa 04; nee_only/bsdf_only=comparação)')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/req3', help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração/estimativa de tempo')

  args = parser.parse_args()

  print('=' * 70)
  print(f'ETAPA 04: MIS (power heuristic β=2) — Cornell Box (modo={args.mode})')
  print('=' * 70)
  print(f'Configuração:')
  print(f'  modo: {args.mode}')
  print(f'  spp: {args.spp}')
  print(f'  depth (máx): {args.depth}')
  print(f'  depth (mín): {args.min_depth}')
  print(f'  seed: {args.seed}')
  print(f'  resolução: {args.width}x{args.height}')
  print(f'  saída: {args.out}')
  print('=' * 70)

  scene, camera = build_proj2_cornell_basic_scene()

  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=args.mode,
    seed=args.seed,
  )

  name = f'proj2_req3_{args.mode}'
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
