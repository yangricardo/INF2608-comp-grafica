"""WRAPPER DE COMPATIBILIDADE: re-exporta de materials/

Este arquivo mantém compatibilidade com código que importa de path_tracing.material.
Todas as implementações foram movidas para path_tracing/materials/ (modular).

Referências:
- materials.base.Material: interface base
- materials.emissive.EmissiveMaterial: emissão própria
- materials.phong.PhongMaterial: iluminação direta
- materials.reflective.ReflectiveMaterial: reflexão especular
- materials.transparent.TransparentMaterial: refração + absorção
"""

from __future__ import annotations

# Re-exporta interface base
from .materials.base import Material

# Re-exporta implementações específicas
from .materials.emissive import EmissiveMaterial
from .materials.phong import PhongMaterial
from .materials.reflective import ReflectiveMaterial
from .materials.transparent import TransparentMaterial

__all__ = [
  'Material',
  'EmissiveMaterial',
  'PhongMaterial',
  'ReflectiveMaterial',
  'TransparentMaterial',
]
