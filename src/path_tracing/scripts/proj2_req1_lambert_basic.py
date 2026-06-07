#!/usr/bin/env python3
"""Etapa 02: Path Tracer unidirecional — Cornell Box básica.

Uso:
  python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 64 --depth 6 --out out/proj2/req1
"""

import sys
import argparse
from pathlib import Path

# Adiciona src ao path se necessário
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes import build_proj2_cornell_basic_scene


_ARGV = ' '.join(sys.argv)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Etapa 02: Path Tracer unidirecional — Cornell Box básica (7.0 pts)',
  )
  parser.add_argument('--spp', type=int, default=16, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=6, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima (exigência: 4)')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/req1', help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração/estimativa de tempo')

  args = parser.parse_args()

  print('=' * 70)
  print('ETAPA 02: Path Tracer Unidirecional — Cornell Box Básica')
  print('=' * 70)
  print(f'Configuração:')
  print(f'  spp: {args.spp}')
  print(f'  depth (máx): {args.depth}')
  print(f'  depth (mín): {args.min_depth}')
  print(f'  seed: {args.seed}')
  print(f'  gamma: {args.gamma}')
  print(f'  resolução: {args.width}x{args.height}')
  print(f'  saída: {args.out}')
  print('=' * 70)

  print('Construindo cena Cornell Box...')
  scene, camera = build_proj2_cornell_basic_scene()

  print('Inicializando integrador (BSDF-only, sem NEE)...')
  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode='bsdf_only',
    seed=args.seed,
  )

  print('Renderizando...')
  out_path = run_render_with_estimation(
    render=Render(out_root=args.out),
    scene=scene,
    cam=camera,
    width=args.width,
    height=args.height,
    name='proj2_req1_lambert_basic',
    samples_per_pixel=args.spp,
    sampling_mode='jittered',
    seed=args.seed,
    gamma_fix=args.gamma,
    estimator_options=EstimatorOptions(calibrate=not args.no_calibrate, calibrate_only=False),
    integrator=integrator,
    command_line=_ARGV,
  )

  print(f'Renderização concluída: {out_path}')
