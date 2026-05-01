from __future__ import annotations

from pyglm import glm
from ray_tracing_2.ray import Ray

class Camera:
  def __init__(self, eye: glm.vec3, center: glm.vec3, up: glm.vec3, fov: float, width: int, height: int, focal_distance: float = 1.0):
    self.eye = glm.vec3(eye)
    self.center = glm.vec3(center)
    self.up = glm.vec3(up)
    self.angle = fov
    # Neste projeto, focal_distance controla apenas a distância geométrica do
    # plano de projeção no modelo pinhole. Ele altera a abertura angular
    # efetiva junto com o FOV, mas não modela foco físico, lente fina nem
    # profundidade de campo como em câmeras baseadas em abertura.
    self.focal_distance = float(focal_distance)
    # Slide 4, pp. 19-23: a câmera pinhole é definida por olho, alvo e vetor up,
    # isto é, por uma base ortonormal que fixa a mudança de coordenadas entre
    # espaço da câmera e espaço do mundo.
    self.inv_view = glm.inverse(glm.lookAt(self.eye, glm.vec3(center), glm.vec3(up)))
    # Slide 4, pp. 24-29: a proporção e o FOV definem a janela de projeção do
    # raio primário por semelhança de triângulos.
    self.aspect = width / height
    self.fov_tan = glm.tan(glm.radians(fov) / 2.0)
    # TODO(camera): se o projeto evoluir para lente fina, separar explicitamente
    # a distância do plano de projeção do parâmetro de foco físico/apertura.

  def generate_ray(self, xn: float, yn: float) -> Ray:
    # Slide 4, p. 29: converte a amostra normalizada do pixel em um ponto no
    # plano da câmera; a direção do raio nasce do olho e atravessa esse ponto.
    # Fórmulas do slide: Δv = f * tan(θ/2) e Δu = Δv * (w/h).
    dv = self.fov_tan * self.focal_distance
    du = dv * self.aspect
    p_cam = glm.vec4(-du + 2.0 * du * xn, dv - 2.0 * dv * yn, -self.focal_distance, 1.0)
    # Slide 4, p. 29: transforma o ponto do espaço da câmera para o espaço do mundo.
    p_world = self.inv_view * p_cam
    return Ray(self.eye, glm.vec3(p_world) - self.eye)