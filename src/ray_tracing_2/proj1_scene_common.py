from __future__ import annotations

from dataclasses import dataclass

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.light import AmbientLight, AreaLight, AreaLightSamplingMode, PointLight
from ray_tracing_2.material import EmissiveMaterial, PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Instance, Sphere, TriangleMesh


@dataclass(frozen=True)
class Proj1CameraConfig:
  eye: tuple[float, float, float] = (2.775, 3.200, 12.775)
  center: tuple[float, float, float] = (2.775, 2.775, 2.775)
  up: tuple[float, float, float] = (0.0, 1.0, 0.0)
  fov: float = 50.0
  focal_distance: float = 1.0


CANONICAL_CAMERA = Proj1CameraConfig()
# Geometria canônica da luminária retangular. Os slides de luz de área (parte 2,
# pp. 14-23) descrevem a fonte por um ponto de origem p e duas arestas e_u/e_v.
# Mantemos essa parametrização em constantes para forçar coincidência entre a
# camada visual (painel emissivo) e a camada física (AreaLight).
# O ponto P fica ligeiramente abaixo do teto (y=5.55) para evitar interseção
# geométrica com a malha do teto, mantendo a fonte visível e funcionando bem.
REXT_AREA_LIGHT_P = glm.vec3(1.875, 5.15, 2.575)
REXT_AREA_LIGHT_EU = glm.vec3(1.80, 0.0, 0.0)
REXT_AREA_LIGHT_EV = glm.vec3(0.0, 0.0, 0.40)


def build_proj1_camera(width: int, height: int, config: Proj1CameraConfig = CANONICAL_CAMERA) -> Camera:
  return Camera(
    eye=glm.vec3(*config.eye),
    center=glm.vec3(*config.center),
    up=glm.vec3(*config.up),
    fov=config.fov,
    width=width,
    height=height,
    focal_distance=config.focal_distance,
  )


def _translate_rotate_y(tx: float, ty: float, tz: float, ry_deg: float = 0.0) -> glm.mat4:
  ry = glm.radians(ry_deg)
  c = glm.cos(ry)
  s = glm.sin(ry)

  matrix = glm.mat4(1.0)
  matrix[0][0] = c
  matrix[0][2] = -s
  matrix[1][1] = 1.0
  matrix[2][0] = s
  matrix[2][2] = c
  matrix[3][0] = tx
  matrix[3][1] = ty
  matrix[3][2] = tz
  return matrix


def build_block_material(kind: str):
  if kind == 'reflective':
    return ReflectiveMaterial(
      ambient=glm.vec3(0.03),
      diffuse=glm.vec3(0.25),
      specular=glm.vec3(0.05),
      shininess=32.0,
      reflectivity=glm.vec3(0.55),
    )
  if kind == 'transparent':
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


def white_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.08),
    diffuse=glm.vec3(0.75),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def red_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.08, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.05, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def green_wall_material() -> PhongMaterial:
  return PhongMaterial(
    ambient=glm.vec3(0.0, 0.08, 0.0),
    diffuse=glm.vec3(0.05, 0.75, 0.05),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )


def build_cornell_room(scene: Scene) -> None:
  white = white_wall_material()
  red = red_wall_material()
  green = green_wall_material()

  front_wall = Box(p_min=glm.vec3(-0.10, -0.10, -0.10), p_max=glm.vec3(5.65, 5.65, 0.0), material=white)
  left_wall = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(0.0, 5.55, 5.55), material=green)
  right_wall = Box(p_min=glm.vec3(5.55, -0.10, 0.0), p_max=glm.vec3(5.65, 5.55, 5.55), material=red)
  ceiling = Box(p_min=glm.vec3(0.0, 5.55, 0.0), p_max=glm.vec3(5.55, 5.65, 5.55), material=white)
  floor = Box(p_min=glm.vec3(-0.10, -0.10, 0.0), p_max=glm.vec3(5.65, 0.0, 5.55), material=white)
  scene.objects.extend([front_wall, left_wall, right_wall, ceiling, floor])


def build_proj1_scene(*, ambient: glm.vec3 = glm.vec3(0.18, 0.18, 0.18), max_depth: int = 4) -> Scene:
  return Scene(ambient_light=AmbientLight(ambient), max_depth=max_depth)


def add_ceiling_point_light(scene: Scene, *, power: glm.vec3 = glm.vec3(0.8, 0.8, 0.8), y: float = 5.45) -> None:
  scene.lights.append(PointLight(pos=glm.vec3(2.775, y, 2.775), power=power))


def add_req1_geometry_objects(scene: Scene) -> None:
  large_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 3.30, 1.65),
    material=build_block_material('opaque'),
  )
  small_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.65, 0.30),
    material=build_block_material('opaque'),
  )

  scene.objects.extend([
    Instance(large_box, _translate_rotate_y(0.65, 0.0, 1.30, ry_deg=22.5)),
    Instance(small_box, _translate_rotate_y(3.40, 0.0, 3.65, ry_deg=-18.0)),
    Sphere(center=glm.vec3(3.95, 0.65, 4.65), radius=0.65, material=build_block_material('opaque')),
  ])


def add_req2_light_probe_objects(scene: Scene) -> None:
  neutral = PhongMaterial(
    ambient=glm.vec3(0.03),
    diffuse=glm.vec3(0.70),
    specular=glm.vec3(0.15),
    shininess=20.0,
  )
  glossy = PhongMaterial(
    ambient=glm.vec3(0.02),
    diffuse=glm.vec3(0.35),
    specular=glm.vec3(0.55),
    shininess=96.0,
  )

  scene.objects.extend([
    Sphere(center=glm.vec3(1.45, 0.65, 4.10), radius=0.65, material=neutral),
    Sphere(center=glm.vec3(3.95, 0.65, 3.95), radius=0.65, material=glossy),
    Box(
      p_min=glm.vec3(2.25, 0.0, 1.75),
      p_max=glm.vec3(3.20, 1.65, 2.65),
      material=build_block_material('opaque'),
    ),
  ])


def add_req3_phong_objects(scene: Scene) -> None:
  matte_red = PhongMaterial(
    ambient=glm.vec3(0.06, 0.0, 0.0),
    diffuse=glm.vec3(0.75, 0.10, 0.10),
    specular=glm.vec3(0.05),
    shininess=16.0,
  )
  glossy_blue = PhongMaterial(
    ambient=glm.vec3(0.0, 0.02, 0.07),
    diffuse=glm.vec3(0.20, 0.25, 0.75),
    specular=glm.vec3(0.60),
    shininess=120.0,
  )

  low_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 1.10, 1.65),
    material=matte_red,
  )
  tall_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.10, 2.30, 1.10),
    material=glossy_blue,
  )

  scene.objects.extend([
    Instance(low_box, _translate_rotate_y(0.85, 0.0, 1.10, ry_deg=18.0)),
    Instance(tall_box, _translate_rotate_y(3.25, 0.0, 2.85, ry_deg=-16.0)),
    Sphere(center=glm.vec3(2.10, 0.62, 4.25), radius=0.62, material=matte_red),
  ])


def add_req2_point_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(1.25, 5.20, 1.35), power=glm.vec3(0.75, 0.68, 0.62)),
    PointLight(pos=glm.vec3(4.35, 4.85, 2.55), power=glm.vec3(0.45, 0.50, 0.65)),
    PointLight(pos=glm.vec3(2.75, 5.45, 4.85), power=glm.vec3(0.35, 0.35, 0.32)),
  ])


def add_req3_phong_shadow_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(2.85, 5.40, 2.35), power=glm.vec3(0.95, 0.95, 0.95)),
    PointLight(pos=glm.vec3(1.35, 3.55, 4.95), power=glm.vec3(0.25, 0.28, 0.32)),
  ])


def add_req4_sampling_objects(scene: Scene) -> None:
  edge_white = PhongMaterial(
    ambient=glm.vec3(0.02),
    diffuse=glm.vec3(0.85),
    specular=glm.vec3(0.02),
    shininess=8.0,
  )
  edge_black = PhongMaterial(
    ambient=glm.vec3(0.0),
    diffuse=glm.vec3(0.03),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )

  thin_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(2.80, 0.95, 0.12),
    material=edge_black,
  )
  tall_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(0.55, 2.60, 0.55),
    material=edge_white,
  )

  scene.objects.extend([
    Instance(thin_box, _translate_rotate_y(1.05, 0.0, 2.65, ry_deg=-24.0)),
    Instance(tall_box, _translate_rotate_y(3.75, 0.0, 1.85, ry_deg=9.0)),
    Sphere(center=glm.vec3(2.05, 0.45, 4.35), radius=0.45, material=edge_white),
    Sphere(center=glm.vec3(2.75, 0.45, 4.75), radius=0.45, material=edge_black),
  ])


def add_req4_sampling_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(2.75, 5.45, 2.75), power=glm.vec3(0.85, 0.85, 0.85)),
    PointLight(pos=glm.vec3(4.75, 4.35, 4.55), power=glm.vec3(0.20, 0.20, 0.20)),
  ])


# ---------------------------------------------------------------------------
# Requisitos de extensão
# ---------------------------------------------------------------------------

def _make_pyramid_vertices_faces() -> tuple[list[glm.vec3], list[tuple[int, int, int]]]:
  """Vértices e faces de uma pirâmide de base quadrada posicionada no fundo da sala."""
  vertices = [
    glm.vec3(0.75, 0.02, 4.55),
    glm.vec3(1.65, 0.02, 4.55),
    glm.vec3(1.65, 0.02, 5.45),
    glm.vec3(0.75, 0.02, 5.45),
    glm.vec3(1.20, 1.22, 5.00),
  ]
  faces = [
    (0, 1, 2), (0, 2, 3),
    (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4),
  ]
  return vertices, faces


def add_rext_triangle_objects(scene: Scene, *, use_bvh: bool = False) -> None:
  """R_ext triangulos: duas pirâmides TriangleMesh (Phong + reflexiva), com ou sem BVH local."""
  accelerator = 'bvh' if use_bvh else None
  vertices, faces = _make_pyramid_vertices_faces()

  phong_mat = PhongMaterial(
    ambient=glm.vec3(0.05, 0.03, 0.0),
    diffuse=glm.vec3(0.70, 0.50, 0.20),
    specular=glm.vec3(0.20),
    shininess=32.0,
  )
  reflective_mat = ReflectiveMaterial(
    ambient=glm.vec3(0.04),
    diffuse=glm.vec3(0.20),
    specular=glm.vec3(0.30),
    shininess=96.0,
    reflectivity=glm.vec3(0.78),
  )

  left_pyramid = TriangleMesh.from_vertices_faces(
    vertices, faces, phong_mat,
    name='phong_pyramid', accelerator=accelerator,
  )
  right_vertices = [glm.vec3(v.x + 2.6, v.y, v.z) for v in vertices]
  right_pyramid = TriangleMesh.from_vertices_faces(
    right_vertices, faces, reflective_mat,
    name='reflective_pyramid', accelerator=accelerator,
  )
  scene.objects.extend([left_pyramid, right_pyramid])


def add_rext_triangle_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(1.50, 5.35, 4.95), power=glm.vec3(0.90, 0.90, 0.90)),
    PointLight(pos=glm.vec3(4.10, 5.35, 4.95), power=glm.vec3(0.60, 0.65, 0.70)),
  ])


def add_rext_area_light_objects(scene: Scene) -> None:
  """R_ext luz de area: esferas e caixa Phong para observar sombras suaves."""
  neutral = PhongMaterial(
    ambient=glm.vec3(0.03),
    diffuse=glm.vec3(0.72),
    specular=glm.vec3(0.10),
    shininess=24.0,
  )
  scene.objects.extend([
    Sphere(center=glm.vec3(1.45, 0.65, 4.10), radius=0.65, material=neutral),
    Sphere(center=glm.vec3(3.95, 0.65, 3.95), radius=0.65, material=neutral),
    Box(
      p_min=glm.vec3(2.25, 0.0, 1.75),
      p_max=glm.vec3(3.20, 1.65, 2.65),
      material=neutral,
    ),
  ])


def add_rext_area_light(
  scene: Scene,
  *,
  sampling_mode: str = AreaLightSamplingMode.STRATIFIED.value,
  seed: int | None = None,
  samples_u: int = 4,
  samples_v: int = 4,
) -> None:
  """R_ext luz de area: retângulo no teto centrado na sala Cornell."""
  # A AreaLight usa decaimento 1/r^2, ao contrário da PointLight do enunciado.
  # Mantemos a potência elevada para compensar o decaimento com distância, mas
  # reduzimos a área emissiva para ~1/3 do tamanho anterior em cada eixo.
  # Isso deixa a luz mais compacta e direcional sem voltar ao regime escuro.
  # Luz retangular centrada na sala (2.775 em x e z).
  # e_u = 1.60 em X, e_v = 0.60 em Z → razão 2.7:1, claramente não quadrada.
  # O tamanho é suficiente para que a penumbra revele o formato retangular.
  scene.lights.append(
    AreaLight(
      p=REXT_AREA_LIGHT_P,
      e_u=REXT_AREA_LIGHT_EU,
      e_v=REXT_AREA_LIGHT_EV,
      power=glm.vec3(85.0, 85.0, 85.0),
      samples_u=samples_u,
      samples_v=samples_v,
      sampling_mode=sampling_mode,
      seed=seed,
    )
  )


def add_rext_area_light_emissive_panel(
  scene: Scene,
  *,
  emission: glm.vec3 = glm.vec3(1.0, 0.98, 0.95),
  thickness: float = 0.010,
  shadow_passthrough: bool = True,
) -> None:
  """Painel emissivo visível para a câmera, sobreposto à AreaLight."""
  # Os slides do projeto mantêm luzes e materiais como conceitos separados;
  # portanto, este painel não substitui a AreaLight. Seguimos aqui uma versão
  # simplificada da ideia de "área emissiva visível" discutida em PBRT 4e,
  # cap. 12.4, implementada localmente como geometria + emissão constante.
  panel_material = EmissiveMaterial(emission=emission, shadow_passthrough=shadow_passthrough)
  half_t = max(0.0005, thickness * 0.5)
  scene.objects.append(
    Box(
      p_min=glm.vec3(REXT_AREA_LIGHT_P.x, REXT_AREA_LIGHT_P.y - half_t, REXT_AREA_LIGHT_P.z),
      p_max=glm.vec3(
        REXT_AREA_LIGHT_P.x + REXT_AREA_LIGHT_EU.x,
        REXT_AREA_LIGHT_P.y + half_t,
        REXT_AREA_LIGHT_P.z + REXT_AREA_LIGHT_EV.z,
      ),
      material=panel_material,
    )
  )

  frame_material = PhongMaterial(
    ambient=glm.vec3(0.01),
    diffuse=glm.vec3(0.03),
    specular=glm.vec3(0.0),
    shininess=1.0,
  )
  border = 0.06
  bar_thickness = 0.03
  frame_height = 0.06
  x0 = REXT_AREA_LIGHT_P.x
  x1 = REXT_AREA_LIGHT_P.x + REXT_AREA_LIGHT_EU.x
  z0 = REXT_AREA_LIGHT_P.z
  z1 = REXT_AREA_LIGHT_P.z + REXT_AREA_LIGHT_EV.z
  y0 = REXT_AREA_LIGHT_P.y - (frame_height * 0.5)
  y1 = REXT_AREA_LIGHT_P.y + (frame_height * 0.5)

  scene.objects.extend([
    # Moldura escura puramente geométrica: ajuda a leitura perceptual do aspecto
    # retangular da luminária sem alterar a parametrização física da AreaLight.
    # Barra esquerda
    Box(
      p_min=glm.vec3(x0 - border, y0, z0 - border),
      p_max=glm.vec3(x0 - border + bar_thickness, y1, z1 + border),
      material=frame_material,
    ),
    # Barra direita
    Box(
      p_min=glm.vec3(x1 + border - bar_thickness, y0, z0 - border),
      p_max=glm.vec3(x1 + border, y1, z1 + border),
      material=frame_material,
    ),
    # Barra frontal
    Box(
      p_min=glm.vec3(x0 - border + bar_thickness, y0, z0 - border),
      p_max=glm.vec3(x1 + border - bar_thickness, y1, z0 - border + bar_thickness),
      material=frame_material,
    ),
    # Barra traseira
    Box(
      p_min=glm.vec3(x0 - border + bar_thickness, y0, z1 + border - bar_thickness),
      p_max=glm.vec3(x1 + border - bar_thickness, y1, z1 + border),
      material=frame_material,
    ),
  ])


def add_rext_reflective_objects(scene: Scene) -> None:
  """R_ext reflexivo: caixa e esfera com ReflectiveMaterial."""
  mirror_grey = ReflectiveMaterial(
    ambient=glm.vec3(0.04),
    diffuse=glm.vec3(0.35),
    specular=glm.vec3(0.40),
    shininess=64.0,
    reflectivity=glm.vec3(0.65),
  )
  mirror_red = ReflectiveMaterial(
    ambient=glm.vec3(0.06, 0.0, 0.0),
    diffuse=glm.vec3(0.60, 0.08, 0.08),
    specular=glm.vec3(0.30),
    shininess=80.0,
    reflectivity=glm.vec3(0.50),
  )
  tall_box = Box(
    p_min=glm.vec3(0.0, 0.0, 0.0),
    p_max=glm.vec3(1.65, 3.30, 1.65),
    material=mirror_grey,
  )
  scene.objects.extend([
    Instance(tall_box, _translate_rotate_y(0.65, 0.0, 1.30, ry_deg=22.5)),
    Sphere(center=glm.vec3(3.95, 0.65, 4.10), radius=0.65, material=mirror_red),
  ])


def add_rext_refractive_objects(scene: Scene) -> None:
  """R_ext refrativo: esfera e pirâmide com TransparentMaterial (Snell + Beer-Lambert)."""
  transparent_sphere = TransparentMaterial(ior=1.5, attenuation=glm.vec3(1.0))
  transparent_glass = TransparentMaterial(ior=1.5, attenuation=glm.vec3(0.88, 0.94, 0.98))
  vertices, faces = _make_pyramid_vertices_faces()
  pyramid = TriangleMesh.from_vertices_faces(
    vertices, faces, transparent_glass,
    name='transparent_pyramid',
  )
  scene.objects.extend([
    Sphere(center=glm.vec3(3.95, 0.65, 4.10), radius=0.65, material=transparent_sphere),
    pyramid,
  ])


def add_rext_reflective_refractive_lights(scene: Scene) -> None:
  scene.lights.extend([
    PointLight(pos=glm.vec3(2.775, 5.40, 2.775), power=glm.vec3(0.90, 0.90, 0.90)),
    PointLight(pos=glm.vec3(4.55, 4.85, 4.55), power=glm.vec3(0.30, 0.32, 0.35)),
  ])