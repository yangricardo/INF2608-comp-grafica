"""BVH estática local a `TriangleMesh`.

A hierarquia não altera a matemática de interseção dos slides 4, p. 35 e
p. 47-48; ela só usa AABB por slabs (slides 4, p. 11-12) para podar subárvores
antes do teste Möller-Trumbore. Nesta base, a BVH é construída uma vez por
malha, usa median split no eixo dominante e não implementa SAH, compactação
linear ou uma estrutura de aceleração global para toda a cena.

TODO(accel): avaliar uma versão com SAH + layout linear de nós se a malha
passar a ser o gargalo dominante do renderizador.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from pyglm import glm

from ray_tracing_2.hit import Hit
from ray_tracing_2.ray import Ray


def _component_min(vectors: Sequence[glm.vec3]) -> glm.vec3:
  return glm.vec3(
    min(vector.x for vector in vectors),
    min(vector.y for vector in vectors),
    min(vector.z for vector in vectors),
  )


def _component_max(vectors: Sequence[glm.vec3]) -> glm.vec3:
  return glm.vec3(
    max(vector.x for vector in vectors),
    max(vector.y for vector in vectors),
    max(vector.z for vector in vectors),
  )


def _triangle_bounds(triangle: Any) -> tuple[glm.vec3, glm.vec3]:
  vertices = [glm.vec3(triangle.v0), glm.vec3(triangle.v1), glm.vec3(triangle.v2)]
  return _component_min(vertices), _component_max(vertices)


def _triangle_centroid(triangle: Any) -> glm.vec3:
  return glm.vec3((glm.vec3(triangle.v0) + glm.vec3(triangle.v1) + glm.vec3(triangle.v2)) / 3.0)


@dataclass
class AABB:
  p_min: glm.vec3
  p_max: glm.vec3

  @classmethod
  def from_triangles(cls, triangles: Sequence[Any]) -> AABB:
    # Slides 4, p. 11-12, reutilizados no Slide 6: a caixa é descrita pelos
    # mínimos e máximos por componente, isto é, pelo produto cartesiano de três
    # intervalos 1D que depois serão testados pelo método de slabs.
    bounds = [_triangle_bounds(triangle) for triangle in triangles]
    return cls(
      p_min=_component_min([bound[0] for bound in bounds]),
      p_max=_component_max([bound[1] for bound in bounds]),
    )

  def intersects(self, ray: Ray, t_min: float = 0.001, t_max: float = float('inf')) -> tuple[bool, float, float]:
    # Mantém o mesmo raciocínio geométrico do teste de caixa por slabs:
    # se o segmento [t_min, t_max] não entra na AABB, nenhuma primitiva da
    # subárvore pode produzir um hit mais próximo. Em termos algébricos, isso
    # equivale a intersectar intervalos [t_near, t_far] em x, y e z.
    t0 = t_min
    t1 = t_max
    eps = 1e-8

    for axis in range(3):
      origin = ray.o[axis]
      direction = ray.d[axis]
      slab_min = self.p_min[axis]
      slab_max = self.p_max[axis]

      if abs(direction) < eps:
        if origin < slab_min or origin > slab_max:
          return False, t0, t1
        continue

      inv_d = 1.0 / direction
      t_near = (slab_min - origin) * inv_d
      t_far = (slab_max - origin) * inv_d

      if t_near > t_far:
        t_near, t_far = t_far, t_near

      if t_near > t0:
        t0 = t_near
      if t_far < t1:
        t1 = t_far

      if t1 < t0:
        return False, t0, t1

    return True, t0, t1


@dataclass
class TriangleBVHNode:
  bounds: AABB
  triangles: list[Any] | None = None
  left: TriangleBVHNode | None = None
  right: TriangleBVHNode | None = None
  depth: int = 1

  @property
  def is_leaf(self) -> bool:
    return self.triangles is not None

  def intersect(self, ray: Ray, hit: Hit):
    bounds_hit, _, _ = self.bounds.intersects(ray, 0.001, hit.t)
    if not bounds_hit:
      return False

    if self.is_leaf:
      # Slides 4, p. 35 e p. 47-48: a folha preserva o fluxo de closest-hit;
      # só muda o número de triângulos efetivamente testados.
      found = False
      for triangle in self.triangles or []:
        if triangle.intersect(ray, hit):
          found = True
      return found

    ordered_children: list[tuple[float, TriangleBVHNode]] = []
    if self.left is not None:
      left_hit, left_entry, _ = self.left.bounds.intersects(ray, 0.001, hit.t)
      if left_hit:
        ordered_children.append((left_entry, self.left))
    if self.right is not None:
      right_hit, right_entry, _ = self.right.bounds.intersects(ray, 0.001, hit.t)
      if right_hit:
        ordered_children.append((right_entry, self.right))

    found = False
    for _, child in sorted(ordered_children, key=lambda item: item[0]):
      if child.intersect(ray, hit):
        found = True
    return found


class TriangleBVH:
  def __init__(self, triangles: Sequence[Any], leaf_size: int = 4):
    # Leaf size controla o compromisso entre profundidade de árvore e custo
    # por folha. A estrutura é construída uma única vez para a malha e fica no
    # espaço local do `TriangleMesh`; cenas com múltiplos objetos ainda usam o
    # loop linear de `Scene.compute_intersection()` no nível superior.
    self.leaf_size = max(1, int(leaf_size))
    triangle_list = list(triangles)
    self.root = self._build(triangle_list, depth=1)
    self.node_count = 0
    self.leaf_count = 0
    self.max_depth = 0
    self._collect_stats(self.root, depth=1)

  def _build(self, triangles: list[Any], depth: int) -> TriangleBVHNode | None:
    if not triangles:
      return None

    bounds = AABB.from_triangles(triangles)
    if len(triangles) <= self.leaf_size:
      return TriangleBVHNode(bounds=bounds, triangles=list(triangles), depth=depth)

    extent = bounds.p_max - bounds.p_min
    axis = max(range(3), key=lambda idx: extent[idx])
    # Heurística conservadora: separa pela mediana no eixo dominante.
    # É simples e estável, mas não substitui SAH nem split espacial discutidos
    # nas pp. 30-36 de 6.estrutura_aceleracao.pdf.
    sorted_triangles = sorted(triangles, key=lambda triangle: _triangle_centroid(triangle)[axis])
    middle = len(sorted_triangles) // 2
    left_triangles = sorted_triangles[:middle]
    right_triangles = sorted_triangles[middle:]

    if not left_triangles or not right_triangles:
      return TriangleBVHNode(bounds=bounds, triangles=list(triangles), depth=depth)

    left = self._build(left_triangles, depth + 1)
    right = self._build(right_triangles, depth + 1)
    return TriangleBVHNode(bounds=bounds, left=left, right=right, depth=depth)

  def _collect_stats(self, node: TriangleBVHNode | None, depth: int):
    if node is None:
      return

    self.node_count += 1
    self.max_depth = max(self.max_depth, depth)
    if node.is_leaf:
      self.leaf_count += 1
      return

    self._collect_stats(node.left, depth + 1)
    self._collect_stats(node.right, depth + 1)

  def intersect(self, ray: Ray, hit: Hit):
    if self.root is None:
      return False
    # TODO(accel): adicionar travessia iterativa com pilha explícita se a BVH
    # deixar de ser apenas local à malha e passar a exigir menor overhead.
    return self.root.intersect(ray, hit)