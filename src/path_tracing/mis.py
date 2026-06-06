"""Múltipla Importância de Amostragem (Multiple Importance Sampling).

Referências:
- Slide 9 "Traçado de Caminhos II", seção MIS
- PBRT 4e §2.2.3 "Multiple Importance Sampling"
  https://pbr-book.org/4ed/Monte_Carlo_Integration/Improving_Efficiency.html#MultipleImportanceSampling
- Veach, E. & Guibas, L.J., "Optimally Combining Sampling Techniques for
  Monte Carlo Rendering", SIGGRAPH 1995, pp. 419–428.
  DOI: 10.1145/218380.218498
"""

from __future__ import annotations
from pyglm import glm


def balance_heuristic(
  n_a: int,
  pdf_a: float,
  n_b: int,
  pdf_b: float,
) -> float:
  """Heurística de balanço para MIS (Veach & Guibas, β=1).
  
  Eq. 2.14 (PBRT 4e §2.2.3):
    w_a = (n_a * p_a) / (n_a * p_a + n_b * p_b)
  
  Simples, menor variância em casos balanceados, mais sensível a picos extremos.
  
  Args:
    n_a: número de amostras da estratégia A (típ. 1)
    pdf_a: PDF da estratégia A no ponto amostrado
    n_b: número de amostras da estratégia B (típ. 1)
    pdf_b: PDF da estratégia B no ponto amostrado
  
  Returns:
    Peso w_a ∈ [0, 1] para a amostra A
  """
  # Ref: PBRT 4e §2.2.3; Veach & Guibas SIGGRAPH 1995, Eq. 2.14
  denom = n_a * pdf_a + n_b * pdf_b
  if denom <= 0.0:
    return 0.0
  return (n_a * pdf_a) / denom


def power_heuristic(
  n_a: int,
  pdf_a: float,
  n_b: int,
  pdf_b: float,
  beta: float = 2.0,
) -> float:
  """Heurística de potência para MIS (Veach & Guibas, β=2 padrão).
  
  Eq. 2.15 (PBRT 4e §2.2.3):
    w_a = (n_a * p_a)^β / ((n_a * p_a)^β + (n_b * p_b)^β)
  
  Com β=2 (padrão), reduz mais variância que balance heuristic em casos
  com distribuições desequilibradas, especialmente útil para BSDF + NEE.
  
  Args:
    n_a: número de amostras da estratégia A (típ. 1)
    pdf_a: PDF da estratégia A no ponto amostrado
    n_b: número de amostras da estratégia B (típ. 1)
    pdf_b: PDF da estratégia B no ponto amostrado
    beta: expoente (β=2 padrão; β=1 é balance heuristic)
  
  Returns:
    Peso w_a ∈ [0, 1] para a amostra A
  
  Referência:
    PBRT 4e §2.2.3, p. 103: "In practice, the power heuristic often reduces
    variance even further."
  """
  # Ref: PBRT 4e §2.2.3, Eq. 2.15; Veach & Guibas SIGGRAPH 1995
  denom_a = (n_a * pdf_a) ** beta
  denom_b = (n_b * pdf_b) ** beta
  denom = denom_a + denom_b
  
  if denom <= 0.0:
    return 0.0
  return denom_a / denom
