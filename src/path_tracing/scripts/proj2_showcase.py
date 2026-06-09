#!/usr/bin/env python3
"""Cena showcase: Cornell Box rica para comparar os modos do integrador.

Uma única cena (caixas difusas rotacionadas, esfera de vidro incolor, esfera de vidro
âmbar com absorção Beer-Lambert, esfera difusa colorida e luz poliédrica/octaedro)
renderizada em `bsdf_only`, `nee_only`, `mis` e `mis`+Roleta Russa.

Cada render é copiado para um caminho ESTÁVEL `out/proj2/showcase/proj2_showcase_<modo>[_rr].png`
para que o relatório LaTeX o inclua automaticamente (`\\IfFileExists`).

Uso:
  python -m path_tracing.scripts.proj2_showcase --all --spp 32 --depth 8 --seed 42
  python -m path_tracing.scripts.proj2_showcase --mode mis --use-rr true --spp 64
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
from path_tracing.scenes import build_proj2_cornell_showcase_scene


_ARGV = ' '.join(sys.argv)

def render_one(args, mode: str, use_rr: bool) -> str:
  """Renderiza a showcase num dado modo/RR e copia para um caminho estável."""
  scene, camera = build_proj2_cornell_showcase_scene()
  integrator = PathIntegrator(
    min_depth=args.min_depth,
    max_depth=args.depth,
    mode=mode,
    seed=args.seed,
    use_rr=use_rr,
    rr_min_depth=args.rr_min_depth,
  )
  rr_suffix = '_rr' if use_rr else '_no_rr'
  name = f'proj2_showcase_{mode}{rr_suffix}'

  print('=' * 70)
  print(f'SHOWCASE — modo={mode} use_rr={use_rr} spp={args.spp} depth={args.depth}')
  print('=' * 70)

  sim_dir = run_render_with_estimation(
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

  # Cópia estável (caminho determinístico, sem timestamp) para o relatório.
  src = os.path.join(str(sim_dir), 'render.png')
  stable = os.path.join(args.out, f'{name}.png')
  if os.path.exists(src):
    os.makedirs(args.out, exist_ok=True)
    shutil.copyfile(src, stable)
    print(f'Cópia estável: {stable}')
  return str(sim_dir)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Cena showcase — comparação de modos (bsdf_only/nee_only/mis [+RR]) numa só cena',
  )
  parser.add_argument('--spp', type=int, default=32, help='Samples per pixel')
  parser.add_argument('--depth', type=int, default=8, help='Profundidade máxima')
  parser.add_argument('--min-depth', type=int, default=4, help='Profundidade mínima (exigência: 4)')
  parser.add_argument('--mode', choices=['bsdf_only', 'nee_only', 'mis'], default='mis',
                      help='Modo do integrador (ignorado se --all)')
  parser.add_argument('--use-rr', type=lambda x: x.lower() in ('true', '1', 'yes'), default=False,
                      help='Usar Russian Roulette (true|false; ignorado se --all)')
  parser.add_argument('--rr-min-depth', type=int, default=None,
                      help='Profundidade mínima para RR (default: min_depth)')
  parser.add_argument('--all', action='store_true',
                      help='Renderiza bsdf_only, nee_only, mis e mis+RR em sequência')
  parser.add_argument('--seed', type=int, default=None, help='Seed do RNG')
  parser.add_argument('--gamma', action='store_true', help='Aplicar correção gama')
  parser.add_argument('--out', type=str, default='out/proj2/showcase', help='Diretório de saída')
  parser.add_argument('--width', type=int, default=512, help='Largura da imagem')
  parser.add_argument('--height', type=int, default=512, help='Altura da imagem')
  parser.add_argument('--no-calibrate', action='store_true', help='Pular calibração/estimativa de tempo')

  args = parser.parse_args()

  if args.all:
    jobs = [
      ('bsdf_only', False),
      ('nee_only', False),
      ('mis', False),
      ('mis', True),
    ]
  else:
    jobs = [(args.mode, args.use_rr)]

  for mode, use_rr in jobs:
    render_one(args, mode, use_rr)

  print('Showcase concluída.')
