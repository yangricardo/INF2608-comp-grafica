from __future__ import annotations

# cspell:words pyglm Phong

import json
from dataclasses import dataclass, field
from typing import Any

from pyglm import glm

from ray_tracing_2.camera import Camera
from ray_tracing_2.light import AreaLight, PointLight
from ray_tracing_2.material import EmissiveMaterial, PhongMaterial, ReflectiveMaterial, TransparentMaterial
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Instance, Plane, Rotate, Sphere, Translate, Triangle, TriangleMesh


Vec3Data = list[float]
Mat4RowsData = list[list[float]]


def _vec3_to_list(value: Any) -> Vec3Data | Any:
  try:
    return [float(value.x), float(value.y), float(value.z)]
  except Exception:
    return value


def _list_to_vec3(values: Vec3Data | None, *, field_name: str) -> glm.vec3:
  if values is None:
    raise ValueError(f'Missing vec3 field: {field_name}')
  if len(values) != 3:
    raise ValueError(f'Expected 3 components in {field_name}, got {len(values)}')
  return glm.vec3(float(values[0]), float(values[1]), float(values[2]))


def _optional_list_to_vec3(values: Vec3Data | None, *, field_name: str) -> glm.vec3 | None:
  if values is None:
    return None
  return _list_to_vec3(values, field_name=field_name)


def _mat4_to_rows(matrix: glm.mat4 | None) -> Mat4RowsData | None:
  if matrix is None:
    return None
  return [
    [float(matrix[col][row]) for col in range(4)]
    for row in range(4)
  ]


def _rows_to_mat4(rows: Mat4RowsData | None, *, field_name: str) -> glm.mat4:
  if rows is None:
    raise ValueError(f'Missing mat4 field: {field_name}')
  if len(rows) != 4 or any(len(row) != 4 for row in rows):
    raise ValueError(f'Expected a 4x4 matrix in {field_name}')

  matrix = glm.mat4(1.0)
  for row_idx in range(4):
    for col_idx in range(4):
      matrix[col_idx][row_idx] = float(rows[row_idx][col_idx])
  return matrix


def _shape_chain(obj: Any) -> list[str]:
  chain: list[str] = []
  current = obj
  while current is not None:
    chain.append(type(current).__name__)
    current = getattr(current, 'shape', None)
  return chain


def _extract_material(obj: Any):
  current = obj
  while current is not None:
    material = getattr(current, 'material', None)
    if material is not None:
      return material
    current = getattr(current, 'shape', None)
  return None


def _extract_attr(obj: Any, attr_name: str):
  current = obj
  while current is not None:
    if hasattr(current, attr_name):
      return getattr(current, attr_name)
    current = getattr(current, 'shape', None)
  return None


@dataclass(slots=True)
class MaterialSnapshot:
  type: str
  emission: Vec3Data | None = None
  shadow_passthrough: bool | None = None
  ambient: Vec3Data | None = None
  diffuse: Vec3Data | None = None
  specular: Vec3Data | None = None
  shininess: float | None = None
  reflectivity: Vec3Data | None = None
  attenuation: Vec3Data | None = None
  transmission: Vec3Data | None = None
  reflection_tint: Vec3Data | None = None
  ior: float | None = None
  opacity: float | None = None

  @classmethod
  def from_runtime(cls, material: Any) -> MaterialSnapshot:
    return cls(
      type=type(material).__name__,
      emission=_vec3_to_list(getattr(material, 'emission', None)),
      shadow_passthrough=bool(getattr(material, 'shadow_passthrough')) if hasattr(material, 'shadow_passthrough') else None,
      ambient=_vec3_to_list(getattr(material, 'm_amb', None)),
      diffuse=_vec3_to_list(getattr(material, 'm_dif', None)),
      specular=_vec3_to_list(getattr(material, 'm_spe', None)),
      shininess=float(getattr(material, 'shi', 0.0)) if hasattr(material, 'shi') else None,
      reflectivity=_vec3_to_list(getattr(material, 'reflectivity', None)),
      attenuation=_vec3_to_list(getattr(material, 'attenuation', None)),
      transmission=_vec3_to_list(getattr(material, 'transmission', None)),
      reflection_tint=_vec3_to_list(getattr(material, 'reflection_tint', None)),
      ior=float(getattr(material, 'ior')) if hasattr(material, 'ior') else None,
      opacity=float(getattr(material, 'opacity')) if hasattr(material, 'opacity') else None,
    )

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> MaterialSnapshot:
    return cls(
      type=str(data['type']),
      emission=data.get('emission'),
      shadow_passthrough=bool(data['shadow_passthrough']) if data.get('shadow_passthrough') is not None else None,
      ambient=data.get('ambient'),
      diffuse=data.get('diffuse'),
      specular=data.get('specular'),
      shininess=float(data['shininess']) if data.get('shininess') is not None else None,
      reflectivity=data.get('reflectivity'),
      attenuation=data.get('attenuation'),
      transmission=data.get('transmission'),
      reflection_tint=data.get('reflection_tint'),
      ior=float(data['ior']) if data.get('ior') is not None else None,
      opacity=float(data['opacity']) if data.get('opacity') is not None else None,
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {'type': self.type}
    for key in (
      'emission',
      'shadow_passthrough',
      'ambient',
      'diffuse',
      'specular',
      'shininess',
      'reflectivity',
      'attenuation',
      'transmission',
      'reflection_tint',
      'ior',
      'opacity',
    ):
      value = getattr(self, key)
      if value is not None:
        data[key] = value
    return data

  def to_runtime(self):
    ambient = _list_to_vec3(self.ambient or [0.0, 0.0, 0.0], field_name='material.ambient')
    diffuse = _list_to_vec3(self.diffuse or [0.0, 0.0, 0.0], field_name='material.diffuse')
    specular = _list_to_vec3(self.specular or [0.0, 0.0, 0.0], field_name='material.specular')
    shininess = 1.0 if self.shininess is None else float(self.shininess)

    if self.type == 'EmissiveMaterial':
      emission = _list_to_vec3(self.emission or [0.0, 0.0, 0.0], field_name='material.emission')
      return EmissiveMaterial(
        emission=emission,
        shadow_passthrough=True if self.shadow_passthrough is None else bool(self.shadow_passthrough),
      )

    if self.type == 'ReflectiveMaterial':
      reflectivity = _list_to_vec3(self.reflectivity or [0.5, 0.5, 0.5], field_name='material.reflectivity')
      return ReflectiveMaterial(
        ambient=ambient,
        diffuse=diffuse,
        specular=specular,
        shininess=shininess,
        reflectivity=reflectivity,
      )

    if self.type == 'TransparentMaterial':
      attenuation = _list_to_vec3(self.attenuation or [1.0, 1.0, 1.0], field_name='material.attenuation')
      return TransparentMaterial(
        ambient=ambient,
        diffuse=diffuse,
        specular=specular,
        shininess=shininess,
        ior=1.5 if self.ior is None else float(self.ior),
        attenuation=attenuation,
        transmission=_optional_list_to_vec3(self.transmission, field_name='material.transmission'),
        reflection_tint=_optional_list_to_vec3(self.reflection_tint, field_name='material.reflection_tint'),
        opacity=0.0 if self.opacity is None else float(self.opacity),
      )

    if self.type == 'PhongMaterial':
      return PhongMaterial(
        ambient=ambient,
        diffuse=diffuse,
        specular=specular,
        shininess=shininess,
      )

    raise ValueError(f'Unsupported material snapshot type: {self.type}')


@dataclass(slots=True)
class ShapeSnapshot:
  type: str
  material: MaterialSnapshot | None = None
  shape: ShapeSnapshot | None = None
  shape_chain: list[str] | None = None
  center: Vec3Data | None = None
  pos: Vec3Data | None = None
  normal: Vec3Data | None = None
  v0: Vec3Data | None = None
  v1: Vec3Data | None = None
  v2: Vec3Data | None = None
  geo_normal: Vec3Data | None = None
  radius: float | None = None
  p_min: Vec3Data | None = None
  p_max: Vec3Data | None = None
  vertices: list[Vec3Data] | None = None
  faces: list[list[int]] | None = None
  name: str | None = None
  accelerator: str | None = None
  bvh_leaf_size: int | None = None
  vertex_count: int | None = None
  face_count: int | None = None
  triangle_count: int | None = None
  bvh_node_count: int | None = None
  bvh_leaf_count: int | None = None
  bvh_max_depth: int | None = None
  matrix: Mat4RowsData | None = None

  @classmethod
  def from_runtime(cls, obj: Any) -> ShapeSnapshot:
    type_name = type(obj).__name__
    material = _extract_material(obj)
    snapshot = cls(
      type=type_name,
      material=MaterialSnapshot.from_runtime(material) if material is not None else None,
      shape_chain=_shape_chain(obj),
    )

    if isinstance(obj, Sphere):
      snapshot.center = _vec3_to_list(obj.center)
      snapshot.radius = float(obj.radius)
      return snapshot

    if isinstance(obj, Plane):
      snapshot.pos = _vec3_to_list(obj.pos)
      snapshot.normal = _vec3_to_list(obj.normal)
      return snapshot

    if isinstance(obj, Box):
      snapshot.p_min = _vec3_to_list(obj.p_min)
      snapshot.p_max = _vec3_to_list(obj.p_max)
      return snapshot

    if isinstance(obj, Triangle):
      snapshot.v0 = _vec3_to_list(obj.v0)
      snapshot.v1 = _vec3_to_list(obj.v1)
      snapshot.v2 = _vec3_to_list(obj.v2)
      snapshot.geo_normal = _vec3_to_list(obj.geo_normal)
      return snapshot

    if isinstance(obj, TriangleMesh):
      snapshot.vertices = [_vec3_to_list(vertex) for vertex in obj.vertices]
      snapshot.faces = [list(face) for face in obj.faces]
      snapshot.name = obj.name
      snapshot.accelerator = obj.accelerator
      snapshot.bvh_leaf_size = obj.bvh_leaf_size
      snapshot.vertex_count = len(obj.vertices)
      snapshot.face_count = len(obj.faces)
      snapshot.triangle_count = len(obj.triangles)
      snapshot.bvh_node_count = getattr(obj, 'bvh_node_count', None)
      snapshot.bvh_leaf_count = getattr(obj, 'bvh_leaf_count', None)
      snapshot.bvh_max_depth = getattr(obj, 'bvh_max_depth', None)
      return snapshot

    if isinstance(obj, Instance):
      snapshot.matrix = _mat4_to_rows(obj.m)
      snapshot.shape = cls.from_runtime(obj.shape)
      vertices = _extract_attr(obj, 'vertices')
      faces = _extract_attr(obj, 'faces')
      triangles = _extract_attr(obj, 'triangles')
      accelerator = _extract_attr(obj, 'accelerator')
      bvh_leaf_size = _extract_attr(obj, 'bvh_leaf_size')
      bvh_node_count = _extract_attr(obj, 'bvh_node_count')
      bvh_leaf_count = _extract_attr(obj, 'bvh_leaf_count')
      bvh_max_depth = _extract_attr(obj, 'bvh_max_depth')
      if vertices is not None:
        snapshot.vertex_count = len(vertices)
      if faces is not None:
        snapshot.face_count = len(faces)
      if triangles is not None:
        snapshot.triangle_count = len(triangles)
      if accelerator is not None:
        snapshot.accelerator = accelerator
      if bvh_leaf_size is not None:
        snapshot.bvh_leaf_size = int(bvh_leaf_size)
      if bvh_node_count is not None:
        snapshot.bvh_node_count = int(bvh_node_count)
      if bvh_leaf_count is not None:
        snapshot.bvh_leaf_count = int(bvh_leaf_count)
      if bvh_max_depth is not None:
        snapshot.bvh_max_depth = int(bvh_max_depth)
      return snapshot

    raise ValueError(f'Unsupported shape snapshot type: {type_name}')

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> ShapeSnapshot:
    return cls(
      type=str(data['type']),
      material=MaterialSnapshot.from_dict(data['material']) if data.get('material') is not None else None,
      shape=cls.from_dict(data['shape']) if data.get('shape') is not None else None,
      shape_chain=list(data['shape_chain']) if data.get('shape_chain') is not None else None,
      center=data.get('center'),
      pos=data.get('pos'),
      normal=data.get('normal'),
      v0=data.get('v0'),
      v1=data.get('v1'),
      v2=data.get('v2'),
      geo_normal=data.get('geo_normal'),
      radius=float(data['radius']) if data.get('radius') is not None else None,
      p_min=data.get('p_min'),
      p_max=data.get('p_max'),
      vertices=data.get('vertices'),
      faces=data.get('faces'),
      name=data.get('name'),
      accelerator=data.get('accelerator'),
      bvh_leaf_size=int(data['bvh_leaf_size']) if data.get('bvh_leaf_size') is not None else None,
      vertex_count=int(data['vertex_count']) if data.get('vertex_count') is not None else None,
      face_count=int(data['face_count']) if data.get('face_count') is not None else None,
      triangle_count=int(data['triangle_count']) if data.get('triangle_count') is not None else None,
      bvh_node_count=int(data['bvh_node_count']) if data.get('bvh_node_count') is not None else None,
      bvh_leaf_count=int(data['bvh_leaf_count']) if data.get('bvh_leaf_count') is not None else None,
      bvh_max_depth=int(data['bvh_max_depth']) if data.get('bvh_max_depth') is not None else None,
      matrix=data.get('matrix'),
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {'type': self.type}
    if self.material is not None:
      data['material'] = self.material.to_dict()
    if self.shape is not None:
      data['shape'] = self.shape.to_dict()
    for key in (
      'shape_chain',
      'center',
      'pos',
      'normal',
      'v0',
      'v1',
      'v2',
      'geo_normal',
      'radius',
      'p_min',
      'p_max',
      'vertices',
      'faces',
      'name',
      'accelerator',
      'bvh_leaf_size',
      'vertex_count',
      'face_count',
      'triangle_count',
      'bvh_node_count',
      'bvh_leaf_count',
      'bvh_max_depth',
      'matrix',
    ):
      value = getattr(self, key)
      if value is not None:
        data[key] = value
    return data

  def to_runtime(self):
    if self.type == 'Sphere':
      if self.material is None:
        raise ValueError('Sphere snapshot is missing material')
      return Sphere(
        center=_list_to_vec3(self.center, field_name='shape.center'),
        radius=float(self.radius) if self.radius is not None else 1.0,
        material=self.material.to_runtime(),
      )

    if self.type == 'Plane':
      if self.material is None:
        raise ValueError('Plane snapshot is missing material')
      return Plane(
        pos=_list_to_vec3(self.pos, field_name='shape.pos'),
        normal=_list_to_vec3(self.normal, field_name='shape.normal'),
        material=self.material.to_runtime(),
      )

    if self.type == 'Box':
      if self.material is None:
        raise ValueError('Box snapshot is missing material')
      return Box(
        p_min=_list_to_vec3(self.p_min, field_name='shape.p_min'),
        p_max=_list_to_vec3(self.p_max, field_name='shape.p_max'),
        material=self.material.to_runtime(),
      )

    if self.type == 'Triangle':
      if self.material is None:
        raise ValueError('Triangle snapshot is missing material')
      return Triangle(
        _list_to_vec3(self.v0, field_name='shape.v0'),
        _list_to_vec3(self.v1, field_name='shape.v1'),
        _list_to_vec3(self.v2, field_name='shape.v2'),
        self.material.to_runtime(),
      )

    if self.type == 'TriangleMesh':
      if self.material is None:
        raise ValueError('TriangleMesh snapshot is missing material')
      vertices = [_list_to_vec3(vertex, field_name='shape.vertices') for vertex in (self.vertices or [])]
      faces: list[tuple[int, int, int]] = [
        (int(face[0]), int(face[1]), int(face[2]))
        for face in (self.faces or [])
      ]
      return TriangleMesh.from_vertices_faces(
        vertices=vertices,
        faces=faces,
        material=self.material.to_runtime(),
        name=self.name,
        accelerator=self.accelerator,
        bvh_leaf_size=4 if self.bvh_leaf_size is None else int(self.bvh_leaf_size),
      )

    if self.type in {'Instance', 'Translate', 'Rotate'}:
      if self.shape is None:
        raise ValueError(f'{self.type} snapshot is missing nested shape')
      matrix = _rows_to_mat4(self.matrix, field_name='shape.matrix')
      return Instance(self.shape.to_runtime(), matrix)

    raise ValueError(f'Unsupported shape snapshot type: {self.type}')


@dataclass(slots=True)
class LightSnapshot:
  type: str
  pos: Vec3Data | None = None
  power: Vec3Data | None = None
  p: Vec3Data | None = None
  e_u: Vec3Data | None = None
  e_v: Vec3Data | None = None
  samples_u: int | None = None
  samples_v: int | None = None
  light_sampling_mode: str | None = None

  @classmethod
  def from_runtime(cls, light: Any) -> LightSnapshot:
    snapshot = cls(
      type=type(light).__name__,
      pos=_vec3_to_list(getattr(light, 'pos', None)),
      power=_vec3_to_list(getattr(light, 'power', None)),
    )
    if isinstance(light, AreaLight):
      snapshot.p = _vec3_to_list(light.p)
      snapshot.e_u = _vec3_to_list(light.e_u)
      snapshot.e_v = _vec3_to_list(light.e_v)
      snapshot.samples_u = int(light.samples_u)
      snapshot.samples_v = int(light.samples_v)
      snapshot.light_sampling_mode = light.sampling_mode.value
    return snapshot

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> LightSnapshot:
    return cls(
      type=str(data['type']),
      pos=data.get('pos'),
      power=data.get('power'),
      p=data.get('p'),
      e_u=data.get('e_u'),
      e_v=data.get('e_v'),
      samples_u=int(data['samples_u']) if data.get('samples_u') is not None else None,
      samples_v=int(data['samples_v']) if data.get('samples_v') is not None else None,
      light_sampling_mode=data.get('light_sampling_mode'),
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {'type': self.type}
    for key in ('pos', 'power', 'p', 'e_u', 'e_v', 'samples_u', 'samples_v', 'light_sampling_mode'):
      value = getattr(self, key)
      if value is not None:
        data[key] = value
    return data

  def to_runtime(self):
    if self.type == 'PointLight':
      return PointLight(
        pos=_list_to_vec3(self.pos, field_name='light.pos'),
        power=_list_to_vec3(self.power, field_name='light.power'),
      )

    if self.type == 'AreaLight':
      origin = self.p if self.p is not None else self.pos
      return AreaLight(
        p=_list_to_vec3(origin, field_name='light.p'),
        e_u=_list_to_vec3(self.e_u, field_name='light.e_u'),
        e_v=_list_to_vec3(self.e_v, field_name='light.e_v'),
        power=_list_to_vec3(self.power, field_name='light.power'),
        samples_u=4 if self.samples_u is None else int(self.samples_u),
        samples_v=4 if self.samples_v is None else int(self.samples_v),
        sampling_mode='stratified' if self.light_sampling_mode is None else self.light_sampling_mode,
      )

    raise ValueError(f'Unsupported light snapshot type: {self.type}')


@dataclass(slots=True)
class RenderSettingsSnapshot:
  name: str
  width: int
  height: int
  samples_per_pixel: int
  sampling_mode: str
  seed: int | None = None
  gamma_fix: bool = False
  render_time_seconds: float | None = None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> RenderSettingsSnapshot:
    return cls(
      name=str(data['name']),
      width=int(data['width']),
      height=int(data['height']),
      samples_per_pixel=int(data['samples_per_pixel']),
      sampling_mode=str(data['sampling_mode']),
      seed=int(data['seed']) if data.get('seed') is not None else None,
      gamma_fix=bool(data.get('gamma_fix', False)),
      render_time_seconds=float(data['render_time_seconds']) if data.get('render_time_seconds') is not None else None,
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {
      'name': self.name,
      'width': int(self.width),
      'height': int(self.height),
      'samples_per_pixel': int(self.samples_per_pixel),
      'sampling_mode': self.sampling_mode,
      'seed': self.seed,
      'gamma_fix': bool(self.gamma_fix),
    }
    if self.render_time_seconds is not None:
      data['render_time_seconds'] = float(self.render_time_seconds)
    return data


@dataclass(slots=True)
class SceneSettingsSnapshot:
  ambient_light: Vec3Data | None = None
  background_color: Vec3Data | None = None
  max_depth: int | None = None
  ray_epsilon: float | None = None

  @classmethod
  def from_runtime(cls, scene: Scene) -> SceneSettingsSnapshot:
    return cls(
      ambient_light=_vec3_to_list(getattr(scene, 'ambient_light', None)),
      background_color=_vec3_to_list(getattr(scene, 'background_color', None)),
      max_depth=int(scene.max_depth) if hasattr(scene, 'max_depth') else None,
      ray_epsilon=float(scene.ray_epsilon) if hasattr(scene, 'ray_epsilon') else None,
    )

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> SceneSettingsSnapshot:
    return cls(
      ambient_light=data.get('ambient_light'),
      background_color=data.get('background_color'),
      max_depth=int(data['max_depth']) if data.get('max_depth') is not None else None,
      ray_epsilon=float(data['ray_epsilon']) if data.get('ray_epsilon') is not None else None,
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key in ('ambient_light', 'background_color', 'max_depth', 'ray_epsilon'):
      value = getattr(self, key)
      if value is not None:
        data[key] = value
    return data


@dataclass(slots=True)
class CameraSnapshot:
  eye: Vec3Data | None = None
  center: Vec3Data | None = None
  up: Vec3Data | None = None
  fov: float | None = None
  focal_distance: float | None = None
  aspect: float | None = None

  @classmethod
  def from_runtime(cls, cam: Camera) -> CameraSnapshot:
    return cls(
      eye=_vec3_to_list(getattr(cam, 'eye', None)),
      center=_vec3_to_list(getattr(cam, 'center', None)),
      up=_vec3_to_list(getattr(cam, 'up', None)),
      fov=float(cam.angle) if hasattr(cam, 'angle') else None,
      focal_distance=float(cam.focal_distance) if hasattr(cam, 'focal_distance') else None,
      aspect=float(cam.aspect) if hasattr(cam, 'aspect') else None,
    )

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> CameraSnapshot:
    return cls(
      eye=data.get('eye'),
      center=data.get('center'),
      up=data.get('up'),
      fov=float(data['fov']) if data.get('fov') is not None else None,
      focal_distance=float(data['focal_distance']) if data.get('focal_distance') is not None else None,
      aspect=float(data['aspect']) if data.get('aspect') is not None else None,
    )

  def to_dict(self) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key in ('eye', 'center', 'up', 'fov', 'focal_distance', 'aspect'):
      value = getattr(self, key)
      if value is not None:
        data[key] = value
    return data

  def to_runtime(self, *, width: int, height: int) -> Camera:
    return Camera(
      eye=_list_to_vec3(self.eye, field_name='camera.eye'),
      center=_list_to_vec3(self.center, field_name='camera.center'),
      up=_list_to_vec3(self.up, field_name='camera.up'),
      fov=45.0 if self.fov is None else float(self.fov),
      width=int(width),
      height=int(height),
      focal_distance=1.0 if self.focal_distance is None else float(self.focal_distance),
    )


@dataclass(slots=True)
class RenderSnapshot:
  render: RenderSettingsSnapshot
  scene: SceneSettingsSnapshot
  camera: CameraSnapshot
  objects: list[ShapeSnapshot] = field(default_factory=list)
  lights: list[LightSnapshot] = field(default_factory=list)
  schema_version: str = '1.0'

  @classmethod
  def from_runtime(
    cls,
    *,
    scene: Scene,
    cam: Camera,
    width: int,
    height: int,
    name: str,
    samples_per_pixel: int,
    sampling_mode: str,
    seed: int | None,
    gamma_fix: bool,
    render_time_seconds: float | None = None,
  ) -> RenderSnapshot:
    return cls(
      render=RenderSettingsSnapshot(
        name=name,
        width=int(width),
        height=int(height),
        samples_per_pixel=int(samples_per_pixel),
        sampling_mode=str(sampling_mode),
        seed=seed,
        gamma_fix=bool(gamma_fix),
        render_time_seconds=render_time_seconds,
      ),
      scene=SceneSettingsSnapshot.from_runtime(scene),
      camera=CameraSnapshot.from_runtime(cam),
      objects=[ShapeSnapshot.from_runtime(obj) for obj in scene.objects],
      lights=[LightSnapshot.from_runtime(light) for light in scene.lights],
    )

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> RenderSnapshot:
    return cls(
      render=RenderSettingsSnapshot.from_dict(data['render']),
      scene=SceneSettingsSnapshot.from_dict(data.get('scene', {})),
      camera=CameraSnapshot.from_dict(data.get('camera', {})),
      objects=[ShapeSnapshot.from_dict(obj) for obj in data.get('objects', [])],
      lights=[LightSnapshot.from_dict(light) for light in data.get('lights', [])],
      schema_version=str(data.get('schema_version', '1.0')),
    )

  @classmethod
  def from_json(cls, payload: str) -> RenderSnapshot:
    return cls.from_dict(json.loads(payload))

  def to_dict(self) -> dict[str, Any]:
    return {
      'schema_version': self.schema_version,
      'render': self.render.to_dict(),
      'scene': self.scene.to_dict(),
      'camera': self.camera.to_dict(),
      'objects': [obj.to_dict() for obj in self.objects],
      'lights': [light.to_dict() for light in self.lights],
    }

  def to_json(self, **kwargs: Any) -> str:
    return json.dumps(self.to_dict(), **kwargs)

  def to_markdown(
    self,
    *,
    image_name: str = 'render.png',
    properties_json_name: str = 'properties.json',
  ) -> str:
    props = self.to_dict()
    lines = []
    lines.append('# Propriedades da Simulação')
    lines.append('')
    lines.append(f'![Imagem da Simulação]({image_name})')
    lines.append('')

    render_settings: dict[str, Any] | None = props.get('render') if isinstance(props, dict) else None
    if render_settings:
      lines.append('## Render')
      lines.append('')
      for key, value in render_settings.items():
        lines.append(f'- **{key}**: {value}')
      if self.render.render_time_seconds is not None:
        lines.append(f'- **render_time_minutes**: {self.render.render_time_seconds / 60.0}')
      lines.append('')

    scene_settings: dict[str, Any] | None = props.get('scene') if isinstance(props, dict) else None
    if scene_settings:
      lines.append('## Scene')
      lines.append('')
      for key, value in scene_settings.items():
        lines.append(f'- **{key}**: {value}')
      lines.append('')

    camera_settings: dict[str, Any] | None = props.get('camera') if isinstance(props, dict) else None
    if camera_settings:
      lines.append('## Camera')
      lines.append('')
      for key, value in camera_settings.items():
        lines.append(f'- **{key}**: {value}')
      lines.append('')

    lines.append('## Objetos (detalhado)')
    lines.append('')
    objects: list[dict[str, Any]] | None = props.get('objects') if isinstance(props, dict) else None
    if objects:
      for index, obj in enumerate(objects):
        lines.append(f'### Objeto {index + 1}: {obj.get("type", "Unknown")}')
        if 'shape_chain' in obj:
          lines.append(f'- **shape_chain**: {obj.get("shape_chain")}')
        if 'center' in obj:
          lines.append(f'- **center**: {obj.get("center")}')
        if 'pos' in obj:
          lines.append(f'- **pos**: {obj.get("pos")}')
        if 'normal' in obj:
          lines.append(f'- **normal**: {obj.get("normal")}')
        if 'radius' in obj:
          lines.append(f'- **radius**: {obj.get("radius")}')
        if 'p_min' in obj:
          lines.append(f'- **p_min**: {obj.get("p_min")}')
        if 'p_max' in obj:
          lines.append(f'- **p_max**: {obj.get("p_max")}')
        if 'accelerator' in obj:
          lines.append(f'- **accelerator**: {obj.get("accelerator")}')
        material = obj.get('material')
        if isinstance(material, dict):
          lines.append('- **material**:')
          for key, value in material.items():
            lines.append(f'  - **{key}**: {value}')
        lines.append('')
    else:
      lines.append('- (Nenhum objeto detalhado fornecido)')
      lines.append('')

    lines.append('## Luzes (detalhado)')
    lines.append('')
    lights: list[dict[str, Any]] | None = props.get('lights') if isinstance(props, dict) else None
    if lights:
      for index, light in enumerate(lights):
        light_type = light.get('type', 'Light')
        lines.append(f'- **Light {index + 1} ({light_type})**:')
        if 'pos' in light:
          lines.append(f'  - pos: {light.get("pos")}')
        if 'power' in light:
          lines.append(f'  - power: {light.get("power")}')
        if 'samples_u' in light:
          lines.append(f'  - samples_u: {light.get("samples_u")}')
        if 'samples_v' in light:
          lines.append(f'  - samples_v: {light.get("samples_v")}')
        if 'light_sampling_mode' in light:
          lines.append(f'  - light_sampling_mode: {light.get("light_sampling_mode")}')
        if 'e_u' in light:
          lines.append(f'  - e_u: {light.get("e_u")}')
        if 'e_v' in light:
          lines.append(f'  - e_v: {light.get("e_v")}')
        lines.append('')
    else:
      lines.append('- (Nenhuma luz detalhada fornecida)')
      lines.append('')

    lines.append('## Artefatos')
    lines.append('')
    lines.append(f'- [Snapshot JSON]({properties_json_name}): payload serializado do render, da câmera, da cena, dos objetos e das luzes.')
    lines.append('')
    lines.append('> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.')
    return '\n'.join(lines)

  def to_runtime_scene(self) -> Scene:
    ambient = glm.vec3(1.0, 1.0, 1.0) if self.scene.ambient_light is None else _list_to_vec3(self.scene.ambient_light, field_name='scene.ambient_light')
    scene = Scene(
      ambient_light=ambient,
      max_depth=4 if self.scene.max_depth is None else int(self.scene.max_depth),
      ray_epsilon=0.001 if self.scene.ray_epsilon is None else float(self.scene.ray_epsilon),
    )
    if self.scene.background_color is not None:
      scene.background_color = _list_to_vec3(self.scene.background_color, field_name='scene.background_color')
    scene.objects.extend(obj.to_runtime() for obj in self.objects)
    scene.lights.extend(light.to_runtime() for light in self.lights)
    return scene

  def to_runtime_camera(self) -> Camera:
    return self.camera.to_runtime(width=self.render.width, height=self.render.height)
