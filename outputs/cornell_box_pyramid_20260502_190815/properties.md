# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: cornell_box_pyramid
- **width**: 16
- **height**: 16
- **samples_per_pixel**: 1
- **sampling_mode**: jittered
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 0.08356637500037323
- **render_time_minutes**: 0.0013927729166728871

## Estimativa de Raios

- **Raios Primários**: 256
- **Raios Secundários**: 18
- **Shadow Rays**: 265
- **Total de Raios**: 539
- **Throughput**: 23,610 raios/segundo
- **Tempo Estimado**: 0.023s (0.000 min)
- **Tempo Estimado (minutos)**: 0.000
- **Tempo Estimado (interseções)**: 0.023s
- **Primary Hit Ratio**: 0.162
- **Recursive Surface Ratio**: 0.364
- **Shadow Samples/Hit**: 6

### Calibração (rápida)
- **elapsed_seconds**: 0.040
- **samples_tested**: 256
- **rays_traced**: 476
- **intersection_tests**: 10,318
- **shadow_rays**: 462
- **measured_throughput**: 23611 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 0.023s
- **Rays Model (real)**: 0.084s
- **Rays Model (erro abs)**: 0.061s
- **Rays Model (erro rel)**: 72.682%
- **Rays Model (fator real/estimado)**: 3.66x
- **Rays Model (acurácia)**: 27.32%
- **Intersection Model (estimado)**: 0.023s
- **Intersection Model (real)**: 0.084s
- **Intersection Model (erro abs)**: 0.061s
- **Intersection Model (erro rel)**: 72.682%
- **Intersection Model (fator real/estimado)**: 3.66x
- **Intersection Model (acurácia)**: 27.32%

## Scene

- **ambient_light**: [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 4
- **ray_epsilon**: 0.001

## Camera

- **eye**: [2.7750000953674316, 3.200000047683716, 12.774999618530273]
- **center**: [2.7750000953674316, 2.7750000953674316, 2.7750000953674316]
- **up**: [0.0, 1.0, 0.0]
- **fov**: 50.0
- **focal_distance**: 1.0
- **aspect**: 1.0

## Objetos (detalhado)

### Objeto 1: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, -0.10000000149011612]
- **p_max**: [5.650000095367432, 5.650000095367432, 0.0]
- **material**:
  - **type**: ReflectiveMaterial
  - **ambient**: [0.07999999821186066, 0.07999999821186066, 0.07999999821186066]
  - **diffuse**: [0.75, 0.75, 0.75]
  - **specular**: [0.05000000074505806, 0.05000000074505806, 0.05000000074505806]
  - **shininess**: 32.0
  - **reflectivity**: [0.550000011920929, 0.550000011920929, 0.550000011920929]

### Objeto 2: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [0.0, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.0, 0.07999999821186066, 0.0]
  - **diffuse**: [0.05000000074505806, 0.75, 0.05000000074505806]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 3: Box
- **shape_chain**: ['Box']
- **p_min**: [5.550000190734863, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.0, 0.0]
  - **diffuse**: [0.75, 0.05000000074505806, 0.05000000074505806]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 4: Box
- **shape_chain**: ['Box']
- **p_min**: [0.0, 5.550000190734863, 0.0]
- **p_max**: [5.550000190734863, 5.650000095367432, 5.550000190734863]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.07999999821186066, 0.07999999821186066]
  - **diffuse**: [0.75, 0.75, 0.75]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 5: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 0.0, 5.550000190734863]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.07999999821186066, 0.07999999821186066]
  - **diffuse**: [0.75, 0.75, 0.75]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 6: Translate
- **shape_chain**: ['Translate', 'Rotate', 'Box']
- **material**:
  - **type**: TransparentMaterial
  - **ambient**: [0.0, 0.0, 0.0]
  - **diffuse**: [0.0, 0.0, 0.0]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0
  - **attenuation**: [1.0, 1.0, 1.0]
  - **ior**: 1.5

### Objeto 7: Translate
- **shape_chain**: ['Translate', 'Rotate', 'Box']
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.0, 0.0]
  - **diffuse**: [0.75, 0.05000000074505806, 0.05000000074505806]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 8: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.5, 0.5, 5.0]
- **radius**: 0.6
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.0, 0.07999999821186066, 0.0]
  - **diffuse**: [0.05000000074505806, 0.75, 0.05000000074505806]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

### Objeto 9: TriangleMesh
- **shape_chain**: ['TriangleMesh']
- **material**:
  - **type**: TransparentMaterial
  - **ambient**: [0.0, 0.0, 0.0]
  - **diffuse**: [0.0, 0.0, 0.0]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0
  - **attenuation**: [0.8799999952316284, 0.9399999976158142, 0.9800000190734863]
  - **ior**: 1.5

### Objeto 10: TriangleMesh
- **shape_chain**: ['TriangleMesh']
- **material**:
  - **type**: ReflectiveMaterial
  - **ambient**: [0.03999999910593033, 0.03999999910593033, 0.03999999910593033]
  - **diffuse**: [0.20000000298023224, 0.20000000298023224, 0.20000000298023224]
  - **specular**: [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]
  - **shininess**: 96.0
  - **reflectivity**: [0.7799999713897705, 0.7799999713897705, 0.7799999713897705]

### Objeto 11: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
- **radius**: 0.1
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [1.0, 1.0, 1.0]
  - **diffuse**: [0.0, 0.0, 0.0]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 0.0

## Luzes (detalhado)

- **Light 1 (AreaLight)**:
  - pos: [1.25, 1.9500000476837158, 13.449999809265137]
  - power: [80.0, 80.0, 80.0]
  - samples_u: 2
  - samples_v: 2
  - light_sampling_mode: stratified
  - e_u: [3.049999952316284, 0.0, 0.0]
  - e_v: [0.0, 2.3499999046325684, 0.0]

- **Light 2 (PointLight)**:
  - pos: [2.7750000953674316, 5.0, 2.7750000953674316]
  - power: [0.699999988079071, 0.699999988079071, 0.699999988079071]

- **Light 3 (PointLight)**:
  - pos: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
  - power: [0.699999988079071, 0.699999988079071, 0.699999988079071]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.