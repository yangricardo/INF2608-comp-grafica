from __future__ import annotations

import argparse
from typing import Sequence

from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AreaLightSamplingMode


class CLIHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
  pass


def build_parser(description: str, examples: Sequence[str] | None = None) -> argparse.ArgumentParser:
  epilog = None
  if examples:
    epilog = 'Examples:\n' + '\n'.join(f'  {example}' for example in examples)
  return argparse.ArgumentParser(
    description=description,
    epilog=epilog,
    formatter_class=CLIHelpFormatter,
  )


def add_image_size_arguments(
  parser: argparse.ArgumentParser,
  *,
  width_default: int | None,
  height_default: int | None,
  width_help: str = 'Image width in pixels',
  height_help: str = 'Image height in pixels',
) -> None:
  parser.add_argument('--width', type=int, default=width_default, help=width_help)
  parser.add_argument('--height', type=int, default=height_default, help=height_help)


def add_sampling_arguments(
  parser: argparse.ArgumentParser,
  *,
  spp_default: int = 1,
  sampling_mode_default: str = SamplingMode.JITTERED.value,
) -> None:
  parser.add_argument('--spp', type=int, default=spp_default, help='Samples per pixel (anti-aliasing)')
  parser.add_argument(
    '--sampling_mode',
    choices=[mode.value for mode in SamplingMode],
    default=sampling_mode_default,
    help='Sampling mode for film AA',
  )


def add_light_sampling_argument(
  parser: argparse.ArgumentParser,
  *,
  default: str = AreaLightSamplingMode.STRATIFIED.value,
  help_text: str = 'Sampling mode for area lights',
) -> None:
  parser.add_argument(
    '--light_sampling_mode',
    choices=[mode.value for mode in AreaLightSamplingMode],
    default=default,
    help=help_text,
  )


def add_seed_argument(parser: argparse.ArgumentParser) -> None:
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')


def add_gamma_fix_argument(parser: argparse.ArgumentParser) -> None:
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image')