"""Padrões bidimensionais compartilhados pelas extensões do Slide 5.

As funções deste módulo geram coordenadas no domínio normalizado ``[0,1]^2``.
Em `film.py`, esse domínio representa a área do pixel para anti-aliasing
(`5.tracado_de_raios2.pdf`, pp. 4-9). Em `light.py`, ele representa a
parametrização local da fonte retangular antes do mapeamento afim para o
emissor (`5.tracado_de_raios2.pdf`, pp. 14-23).
"""

from __future__ import annotations

import random


def uniform_samples_2d(sample_count: int, rng: random.Random) -> list[tuple[float, float]]:
  """Retorna amostras uniformes independentes no quadrado unitário.

  Este é o padrão aleatório puro usado na formulação de Monte Carlo do
  Slide 5, reproduzindo a construção canônica ``xi in [0,1)`` tanto para o
  jitter subpixel (`5.tracado_de_raios2.pdf`, pp. 4-9) quanto para a luz de
  área (`5.tracado_de_raios2.pdf`, pp. 14-23).
  """
  count = max(0, int(sample_count))
  return [(rng.random(), rng.random()) for _ in range(count)]


def regular_grid_samples_2d(samples_u: int, samples_v: int) -> list[tuple[float, float]]:
  """Retorna amostras determinísticas no centro de uma grade regular ``samples_u x samples_v``.

  Geometricamente, cada par corresponde ao centro de uma subcélula no domínio
  normalizado do emissor. Isso materializa o padrão regular discutido para luz
  de área no Slide 5 (`5.tracado_de_raios2.pdf`, pp. 14-23).
  """
  count_u = max(1, int(samples_u))
  count_v = max(1, int(samples_v))
  return [
    ((iu + 0.5) / count_u, (iv + 0.5) / count_v)
    for iu in range(count_u)
    for iv in range(count_v)
  ]


def stratified_grid_samples_2d(samples_u: int, samples_v: int, rng: random.Random) -> list[tuple[float, float]]:
  """Retorna uma amostra com jitter por célula de uma grade regular no quadrado unitário.

  O domínio preserva a partição regular ``samples_u x samples_v``, mas a posição
  da amostra é aleatorizada dentro de cada célula. Este é o padrão estratificado
  usado para reduzir variância sem perder cobertura espacial, em linha com o
  Slide 5 (`5.tracado_de_raios2.pdf`, pp. 4-9 e 14-23).
  """
  count_u = max(1, int(samples_u))
  count_v = max(1, int(samples_v))
  return [
    ((iu + rng.random()) / count_u, (iv + rng.random()) / count_v)
    for iu in range(count_u)
    for iv in range(count_v)
  ]