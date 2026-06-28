# Propriedades da Simulação

## Comando

```bash
/Users/yang/projects/INF2608-comp-grafica/src/path_tracing/scripts/proj2_req7_mirror.py --spp 10 --depth 10 --mode mis
```

![Imagem da Simulação](render.png)

## Render

- **name**: proj2_req7_mirror_mis_no_rr
- **width**: 512
- **height**: 512
- **samples_per_pixel**: 10
- **sampling_mode**: jittered
- **seed**: None
- **gamma_fix**: False
- **integrator_mode**: mis
- **command_line**: /Users/yang/projects/INF2608-comp-grafica/src/path_tracing/scripts/proj2_req7_mirror.py --spp 10 --depth 10 --mode mis
- **render_time_seconds**: 291.02191374999893
- **render_time_minutes**: 4.850365229166649

## Estimativa de Caminhos

- **Caminhos Totais**: 2,621,440
- **Bounces Estimados**: 13,107,200 (informativo)
- **Shadow Rays**: 11,010,048
- **Total**: 2,621,440
- **Throughput**: 10,744 caminhos/segundo
- **Tempo Estimado**: 243.981s (4.066 min)
- **Tempo Estimado (minutos)**: 4.066

### Calibração (rápida)
- **elapsed_seconds**: 0.238
- **samples_tested**: 2,560
- **rays_traced**: 0
- **intersection_tests**: 86,660
- **shadow_rays**: 0
- **measured_throughput**: 10744 caminhos/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 243.981s
- **Rays Model (real)**: 291.022s
- **Rays Model (erro abs)**: 47.041s
- **Rays Model (erro rel)**: 16.164%
- **Rays Model (fator real/estimado)**: 1.19x
- **Rays Model (acurácia)**: 83.84%
- **Intersection Model (estimado)**: 50.452s
- **Intersection Model (real)**: 291.022s
- **Intersection Model (erro abs)**: 240.570s
- **Intersection Model (erro rel)**: 82.664%
- **Intersection Model (fator real/estimado)**: 5.77x
- **Intersection Model (acurácia)**: 17.34%

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
  - **albedo**: [0.7300000190734863, 0.7300000190734863, 0.7300000190734863]

### Objeto 2: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [0.0, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF
  - **albedo**: [0.11999999731779099, 0.44999998807907104, 0.15000000596046448]

### Objeto 3: Box
- **shape_chain**: ['Box']
- **p_min**: [5.550000190734863, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 5.550000190734863, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF
  - **albedo**: [0.6499999761581421, 0.05000000074505806, 0.05000000074505806]

### Objeto 4: Box
- **shape_chain**: ['Box']
- **p_min**: [0.0, 5.550000190734863, 0.0]
- **p_max**: [5.550000190734863, 5.650000095367432, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF
  - **albedo**: [0.7300000190734863, 0.7300000190734863, 0.7300000190734863]

### Objeto 5: Box
- **shape_chain**: ['Box']
- **p_min**: [-0.10000000149011612, -0.10000000149011612, 0.0]
- **p_max**: [5.650000095367432, 0.0, 5.550000190734863]
- **material**:
  - **type**: LambertianBSDF
  - **albedo**: [0.7300000190734863, 0.7300000190734863, 0.7300000190734863]

### Objeto 6: Box
- **shape_chain**: ['Box']
- **p_min**: [1.274999976158142, 5.448999881744385, 1.274999976158142]
- **p_max**: [4.275000095367432, 5.550000190734863, 4.275000095367432]
- **material**:
  - **type**: EmissiveBSDF
  - **emission**: [7.0, 7.0, 7.0]

### Objeto 7: Sphere
- **shape_chain**: ['Sphere']
- **center**: [2.7750000953674316, 1.0099999904632568, 2.7750000953674316]
- **radius**: 1.0
- **material**:
  - **type**: MirrorBSDF

## Luzes (detalhado)

- **Light 1 (RectAreaLight)**:
  - Le: [7.0, 7.0, 7.0]
  - corner: [1.274999976158142, 5.449999809265137, 1.274999976158142]
  - edge_u: [3.0, 0.0, 0.0]
  - edge_v: [0.0, 0.0, 3.0]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.