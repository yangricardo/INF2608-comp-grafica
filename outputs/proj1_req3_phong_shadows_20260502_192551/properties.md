# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj1_req3_phong_shadows
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 25
- **sampling_mode**: stratified
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 525.7041507089998
- **render_time_minutes**: 8.761735845149996

## Estimativa de Raios

- **Raios Primários**: 12,000,000
- **Raios Secundários**: 0
- **Shadow Rays**: 12,187,500
- **Total de Raios**: 24,187,500
- **Throughput**: 46,131 raios/segundo
- **Tempo Estimado**: 524.316s (8.739 min)
- **Tempo Estimado (minutos)**: 8.739
- **Tempo Estimado (interseções)**: 524.316s
- **Primary Hit Ratio**: 0.508
- **Recursive Surface Ratio**: 0.000
- **Shadow Samples/Hit**: 2

### Calibração (rápida)
- **elapsed_seconds**: 0.280
- **samples_tested**: 6,400
- **rays_traced**: 6,400
- **intersection_tests**: 103,200
- **shadow_rays**: 6,500
- **measured_throughput**: 46132 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 524.316s
- **Rays Model (real)**: 525.704s
- **Rays Model (erro abs)**: 1.388s
- **Rays Model (erro rel)**: 0.264%
- **Rays Model (fator real/estimado)**: 1.00x
- **Rays Model (acurácia)**: 99.74%
- **Intersection Model (estimado)**: 524.316s
- **Intersection Model (real)**: 525.704s
- **Intersection Model (erro abs)**: 1.388s
- **Intersection Model (erro rel)**: 0.264%
- **Intersection Model (fator real/estimado)**: 1.00x
- **Intersection Model (acurácia)**: 99.74%

## Scene

- **ambient_light**: [0.019999999552965164, 0.019999999552965164, 0.019999999552965164]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 2
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

### Objeto 6: Instance
- **shape_chain**: ['Instance', 'Box']
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.05999999865889549, 0.0, 0.0]
  - **diffuse**: [0.75, 0.10000000149011612, 0.10000000149011612]
  - **specular**: [0.05000000074505806, 0.05000000074505806, 0.05000000074505806]
  - **shininess**: 16.0

### Objeto 7: Instance
- **shape_chain**: ['Instance', 'Box']
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.0, 0.019999999552965164, 0.07000000029802322]
  - **diffuse**: [0.20000000298023224, 0.25, 0.75]
  - **specular**: [0.6000000238418579, 0.6000000238418579, 0.6000000238418579]
  - **shininess**: 120.0

### Objeto 8: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.0999999046325684, 0.6200000047683716, 4.25]
- **radius**: 0.62
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.05999999865889549, 0.0, 0.0]
  - **diffuse**: [0.75, 0.10000000149011612, 0.10000000149011612]
  - **specular**: [0.05000000074505806, 0.05000000074505806, 0.05000000074505806]
  - **shininess**: 16.0

## Luzes (detalhado)

- **Light 1 (PointLight)**:
  - pos: [2.8499999046325684, 5.400000095367432, 2.3499999046325684]
  - power: [0.949999988079071, 0.949999988079071, 0.949999988079071]

- **Light 2 (PointLight)**:
  - pos: [1.350000023841858, 3.549999952316284, 4.949999809265137]
  - power: [0.25, 0.2800000011920929, 0.3199999928474426]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.