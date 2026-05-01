from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Sequence

from ray_tracing_2.film import SamplingMode, sampling_mode_help_text
from ray_tracing_2.light import AreaLightSamplingMode


MATERIAL_MODEL_CHOICES = ['opaque', 'reflective', 'transparent']


@dataclass(slots=True)
class CommonRenderOptions:
  """Agrupa os parâmetros compartilhados entre CLI, entrypoints e `Render.render()`.

  O objetivo é padronizar a fronteira `argparse.Namespace -> render(...)`
  sem empurrar detalhes de cena para `Render.render()`. Em particular,
  `sampling_mode` continua sendo o controle público do filme, enquanto
  `light_sampling_mode` permanece fora desta classe por pertencer apenas às
  cenas que usam `AreaLight`.
  """

  width: int
  height: int
  spp: int = 1
  sampling_mode: str = SamplingMode.JITTERED.value
  seed: int | None = None
  gamma_fix: bool = False

  def __post_init__(self) -> None:
    self.width = int(self.width)
    self.height = int(self.height)
    self.spp = int(self.spp)
    self.sampling_mode = str(self.sampling_mode)
    self.seed = None if self.seed is None else int(self.seed)
    self.gamma_fix = bool(self.gamma_fix)

  @classmethod
  def from_namespace(cls, args: argparse.Namespace) -> CommonRenderOptions:
    return cls(
      width=int(args.width),
      height=int(args.height),
      spp=int(args.spp),
      sampling_mode=str(args.sampling_mode),
      seed=getattr(args, 'seed', None),
      gamma_fix=bool(getattr(args, 'gamma_fix', False)),
    )

  def to_entrypoint_kwargs(self) -> dict[str, Any]:
    return {
      'width': self.width,
      'height': self.height,
      'spp': self.spp,
      'sampling_mode': self.sampling_mode,
      'seed': self.seed,
      'gamma_fix': self.gamma_fix,
    }

  def to_render_kwargs(self, *, name: str) -> dict[str, Any]:
    return {
      'width': self.width,
      'height': self.height,
      'name': name,
      'samples_per_pixel': self.spp,
      'sampling_mode': self.sampling_mode,
      'seed': self.seed,
      'gamma_fix': self.gamma_fix,
    }


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
  parser.add_argument(
    '--spp',
    type=int,
    default=spp_default,
    help='Requested film samples per pixel. In center mode the effective value is always 1.',
  )
  parser.add_argument(
    '--sampling_mode',
    choices=[mode.value for mode in SamplingMode],
    default=sampling_mode_default,
    help=sampling_mode_help_text(),
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


def add_common_render_arguments(
  parser: argparse.ArgumentParser,
  *,
  width_default: int | None,
  height_default: int | None,
  spp_default: int = 1,
  sampling_mode_default: str = SamplingMode.JITTERED.value,
  width_help: str = 'Image width in pixels',
  height_help: str = 'Image height in pixels',
) -> None:
  add_image_size_arguments(
    parser,
    width_default=width_default,
    height_default=height_default,
    width_help=width_help,
    height_help=height_help,
  )
  add_sampling_arguments(
    parser,
    spp_default=spp_default,
    sampling_mode_default=sampling_mode_default,
  )
  add_seed_argument(parser)
  add_gamma_fix_argument(parser)


def add_max_depth_argument(
  parser: argparse.ArgumentParser,
  *,
  default: int = 4,
  help_text: str = 'Maximum recursion depth for reflection/refraction',
) -> None:
  parser.add_argument('--max_depth', type=int, default=default, help=help_text)


def add_block_material_arguments(
  parser: argparse.ArgumentParser,
  *,
  small_default: str = 'opaque',
  large_default: str = 'opaque',
) -> None:
  parser.add_argument(
    '--small_block_material',
    choices=MATERIAL_MODEL_CHOICES,
    default=small_default,
    help='Material model used by the small block',
  )
  parser.add_argument(
    '--large_block_material',
    choices=MATERIAL_MODEL_CHOICES,
    default=large_default,
    help='Material model used by the large block',
  )