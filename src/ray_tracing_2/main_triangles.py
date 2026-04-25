"""Entrada principal para demonstrar geometria representada por triângulos.

O arquivo carrega uma especificação JSON da cena, incluindo a malha triangulada,
e a renderiza com a infraestrutura existente de câmera, luz e materiais.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.film import SamplingMode
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.render import Render
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Instance, Plane, Sphere, TriangleMesh


def _vec3(values) -> glm.vec3:
  return glm.vec3(float(values[0]), float(values[1]), float(values[2]))


def _material_from_spec(spec: dict | None, default_ambient, default_diffuse, default_specular, default_shininess: float) -> PhongMaterial:
  if spec is None:
    spec = {}
  ambient = spec.get('ambient', list(default_ambient))
  diffuse = spec.get('diffuse', list(default_diffuse))
  specular = spec.get('specular', list(default_specular))
  shininess = spec.get('shininess', default_shininess)
  # Slide 4, p. 41-49: o mesmo modelo de Phong é usado para todos os objetos da cena.
  return PhongMaterial(ambient=_vec3(ambient), diffuse=_vec3(diffuse), specular=_vec3(specular), shininess=float(shininess))


def _triangle_mesh_from_spec(spec: dict) -> TriangleMesh:
  # Slide 4, p. 35 e p. 47-48: a malha JSON é convertida para triângulos e usa o mesmo closest-hit das demais primitivas.
  vertices = [_vec3(vertex) for vertex in spec.get('vertices', [])]
  faces: list[tuple[int, int, int]] = []

  for raw_face in spec.get('faces', []):
    indices = [int(index) - 1 for index in raw_face]
    if len(indices) < 3:
      continue

    anchor = indices[0]
    for i in range(1, len(indices) - 1):
      faces.append((anchor, indices[i], indices[i + 1]))

  material = _material_from_spec(
    spec.get('material'),
    default_ambient=(0.1, 0.0, 0.0),
    default_diffuse=(0.7, 0.0, 0.0),
    default_specular=(1.0, 1.0, 1.0),
    default_shininess=50.0,
  )
  return TriangleMesh.from_vertices_faces(vertices, faces, material, name=spec.get('name'))


def _mesh_transform_from_spec(spec: dict | None) -> glm.mat4:
  # Slide 5, p. 12-13: a malha é instanciada com translação, rotação e escala.
  matrix = glm.mat4(1.0)
  if spec is None:
    return matrix

  translate = spec.get('translate')
  if translate is not None:
    matrix = glm.translate(matrix, _vec3(translate))

  rotate_y = spec.get('rotate_y')
  if rotate_y is not None:
    matrix = matrix * glm.rotate(glm.mat4(1.0), glm.radians(float(rotate_y)), glm.vec3(0.0, 1.0, 0.0))

  scale = spec.get('scale')
  if scale is not None:
    matrix = matrix * glm.scale(glm.mat4(1.0), _vec3(scale))

  return glm.mat4(matrix)


def render(
  scene_path: str | Path | None = None,
  width: int | None = None,
  height: int | None = None,
  spp: int = 16,
  sampling_mode: str = 'jittered',
  seed: int | None = None,
  gamma_fix: bool = False,
):
  default_scene = Path(__file__).resolve().parents[2] / 'inputs' / 'triangle_pyramid.json'
  spec_path = Path(scene_path) if scene_path is not None else default_scene
  spec = json.loads(spec_path.read_text(encoding='utf-8'))

  W = int(width if width is not None else spec.get('width', 800))
  H = int(height if height is not None else spec.get('height', 600))

  # Slide 4, p. 24-29: câmera pinhole e enquadramento da cena de teste.
  camera_spec = spec.get('camera') or {}
  cam = Camera(
    eye=_vec3(camera_spec.get('eye', [0.0, 0.55, 4.35])),
    center=_vec3(camera_spec.get('center', [0.0, 0.05, 0.0])),
    up=_vec3(camera_spec.get('up', [0.0, 1.0, 0.0])),
    fov=float(camera_spec.get('fov', 45.0)),
    width=W,
    height=H,
  )

  # Slide 4, p. 41-49: reduzimos a ambientação para que a sombra não seja lavada.
  scene = Scene(
    ambient_light=AmbientLight(_vec3(spec.get('ambient_light', [0.12, 0.12, 0.12]))),
    max_depth=int(spec.get('max_depth', 4)),
  )
  if 'background_color' in spec:
    scene.background_color = _vec3(spec['background_color'])

  # Slide 4, p. 41-49: Phong avermelhado para destacar a malha, como na cena da esfera.
  mesh_specs = []
  if spec.get('mesh') is not None:
    mesh_specs.append(spec['mesh'])
  mesh_specs.extend(spec.get('meshes', []))
  for mesh_spec in mesh_specs:
    mesh = _triangle_mesh_from_spec(mesh_spec)
    mesh = Instance(mesh, _mesh_transform_from_spec(mesh_spec.get('transform')))
    scene.objects.append(mesh)

  # Slide 4, p. 11-18 e p. 41-49: um segundo objeto com material distinto ajuda a comparar cor e sombra.
  # Posicionamos a esfera à frente e à direita da malha para que a luz gere sombra visível sobre os triângulos.
  for sphere_spec in spec.get('spheres', []):
    sphere_material = _material_from_spec(
      sphere_spec.get('material'),
      default_ambient=(0.0, 0.0, 0.1),
      default_diffuse=(0.0, 0.0, 0.7),
      default_specular=(1.0, 1.0, 1.0),
      default_shininess=40.0,
    )
    scene.objects.append(
      Sphere(
        center=_vec3(sphere_spec.get('center', [1.05, 0.55, 0.75])),
        radius=float(sphere_spec.get('radius', 0.34)),
        material=sphere_material,
      )
    )

  plane_spec = spec.get('plane')
  if plane_spec is not None:
    floor_material = _material_from_spec(
      plane_spec.get('material'),
      default_ambient=(0.08, 0.08, 0.08),
      default_diffuse=(0.4, 0.4, 0.4),
      default_specular=(0.0, 0.0, 0.0),
      default_shininess=1.0,
    )
    scene.objects.append(Plane(pos=glm.vec3(0.0, float(plane_spec.get('y', -1.0)), 0.0), normal=glm.vec3(0, 1, 0), material=floor_material))

  # Slide 4, p. 40: luz fora do eixo para que a sombra não fique colada ao objeto.
  for light_spec in spec.get('lights', []):
    scene.lights.append(PointLight(pos=_vec3(light_spec.get('pos', [2.4, 4.9, 3.4])), power=_vec3(light_spec.get('power', [110.0, 110.0, 110.0]))))

  r = Render()
  r.render(
    scene=scene,
    cam=cam,
    width=W,
    height=H,
    name='main_triangles',
    samples_per_pixel=spp,
    sampling_mode=sampling_mode,
    seed=seed,
    gamma_fix=gamma_fix,
  )


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--scene', '--json', type=str, default=None, help='Path to JSON scene specification')
  parser.add_argument('--width', type=int, default=None, help='Image width in pixels (defaults to JSON value)')
  parser.add_argument('--height', type=int, default=None, help='Image height in pixels (defaults to JSON value)')
  parser.add_argument('--spp', type=int, default=16, help='Samples per pixel (anti-aliasing)')
  parser.add_argument('--sampling_mode', choices=[m.value for m in SamplingMode], default='jittered', help='Sampling mode for AA')
  parser.add_argument('--seed', type=int, default=None, help='RNG seed for reproducibility')
  parser.add_argument('--gamma_fix', '--gama_fix', action='store_true', default=False, help='Apply gamma correction to final image (gamma_fix)')
  args = parser.parse_args()
  render(scene_path=args.scene, width=args.width, height=args.height, spp=args.spp, sampling_mode=args.sampling_mode, seed=args.seed, gamma_fix=args.gamma_fix)