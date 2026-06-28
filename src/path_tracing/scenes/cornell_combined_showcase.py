"""Cena combinada: Wall Lights + Dielétrico Multi-Material.

Reúne numa Cornell Box todos os recursos implementados no projeto:
  - 3 fontes de luz: RectAreaLight (teto branco) + 2 TriangleMeshLight hexagonais
    (parede esq. verde-esmeralda, parede dir. vermelho-laranja)
  - 4 esferas DielectricBSDF: 2 no piso (IOR=1.5 incolor e âmbar) e 2 suspensas
    (IOR=1.33 água incolor e azul-esverdeada)
  - 2 caixas Lambertianas rotacionadas
  - 1 esfera difusa azul (color bleeding)
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere, TriangleMesh, Instance
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..bsdf.dielectric import DielectricBSDF
from ..lights.area_rect import RectAreaLight
from ..lights.area_mesh import TriangleMeshLight
from .polyhedra import hexagonal_panel


def _translate_rotate_y(tx: float, ty: float, tz: float, ry_deg: float = 0.0) -> glm.mat4:
  """Matriz que rotaciona em torno de Y e depois translada."""
  ry = glm.radians(ry_deg)
  c = glm.cos(ry)
  s = glm.sin(ry)
  m = glm.mat4(1.0)
  m[0][0] = c
  m[0][2] = -s
  m[1][1] = 1.0
  m[2][0] = s
  m[2][2] = c
  m[3][0] = tx
  m[3][1] = ty
  m[3][2] = tz
  return m


def build_proj2_cornell_combined_showcase_scene() -> tuple[Scene, Camera]:
  """Cornell Box combinando wall lights e showcase dielétrico multi-material.

  Fontes de luz:
    - RectAreaLight 3×3 branca no teto (Le=6)
    - TriangleMeshLight hexagonal verde-esmeralda na parede esq. (Le=(4,15,4))
    - TriangleMeshLight hexagonal vermelho-laranja na parede dir. (Le=(15,4,4))

  Dielétricos:
    Piso-esq.     (1.50, 0.80, 3.40) r=0.80  IOR=1.5  incolor
    Piso-dir.     (3.90, 0.80, 3.60) r=0.80  IOR=1.5  âmbar (absorção azul)
    Suspensa-esq. (1.40, 3.60, 2.00) r=0.75  IOR=1.33 água incolor
    Suspensa-dir. (4.10, 2.60, 2.20) r=0.75  IOR=1.33 água azul-esverdeada

  Difusos:
    Caixa alta rotacionada (18°), caixa baixa rotacionada (−20°),
    esfera difusa azul (color bleeding).
  """
  scene = Scene(ambient_light=glm.vec3(0.0), max_depth=12)
  scene.background_color = glm.vec3(0.0)

  # === PAREDES ===
  white = LambertianBSDF(glm.vec3(0.73, 0.73, 0.73))
  red   = LambertianBSDF(glm.vec3(0.65, 0.05, 0.05))
  green = LambertianBSDF(glm.vec3(0.12, 0.45, 0.15))

  scene.objects.extend([
    Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3( 5.65,  5.65, 0.00), material=white),
    Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3( 0.00,  5.55, 5.55), material=green),
    Box(p_min=glm.vec3( 5.55, -0.10,  0.00), p_max=glm.vec3( 5.65,  5.55, 5.55), material=red),
    Box(p_min=glm.vec3( 0.00,  5.55,  0.00), p_max=glm.vec3( 5.55,  5.65, 5.55), material=white),
    Box(p_min=glm.vec3(-0.10, -0.10,  0.00), p_max=glm.vec3( 5.65,  0.00, 5.55), material=white),
  ])

  # === TETO — RectAreaLight + Box emissivo ===
  Le_ceil = glm.vec3(6.0, 6.0, 6.0)
  scene.objects.append(Box(
    p_min=glm.vec3(1.275, 5.449, 1.275),
    p_max=glm.vec3(4.275, 5.550, 4.275),
    material=EmissiveBSDF(Le_ceil),
  ))
  scene.lights.append(RectAreaLight(
    corner=glm.vec3(1.275, 5.45, 1.275),
    edge_u=glm.vec3(3.0, 0.0, 0.0),
    edge_v=glm.vec3(0.0, 0.0, 3.0),
    Le=Le_ceil,
  ))

  # === PAREDE ESQUERDA — hexágono verde-esmeralda ===
  Le_left = glm.vec3(4.0, 15.0, 4.0)
  verts_l, faces_l = hexagonal_panel(
    center=glm.vec3(0.01, 2.775, 2.775),
    normal=glm.vec3(1.0, 0.0, 0.0),
    radius=1.2,
    up=glm.vec3(0.0, 1.0, 0.0),
  )
  scene.objects.append(TriangleMesh.from_vertices_faces(verts_l, faces_l, EmissiveBSDF(Le_left), name='hex_left'))
  scene.lights.append(TriangleMeshLight(vertices=verts_l, faces=faces_l, Le=Le_left))

  # === PAREDE DIREITA — hexágono vermelho-laranja ===
  Le_right = glm.vec3(15.0, 4.0, 4.0)
  verts_r, faces_r = hexagonal_panel(
    center=glm.vec3(5.54, 2.775, 2.775),
    normal=glm.vec3(-1.0, 0.0, 0.0),
    radius=1.2,
    up=glm.vec3(0.0, 1.0, 0.0),
  )
  scene.objects.append(TriangleMesh.from_vertices_faces(verts_r, faces_r, EmissiveBSDF(Le_right), name='hex_right'))
  scene.lights.append(TriangleMeshLight(vertices=verts_r, faces=faces_r, Le=Le_right))

  # === CAIXAS LAMBERTIANAS ROTACIONADAS ===
  tall_box  = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 3.30, 1.65), material=white)
  short_box = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 1.10, 1.65), material=white)
  scene.objects.append(Instance(tall_box,  _translate_rotate_y(0.55, 0.0, 0.70, ry_deg= 18.0)))
  scene.objects.append(Instance(short_box, _translate_rotate_y(3.30, 0.0, 0.70, ry_deg=-20.0)))

  # === ESFERAS DIELÉTRICAS NO PISO ===
  scene.objects.append(Sphere(
    center=glm.vec3(1.50, 0.80, 3.40), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=None),
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(3.90, 0.80, 3.60), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=glm.vec3(0.2, 0.6, 1.2)),
  ))

  # === ESFERAS DIELÉTRICAS SUSPENSAS ===
  scene.objects.append(Sphere(
    center=glm.vec3(1.40, 3.60, 2.00), radius=0.75,
    material=DielectricBSDF(ior=1.33, absorption=None),
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(4.10, 2.60, 2.20), radius=0.75,
    material=DielectricBSDF(ior=1.33, absorption=glm.vec3(0.30, 0.05, 0.10)),
  ))

  # === ESFERA DIFUSA AZUL (color bleeding) ===
  scene.objects.append(Sphere(
    center=glm.vec3(2.70, 0.55, 4.70), radius=0.55,
    material=LambertianBSDF(glm.vec3(0.20, 0.30, 0.80)),
  ))

  # === CÂMERA ===
  camera = Camera(
    eye=glm.vec3(2.775, 3.200, 12.775),
    center=glm.vec3(2.775, 2.775, 2.775),
    up=glm.vec3(0.0, 1.0, 0.0),
    fov=50.0,
    width=512,
    height=512,
    focal_distance=1.0,
  )

  return scene, camera
