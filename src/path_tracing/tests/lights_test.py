"""Testes para o módulo lights/ do path_tracing.

Cobre:
1. Uniformidade de ``RectAreaLight.sample_Li`` (média das coords = centro).
2. Conservação de PDF: ∫ pdf_solid_angle dω ≈ 1 (Monte Carlo).
3. Consistência sample⇄pdf: sortear wi, depois pdf_Li, ambos batem.
4. ``PointLight`` MIS: ``is_delta=True``, ``pdf_solid_angle=math.inf``.
5. ``TriangleMeshLight`` básico: pdf > 0 só para lado emissor.
6. ``octahedron`` outward: dot(cross, centroid - center) > 0.

Execução::

    python -m path_tracing.tests.lights_test

Tolerâncias podem ser ajustadas se rodando em hardware lento. Os valores
abaixo foram calibrados para 50k amostras em CPU moderna (Python puro).

Convenção de normal: a luz retangular ``RectAreaLight(corner, edge_u, edge_v, Le)``
tem ``normal = normalize(cross(edge_u, edge_v))``. Esta normal aponta PARA
FORA do lado emissor (outward). O lado emissor é, portanto, o hemisfério
onde ``dot(wi, normal) < 0`` — i.e., a direção que aponta de volta para a
luz. Para o caso típico (luz no teto emitindo para baixo), usa-se
``edge_u = +x``, ``edge_v = +z``, dando ``normal = (0, -1, 0)``, e o ref
fica abaixo (y < altura da luz); wi aponta para cima (y > 0).
"""

from __future__ import annotations

import math
import os
import random
import sys
import unittest

# Permitir ``python -m path_tracing.tests.lights_test``
_pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _pkg_root not in sys.path:
  sys.path.insert(0, _pkg_root)

from pyglm import glm  # noqa: E402

from path_tracing.lights.base import Light  # noqa: E402
from path_tracing.lights.point import PointLight  # noqa: E402
from path_tracing.lights.area_rect import RectAreaLight  # noqa: E402
from path_tracing.lights.area_mesh import TriangleMeshLight  # noqa: E402
from path_tracing.scenes.polyhedra import octahedron  # noqa: E402


# ===========================================================================
# Helpers
# ===========================================================================

def _sample_hemisphere_uniform(
  n: int, normal: glm.vec3, rng: random.Random
) -> list[glm.vec3]:
  """Amostra wi uniformemente no hemisfério definido por dot(wi, normal) > 0."""
  n_len = glm.length(normal)
  if n_len < 1e-9:
    raise ValueError("normal degenerada")
  n_hat = normal / n_len
  if abs(n_hat.y) < 0.9:
    t = glm.normalize(glm.cross(n_hat, glm.vec3(0, 1, 0)))
  else:
    t = glm.normalize(glm.cross(n_hat, glm.vec3(1, 0, 0)))
  b = glm.cross(n_hat, t)
  out: list[glm.vec3] = []
  for _ in range(n):
    u1 = rng.random()
    u2 = rng.random()
    r = math.sqrt(max(0.0, 1.0 - u1 * u1))
    phi = 2.0 * math.pi * u2
    local = glm.vec3(r * math.cos(phi), u1, r * math.sin(phi))
    out.append(glm.normalize(t * local.x + n_hat * local.y + b * local.z))
  return out


# ===========================================================================
# 1. Uniformidade de RectAreaLight
# ===========================================================================

class RectUniformityTest(unittest.TestCase):
  """Amostras no retângulo devem cair uniformemente dentro do paralelogramo."""

  def test_mean_position_is_center(self):
    rng = random.Random(0xC0FFEE)
    n = 50_000
    # Luz no "teto" y=5, edge_u=+x, edge_v=+z → normal = (0,-1,0).
    # Lado emissor: ref ABAIXO, wi aponta para CIMA.
    light = RectAreaLight(
      corner=glm.vec3(0, 5, 0),
      edge_u=glm.vec3(2, 0, 0),
      edge_v=glm.vec3(0, 0, 3),
      Le=glm.vec3(1, 1, 1),
    )
    ref = glm.vec3(1, 0, 1.5)
    sum_x = sum_z = 0.0
    n_valid = 0
    for _ in range(n):
      u = glm.vec2(rng.random(), rng.random())
      s = light.sample_Li(ref, u)
      if s is None:
        continue
      p = s['p_on_light']
      sum_x += p.x
      sum_z += p.z
      n_valid += 1
    self.assertGreater(n_valid, int(0.95 * n), 'amostras invalidas demais')
    mean_x = sum_x / n_valid
    mean_z = sum_z / n_valid
    # Centro: corner + 0.5*(2,0,0) + 0.5*(0,0,3) = (1, 5, 1.5)
    self.assertAlmostEqual(mean_x, 1.0, delta=0.05)
    self.assertAlmostEqual(mean_z, 1.5, delta=0.05)


# ===========================================================================
# 2. Conservação de PDF do RectAreaLight
# ===========================================================================

class RectPDFConservationTest(unittest.TestCase):
  """∫_Ω pdf_solid_angle(ω) dω ≈ 1 sobre o hemisfério emissor."""

  def test_pdf_integrates_to_one(self):
    rng = random.Random(0xDEADBEEF)
    light = RectAreaLight(
      corner=glm.vec3(0, 5, 0),
      edge_u=glm.vec3(2, 0, 0),
      edge_v=glm.vec3(0, 0, 2),
      Le=glm.vec3(1, 1, 1),
    )
    # Lado emissor: ref embaixo (y=0), wi aponta para cima (+y).
    # O hemisfério emissor é o hemisfério definido por -light.normal = (0,+1,0).
    ref = glm.vec3(1, 0, 1)
    n = 50_000
    emitter_hemi = -light.normal  # (0, +1, 0)
    wis = _sample_hemisphere_uniform(n, emitter_hemi, rng)
    pdf_hemi = 1.0 / (2.0 * math.pi)
    acc = 0.0
    n_hit = 0
    for wi in wis:
      pdf = light.pdf_Li(ref, wi)
      if pdf > 0.0:
        n_hit += 1
      acc += pdf / pdf_hemi
    estimate = acc / n
    self.assertAlmostEqual(estimate, 1.0, delta=0.10,
                           msg=f'integral pdf = {estimate:.4f} (esperado 1.0)')
    self.assertGreater(n_hit, 100)


# ===========================================================================
# 3. Consistência sample ⇄ pdf do RectAreaLight
# ===========================================================================

class RectSamplePDFConsistencyTest(unittest.TestCase):
  """Sortear wi via sample_Li, depois pdf_Li, deve bater dentro de tolerância."""

  def test_sample_pdf_consistency(self):
    rng = random.Random(0xABCD)
    light = RectAreaLight(
      corner=glm.vec3(0, 5, 0),
      edge_u=glm.vec3(1, 0, 0),
      edge_v=glm.vec3(0, 0, 1),
      Le=glm.vec3(1, 1, 1),
    )
    ref = glm.vec3(0.5, 0, 0.5)
    n = 10_000
    ratios = []
    for _ in range(n):
      u = glm.vec2(rng.random(), rng.random())
      s = light.sample_Li(ref, u)
      if s is None:
        continue
      wi = s['wi']
      pdf_ret = s['pdf_solid_angle']
      pdf_q = light.pdf_Li(ref, wi)
      if pdf_q > 0.0:
        ratios.append(pdf_ret / pdf_q)
    self.assertGreater(len(ratios), 100, 'amostras validas insuficientes')
    mean = sum(ratios) / len(ratios)
    self.assertAlmostEqual(mean, 1.0, delta=0.05,
                           msg=f'consistencia sample/pdf falhou: mean={mean}')


# ===========================================================================
# 4. PointLight MIS
# ===========================================================================

class PointLightMISTest(unittest.TestCase):

  def test_is_delta_flag(self):
    self.assertTrue(PointLight.is_delta,
                    'PointLight deve marcar is_delta=True')

  def test_sample_Li_returns_infinite_pdf(self):
    pl = PointLight(pos=glm.vec3(0, 5, 0), power=glm.vec3(1, 1, 1))
    s = pl.sample_Li(glm.vec3(0, 0, 0), glm.vec2(0.5, 0.5))
    self.assertIs