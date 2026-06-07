# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj2_req7_water_mis_no_rr
- **width**: 512
- **height**: 512
- **samples_per_pixel**: 64
- **sampling_mode**: jittered
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 1974.3898317500134
- **render_time_minutes**: 32.90649719583356

## Estimativa de Raios

- **Raios Primários**: 16,777,216
- **Raios Secundários**: 83,886,080
- **Shadow Rays**: 70,464,307
- **Total de Raios**: 16,777,216
- **Throughput**: 10,769 raios/segundo
- **Tempo Estimado**: 1557.871s (25.965 min)
- **Tempo Estimado (minutos)**: 25.965
- **Tempo Estimado (interseções)**: 337.313s
- **Primary Hit Ratio**: 0.700
- **Recursive Surface Ratio**: 0.857
- **Shadow Samples/Hit**: 1

### Calibração (rápida)
- **elapsed_seconds**: 1.521
- **samples_tested**: 16,384
- **rays_traced**: 0
- **intersection_tests**: 529,683
- **shadow_rays**: 0
- **measured_throughput**: 10769 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 1557.871s
- **Rays Model (real)**: 1974.390s
- **Rays Model (erro abs)**: 416.519s
- **Rays Model (erro rel)**: 21.096%
- **Rays Model (fator real/estimado)**: 1.27x
- **Rays Model (acurácia)**: 78.90%
- **Intersection Model (estimado)**: 337.313s
- **Intersection Model (real)**: 1974.390s
- **Intersection Model (erro abs)**: 1637.077s
- **Intersection Model (erro rel)**: 82.916%
- **Intersection Model (fator real/estimado)**: 5.85x
- **Intersection Model (acurácia)**: 17.08%

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
- **p_min**: [2.2750000953674316, 0.0, 2.2750000953674316]
- **p_max**: [3.2750000953674316, 1.0, 3.2750000953674316]
- **material**:
  - **type**: DielectricBSDF
  - **ior**: 1.33

## Luzes (detalhado)

- **Light 1 (RectAreaLight)**:

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.