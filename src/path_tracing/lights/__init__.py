"""Luzes para path tracing (área retangular, malha, infinita).

Hierarquia:
- Light (lights.base): interface base para todas as luzes (sample_Li, pdf_Li)
- RectAreaLight: luz retangular planar
"""

from __future__ import annotations

from .base import Light
from .area_rect import RectAreaLight

__all__ = ['Light', 'RectAreaLight']

