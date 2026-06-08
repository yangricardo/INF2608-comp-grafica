"""Geradores de poliedros (vértices + faces triangulares) para luzes de malha.

Usado tanto pela cena isolada da Etapa 06 quanto pela cena "showcase". As faces
saem com winding tal que ``cross(v1-v0, v2-v0)`` aponta para FORA do centro, de
modo que a normal usada por ``TriangleMeshLight`` (emissão unilateral outward)
ilumine o ambiente ao redor.

Ref: PBRT 4e §6.5 "Triangle Meshes"; §12.4 "Area Lights".
"""

from __future__ import annotations
import math
from pyglm import glm


def _orient_outward(
  vertices: list[glm.vec3],
  faces: list[tuple[int, int, int]],
  center: glm.vec3,
) -> list[tuple[int, int, int]]:
  """Garante winding com normal apontando para fora do ``center``.

  Para cada face, se ``dot(cross(e1, e2), centroide - center) < 0`` a face está
  invertida (normal para dentro) e seus dois últimos índices são trocados.
  """
  oriented: list[tuple[int, int, int]] = []
  for i0, i1, i2 in faces:
    v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
    normal = glm.cross(v1 - v0, v2 - v0)
    centroid = (v0 + v1 + v2) / 3.0
    if glm.dot(normal, centroid - center) < 0.0:
      oriented.append((i0, i2, i1))  # inverte winding
    else:
      oriented.append((i0, i1, i2))
  return oriented


def hexagonal_panel(
  center: glm.vec3,
  normal: glm.vec3,
  radius: float,
  up: glm.vec3 | None = None,
) -> tuple[list[glm.vec3], list[tuple[int, int, int]]]:
  """Hexágono regular plano — 7 vértices (1 hub + 6 externos), 6 faces em leque.

  As normais outward das faces apontam na direção de ``normal``.
  ``up`` define o eixo local Y no plano; se None, escolhe um vetor perpendicular a ``normal``.
  """
  n = glm.normalize(glm.vec3(normal))

  if up is not None:
    u_raw = glm.vec3(up)
  elif abs(n.y) < 0.9:
    u_raw = glm.vec3(0.0, 1.0, 0.0)
  else:
    u_raw = glm.vec3(1.0, 0.0, 0.0)

  u = glm.normalize(u_raw - glm.dot(u_raw, n) * n)
  # v = cross(n, u): com winding CCW em {u,v}, cross(e1,e2) ∝ n (outward)
  v = glm.normalize(glm.cross(n, u))

  c = glm.vec3(center)
  r = float(radius)

  vertices: list[glm.vec3] = [c]
  for i in range(6):
    theta = math.radians(60.0 * i)
    vertices.append(c + r * math.cos(theta) * u + r * math.sin(theta) * v)

  # Leque: (hub=0, v_i, v_{i mod 6 + 1}), i=1..6
  faces: list[tuple[int, int, int]] = [(0, i, i % 6 + 1) for i in range(1, 7)]

  return vertices, faces


def octahedron(
  center: glm.vec3,
  radius: float,
) -> tuple[list[glm.vec3], list[tuple[int, int, int]]]:
  """Octaedro regular (6 vértices, 8 faces) centrado em ``center``.

  Os 6 vértices ficam a ``radius`` ao longo de ±x, ±y, ±z. As 8 faces ligam um
  vértice de cada par de eixos; o winding é corrigido para normais outward.

  Returns:
    (vertices, faces) prontos para ``TriangleMesh.from_vertices_faces`` e
    ``TriangleMeshLight``.
  """
  c = glm.vec3(center)
  r = float(radius)
  px = c + glm.vec3(r, 0.0, 0.0)
  nx = c + glm.vec3(-r, 0.0, 0.0)
  py = c + glm.vec3(0.0, r, 0.0)
  ny = c + glm.vec3(0.0, -r, 0.0)
  pz = c + glm.vec3(0.0, 0.0, r)
  nz = c + glm.vec3(0.0, 0.0, -r)

  # Índices: 0=+x 1=-x 2=+y 3=-y 4=+z 5=-z
  vertices = [px, nx, py, ny, pz, nz]
  # 4 faces superiores (ao redor de +y) + 4 inferiores (ao redor de -y)
  faces = [
    (2, 0, 4), (2, 4, 1), (2, 1, 5), (2, 5, 0),  # topo
    (3, 4, 0), (3, 1, 4), (3, 5, 1), (3, 0, 5),  # base
  ]
  faces = _orient_outward(vertices, faces, c)
  return vertices, faces
