import numpy as np
from PIL import Image
import glm
from ray import Ray
from camera import Camera
from scene import Scene
from shape import Sphere
from material import PhongMaterial
from light import PointLight


def render():
  W, H = 400, 300
  cam = Camera(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0), 45, W, H)
  scene = Scene()
  
  # Objetos e Luzes
  mat_red = PhongMaterial(glm.vec3(0.1, 0, 0), glm.vec3(0.7, 0, 0), glm.vec3(1, 1, 1), 50)
  scene.objects.append(Sphere(glm.vec3(0, 0, 0), 1.0, mat_red))
  scene.lights.append(PointLight(glm.vec3(5, 5, 5), glm.vec3(150, 150, 150)))

  # Render Loop [cite: 4, 35]
  img = np.zeros((H, W, 3), dtype=np.uint8)
  for j in range(H):
    for i in range(W):
      xn, yn = (i + 0.5) / W, (j + 0.5) / H
      ray = cam.generate_ray(xn, yn)
      color = glm.clamp(scene.trace_ray(ray), 0, 1)
      img[j, i] = (color * 255)

  Image.fromarray(img).save("render_final.png")
  print("Renderização concluída. Imagem salva como 'render_final.png'.")

if __name__ == "__main__":
    render()