# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj1_req2_point_lights
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 25
- **sampling_mode**: stratified
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 501.9072476250003
- **render_time_minutes**: 8.365120793750005

## Estimativa de Raios

- **Raios Primários**: 12,000,000
- **Raios Secundários**: 0
- **Shadow Rays**: 18,281,250
- **Total de Raios**: 30,281,250
- **Throughput**: 56,225 raios/segundo
- **Tempo Estimado**: 538.570s (8.976 min)
- **Tempo Estimado (minutos)**: 8.976
- **Tempo Estimado (interseções)**: 538.570s
- **Primary Hit Ratio**: 0.508
- **Recursive Surface Ratio**: 0.000
- **Shadow Samples/Hit**: 3

### Calibração (rápida)
- **elapsed_seconds**: 0.287
- **samples_tested**: 6,400
- **rays_traced**: 6,400
- **intersection_tests**: 129,200
- **shadow_rays**: 9,750
- **measured_throughput**: 56225 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 538.570s
- **Rays Model (real)**: 501.907s
- **Rays Model (erro abs)**: 36.663s
- **Rays Model (erro rel)**: 7.305%
- **Rays Model (fator real/estimado)**: 0.93x
- **Rays Model (acurácia)**: 92.70%
- **Intersection Model (estimado)**: 538.570s
- **Intersection Model (real)**: 501.907s
- **Intersection Model (erro abs)**: 36.663s
- **Intersection Model (erro rel)**: 7.305%
- **Intersection Model (fator real/estimado)**: 0.93x
- **Intersection Model (acurácia)**: 92.70%

## Scene

- **ambient_light**: [0.029999999329447746, 0.029999999329447746, 0.029999999329447746]
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

### Objeto 6: Sphere
- **shape_chain**: ['Sphere']
- **center**: [1.4500000476837158, 0.6499999761581421, 4.099999904632568]
- **radius**: 0.65
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.029999999329447746, 0.029999999329447746, 0.029999999329447746]
  - **diffuse**: [0.699999988079071, 0.699999988079071, 0.699999988079071]
  - **specular**: [0.15000000596046448, 0.15000000596046448, 0.15000000596046448]
  - **shininess**: 20.0

### Objeto 7: Sphere
- **shape_chain**: ['Sphere']
- **center**: [3.950000047683716, 0.6499999761581421, 3.950000047683716]
- **radius**: 0.65
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.019999999552965164, 0.019999999552965164, 0.019999999552965164]
  - **diffuse**: [0.3499999940395355, 0.3499999940395355, 0.3499999940395355]
  - **specular**: [0.550000011920929, 0.550000011920929, 0.550000011920929]
  - **shininess**: 96.0

### Objeto 8: Box
- **shape_chain**: ['Box']
- **p_min**: [2.25, 0.0, 1.75]
- **p_max**: [3.200000047683716, 1.649999976158142, 2.6500000953674316]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **diffuse**: [0.5, 0.5, 0.5]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

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