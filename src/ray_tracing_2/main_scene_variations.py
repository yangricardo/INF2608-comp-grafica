"""
Gera variações simples de cena reutilizando o renderizador existente.

Este script monta várias cenas mudando posições/raios da(s) esfera(s) e do plano,
executa o loop de render (idêntico ao usado em `src/main.py`) e salva imagens
com nomes descritivos. Serve para testar rapidamente o efeito de translações
de objetos e pequenas mudanças de geometria, sem alterar o núcleo do
traçador de raios.

Contribui com o que está documentado no README: mostra como construir cenas
com `Scene`, `Shape`, `Material` e `Light`, e como gerar imagens via `Camera`.
"""
from __future__ import annotations
import os

from pyglm import glm
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Sphere, Plane
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.light import PointLight
from ray_tracing_2.film import Film
import argparse
from typing import Optional


def render_scene_with_film(scene: Scene, cam: Camera, W: int, H: int, out_name: str, samples_per_pixel: int = 16, sampling_mode: str = 'jittered', seed: Optional[int] = None, gamma_fix: bool = False):
  """Renderiza a cena usando a classe `Film` e salva como PNG.

  Comentário (PT): expõe parâmetros de amostragem por pixel (AA) conforme
  Slide 4, p. 25-29. `samples_per_pixel`, `sampling_mode` e `seed` controlam
  o comportamento de anti-aliasing e a reprodutibilidade.
  """
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  from ray_tracing_2.render import Render
  r = Render()
  base = os.path.splitext(os.path.basename(out_name))[0]
  # Render infere automaticamente os props a partir da `Scene`.
  r.render(scene=scene, cam=cam, width=W, height=H, name=base, samples_per_pixel=samples_per_pixel, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)


def build_scene(sx: float, sy: float, sr: float, plane_y: float = -1.0) -> Scene:
  """Constrói uma cena simples com um plano e uma esfera.

  Os parâmetros controlam a posição (`sx`, `sy`) e o raio (`sr`) da esfera,
  além da altura do plano (`plane_y`). A função retorna uma instância de
  `Scene` já populada com materiais e duas luzes de teste.
  """
  scene = Scene()

  # Slide 4, p. 41-49: materiais com componentes pequenos para evidenciar sombra e brilho.
  mat_floor = PhongMaterial(ambient=glm.vec3(0.02, 0.02, 0.02),
                            diffuse=glm.vec3(0.6, 0.6, 0.6),
                            specular=glm.vec3(0.3, 0.3, 0.3),
                            shininess=10)
  mat_sphere = PhongMaterial(ambient=glm.vec3(0.01, 0.01, 0.02),
                             diffuse=glm.vec3(0.1, 0.3, 0.8),
                             specular=glm.vec3(1, 1, 1),
                             shininess=100)

  # Slide 4, p. 11-18: plano e esfera são os objetos geométricos usados nas variações.
  scene.objects.append(Plane(pos=glm.vec3(0, plane_y, 0), normal=glm.vec3(0, 1, 0), material=mat_floor))
  scene.objects.append(Sphere(center=glm.vec3(sx, sy, 0), radius=sr, material=mat_sphere))

  # Slide 4, p. 40: duas luzes pontuais ajudam a mostrar atenuação, sombra e especular.
  scene.lights.append(PointLight(pos=glm.vec3(5, 5, 5), power=glm.vec3(150, 150, 150)))
  scene.lights.append(PointLight(pos=glm.vec3(-5, 5, 3), power=glm.vec3(80, 80, 120)))

  return scene


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--width', type=int, default=400)
  parser.add_argument('--height', type=int, default=300)
  parser.add_argument('--spp', type=int, default=16, help='Samples per pixel (AA)')
  parser.add_argument('--sampling_mode', choices=['jittered', 'stratified'], default='jittered')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()

  W, H = args.width, args.height
  # Slide 4, p. 14 e p. 29: câmera fixa para comparar as variações de geometria.
  cam = Camera(eye=glm.vec3(0, 0, 5), center=glm.vec3(0, 0, 0), up=glm.vec3(0, 1, 0), fov=45, width=W, height=H)

  # Pequena grade de parâmetros para gerar um conjunto controlado de imagens.
  xs = [-1.5, 0.0, 1.5]
  ys = [0.0, 0.5]
  rs = [0.5, 1.0]

  idx = 0
  for x in xs:
    for y in ys:
      for r in rs:
        # Monta a cena com os parâmetros atuais e renderiza uma nova imagem.
        scene = build_scene(sx=x, sy=y, sr=r, plane_y=-1.0)
        out_name = f"render_var_{idx:02d}_x{x}_y{y}_r{r}.png"
        render_scene_with_film(scene=scene, cam=cam, W=W, H=H, out_name=out_name, samples_per_pixel=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)
        idx += 1

  print("All renders complete.")


if __name__ == "__main__":
  main()
