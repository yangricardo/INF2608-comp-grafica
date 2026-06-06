"""Construção de bases ortonormais locais (Local Orthonormal Bases).

Referências:
- Slide 9 "Traçado de Caminhos II", seção HemisphereToGlobal
- PBRT 4e §3.3 "Vectors" (CoordinateSystem)
- Frisvad, J.R., "Building an Orthonormal Basis from a 3D Unit Vector Without Normalization",
  Journal of Graphics Tools 16(3):151–159, August 2012.
  DOI: 10.1080/2165347X.2012.689606
"""

from __future__ import annotations
from pyglm import glm


class ONB:
  """Base ortonormal local com x (tangent), y (bitangent) e z (normal).
  
  Construída via Frisvad branchless para eficiência. Permite converter
  direções em frame local ↔ frame global sem ramos de controle.
  """
  
  def __init__(self, normal: glm.vec3):
    """Inicializa ONB com normal como z.
    
    Args:
      normal: vetor normal (será normalizado internamente)
    """
    self.n = glm.normalize(glm.vec3(normal))
    self.t, self.b = frisvad_branchless(self.n)
  
  def local_to_global(self, local_dir: glm.vec3) -> glm.vec3:
    """Converte direção em frame local para frame global.
    
    Frame local: x=t, y=b, z=n
    
    Args:
      local_dir: direção em frame local (típ. z ≥ 0 para hemisfério cosseno)
    
    Returns:
      Direção em frame global
    """
    return self.t * local_dir.x + self.b * local_dir.y + self.n * local_dir.z
  
  def global_to_local(self, global_dir: glm.vec3) -> glm.vec3:
    """Converte direção em frame global para frame local.
    
    Args:
      global_dir: direção em frame global
    
    Returns:
      Direção em frame local
    """
    return glm.vec3(
      glm.dot(self.t, global_dir),
      glm.dot(self.b, global_dir),
      glm.dot(self.n, global_dir),
    )


def frisvad_branchless(n: glm.vec3) -> tuple[glm.vec3, glm.vec3]:
  """Constrói base ortonormal (t, b) com z=n, sem ramos.
  
  Implementação branchless de Frisvad (JGT 2012). Evita instabilidade numérica
  na geometria comparada a métodos com sqrt(1-nz²).
  
  Fórmula:
    se n.z < -0.9999999:
      t = (0, -1, 0)
      b = (-1, 0, 0)
    senão:
      a = 1 / (1 + n.z)
      k = -n.x * n.y * a
      t = (1 - n.x² * a, k, -n.x)
      b = (k, 1 - n.y² * a, -n.y)
  
  Args:
    n: normal (esperado normalizado)
  
  Returns:
    Tupla (t, b) onde (t, b, n) forma base ortonormal dextrógira.
  
  Referência:
    Frisvad, J.R., "Building an Orthonormal Basis from a 3D Unit Vector
    Without Normalization", JGT 16(3):151–159, 2012.
    DOI: 10.1080/2165347X.2012.689606
  """
  # Ref: PBRT 4e §3.3 Vectors; Frisvad JGT 2012
  
  if n.z < -0.9999999:
    # Caso singular: normal aponta para baixo (-z); usar vetores alinhados com eixos
    t = glm.vec3(0.0, -1.0, 0.0)
    b = glm.vec3(-1.0, 0.0, 0.0)
  else:
    # Caso genérico: fórmula sem ramos
    a = 1.0 / (1.0 + n.z)
    k = -n.x * n.y * a
    t = glm.vec3(1.0 - n.x * n.x * a, k, -n.x)
    b = glm.vec3(k, 1.0 - n.y * n.y * a, -n.y)
  
  # Normalizar para garantir unitários (Frisvad garante quase-norma 1, mas numérica)
  t = glm.normalize(t)
  b = glm.normalize(b)
  
  return t, b
