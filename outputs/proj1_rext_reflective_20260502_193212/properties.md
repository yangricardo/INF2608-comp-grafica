# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: proj1_rext_reflective
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 4
- **sampling_mode**: stratified
- **seed**: None
- **gamma_fix**: False
- **render_time_seconds**: 75.97067725000306
- **render_time_minutes**: 1.2661779541667177

## Estimativa de Raios

- **Raios Primários**: 1,920,000
- **Raios Secundários**: 324,641
- **Shadow Rays**: 2,228,014
- **Total de Raios**: 4,472,655
- **Throughput**: 52,439 raios/segundo
- **Tempo Estimado**: 85.291s (1.422 min)
- **Tempo Estimado (minutos)**: 1.422
- **Tempo Estimado (interseções)**: 85.291s
- **Primary Hit Ratio**: 0.496
- **Recursive Surface Ratio**: 0.286
- **Shadow Samples/Hit**: 2

### Calibração (rápida)
- **elapsed_seconds**: 0.041
- **samples_tested**: 1,024
- **rays_traced**: 1,080
- **intersection_tests**: 15,064
- **shadow_rays**: 1,072
- **measured_throughput**: 52440 raios/segundo

## Qualidade da Estimativa

- **Rays Model (estimado)**: 85.291s
- **Rays Model (real)**: 75.971s
- **Rays Model (erro abs)**: 9.320s
- **Rays Model (erro rel)**: 12.268%
- **Rays Model (fator real/estimado)**: 0.89x
- **Rays Model (acurácia)**: 87.73%
- **Intersection Model (estimado)**: 85.291s
- **Intersection Model (real)**: 75.971s
- **Intersection Model (erro abs)**: 9.320s
- **Intersection Model (erro rel)**: 12.268%
- **Intersection Model (fator real/estimado)**: 0.89x
- **Intersection Model (acurácia)**: 87.73%

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

### Objeto 6: Instance
- **shape_chain**: ['Instance', 'Box']
- **material**:
  - **type**: ReflectiveMaterial
  - **ambient**: [0.03999999910593033, 0.03999999910593033, 0.03999999910593033]
  - **diffuse**: [0.3499999940395355, 0.3499999940395355, 0.3499999940395355]
  - **specular**: [0.4000000059604645, 0.4000000059604645, 0.4000000059604645]
  - **shininess**: 64.0
  - **reflectivity**: [0.6499999761581421, 0.6499999761581421, 0.6499999761581421]

### Objeto 7: Sphere
- **shape_chain**: ['Sphere']
- **center**: [3.950000047683716, 0.6499999761581421, 4.099999904632568]
- **radius**: 0.65
- **material**:
  - **type**: ReflectiveMaterial
  - **ambient**: [0.05999999865889549, 0.0, 0.0]
  - **diffuse**: [0.6000000238418579, 0.07999999821186066, 0.07999999821186066]
  - **specular**: [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]
  - **shininess**: 80.0
  - **reflectivity**: [0.5, 0.5, 0.5]

## Luzes (detalhado)

- **Light 1 (PointLight)**:
  - pos: [2.7750000953674316, 5.400000095367432, 2.7750000953674316]
  - power: [0.8999999761581421, 0.8999999761581421, 0.8999999761581421]

- **Light 2 (PointLight)**:
  - pos: [4.550000190734863, 4.849999904632568, 4.550000190734863]
  - power: [0.30000001192092896, 0.3199999928474426, 0.3499999940395355]

## Artefatos

- [Snapshot JSON](properties.json): payload serializado do render, da câmera, da cena, dos objetos e das luzes.

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada e navegar até o snapshot JSON.