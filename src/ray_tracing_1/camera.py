import glm
from .ray import Ray

class Camera:
  def __init__(self, eye: glm.vec3, center: glm.vec3, up: glm.vec3, fov: float, width: int, height: int):
    self.eye = glm.vec3(eye)
    self.center = glm.vec3(center)
    self.up = glm.vec3(up)
    self.angle = fov
    self.inv_view = glm.inverse(glm.lookAt(self.eye, glm.vec3(center), glm.vec3(up)))
    self.aspect = width / height
    self.fov_tan = glm.tan(glm.radians(fov) / 2.0)

  def generate_ray(self, xn: float, yn: float) -> Ray:
    # [cite: 4, 29]
    dv = self.fov_tan
    du = dv * self.aspect
    p_cam = glm.vec4(-du + 2.0 * du * xn, dv - 2.0 * dv * yn, -1.0, 1.0)
    p_world = self.inv_view * p_cam
    return Ray(self.eye, glm.vec3(p_world) - self.eye)