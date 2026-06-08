"""Cena "wall lights": Cornell Box com luz retangular no teto e painéis hexagonais nas paredes.

Três fontes de luz independentes:
  - Teto: RectAreaLight 3×3 branca (Le=6)  + Box EmissiveBSDF visível
  - Parede esquerda (verde): TriangleMeshLight hexagonal verde-esmeralda (Le=(4,15,4))
  - Parede direita (vermelha): TriangleMeshLight hexagonal vermelho-laranja (Le=(15,4,4))

Os painéis hexagonais são planos (todas as normais apontam para dentro da sala),
o que garante emissão unidirecional correta para NEE/MIS independentemente do
bug abs() em TriangleMeshLight.pdf_Li.
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


def build_proj2_cornell_wall_lights_scene(
  amber_absorption: glm.vec3 | None = None,
) -> tuple[Scene, Camera]:
  """Cornell Box com luz retangular no teto e luzes hexagonais nas paredes laterais.

  Args:
    amber_absorption: coeficiente Beer-Lambert σ da esfera de vidro âmbar
      (default (0.2, 0.6, 1.2) — absorve azul → âmbar).

  Returns:
    (scene, camera).
  """
  if amber_absorption is None:
    amber_absorption = glm.vec3(0.2, 0.6, 1.2)

  scene = Scene(ambient_light=glm.vec3(0.0), max_depth=8)
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
  # Plano X=0.01, normal +X (aponta para dentro da sala), raio 1.2 unidades
  Le_left = glm.vec3(4.0, 15.0, 4.0)
  verts_l, faces_l = hexagonal_panel(
    center=glm.vec3(0.01, 2.775, 2.775),
    normal=glm.vec3(1.0, 0.0, 0.0),
    radius=1.2,
    up=glm.vec3(0.0, 1.0, 0.0),
  )
  scene.objects.append(
    TriangleMesh.from_vertices_faces(verts_l, faces_l, EmissiveBSDF(Le_left), name='hex_left')
  )
  scene.lights.append(TriangleMeshLight(vertices=verts_l, faces=faces_l, Le=Le_left))

  # === PAREDE DIREITA — hexágono vermelho-laranja ===
  # Plano X=5.54, normal -X (aponta para dentro da sala), raio 1.2 unidades
  Le_right = glm.vec3(15.0, 4.0, 4.0)
  verts_r, faces_r = hexagonal_panel(
    center=glm.vec3(5.54, 2.775, 2.775),
    normal=glm.vec3(-1.0, 0.0, 0.0),
    radius=1.2,
    up=glm.vec3(0.0, 1.0, 0.0),
  )
  scene.objects.append(
    TriangleMesh.from_vertices_faces(verts_r, faces_r, EmissiveBSDF(Le_right), name='hex_right')
  )
  scene.lights.append(TriangleMeshLight(vertices=verts_r, faces=faces_r, Le=Le_right))

  # === OBJETOS DIFUSOS ROTACIONADOS ===
  tall_box  = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 3.30, 1.65), material=white)
  short_box = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 1.10, 1.65), material=white)
  scene.objects.append(Instance(tall_box,  _translate_rotate_y(0.55, 0.0, 0.70, ry_deg= 18.0)))
  scene.objects.append(Instance(short_box, _translate_rotate_y(3.30, 0.0, 0.70, ry_deg=-20.0)))

  # === DIELÉTRICOS ===
  scene.objects.append(Sphere(
    center=glm.vec3(1.50, 0.80, 3.40), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=None),
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(3.90, 0.80, 3.60), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=amber_absorption),
  ))

  # === ESFERA DIFUSA COLORIDA (color bleeding) ===
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
