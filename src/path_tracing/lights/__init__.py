"""Luzes para ray tracing e path tracing (área retangular, pontual, infinita).

Hierarquia:
- Light: interface base para todas as luzes (sample_Li, pdf_Li para path tracing)
- PointLight: luz pontual isotrópica com interface legada (radiance, sample_radiance)
- AreaLight: luz retangular com penumbra e 3 modos de amostragem
- RectAreaLight: luz retangular moderna para path tracing (sample_Li, pdf_Li)
- AreaLightSamplingMode: enum para modos REGULAR, UNIFORM, STRATIFIED

Referências:
- Slide 4, pp. 40-41: ray tracing clássico
- Slide 5, pp. 14-23: area lights e penumbra
- PBRT 4e §12 "Light Sources"
"""

from __future__ import annotations

from .base import Light
from .point import PointLight
from .area import AreaLight, AreaLightSamplingMode
from .area_rect import RectAreaLight

__all__ = [
  'Light',
  'PointLight',
  'AreaLight',
  'AreaLightSamplingMode',
  'RectAreaLight',
]

