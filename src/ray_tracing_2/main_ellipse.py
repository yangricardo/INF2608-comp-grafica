"""
Entrada principal para demonstrar instanciação de objetos com `Instance`.

Este arquivo replica a cena simples de `main.py`, mas transforma a esfera
unitária em um elipsoide por meio de uma matriz de escala não uniforme.
Isso mostra, na prática, a ideia dos slides 9 a 13 sobre instanciação.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import PointLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Instance, Plane, Sphere


def render(spp: int = 1, sampling_mode: str = "jittered", seed: int | None = None, gamma_fix: bool = False):
  """Renderiza um elipsoide instanciado a partir de uma esfera unitária."""
  W, H = 400, 300
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45.0, width=W, height=H)

  mat_red = PhongMaterial(
    ambient=glm.vec3(0.1, 0, 0),
    diffuse=glm.vec3(0.7, 0, 0),
    specular=glm.vec3(1, 1, 1),
    shininess=50.0,
  )
  mat_gray = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  scene = Scene()
  base_sphere = Sphere(center=glm.vec3(0, 0, 0), radius=1.0, material=mat_red)
  scale_matrix = glm.scale(glm.mat4(1.0), glm.vec3(0.5, 0.95, 0.5))
  ellipsoid = Instance(base_sphere, scale_matrix)

  scene.objects.append(ellipsoid)
  scene.objects.append(Plane(pos=glm.vec3(0, -1.0, 0), normal=glm.vec3(0, 1, 0), material=mat_gray))
  scene.lights.append(PointLight(pos=glm.vec3(0, 5, 0), power=glm.vec3(150.0)))

  r = Render()
  r.render(
    scene=scene,
    cam=cam,
    width=W,
    height=H,
    name="main_ellipse",
    samples_per_pixel=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--spp", type=int, default=1, help="Samples per pixel (anti-aliasing)")
  parser.add_argument("--sampling_mode", choices=[m.value for m in SamplingMode], default="jittered", help="Sampling mode for AA")
  parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
  parser.add_argument("--gamma_fix", action="store_true", default=False, help="Apply gamma correction to final image (gamma_fix)")
  args = parser.parse_args()
  render(spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)