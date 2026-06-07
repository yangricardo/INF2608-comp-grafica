"""Interface base para luzes no path tracing.

Referência:
- PBRT 4e §12 "Light Sources"
"""

from __future__ import annotations
from pyglm import glm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..hit import Hit
  from ..scene import Scene


class Light:
  """Interface base para todas as luzes.

  Luzes amostram sua emissão em um ponto de referência e retornam
  PDF em ângulo sólido (para conversão de área).

  Atributos de classe:
    is_delta: True se a luz é uma distribuição delta (PointLight).
      Nesse caso, pdf_solid_angle = +inf e o integrador deve
      curto-circuitar o cálculo MIS (peso = 1.0), em linha com
      PBRT 4e §12.1.1 "Point Lights".
  """

  is_delta: bool = False

  def contains(self, hit) -> bool:
    """Retorna True se o hit pertence a esta luz (para o shadow-ray de NEE).

    Quando a luz NEE coincide geometricamente com um painel emissor
    (EmissiveBSDF), o shadow ray não deve ocluir o caminho — caso
    contrário, o termo NEE é contabilizado em dobro (uma vez pelo
    NEE e outra pela emissão direta). O default é False: luzes que
    não representam uma primitiva da cena (PointLight, RectAreaLight
    sem malha correspondente) ficam transparentes para o shadow ray.

    Subclasses que mapeiam para uma primitiva devem sobrescrever.

    Ref: PBRT 4e §13.4 "A Better Path Tracer" — "Light Leaks".
    """
    return False

  def sample_Li(self, ref_point: glm.vec3, u: glm.vec2) -> dict | None:
    """Amostra um ponto na superfície da luz.

    Args:
      ref_point: ponto de referência na cena de onde a luz é vista
      u: variáveis aleatórias 2D uniformes em [0,1)²

    Returns:
      Dict com:
        - 'p_on_light': ponto amostrado na superfície da luz
        - 'wi': direção normalizada de ref_point para p_on_light
        - 'Li': radiância Le emitida
        - 'pdf_solid_angle': PDF em ângulo sólido (para importância)
        - 'distance': distância de ref_point a p_on_light
        - 'cos_at_light': cosseno do ângulo entre normal luz e -wi
      Retorna None se amostra for inválida.
    """
    raise NotImplementedError("Light subclasses must implement sample_Li()")

  def pdf_Li(self, ref_point: glm.vec3, wi: glm.vec3) -> float:
    """Calcula PDF em ângulo sólido (para MIS).

    Args:
      ref_point: ponto de referência
      wi: direção normalizada

    Returns:
      PDF dessa direção em ângulo sólido
    """
    raise NotImplementedError("Light subclasses must implement pdf_Li()")

  def radiance(self, scene: "Scene", hit: "Hit") -> tuple[glm.vec3, glm.vec3]:
    """Interface legada: retorna radiância incidente e direção.

    Stub padrão — PointLight e AreaLight sobrescrevem com implementação real.
    Presente na base para type-safety quando scene.lights é list[Light].
    """
    return glm.vec3(0.0), glm.vec3(0.0, 0.0, 1.0)

  def sample_radiance(self, scene: "Scene", hit: "Hit") -> list[tuple[glm.vec3, glm.vec3]]:
    """Interface legada: amostra múltiplos pontos para penumbra.

    Stub padrão — delega para radiance(). AreaLight sobrescreve com grid de amostras.
    Slide 5, pp. 14-23; Slide 4, pp. 40-41.
    """
    return [self.radiance(scene, hit)]
