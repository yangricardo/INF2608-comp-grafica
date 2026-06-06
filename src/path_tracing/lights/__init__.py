"""Luzes para path tracing (área retangular, malha, infinita)."""

from __future__ import annotations

from .base import Light
from .area_rect import RectAreaLight

__all__ = ['Light', 'RectAreaLight']

