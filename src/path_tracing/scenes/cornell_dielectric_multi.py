"""Cena Cornell Box com quatro esferas dielétricas em variações de IOR e absorção.

Demonstra o espectro completo de DielectricBSDF:
  - Vidro incolor (IOR=1.5): alta reflectância Fresnel em ângulos rasantes
  - Vidro âmbar (IOR=1.5, absorção azul): coloração por Beer-Lambert
  - Água incolor (IOR=1.33): refração mais suave, menos Fresnel
  - Água azul-esverdeada (IOR=1.33, absorção vermelha): coloração por Beer-Lambert
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
  """Cornell Box com quatro esferas dielétricas (2×2) ilustrando variações de IOR e absorção.

  Layout das esferas (raio=0.75, pousadas no piso):
    Frente-esq  (1.40, 0.75, 1.50): vidro incolor    IOR=1.5
    Frente-dir  (4.15, 0.75, 1.50): vidro âmbar      IOR=1.5, absorção azul
    Fundo-esq   (1.40, 0.75, 3.90): água incolor     IOR=1.33
    Fundo-dir   (4.15, 0.75, 3.90): água azul-esverdeada IOR=1.33, absorção vermelha
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
  y = r + 0.01  # centro ligeiramente acima do piso para evitar auto-interseção

  # Frente-esquerda: vidro incolor IOR=1.5
  scene.objects.append(Sphere(
    center=glm.vec3(1.40, y, 1.50),
    radius=r,
    material=DielectricBSDF(ior=1.5, absorption=None),
  ))

  # Frente-direita: vidro âmbar IOR=1.5 (absorve azul → tom amarelo-âmbar)
  scene.objects.append(Sphere(
    center=glm.vec3(4.15, y, 1.50),
    radius=r,
    material=DielectricBSDF(ior=1.5, absorption=glm.vec3(0.2, 0.6, 1.2)),
  ))

  # Fundo-esquerda: água incolor IOR=1.33
  scene.objects.append(Sphere(
    center=glm.vec3(1.40, y, 3.90),
    radius=r,
    material=DielectricBSDF(ior=1.33, absorption=None),
  ))

  # Fundo-direita: água azul-esverdeada IOR=1.33 (absorve vermelho → tom azul-esverdeado)
  scene.objects.append(Sphere(
    center=glm.vec3(4.15, y, 3.90),
    radius=r,
    material=DielectricBSDF(ior=1.33, absorption=glm.vec3(0.30, 0.05, 0.10)),
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
