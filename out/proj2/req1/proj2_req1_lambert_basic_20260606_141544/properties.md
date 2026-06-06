# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj2_req1_lambert_basic
- **width**: 64
- **height**: 64
- **samples_per_pixel**: 4
- **sampling_mode**: jittered
- **seed**: 42
- **gamma_fix**: False
- **render_time_seconds**: 1.3867435830179602
- **render_time_minutes**: 0.023112393050299336

## Estimativa de Raios

- **Raios Primários**: 16,384
- **Raios Secundários**: 18,060
- **Shadow Rays**: 0
- **Total de Raios**: 34,444
- **Throughput**: 17,673 raios/segundo
- **Tempo Estimado**: 1.949s (0.032 min)
- **Tempo Estimado (minutos)**: 0.032
- **Tempo Estimado (interseções)**: 1995.662s
- **Primary Hit Ratio**: 0.700
- **Recursive Surface Ratio**: 0.889
- **Shadow Samples/Hit**: 0

### Calibração (rápida)
- **elapsed_seconds**: 0.058
- **samples_tested**: 1,024
- **rays_traced**: 0
- **intersection_tests**: 25,290
- **shadow_rays**: 0
- **measured_throughput**: 17674 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 1.949s
- **Rays Model (real)**: 1.387s
- **Rays Model (erro abs)**: 0.562s
- **Rays Model (erro rel)**: 40.537%
- **Rays Model (fator real/estimado)**: 0.71x
- **Rays Model (acurácia)**: 59.46%
- **Intersection Model (estimado)**: 1995.662s
- **Intersection Model (real)**: 1.387s
- **Intersection Model (erro abs)**: 1994.276s
- **Intersection Model (erro rel)**: 143809.978%
- **Intersection Model (fator real/estimado)**: 0.00x
- **Intersection Model (acurácia)**: 0.00%

## Scene

- **ambient_light**: [0.0, 0.0, 0.0]
- **background_color**: [0.0, 0.0, 0.0]
- **max_depth**: 8
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
  - **type**: LambertianBSDF

### Objeto 2: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [0.0, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF

### Objeto 3: Box
- **shape_chain**: ['Box']
- **p_min**: [5.550000190734863, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF

### Objeto 4: Box
- **shape_chain**: ['Box']
- **p_min**: [0.0, 5.550000190734863, 0.0]
- **p_max**: [5.550000190734863, 5.650000095367432, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF

### Objeto 5: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 0.0, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF

### Objeto 6: Box
- **shape_chain**: ['Box']
- **p_min**: [1.274999976158142, 5.449999809265137, 1.274999976158142]
- **p_max**: [4.275000095367432, 5.550000190734863, 4.275000095367432]
- **material**:
  - **type**: EmissiveBSDF

### Objeto 7: Box
- **shape_chain**: ['Box']
- **p_min**: [0.8500000238418579, 0.0, 0.8500000238418579]
- **p_max**: [2.5, 1.100000023841858, 2.5]
- **material**:
  - **type**: LambertianBSDF

### Objeto 8: Box
- **shape_chain**: ['Box']
- **p_min**: [3.0, 0.0, 2.799999952316284]
- **p_max**: [4.099999904632568, 2.299999952316284, 3.9000000953674316]
- **material**:
  - **type**: LambertianBSDF

### Objeto 9: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.0999999046325684, 0.6200000047683716, 4.25]
- **radius**: 0.62
- **material**:
  - **type**: LambertianBSDF

## Luzes (detalhado)

- (Nenhuma luz detalhada fornecida)

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.