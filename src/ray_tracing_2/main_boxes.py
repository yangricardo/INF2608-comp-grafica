from __future__ import annotations

from pyglm import glm
from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene
from ray_tracing_2.shape import Box, Plane, Sphere
from ray_tracing_2.material import PhongMaterial
from ray_tracing_2.light import AmbientLight, PointLight
from ray_tracing_2.film import Film, SamplingMode
from ray_tracing_2.render import Render
import argparse

def main():
    # 1. Configuração da Câmara (Mantendo os parâmetros padrão do projeto)
    eye = glm.vec3(2.78, 2.73, -8.00)
    center = glm.vec3(2.78, 2.73, 0.00)
    up = glm.vec3(0, 1, 0)
    fov = 39.3
    cam = Camera(eye, center, up, fov, width=800, height=600)

    # 2. Criação da Cena
    scene = Scene(ambient_light=AmbientLight(10, 10, 10))  # Luz ambiente fraca para evitar escuridão total
    

    # 3. Definição das Luzes (Conforme proj1-exemplo.pdf)
    light_pos = glm.vec3(2.775, 5.55, 2.775)
    light_intensity = glm.vec3(0.7, 0.7, 0.7)
    scene.lights.append(PointLight(light_intensity, light_pos))
    

    # 4. Materiais
    material_branco = PhongMaterial(
        diffuse=glm.vec3(0.73, 0.73, 0.73),
        specular=glm.vec3(0.5, 0.5, 0.5),
        ambient=glm.vec3(0.1, 0.1, 0.1),
        shininess=50.0
    )
    
    material_luz = PhongMaterial(
        diffuse=glm.vec3(1.0, 1.0, 1.0),
        ambient=glm.vec3(1.0, 1.0, 1.0), # Emissivo simulado
        specular=glm.vec3(0, 0, 0),
        shininess=0
    )

    material_cinza = PhongMaterial(ambient=glm.vec3(0.1), diffuse=glm.vec3(0.5), specular=glm.vec3(1), shininess=50.0)

    # 5. Adição de Objetos
    
    # Subsituição: Box no lugar da esfera original
    # Posicionada centralmente na base
    small_block = Box(
      p_min=glm.vec3(0.0, 0.0, 0.0),
      p_max=glm.vec3(1.65, 1.65, 1.65),
      material=material_cinza,
    )
    big_block = Box(
      p_min=glm.vec3(0.0, 0.0, 0.0),
      p_max=glm.vec3(1.65, 3.30, 1.65),
      material=material_cinza,
    )
    scene.objects.append(small_block)
    scene.objects.append(big_block)

    # Adição: Esfera na mesma posição da PointLight
    # Raio pequeno (0.1) para não obstruir toda a luz mas ser visível
    scene.objects.append(Sphere(center=light_pos, radius=0.1, material=material_luz))
    scene.lights.append(PointLight(pos=glm.vec3(2.775,5.55,2.775), power=glm.vec3(0.7, 0.7, 0.7)))
    # 6. Renderização
    # Configuração padrão de 800x600 e 25 raios por pixel para o teste
    render = Render(out_root="outputs")
    render.render(
        scene=scene,
        cam=cam,
        width=800,
        height=600,
        name="cornell_box",
        samples_per_pixel=1,
        sampling_mode=SamplingMode.JITTERED.value,
        seed=42,
        gamma_fix=False
    )

if __name__ == "__main__":
    main()