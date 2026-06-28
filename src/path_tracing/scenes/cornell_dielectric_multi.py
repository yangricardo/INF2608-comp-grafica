"""Cena Cornell Box com quatro esferas dielétricas em variações de IOR e absorção.

Composição: duas esferas no piso (primeiro plano, z≈3.5) e duas suspensas em
alturas distintas (fundo, z≈1.8), criando escalonamento em profundidade.

  - Esq-piso    (1.40, 0.76, 3.50): vidro incolor IOR=1.5
  - Dir-piso    (4.15, 0.76, 3.50): água azul-esverdeada IOR=1.33
  - Esq-suspensa (1.40, 2.50, 1.80): vidro âmbar IOR=1.5
  - Dir-suspensa (4.15, 3.50, 1.80): água incolor IOR=1.33
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


def build_proj2_cornell_dielectric_multi_scene() -> tuple[Scene, Camera]:
  """Cornell Box com quatro esferas dielétricas ilustrando variações de IOR e absorção.

  Composição (raio=0.75):
    Esq-piso     (1.40, 0.76, 3.50): vidro incolor IOR=1.5 — primeiro plano
    Dir-piso     (4.15, 0.76, 3.50): água azul-esverdeada IOR=1.33 — primeiro plano
    Esq-suspensa (1.40, 2.50, 1.80): vidro âmbar IOR=1.5 — suspensa, altura média
    Dir-suspensa (4.15, 3.50, 1.80): água incolor IOR=1.33 — suspensa, altura alta
  """
  scene = Scene(
    ambient_light=glm.vec3(0.0),
    max_depth=8,
  )
  scene.background_color = glm.vec3(0.0)

  # === MATERIAIS DAS PAREDES ===
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

  # === PAINEL EMISSIVO (teto) ===
  light_bsdf = EmissiveBSDF(glm.vec3(7.0, 7.0, 7.0))
  light_panel = Box(
    p_min=glm.vec3(1.275, 5.449, 1.275),
    p_max=glm.vec3(4.275, 5.550, 4.275),
    material=light_bsdf,
  )
  scene.objects.append(light_panel)

  # === LUZ NEE ===
  scene.lights.append(RectAreaLight(
    corner=glm.vec3(1.275, 5.45, 1.275),
    edge_u=glm.vec3(3.0, 0.0, 0.0),
    edge_v=glm.vec3(0.0, 0.0, 3.0),
    Le=glm.vec3(7.0, 7.0, 7.0),
  ))

  # === QUATRO ESFERAS DIELÉTRICAS ===
  r = 0.75  # raio comum

  # Piso — primeiro plano (z=3.50, próximas à câmera)
  scene.objects.append(Sphere(
    center=glm.vec3(1.40, r + 0.01, 3.50),
    radius=r,
    material=DielectricBSDF(ior=1.5, absorption=None),
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(4.15, r + 0.01, 3.50),
    radius=r,
    material=DielectricBSDF(ior=1.33, absorption=glm.vec3(0.30, 0.05, 0.10)),
  ))

  # Suspensas — fundo (z=1.80, recuadas), alturas distintas
  scene.objects.append(Sphere(
    center=glm.vec3(1.40, 2.50, 1.80),
    radius=r,
    material=DielectricBSDF(ior=1.5, absorption=glm.vec3(0.2, 0.6, 1.2)),
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(4.15, 3.50, 1.80),
    radius=r,
    material=DielectricBSDF(ior=1.33, absorption=None),
  ))

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
