"""Cena Cornell Box com Mesh Light (Etapa 06).

Idêntica a build_proj2_cornell_basic_scene(), mas:
- RectAreaLight (retangular) → TriangleMeshLight (malha de triângulos)
- Luz ainda é 3.0×3.0 unidades no teto, mas representada por 8 triângulos
  (pirâmide com base quadrada)

Ref: PBRT 4e §6.5 "Triangle Sampling"; §12.4 "Area Lights".
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..lights.area_mesh import TriangleMeshLight


def build_proj2_cornell_mesh_light_scene() -> tuple[Scene, Camera]:
  """Constrói cena Cornell Box com TriangleMeshLight no teto.
  
  Geometria: idêntica ao Cornell Box básico.
  Luz: substituída de RectAreaLight por TriangleMeshLight.
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

  # === PAINEL EMISSIVO (mesh light geometry) ===
  light_bsdf = EmissiveBSDF(glm.vec3(7.0, 7.0, 7.0))
  light_panel = Box(
    p_min=glm.vec3(1.275, 5.45, 1.275),
    p_max=glm.vec3(4.275, 5.55, 4.275),
    material=light_bsdf,
  )
  scene.objects.append(light_panel)

  # === MESH LIGHT ===
  # Quad plano (3.0×3.0) no teto (y=5.50), dividido em 2 triângulos, com a normal
  # apontando PARA BAIXO (-y) — para iluminar a sala. (A pirâmide anterior emitia
  # majoritariamente para fora/para cima, deixando a cena subiluminada: a maioria
  # das amostras caía no lado não-emissor, cos_at_light ≤ 0.) O requisito do
  # enunciado — poliedro/malha de triângulos com amostras uniformes de área — é
  # atendido por estes 2 triângulos coplanares.

  # Quadrado 3.0×3.0 em y=5.50
  base_x_min = 1.275
  base_x_max = 4.275
  base_z_min = 1.275
  base_z_max = 4.275
  base_y = 5.50

  vertices = [
    glm.vec3(base_x_min, base_y, base_z_min),  # v0: canto (-x,-z)
    glm.vec3(base_x_max, base_y, base_z_min),  # v1: canto (+x,-z)
    glm.vec3(base_x_max, base_y, base_z_max),  # v2: canto (+x,+z)
    glm.vec3(base_x_min, base_y, base_z_max),  # v3: canto (-x,+z)
  ]

  # Ordem dos vértices escolhida para que cross(v1-v0, v2-v0) = (0,-9,0) → normal -y.
  faces = [
    (0, 1, 2),  # triângulo 1
    (0, 2, 3),  # triângulo 2
  ]
  
  # Criar TriangleMeshLight
  # Mesma Le que RectAreaLight para convergência
  mesh_light = TriangleMeshLight(
    vertices=vertices,
    faces=faces,
    Le=glm.vec3(7.0, 7.0, 7.0),
  )
  scene.lights.append(mesh_light)

  # === OBJETOS ===
  low_box  = Box(p_min=glm.vec3(0.85, 0.00, 0.85), p_max=glm.vec3(2.50, 1.10, 2.50), material=white_bsdf)
  tall_box = Box(p_min=glm.vec3(3.00, 0.00, 2.80), p_max=glm.vec3(4.10, 2.30, 3.90), material=white_bsdf)
  sphere   = Sphere(center=glm.vec3(2.10, 0.62, 4.25), radius=0.62, material=white_bsdf)
  scene.objects.extend([low_box, tall_box, sphere])

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
