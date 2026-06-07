"""Cena Cornell Box com Mesh Light (Etapa 06).

Idêntica a build_proj2_cornell_basic_scene(), mas a fonte é uma **luz poliédrica**:
- RectAreaLight (retangular) → TriangleMeshLight (malha de triângulos)
- A luz é um **octaedro** suspenso no teto (8 faces triangulares), claramente um
  poliedro — não um quad plano. O mesmo octaedro serve de geometria emissiva
  (visível para a câmera) e de luz para NEE.

Ref: PBRT 4e §6.5 "Triangle Sampling"; §12.4 "Area Lights".
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere, TriangleMesh
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..lights.area_mesh import TriangleMeshLight
from .polyhedra import octahedron


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

  # === LUZ POLIÉDRICA (octaedro) ===
  # Octaedro suspenso no teto: poliedro nítido (8 faces). O MESMO octaedro é tanto
  # a geometria emissiva visível (TriangleMesh + EmissiveBSDF) quanto a luz de NEE
  # (TriangleMeshLight). Le maior que o painel 3x3 porque a área é menor (ajustável).
  light_center = glm.vec3(2.775, 4.90, 2.775)
  Le = glm.vec3(18.0, 18.0, 18.0)
  verts, faces = octahedron(light_center, radius=0.60)
  scene.objects.append(
    TriangleMesh.from_vertices_faces(verts, faces, EmissiveBSDF(Le), name='octahedron_light')
  )
  scene.lights.append(TriangleMeshLight(vertices=verts, faces=faces, Le=Le))

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
