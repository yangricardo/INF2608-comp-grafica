"""
Entrada principal: monta uma cena simples (esfera + luz) e executa o
loop de renderização usando a implementação de traçado de raios do projeto.

Este arquivo demonstra o fluxo básico descrito no README: construir uma
`Camera`, popular uma `Scene` com `Shape` e `Material`, e iterar sobre os
pixels gerando raios com `Camera.generate_ray` para avaliar cor via
`Scene.trace_ray`.
"""

from __future__ import annotations

from pyglm import glm
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Plane, Rotate, Sphere, Translate
from ray_tracing_2.material import PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.light import AmbientLight, AreaLight, PointLight
from ray_tracing_2.film import Film, SamplingMode
from ray_tracing_2.render import Render
import argparse



def _build_block_material(kind: str):
  if kind == 'reflective':
    return ReflectiveMaterial(
      ambient=glm.vec3(0.03),
      diffuse=glm.vec3(0.25),
      specular=glm.vec3(0.05),
      shininess=32.0,
      reflectivity=glm.vec3(0.55),
    )
  if kind == 'transparent':
    # 5.tracado_de_raios2.pdf - p.36: cena com vidro (a = (0.8, 0.9, 0.8))
    return TransparentMaterial(
      ior=1.5,
      attenuation=glm.vec3(0.8, 0.9, 0.8),
    )
  return PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.5),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )



def render(spp: int = 1,
           sampling_mode: str = 'jittered',
           seed: int | None = None,
           gamma_fix: bool = False,
           max_depth: int = 10,
           small_block_material: str = 'opaque',
           large_block_material: str = 'opaque'):
  """Renderiza a cena de exemplo e salva `render_final.png`.

  O procedimento segue o pipeline principal:
  1. Cria `Camera` com parâmetros de pinhole.
  2. Monta `Scene` com objetos e luzes.
  3. Para cada pixel, gera um raio primário e avalia a cor com
     `Scene.trace_ray`.
  """
  # Slide 4, p. 24-29: define a resolução do filme e a câmera pinhole da cena.
  W, H = 800, 600
  # Cria a câmera (proj1-exemplo.pdf)
  cam = Camera(eye=glm.vec3(2.775, 3.200, 12.775), center=glm.vec3(2.775, 2.775, 2.775), up=glm.vec3(0, 1, 0), fov=50, width=W, height=H, focal_distance=1.0)
  
  # Cria cena com luz ambiente
  scene = Scene(ambient_light=AmbientLight(0.3, 0.3, 0.3), max_depth=max_depth)
  
  white_phong_material = PhongMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  red_phong_material = PhongMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  reflexive_red_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  green_phong_material = PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  reflexive_green_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  reflexive_white_phong_material = ReflectiveMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.05),
    shininess=32.0,
    reflectivity=glm.vec3(0.55),
  )
  transparent_mat = TransparentMaterial(ior=1.5, attenuation=glm.vec3(1))
  small_block_surface = _build_block_material(small_block_material)
  large_block_surface = _build_block_material(large_block_material)

  # Cria objetos da cena: paredes, blocos e luz pontual.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=reflexive_white_phong_material)
  left_wall = Box(p_min=glm.vec3(-0.1, -0.1, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green_phong_material)
  right_wall = Box(p_min=glm.vec3(5.55, -0.1, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red_phong_material)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=reflexive_white_phong_material)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white_phong_material)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])

  # Blocos instanciados conforme proj1-exemplo.pdf
  small_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 1.65, 0.30), material=transparent_mat)
  small_block = Rotate(angle_deg=-18.0, x=0, y=1, z=0, shape=small_block)
  small_block = Translate(3.40, 1.2, 5.65, small_block)
  large_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 3.30, 1.65), material=red_phong_material)
  large_block = Rotate(angle_deg=22.5, x=0, y=1, z=0, shape=large_block)
  large_block = Translate(0.65, 0.0, 1.30, large_block)
  scene.objects.extend([small_block, large_block])
  red_sphere = Sphere(center=glm.vec3(2.5, 0.5, 5.0), radius=0.6, material=green_phong_material)
  scene.objects.append(red_sphere)
  
  # Luminária: proj1-exemplo.pdf — Sphere(vec3(2.775,5.55,2.775), 0.1)
  # Usa TransparentMaterial(ior=1.5, attenuation=1.0) para que os raios de sombra
  # passem sem atenuação (shadow_transmittance retorna vec3(1.0)) enquanto
  # permanece visível para raios primários como uma esfera de vidro.
  lamp_material = TransparentMaterial(ior=0.5, attenuation=glm.vec3(0.3))
  lamp_sphere = Sphere(center=glm.vec3(2.775, 5.55, 2.775), radius=0.1, material=lamp_material)
  scene.objects.append(lamp_sphere)
  # Fonte de luz conforme proj1-exemplo.pdf
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5.35, 2.775), power=glm.vec3(0.7, 0.7, 0.7)))  
  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  r.render(scene=scene, cam=cam, width=W, height=H, name='cornell_box', samples_per_pixel=spp, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', '--gama_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  parser.add_argument('--max_depth', type=int, default=4, help='Maximum recursion depth for reflection/refraction')
  parser.add_argument('--small_block_material', choices=['opaque', 'reflective', 'transparent'], default='opaque', help='Material model used by the small block')
  parser.add_argument('--large_block_material', choices=['opaque', 'reflective', 'transparent'], default='opaque', help='Material model used by the large block')
  args = parser.parse_args()
  render(
    spp=args.spp,
    sampling_mode=args.sampling_mode,
    seed=args.seed,
    gamma_fix=args.gamma_fix,
    max_depth=args.max_depth,
    small_block_material=args.small_block_material,
    large_block_material=args.large_block_material,
  )