"""Cena Cornell Box com cubo de água (IOR=1.33).

Estende cornell_basic com cubo transparente de água no centro do piso.
Demonstra refração com Snell's law e Fresnel com IOR mais próximo da realidade.
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..bsdf.dielectric import DielectricBSDF
from ..lights.area_rect import RectAreaLight


def build_proj2_cornell_water_scene(absorption: glm.vec3 | None = None) -> tuple[Scene, Camera]:
  """Constrói Cornell Box com cubo de água (IOR=1.33).

  Geometria:
  - Cornell Box padrão com paredes em Lambertian
  - Luz: RectAreaLight 3×3 no teto
  - Objeto: cubo de água (1.0×1.0×1.0) no piso, centrado em x,z

  Validação:
  - IOR=1.33 mais próximo da realidade que vidro (1.5)
  - Refração notavelmente diferente do vidro
  - Reflexão Fresnel menos pronunciada em ângulos normais

  Args:
    absorption: coeficiente de absorção Beer-Lambert σ (RGB). None/0 = incolor.
      Ex.: glm.vec3(0.30, 0.05, 0.10) absorve mais o vermelho → tom azul-esverdeado.
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

  # === PAREDES ===
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65,  0.00), material=white_bsdf)
  left_wall  = Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3(0.00, 5.55,  5.55), material=green_bsdf)
  right_wall = Box(p_min=glm.vec3( 5.55, -0.10,  0.00), p_max=glm.vec3(5.65, 5.55,  5.55), material=red_bsdf)
  ceiling    = Box(p_min=glm.vec3( 0.00,  5.55,  0.00), p_max=glm.vec3(5.55, 5.65,  5.55), material=white_bsdf)
  floor_box  = Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3(5.65, 0.00,  5.55), material=white_bsdf)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor_box])

  # === PAINEL EMISSIVO ===
  light_bsdf = EmissiveBSDF(glm.vec3(7.0, 7.0, 7.0))
  light_panel = Box(
    p_min=glm.vec3(1.275, 5.449, 1.275),
    p_max=glm.vec3(4.275, 5.550, 4.275),
    material=light_bsdf,
  )
  scene.objects.append(light_panel)

  # === LUZ (NEE) ===
  scene.lights.append(RectAreaLight(
    corner=glm.vec3(1.275, 5.45, 1.275),
    edge_u=glm.vec3(3.0, 0.0, 0.0),
    edge_v=glm.vec3(0.0, 0.0, 3.0),
    Le=glm.vec3(7.0, 7.0, 7.0),
  ))

  # === CUBO DE ÁGUA ===
  water_bsdf = DielectricBSDF(ior=1.33, absorption=absorption)
  water_cube = Box(
    p_min=glm.vec3(2.275, 0.00, 2.275),  # p_min no piso
    p_max=glm.vec3(3.275, 1.00, 3.275),  # cubo 1.0×1.0×1.0
    material=water_bsdf,
  )
  scene.objects.append(water_cube)

  # === CÂMERA ===
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
