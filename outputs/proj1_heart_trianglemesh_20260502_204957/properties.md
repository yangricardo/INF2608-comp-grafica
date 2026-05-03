# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj1_heart_trianglemesh
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 1
- **sampling_mode**: jittered
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 40.47782145800011
- **render_time_minutes**: 0.6746303576333351

## Estimativa de Raios

- **Raios Primários**: 480,000
- **Raios Secundários**: 53,906
- **Shadow Rays**: 1,513,418
- **Total de Raios**: 2,047,324
- **Throughput**: 48,330 raios/segundo
- **Tempo Estimado**: 42.361s (0.706 min)
- **Tempo Estimado (minutos)**: 0.706
- **Tempo Estimado (interseções)**: 42.361s
- **Primary Hit Ratio**: 0.945
- **Recursive Surface Ratio**: 0.111
- **Shadow Samples/Hit**: 3

### Calibração (rápida)
- **elapsed_seconds**: 0.021
- **samples_tested**: 256
- **rays_traced**: 260
- **intersection_tests**: 8,973
- **shadow_rays**: 737
- **measured_throughput**: 48331 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 42.361s
- **Rays Model (real)**: 40.478s
- **Rays Model (erro abs)**: 1.883s
- **Rays Model (erro rel)**: 4.651%
- **Rays Model (fator real/estimado)**: 0.96x
- **Rays Model (acurácia)**: 95.35%
- **Intersection Model (estimado)**: 42.361s
- **Intersection Model (real)**: 40.478s
- **Intersection Model (erro abs)**: 1.883s
- **Intersection Model (erro rel)**: 4.651%
- **Intersection Model (fator real/estimado)**: 0.96x
- **Intersection Model (acurácia)**: 95.35%

## Scene

- **ambient_light**: [0.029999999329447746, 0.029999999329447746, 0.029999999329447746]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 4
- **ray_epsilon**: 0.001

## Camera

- **eye**: [2.7750000953674316, 3.200000047683716, 12.774999618530273]
- **center**: [2.7750000953674316, 2.7750000953674316, 2.7750000953674316]
- **up**: [0.0, 1.0, 0.0]
- **fov**: 50.0
- **focal_distance**: 1.0
- **aspect**: 1.3333333333333333

## Objetos (detalhado)

### Objeto 1: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, -0.10000000149011612]
- **p_max**: [5.650000095367432, 5.650000095367432, 0.0]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.07999999821186066, 0.07999999821186066]
  - **diffuse**: [0.75, 0.75, 0.75]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

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

### Objeto 6: Sphere
- **shape_chain**: ['Sphere']
- **center**: [1.25, 5.199999809265137, 1.350000023841858]
- **radius**: 0.07
- **material**:
  - **type**: EmissiveMaterial
  - **emission**: [1.0, 0.949999988079071, 0.8999999761581421]
  - **shadow_passthrough**: True

### Objeto 7: Sphere
- **shape_chain**: ['Sphere']
- **center**: [4.349999904632568, 4.849999904632568, 2.549999952316284]
- **radius**: 0.07
- **material**:
  - **type**: EmissiveMaterial
  - **emission**: [1.0, 0.949999988079071, 0.8999999761581421]
  - **shadow_passthrough**: True

### Objeto 8: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.75, 5.449999809265137, 4.849999904632568]
- **radius**: 0.07
- **material**:
  - **type**: EmissiveMaterial
  - **emission**: [1.0, 0.949999988079071, 0.8999999761581421]
  - **shadow_passthrough**: True

### Objeto 9: TriangleMesh
- **shape_chain**: ['TriangleMesh']
- **accelerator**: bvh
- **material**:
  - **type**: ReflectiveMaterial
  - **ambient**: [0.07000000029802322, 0.009999999776482582, 0.019999999552965164]
  - **diffuse**: [0.30000001192092896, 0.05000000074505806, 0.10000000149011612]
  - **specular**: [0.6499999761581421, 0.6499999761581421, 0.6499999761581421]
  - **shininess**: 140.0
  - **reflectivity**: [0.6200000047683716, 0.550000011920929, 0.5799999833106995]

## Luzes (detalhado)

- **Light 1 (PointLight)**:
  - pos: [1.25, 5.199999809265137, 1.350000023841858]
  - power: [0.75, 0.6800000071525574, 0.6200000047683716]

- **Light 2 (PointLight)**:
  - pos: [4.349999904632568, 4.849999904632568, 2.549999952316284]
  - power: [0.44999998807907104, 0.5, 0.6499999761581421]

- **Light 3 (PointLight)**:
  - pos: [2.75, 5.449999809265137, 4.849999904632568]
  - power: [0.3499999940395355, 0.3499999940395355, 0.3199999928474426]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.