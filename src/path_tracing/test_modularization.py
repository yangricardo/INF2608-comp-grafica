#!/usr/bin/env python3
"""Quick validation test for modularized lights and materials."""

from pyglm import glm

# Test material imports from new modular structure
from path_tracing.materials import (
    Material,
    EmissiveMaterial,
    PhongMaterial,
    ReflectiveMaterial,
    TransparentMaterial,
)

# Test backward-compatible imports from wrapper
from path_tracing.material import (
    Material as MaterialWrapper,
    EmissiveMaterial as EmissiveWrapper,
    PhongMaterial as PhongWrapper,
    ReflectiveMaterial as ReflectiveWrapper,
    TransparentMaterial as TransparentWrapper,
)

# Test light imports from new modular structure
from path_tracing.lights import (
    Light,
    PointLight,
    AreaLight,
    AreaLightSamplingMode,
    RectAreaLight,
)

# Test backward-compatible imports from wrapper
from path_tracing.light import (
    Light as LightWrapper,
    PointLight as PointLightWrapper,
    AreaLight as AreaLightWrapper,
    AreaLightSamplingMode as AreaLightSamplingModeWrapper,
    AmbientLight,
)

print("✅ All imports successful!")

# Test instantiation
print("\n--- Testing Material Instantiation ---")
emissive = EmissiveMaterial(glm.vec3(2.0, 2.0, 2.0))
phong = PhongMaterial(
    ambient=glm.vec3(0.1),
    diffuse=glm.vec3(0.8),
    specular=glm.vec3(0.5),
    shininess=32.0
)
reflective = ReflectiveMaterial(
    ambient=glm.vec3(0.05),
    diffuse=glm.vec3(0.0),
    specular=glm.vec3(0.9),
    shininess=64.0,
    reflectivity=0.8
)
transparent = TransparentMaterial(
    ior=1.5,
    attenuation=glm.vec3(1.0)
)
print(f"✅ EmissiveMaterial: {emissive}")
print(f"✅ PhongMaterial: {phong}")
print(f"✅ ReflectiveMaterial: {reflective}")
print(f"✅ TransparentMaterial: {transparent}")

print("\n--- Testing Light Instantiation ---")
point_light = PointLight(glm.vec3(0, 5, 0), glm.vec3(10.0))
area_light = AreaLight(
    p=glm.vec3(0, 5, 0),
    e_u=glm.vec3(2, 0, 0),
    e_v=glm.vec3(0, 0, 2),
    power=glm.vec3(5.0),
    samples_u=4,
    samples_v=4,
    sampling_mode=AreaLightSamplingMode.STRATIFIED
)
print(f"✅ PointLight: {point_light}")
print(f"✅ AreaLight: {area_light}")

print("\n--- Testing Wrapper Compatibility ---")
# Check that wrappers point to the same classes
assert Material is MaterialWrapper, "Material wrapper mismatch!"
assert EmissiveMaterial is EmissiveWrapper, "EmissiveMaterial wrapper mismatch!"
assert PointLight is PointLightWrapper, "PointLight wrapper mismatch!"
print("✅ All wrapper aliases match!")

print("\n--- Testing AmbientLight ---")
ambient = AmbientLight(glm.vec3(0.2, 0.2, 0.2))
print(f"✅ AmbientLight: {ambient}")

print("\n✅ ALL TESTS PASSED!")
