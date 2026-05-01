from __future__ import annotations

from pathlib import Path

from pyglm import glm

from ray_tracing_2.material import Material
from ray_tracing_2.shape import TriangleMesh


def _parse_index(token: str, vertex_count: int) -> int:
  index = int(token)
  if index > 0:
    return index - 1
  return vertex_count + index


def load_obj_mesh(path: str | Path, material: Material, name: str | None = None) -> TriangleMesh:
  # Slide 4, p. 35 e p. 47-48: o OBJ é convertido para triângulos porque a cena
  # usa o mesmo closest-hit das demais primitivas, sem uma estrutura extra de aceleração.
  obj_path = Path(path)
  vertices: list[glm.vec3] = []
  faces: list[tuple[int, int, int]] = []

  for raw_line in obj_path.read_text(encoding='utf-8').splitlines():
    line = raw_line.strip()
    if not line or line.startswith('#'):
      continue

    parts = line.split()
    tag = parts[0]

    if tag == 'v' and len(parts) >= 4:
      vertices.append(glm.vec3(float(parts[1]), float(parts[2]), float(parts[3])))
      continue

    if tag == 'f' and len(parts) >= 4:
      indices: list[int] = []
      for token in parts[1:]:
        index_token = token.split('/')[0]
        if not index_token:
          continue
        indices.append(_parse_index(index_token, len(vertices)))

      if len(indices) < 3:
        continue

      # Slide 4, p. 35 e p. 47-48: a malha é avaliada por triângulos no fluxo de
      # closest-hit; por isso, a triangulação em leque converte faces poligonais
      # do OBJ em triângulos compatíveis com `TriangleMesh`.
      anchor = indices[0]
      for i in range(1, len(indices) - 1):
        faces.append((anchor, indices[i], indices[i + 1]))

  if not vertices or not faces:
    raise ValueError(f'OBJ file {obj_path} does not contain enough vertices/faces')

  mesh_name = name if name is not None else obj_path.stem
  return TriangleMesh.from_vertices_faces(vertices, faces, material, name=mesh_name)