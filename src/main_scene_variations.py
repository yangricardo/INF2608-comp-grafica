import numpy as np
from PIL import Image
import glm
from ray import Ray
from camera import Camera
from scene import Scene
from shape import Sphere, Plane
from material import PhongMaterial
from light import PointLight


def render_scene(scene: Scene, cam: Camera, W: int, H: int, out_name: str):
  img = np.zeros((H, W, 3), dtype=np.uint8)
  for j in range(H):
    for i in range(W):
      xn, yn = (i + 0.5) / W, (j + 0.5) / H
      ray = cam.generate_ray(xn, yn)
      color = glm.clamp(scene.trace_ray(ray), 0, 1)
      img[j, i] = (color * 255)
  Image.fromarray(img).save(out_name)
  print(f"Saved {out_name}")


def build_scene(sx: float, sy: float, sr: float, plane_y: float = -1.0) -> Scene:
  scene = Scene()

  # Materials
  mat_floor = PhongMaterial(ambient=glm.vec3(0.02, 0.02, 0.02), diffuse=glm.vec3(0.6, 0.6, 0.6), specular=glm.vec3(0.3, 0.3, 0.3), shininess=10)
  mat_sphere = PhongMaterial(ambient=glm.vec3(0.01, 0.01, 0.02), diffuse=glm.vec3(0.1, 0.3, 0.8), specular=glm.vec3(1, 1, 1), shininess=100)

  # Objects
  scene.objects.append(Plane(pos=glm.vec3(0, plane_y, 0), normal=glm.vec3(0, 1, 0), material=mat_floor))
  scene.objects.append(Sphere(center=glm.vec3(sx, sy, 0), radius=sr, material=mat_sphere))

  # Lights
  scene.lights.append(PointLight(pos=glm.vec3(5, 5, 5), power=glm.vec3(150, 150, 150)))
  scene.lights.append(PointLight(pos=glm.vec3(-5, 5, 3), power=glm.vec3(80, 80, 120)))

  return scene


def main():
  W, H = 400, 300
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45, width=W, height=H)

  # Parameter grids (kept small to run quickly)
  xs = [-1.5, 0.0, 1.5]
  ys = [0.0, 0.5]
  rs = [0.5, 1.0]

  idx = 0
  for x in xs:
    for y in ys:
      for r in rs:
        scene = build_scene(sx=x, sy=y, sr=r, plane_y=-1.0)
        out_name = f"render_var_{idx:02d}_x{x}_y{y}_r{r}.png"
        render_scene(scene=scene, cam=cam, W=W, H=H, out_name=out_name)
        idx += 1

  print("All renders complete.")


if __name__ == "__main__":
  main()
