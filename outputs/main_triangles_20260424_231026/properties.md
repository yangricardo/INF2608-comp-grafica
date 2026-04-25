# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: main_triangles
- **width**: 320
- **height**: 240
- **samples_per_pixel**: 1
- **sampling_mode**: jittered
- **seed**: 1
- **gamma_fix**: False

## Scene

- **ambient_light**: [0.11999999731779099, 0.11999999731779099, 0.11999999731779099]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 4
- **ray_epsilon**: 0.001

## Camera

- **eye**: [0.0, 0.550000011920929, 4.349999904632568]
- **center**: [0.0, 0.05000000074505806, 0.0]
- **up**: [0.0, 1.0, 0.0]
- **fov**: 45.0
- **focal_distance**: 1.0
- **aspect**: 1.3333333333333333

## Objetos (detalhado)

### Objeto 1: Instance
- **shape_chain**: ['Instance', 'TriangleMesh']
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.10000000149011612, 0.0, 0.0]
  - **diffuse**: [0.699999988079071, 0.0, 0.0]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 50.0

### Objeto 2: Sphere
- **center**: [1.0499999523162842, 0.550000011920929, 0.75]
- **radius**: 0.34
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.0, 0.0, 0.10000000149011612]
  - **diffuse**: [0.0, 0.0, 0.699999988079071]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 40.0

### Objeto 3: Plane
- **pos**: [0.0, -1.0, 0.0]
- **normal**: [0.0, 1.0, 0.0]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.07999999821186066, 0.07999999821186066, 0.07999999821186066]
  - **diffuse**: [0.4000000059604645, 0.4000000059604645, 0.4000000059604645]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

## Luzes (detalhado)

- **Light 1**:
  - pos: [2.4000000953674316, 4.900000095367432, 3.4000000953674316]
  - power: [110.0, 110.0, 110.0]

## Debug (raw JSON)

```json
{
  "render": {
    "name": "main_triangles",
    "width": 320,
    "height": 240,
    "samples_per_pixel": 1,
    "sampling_mode": "jittered",
    "seed": 1,
    "gamma_fix": false
  },
  "scene": {
    "ambient_light": [
      0.11999999731779099,
      0.11999999731779099,
      0.11999999731779099
    ],
    "background_color": [
      0.019999999552965164,
      0.019999999552965164,
      0.05000000074505806
    ],
    "max_depth": 4,
    "ray_epsilon": 0.001
  },
  "camera": {
    "eye": [
      0.0,
      0.550000011920929,
      4.349999904632568
    ],
    "center": [
      0.0,
      0.05000000074505806,
      0.0
    ],
    "up": [
      0.0,
      1.0,
      0.0
    ],
    "fov": 45.0,
    "focal_distance": 1.0,
    "aspect": 1.3333333333333333
  },
  "objects": [
    {
      "type": "Instance",
      "vertex_count": 5,
      "face_count": 6,
      "triangle_count": 6,
      "shape_chain": [
        "Instance",
        "TriangleMesh"
      ],
      "material": {
        "type": "PhongMaterial",
        "ambient": [
          0.10000000149011612,
          0.0,
          0.0
        ],
        "diffuse": [
          0.699999988079071,
          0.0,
          0.0
        ],
        "specular": [
          1.0,
          1.0,
          1.0
        ],
        "shininess": 50.0
      }
    },
    {
      "type": "Sphere",
      "center": [
        1.0499999523162842,
        0.550000011920929,
        0.75
      ],
      "radius": 0.34,
      "material": {
        "type": "PhongMaterial",
        "ambient": [
          0.0,
          0.0,
          0.10000000149011612
        ],
        "diffuse": [
          0.0,
          0.0,
          0.699999988079071
        ],
        "specular": [
          1.0,
          1.0,
          1.0
        ],
        "shininess": 40.0
      }
    },
    {
      "type": "Plane",
      "pos": [
        0.0,
        -1.0,
        0.0
      ],
      "normal": [
        0.0,
        1.0,
        0.0
      ],
      "material": {
        "type": "PhongMaterial",
        "ambient": [
          0.07999999821186066,
          0.07999999821186066,
          0.07999999821186066
        ],
        "diffuse": [
          0.4000000059604645,
          0.4000000059604645,
          0.4000000059604645
        ],
        "specular": [
          0.0,
          0.0,
          0.0
        ],
        "shininess": 1.0
      }
    }
  ],
  "lights": [
    {
      "pos": [
        2.4000000953674316,
        4.900000095367432,
        3.4000000953674316
      ],
      "power": [
        110.0,
        110.0,
        110.0
      ]
    }
  ]
}
```

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.