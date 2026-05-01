"""
Entrada principal para uma cena inspirada na Cornell Box com uma pirâmide
reflexiva ao lado da esfera.

A cena reaproveita o mesmo núcleo físico do projeto: câmera pinhole, paredes
em `Box`, iluminação ambiente, fonte pontual e materiais recursivos nos blocos.
O diferencial é a presença de uma pirâmide triangularizada visível no volume
útil da caixa, para demonstrar convivência entre geometria triangular, reflexão
e refração sem alterar o núcleo do traçador.
"""

from __future__ import annotations

import argparse

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, AreaLight, AreaLightSamplingMode, PointLight
from ray_tracing_2.material import PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Sphere, TriangleMesh, Translate, Rotate


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


def render(width: int = 800,
           height: int = 600,
           spp: int = 1,
           sampling_mode: str = 'jittered',
           light_sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
           seed: int | None = None,
           gamma_fix: bool = False,
           max_depth: int = 10,
           small_block_material: str = 'reflective',
           large_block_material: str = 'transparent'):
  """Renderiza a cena Cornell com uma pirâmide reflexiva e salva `render_final.png`."""
  # Slide 4, p. 24-29: define a resolução do filme e a câmera pinhole da cena.
  W, H = width, height
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
  green_phong_material = PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  small_block_surface = _build_block_material(small_block_material)
  large_block_surface = _build_block_material(large_block_material)
  pyramid_material = ReflectiveMaterial(
    ambient=glm.vec3(0.04),
    diffuse=glm.vec3(0.20),
    specular=glm.vec3(0.30),
    shininess=96.0,
    reflectivity=glm.vec3(0.78),
  )

  # Cria objetos da cena: paredes, blocos, pirâmide e luz pontual.
  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white_phong_material)
  left_wall = Box(p_min=glm.vec3(-0.1, -0.1, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green_phong_material)
  right_wall = Box(p_min=glm.vec3(5.55, -0.1, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red_phong_material)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white_phong_material)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white_phong_material)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])

  # Blocos instanciados conforme proj1-exemplo.pdf, agora com materiais
  # explícitos para comparar reflexão e transparência com a pirâmide lateral.
  small_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 1.65, 0.30), material=small_block_surface)
  small_block = Rotate(angle_deg=-18.0, x=0, y=1, z=0, shape=small_block)
  small_block = Translate(3.40, 1.2, 5.65, small_block)
  large_block = Box(p_min=glm.vec3(0, 0, 0), p_max=glm.vec3(1.65, 3.30, 1.65), material=large_block_surface)
  large_block = Rotate(angle_deg=22.5, x=0, y=1, z=0, shape=large_block)
  large_block = Translate(0.65, 0.0, 1.30, large_block)
  scene.objects.extend([small_block, large_block])

  # Pirâmide triangularizada ao lado da esfera. A base fica levemente acima
  # do piso para evitar coplanaridade numérica com o plano do chão.
  pyramid_vertices = [
    glm.vec3(0.75, 0.02, 4.55),
    glm.vec3(1.65, 0.02, 4.55),
    glm.vec3(1.65, 0.02, 5.45),
    glm.vec3(0.75, 0.02, 5.45),
    glm.vec3(1.20, 1.22, 5.00),
  ]
  pyramid_faces = [
    (0, 1, 2),
    (0, 2, 3),
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4),
  ]
  pyramid = TriangleMesh.from_vertices_faces(
    pyramid_vertices,
    pyramid_faces,
    pyramid_material,
    name='reflective_pyramid',
  )
  scene.objects.append(pyramid)

  red_sphere = Sphere(center=glm.vec3(2.5, 0.5, 5.0), radius=0.6, material=green_phong_material)
  scene.objects.append(red_sphere)

  # Luminária: proj1-exemplo.pdf — Sphere(vec3(2.775,5.55,2.775), 0.1)
  # Aqui a esfera visível da luminária usa PhongMaterial com componente ambiente
  # alta para funcionar como marcador emissivo aparente; a iluminação efetiva da
  # cena continua vindo das luzes explícitas adicionadas logo abaixo.
  lamp_material = PhongMaterial(
    diffuse=glm.vec3(0.0),
    specular=glm.vec3(1),
    shininess=0,
    ambient=glm.vec3(1.0),
  )
  lamp_sphere = Sphere(center=glm.vec3(2.775, 5.45, 2.775), radius=0.1, material=lamp_material)
  scene.objects.append(lamp_sphere)

  # Luz de área atrás da câmera para iluminar a cena pela direção do observador.
  camera_fill_light = AreaLight(
    p=glm.vec3(1.25, 1.95, 13.45),
    e_u=glm.vec3(3.05, 0.0, 0.0),
    e_v=glm.vec3(0.0, 2.35, 0.0),
    power=glm.vec3(80.0, 80.0, 80.0),
    samples_u=2,
    samples_v=2,
    sampling_mode=light_sampling_mode,
    seed=seed,
  )
  scene.lights.append(camera_fill_light)
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5, 2.775), power=glm.vec3(0.7, 0.7, 0.7)))
  # # 5.tracado_de_raios2.pdf - p.35: area light no teto, centralizada entre as paredes laterais.
  # # Inset de ~10% em cada lado do volume útil do box: x/z de 0.555 até 5.0.
  # area_light_origin = glm.vec3(0.555, 5.54, 0.555)
  # area_light_e_u = glm.vec3(4.44, 0.0, 0.0)
  # area_light_e_v = glm.vec3(0.0, 0.0, 4.44)
  # scene.lights.append(
  #   AreaLight(
  #     p=area_light_origin,
  #     e_u=area_light_e_u,
  #     e_v=area_light_e_v,
  #     power=glm.vec3(0.7, 0.7, 0.7),
  #     samples_u=2,
  #     samples_v=2,
  #     seed=seed,
  #   )
  # )

  # Fonte de luz conforme proj1-exemplo.pdf
  scene.lights.append(PointLight(pos=glm.vec3(2.775, 5.55, 2.775), power=glm.vec3(0.7, 0.7, 0.7)))

  # Slide 4, p. 24-29: usa a classe Render para criar saída e markdown
  r = Render()
  r.render(scene=scene, cam=cam, width=W, height=H, name='cornell_box_pyramid', samples_per_pixel=spp, sampling_mode=sampling_mode, seed=seed, gamma_fix=gamma_fix)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--width', type=int, default=800, help='Image width in pixels')
  parser.add_argument('--height', type=int, default=600, help='Image height in pixels')
  parser.add_argument('--spp', type=int, default=1, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--light_sampling_mode', choices=[m.value for m in AreaLightSamplingMode], default=AreaLightSamplingMode.STRATIFIED.value, help='Sampling mode for area lights in the scene')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', '--gama_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  parser.add_argument('--max_depth', type=int, default=4, help='Maximum recursion depth for reflection/refraction')
  parser.add_argument('--small_block_material', choices=['opaque', 'reflective', 'transparent'], default='reflective', help='Material model used by the small block')
  parser.add_argument('--large_block_material', choices=['opaque', 'reflective', 'transparent'], default='transparent', help='Material model used by the large block')
  args = parser.parse_args()
  render(
    width=args.width,
    height=args.height,
    spp=args.spp,
    sampling_mode=args.sampling_mode,
    light_sampling_mode=args.light_sampling_mode,
    seed=args.seed,
    gamma_fix=args.gamma_fix,
    max_depth=args.max_depth,
    small_block_material=args.small_block_material,
    large_block_material=args.large_block_material,
  )