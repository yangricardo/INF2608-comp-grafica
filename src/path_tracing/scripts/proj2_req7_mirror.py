#!/usr/bin/env python3
"""Etapa Extra: Espelho Perfeito (MirrorBSDF).

Renderiza esfera com reflexão especular pura (100%, sem refração).
Contrasta com DielectricBSDF (vidro) para demonstrar delta distributions.

Uso:
  python -m path_tracing.scripts.proj2_req7_mirror --spp 20 --depth 8 --mode mis
  python -m path_tracing.scripts.proj2_req7_mirror --all --spp 20 --depth 8
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyglm import glm
from path_tracing.render import Render
from path_tracing.render_estimator import run_render_with_estimation, EstimatorOptions
from path_tracing.integrators.path_tracer import PathIntegrator
from path_tracing.scenes.cornell_mirror import build_proj2_cornell_mirror_scene

_ARGV = ' '.join(sys.argv)


def render_one(args, mode: str, use_rr: bool) -> str:
  scene, camera = build_proj2_cornell_mirror_scene()
  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=mode,
    seed=args.seed,
    use_rr=use_rr,
    rr_min_depth=args.rr_min_depth,
  )
  rr_suffix = '_rr' if use_rr else '_no_rr'
  name = f'proj2_req7_mirror_{mode}{rr_suffix}'

  print('=' * 70)
  print(f'ESPELHO — modo={mode} use_rr={use_rr} spp={args.spp} depth={args.depth}')
  print('=' * 70)

  sim_dir = run_render_with_estimation(
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

  src = os.path.join(str(sim_dir), 'render.png')
  stable = os.path.join(args.out, f'{name}.png')
  if os.path.exists(src):
    os.makedirs(args.out, exist_ok=True)
    shutil.copyfile(src, stable)
    print(f'Cópia estável: {stable}')
  return str(sim_dir)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Etapa Extra: Espelho Perfeito — Reflexão especular pura',
  )
  parser.add_argument('--spp', type=int, default=20, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=8, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador (ignorado se --all)')
  parser.add_argument('--use-rr', type=lambda x: x.lower() in ('true', '1', 'yes'), default=False,
                      help='Usar Russian Roulette (ignorado se --all)')
  parser.add_argument('--rr-min-depth', type=int, default=None)
  parser.add_argument('--all', action='store_true',
                      help='Renderiza bsdf_only, nee_only, mis e mis+RR em sequência')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/req7_mirror',
                      help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração')

  args = parser.parse_args()

  if args.all:
    jobs = [
      ('bsdf_only', False),
      ('nee_only',  False),
      ('mis',       False),
      ('mis',       True),
    ]
  else:
    jobs = [(args.mode, args.use_rr)]

  for mode, use_rr in jobs:
    render_one(args, mode, use_rr)

  print('Espelho renderizado.')
