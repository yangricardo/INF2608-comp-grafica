"""Cenas para o Projeto 2 (path tracing).

Ref: geometria idêntica a src/ray_tracing_2/proj1_scene_common.py —
mesmas dimensões, mesma câmera, mesmos objetos. Materiais substituídos
de PhongMaterial → LambertianBSDF; luzes de AreaLight/PointLight →
painel EmissiveBSDF no teto.
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..lights.area_rect import RectAreaLight
from ..lights.area_mesh import TriangleMeshLight


def build_proj2_cornell_basic_scene() -> tuple[Scene, Camera]:
  """Constrói cena Cornell Box para path tracing.

  Geometria: idêntica ao Cornell Box do Proj1 (proj1_scene_common.py).
  - Y-up (piso em y=0, teto em y=5.55, caixa aberta em z=5.55)
  - Câmera FORA da caixa em z=12.775 olhando através da face aberta
  - Paredes: Box thin slabs com LambertianBSDF
  - Luz: painel EmissiveBSDF no teto (3x3 unidades, Le=(7,7,7))
  - Objetos: caixa baixa, caixa alta, esfera
  """
  scene = Scene(
    ambient_light=glm.vec3(0.0),
    max_depth=8,
  )
  scene.background_color = glm.vec3(0.0)

  # === MATERIAIS ===
  white_bsdf = LambertianBSDF(glm.vec3(0.73, 0.73, 0.73))
  red_bsdf   = LambertianBSDF(glm.vec3(0.65, 0.05, 0.05))
  green_bsdf = LambertianBSDF(glm.vec3(0.12, 0.45, 0.15))

  # === PAREDES (Box thin slabs — idêntico ao proj1_scene_common.build_cornell_room) ===
  # Face aberta em z=5.55; câmera em z=12.775 olha através dessa abertura
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65,  0.00), material=white_bsdf)
  left_wall  = Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3(0.00, 5.55,  5.55), material=green_bsdf)
  right_wall = Box(p_min=glm.vec3( 5.55, -0.10,  0.00), p_max=glm.vec3(5.65, 5.55,  5.55), material=red_bsdf)
  ceiling    = Box(p_min=glm.vec3( 0.00,  5.55,  0.00), p_max=glm.vec3(5.55, 5.65,  5.55), material=white_bsdf)
  floor_box  = Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3(5.65, 0.00,  5.55), material=white_bsdf)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor_box])

  # === PAINEL EMISSIVO (substitui AreaLight — path tracer amostra via BSDF) ===
  # 3.0×3.0 unidades centrado no teto; Le=(7,7,7) calibrado para exposição razoável
  light_bsdf = EmissiveBSDF(glm.vec3(7.0, 7.0, 7.0))
  light_panel = Box(
    p_min=glm.vec3(1.275, 5.449, 1.275),
    p_max=glm.vec3(4.275, 5.550, 4.275),
    material=light_bsdf,
  )
  scene.objects.append(light_panel)

  # RectAreaLight paralela ao painel: usada por NEE (mode=nee_only/mis).
  # Mesmas coordenadas do EmissiveBSDF Box — corner=p_min do topo do painel,
  # edges ao longo de x e z. Le idêntico para que bsdf_only e nee_only
  # convirjam para o mesmo valor em SPP alto.
  # Ref: PBRT 4e §12.4 Area Lights; §13.4 A Better Path Tracer.
  scene.lights.append(RectAreaLight(
    corner=glm.vec3(1.275, 5.45, 1.275),
    edge_u=glm.vec3(3.0, 0.0, 0.0),
    edge_v=glm.vec3(0.0, 0.0, 3.0),
    Le=glm.vec3(7.0, 7.0, 7.0),
  ))

  # === OBJETOS (estilo req3, axis-aligned) ===
  low_box  = Box(p_min=glm.vec3(0.85, 0.00, 0.85), p_max=glm.vec3(2.50, 1.10, 2.50), material=white_bsdf)
  tall_box = Box(p_min=glm.vec3(3.00, 0.00, 2.80), p_max=glm.vec3(4.10, 2.30, 3.90), material=white_bsdf)
  sphere   = Sphere(center=glm.vec3(2.10, 0.62, 4.25), radius=0.62, material=white_bsdf)
  scene.objects.extend([low_box, tall_box, sphere])

  # === CÂMERA (idêntica ao CANONICAL_CAMERA do proj1) ===
  # eye z=12.775 está FORA da caixa (que termina em z=5.55)
  camera = Camera(
    eye=glm.vec3(2.775, 3.200, 12.775),
    center=glm.vec3(2.775, 2.775,  2.775),
    up=glm.vec3(0.0, 1.0, 0.0),
    fov=50.0,
    width=512,
    height=512,
    focal_distance=1.0,
  )

  return scene, camera


# Re-export cornell_mesh_light scene builder
from .cornell_mesh_light import build_proj2_cornell_mesh_light_scene
from .cornell_glass import build_proj2_cornell_glass_scene
from .cornell_water import build_proj2_cornell_water_scene
from .cornell_showcase import build_proj2_cornell_showcase_scene
from .cornell_wall_lights import build_proj2_cornell_wall_lights_scene
from .cornell_dielectric_multi import build_proj2_cornell_dielectric_multi_scene

__all__ = [
  'build_proj2_cornell_basic_scene',
  'build_proj2_cornell_mesh_light_scene',
  'build_proj2_cornell_glass_scene',
  'build_proj2_cornell_water_scene',
  'build_proj2_cornell_showcase_scene',
  'build_proj2_cornell_wall_lights_scene',
  'build_proj2_cornell_dielectric_multi_scene',
]
