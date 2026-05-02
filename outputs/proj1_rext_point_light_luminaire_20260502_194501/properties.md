# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj1_rext_point_light_luminaire
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 25
- **sampling_mode**: stratified
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 406.76686249999693
- **render_time_minutes**: 6.779447708333282

## Estimativa de Raios

- **Raios Primários**: 12,000,000
- **Raios Secundários**: 0
- **Shadow Rays**: 11,390,625
- **Total de Raios**: 23,390,625
- **Throughput**: 58,716 raios/segundo
- **Tempo Estimado**: 398.367s (6.639 min)
- **Tempo Estimado (minutos)**: 6.639
- **Tempo Estimado (interseções)**: 398.367s
- **Primary Hit Ratio**: 0.949
- **Recursive Surface Ratio**: 0.000
- **Shadow Samples/Hit**: 1

### Calibração (rápida)
- **elapsed_seconds**: 0.212
- **samples_tested**: 6,400
- **rays_traced**: 6,400
- **intersection_tests**: 112,275
- **shadow_rays**: 6,075
- **measured_throughput**: 58716 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 398.367s
- **Rays Model (real)**: 406.767s
- **Rays Model (erro abs)**: 8.399s
- **Rays Model (erro rel)**: 2.065%
- **Rays Model (fator real/estimado)**: 1.02x
- **Rays Model (acurácia)**: 97.94%
- **Intersection Model (estimado)**: 398.367s
- **Intersection Model (real)**: 406.767s
- **Intersection Model (erro abs)**: 8.399s
- **Intersection Model (erro rel)**: 2.065%
- **Intersection Model (fator real/estimado)**: 1.02x
- **Intersection Model (acurácia)**: 97.94%

## Scene

- **ambient_light**: [0.019999999552965164, 0.019999999552965164, 0.019999999552965164]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 3
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
  - **diffuse**: [0.7200000286102295, 0.7200000286102295, 0.7200000286102295]
  - **specular**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **shininess**: 24.0

### Objeto 7: Sphere
- **shape_chain**: ['Sphere']
- **center**: [3.950000047683716, 0.6499999761581421, 3.950000047683716]
- **radius**: 0.65
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.029999999329447746, 0.029999999329447746, 0.029999999329447746]
  - **diffuse**: [0.7200000286102295, 0.7200000286102295, 0.7200000286102295]
  - **specular**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **shininess**: 24.0

### Objeto 8: Box
- **shape_chain**: ['Box']
- **p_min**: [2.25, 0.0, 1.75]
- **p_max**: [3.200000047683716, 1.649999976158142, 2.6500000953674316]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.029999999329447746, 0.029999999329447746, 0.029999999329447746]
  - **diffuse**: [0.7200000286102295, 0.7200000286102295, 0.7200000286102295]
  - **specular**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **shininess**: 24.0

### Objeto 9: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
- **radius**: 0.1
- **material**:
  - **type**: EmissiveMaterial
  - **emission**: [1.0, 0.9800000190734863, 0.949999988079071]
  - **shadow_passthrough**: True

## Luzes (detalhado)

- **Light 1 (PointLight)**:
  - pos: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
  - power: [0.699999988079071, 0.699999988079071, 0.699999988079071]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.