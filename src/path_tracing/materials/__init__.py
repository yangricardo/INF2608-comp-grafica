"""Materiais para ray tracing e path tracing.

Hierarquia:
- Material: interface base abstrata
- EmissiveMaterial: emissão própria (dupla identidade com AreaLight)
- PhongMaterial: iluminação direta (ambiente + difusa + especular)
- ReflectiveMaterial: Phong + reflexão especular com Fresnel-Schlick
- TransparentMaterial: Phong + refração com Snell + absorção Beer

Referências:
- Slide 4-5: ray tracing clássico
- PBRT 4e §5, §9 "Materials"
"""

from __future__ import annotations

from .base import Material
from .emissive import EmissiveMaterial
from .phong import PhongMaterial
from .reflective import ReflectiveMaterial
from .transparent import TransparentMaterial

__all__ = [
  'Material',
  'EmissiveMaterial',
  'PhongMaterial',
  'ReflectiveMaterial',
  'TransparentMaterial',
]
