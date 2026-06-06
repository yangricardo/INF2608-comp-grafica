"""Cena Cornell Box basic para Etapa 02 do Projeto 2.

Referência:
- Veach & Guibas "Optimally Combining Sampling Techniques" (SIGGRAPH 1995)
  — Cornell Box é cena de referência clássica
- PBRT 4e §13 — exemplos de path tracing
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Plane, Sphere, Box
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..lights.area_rect import RectAreaLight


def build_proj2_cornell_basic_scene() -> tuple[Scene, Camera]:
  """Constrói cena Cornell Box básica.
  
  - 5 planos (piso, teto, parede frente, parede trás, parede lateral)
  - Paredes brancas, vermelha (lateral esq), verde (lateral dir)
  - 1 luz retangular no teto
  - Dimensões: 10 x 10 x 10 unidades
  
  Returns:
    Tupla (scene, camera)
  """
  # Criar cena
  scene = Scene(
    ambient_light=glm.vec3(0.0),  # Sem luz ambiente (apenas caminho)
    max_depth=8,
  )
  scene.background_color = glm.vec3(0.0)  # Fundo preto
  
  # === GEOMETRIA ===
  # Dimensões cornell box
  size = 5.0  # Meia dimensão
  
  # Materiais
  white_bsdf = LambertianBSDF(glm.vec3(0.8, 0.8, 0.8))
  red_bsdf = LambertianBSDF(glm.vec3(0.8, 0.0, 0.0))
  green_bsdf = LambertianBSDF(glm.vec3(0.0, 0.8, 0.0))
  
  # Piso (z = -size)
  floor = Plane(
    pos=glm.vec3(0, 0, -size),
    normal=glm.vec3(0, 0, 1),
    material=white_bsdf,
  )
  scene.objects.append(floor)
  
  # Teto (z = +size)
  ceiling = Plane(
    pos=glm.vec3(0, 0, size),
    normal=glm.vec3(0, 0, -1),
    material=white_bsdf,
  )
  scene.objects.append(ceiling)
  
  # Parede frente (y = +size)
  wall_front = Plane(
    pos=glm.vec3(0, size, 0),
    normal=glm.vec3(0, -1, 0),
    material=white_bsdf,
  )
  scene.objects.append(wall_front)
  
  # Parede trás (y = -size)
  wall_back = Plane(
    pos=glm.vec3(0, -size, 0),
    normal=glm.vec3(0, 1, 0),
    material=white_bsdf,
  )
  scene.objects.append(wall_back)
  
  # Parede lateral esquerda (x = -size) — vermelha
  wall_left = Plane(
    pos=glm.vec3(-size, 0, 0),
    normal=glm.vec3(1, 0, 0),
    material=red_bsdf,
  )
  scene.objects.append(wall_left)
  
  # Parede lateral direita (x = +size) — verde
  wall_right = Plane(
    pos=glm.vec3(size, 0, 0),
    normal=glm.vec3(-1, 0, 0),
    material=green_bsdf,
  )
  scene.objects.append(wall_right)
  
  # === OBJETOS ===
  # Esfera no chão (x negativo)
  sphere = Sphere(
    center=glm.vec3(-2.0, -1.0, -size + 1.5),
    radius=1.0,
    material=white_bsdf,
  )
  scene.objects.append(sphere)
  
  # Caixa no chão (x positivo)
  box = Box(
    p_min=glm.vec3(1.0, -2.5, -size),
    p_max=glm.vec3(3.5, -0.5, -size + 3.0),
    material=white_bsdf,
  )
  scene.objects.append(box)
  
  # === LUZ ===
  # Luz retangular no teto (centro, tamanho 3x3)
  light_corner = glm.vec3(-1.5, -1.5, size - 0.01)
  light_edge_u = glm.vec3(3.0, 0, 0)  # Comprimento 3
  light_edge_v = glm.vec3(0, 3.0, 0)  # Profundidade 3
  light_emissive = glm.vec3(2.0, 2.0, 2.0)  # Radiância forte
  
  light = RectAreaLight(
    corner=light_corner,
    edge_u=light_edge_u,
    edge_v=light_edge_v,
    Le=light_emissive,
  )
  scene.lights.append(light)
  
  # === CÂMERA ===
  camera = Camera(
    eye=glm.vec3(0, 0, 6.5),
    center=glm.vec3(0, 0, 0),
    up=glm.vec3(0, 1, 0),
    fov=40.0,
    width=512,
    height=512,
    focal_distance=1.0,
  )
  
  return scene, camera
