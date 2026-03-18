import glm
from typing import Optional
from phong_material import PhongMaterial
from point_light import PointLight
class Hit:
  def __init__(self, t=float('inf')):
    self.t = t
    self.pos = glm.vec3(0)
    self.normal = glm.vec3(0)
    self.material: Optional[PhongMaterial] = None
    self.light: Optional[PointLight] = None