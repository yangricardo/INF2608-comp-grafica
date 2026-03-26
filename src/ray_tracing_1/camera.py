from __future__ import annotations

import glm
from ray_tracing_1.ray import Ray

class Camera:
  def __init__(self, eye: glm.vec3, center: glm.vec3, up: glm.vec3, fov: float, width: int, height: int):
    self.eye = glm.vec3(eye)
    self.center = glm.vec3(center)
    self.up = glm.vec3(up)
    self.angle = fov
    # Slide 4, p. 14: a câmera pinhole é definida por olho, alvo e vetor up.
    self.inv_view = glm.inverse(glm.lookAt(self.eye, glm.vec3(center), glm.vec3(up)))
    # Slide 4, p. 25-29: a proporção e o FOV definem a janela de projeção do raio primário.
    self.aspect = width / height
    self.fov_tan = glm.tan(glm.radians(fov) / 2.0)

  def generate_ray(self, xn: float, yn: float) -> Ray:
    # Slide 4, p. 29: converte o ponto normalizado do pixel em ponto no plano da câmera.
    dv = self.fov_tan
    du = dv * self.aspect
    p_cam = glm.vec4(-du + 2.0 * du * xn, dv - 2.0 * dv * yn, -1.0, 1.0)
    # Slide 4, p. 29: transforma o ponto do espaço da câmera para o espaço do mundo.
    p_world = self.inv_view * p_cam
    return Ray(self.eye, glm.vec3(p_world) - self.eye)