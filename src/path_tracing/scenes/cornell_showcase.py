"""Cena "showcase": Cornell Box rica para exercitar todos os modos do integrador.

Inspirada nas cenas do Projeto 1 (`ray_tracing_2/proj1_scene_common.py`): sala Cornell
canônica, caixas difusas rotacionadas (via `Instance`), esferas e uma luz de área. Aqui a
luz é um **octaedro** (malha de triângulos) e há materiais dielétricos (incolor e com
absorção Beer-Lambert), permitindo comparar `bsdf_only`/`nee_only`/`mis` (+ Roleta Russa)
a partir de uma única cena.

BSDFs usadas: Lambertian (paredes/objetos difusos), Dielectric (vidro), Emissive (luz).
"""

from __future__ import annotations
from pyglm import glm

from ..scene import Scene
from ..camera import Camera
from ..shape import Box, Sphere, TriangleMesh, Instance
from ..bsdf.lambertian import LambertianBSDF
from ..bsdf.emissive import EmissiveBSDF
from ..bsdf.dielectric import DielectricBSDF
from ..lights.area_mesh import TriangleMeshLight
from .polyhedra import octahedron


def _translate_rotate_y(tx: float, ty: float, tz: float, ry_deg: float = 0.0) -> glm.mat4:
  """Matriz que rotaciona em torno de Y e depois translada (igual ao Projeto 1)."""
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


def build_proj2_cornell_showcase_scene(
  amber_absorption: glm.vec3 | None = None,
) -> tuple[Scene, Camera]:
  """Constrói a cena showcase (Cornell Box rica) com luz poliédrica.

  Args:
    amber_absorption: coeficiente Beer-Lambert σ da esfera de vidro âmbar
      (default `(0.2, 0.6, 1.2)` — absorve azul → âmbar).

  Returns:
    (scene, camera).
  """
  if amber_absorption is None:
    amber_absorption = glm.vec3(0.2, 0.6, 1.2)

  scene = Scene(ambient_light=glm.vec3(0.0), max_depth=8)
  scene.background_color = glm.vec3(0.0)

  # === PAREDES (Cornell padrão) ===
  white = LambertianBSDF(glm.vec3(0.73, 0.73, 0.73))
  red = LambertianBSDF(glm.vec3(0.65, 0.05, 0.05))
  green = LambertianBSDF(glm.vec3(0.12, 0.45, 0.15))

  scene.objects.extend([
    Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.00), material=white),   # fundo
    Box(p_min=glm.vec3(-0.10, -0.10, 0.00), p_max=glm.vec3(0.00, 5.55, 5.55), material=green),     # esquerda
    Box(p_min=glm.vec3(5.55, -0.10, 0.00), p_max=glm.vec3(5.65, 5.55, 5.55), material=red),        # direita
    Box(p_min=glm.vec3(0.00, 5.55, 0.00), p_max=glm.vec3(5.55, 5.65, 5.55), material=white),       # teto
    Box(p_min=glm.vec3(-0.10, -0.10, 0.00), p_max=glm.vec3(5.65, 0.00, 5.55), material=white),     # piso
  ])

  # === LUZ POLIÉDRICA (octaedro) — geometria visível + luz NEE ===
  light_center = glm.vec3(2.775, 4.90, 2.775)
  Le = glm.vec3(18.0, 18.0, 18.0)  # área menor que o painel 3x3 → Le maior (ajustável)
  verts, faces = octahedron(light_center, radius=0.60)
  scene.objects.append(
    TriangleMesh.from_vertices_faces(verts, faces, EmissiveBSDF(Le), name='octahedron_light')
  )
  scene.lights.append(TriangleMeshLight(vertices=verts, faces=faces, Le=Le))

  # === OBJETOS DIFUSOS ROTACIONADOS (caixas) ===
  tall_box = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 3.30, 1.65), material=white)
  short_box = Box(p_min=glm.vec3(0.0, 0.0, 0.0), p_max=glm.vec3(1.65, 1.10, 1.65), material=white)
  scene.objects.append(Instance(tall_box, _translate_rotate_y(0.55, 0.0, 0.70, ry_deg=18.0)))
  scene.objects.append(Instance(short_box, _translate_rotate_y(3.30, 0.0, 0.70, ry_deg=-20.0)))

  # === DIELÉTRICOS ===
  scene.objects.append(Sphere(
    center=glm.vec3(1.50, 0.80, 3.40), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=None),                 # vidro incolor
  ))
  scene.objects.append(Sphere(
    center=glm.vec3(3.90, 0.80, 3.60), radius=0.80,
    material=DielectricBSDF(ior=1.5, absorption=amber_absorption),      # vidro âmbar (Beer-Lambert)
  ))

  # === ESFERA DIFUSA COLORIDA (color bleeding) ===
  scene.objects.append(Sphere(
    center=glm.vec3(2.70, 0.55, 4.70), radius=0.55,
    material=LambertianBSDF(glm.vec3(0.20, 0.30, 0.80)),                # azul
  ))

  # === CÂMERA (canônica) ===
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
