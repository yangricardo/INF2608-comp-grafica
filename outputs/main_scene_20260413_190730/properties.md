# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Render

- **name**: main_scene
- **width**: 800
- **height**: 600
- **samples_per_pixel**: 1
- **sampling_mode**: jittered
- **seed**: None
- **gamma_fix**: False

## Scene

- **ambient_light**: [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]
- **background_color**: [0.019999999552965164, 0.019999999552965164, 0.05000000074505806]
- **max_depth**: 4
- **ray_epsilon**: 0.001

## Camera

- **eye**: [2.7750000953674316, 2.7750000953674316, 2.7750000953674316]
- **center**: [2.7750000953674316, 3.200000047683716, 12.774999618530273]
- **up**: [0.0, 1.0, 0.0]
- **fov**: 50.0
- **focal_distance**: 1.0
- **aspect**: 1.3333333333333333

## Objetos (detalhado)

### Objeto 1: Rotate
- **shape_chain**: ['Rotate', 'Translate', 'Box']
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **diffuse**: [0.5, 0.5, 0.5]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 10.0

### Objeto 2: Sphere
- **center**: [2.7750000953674316, 3.200000047683716, 12.774999618530273]
- **radius**: 1.0
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.10000000149011612, 0.0, 0.0]
  - **diffuse**: [0.699999988079071, 0.0, 0.0]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 50.0

### Objeto 3: Plane
- **pos**: [0.0, -1.0, 0.0]
- **normal**: [0.0, 1.0, 0.0]
- **material**:
  - **type**: PhongMaterial
  - **ambient**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **diffuse**: [0.5, 0.5, 0.5]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 10.0

## Luzes (detalhado)

- **Light 1**:
  - pos: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
  - power: [150.0, 150.0, 150.0]

## Debug (raw JSON)

```json
{
  "render": {
    "name": "main_scene",
    "width": 800,
    "height": 600,
    "samples_per_pixel": 1,
    "sampling_mode": "jittered",
    "seed": null,
    "gamma_fix": false
  },
  "scene": {
    "ambient_light": [
      0.30000001192092896,
      0.30000001192092896,
      0.30000001192092896
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
      2.7750000953674316,
      2.7750000953674316,
      2.7750000953674316
    ],
    "center": [
      2.7750000953674316,
      3.200000047683716,
      12.774999618530273
    ],
    "up": [
      0.0,
      1.0,
      0.0
    ],
    "fov": 50.0,
    "focal_distance": 1.0,
    "aspect": 1.3333333333333333
  },
  "objects": [
    {
      "type": "Rotate",
      "shape_chain": [
        "Rotate",
        "Translate",
        "Box"
      ],
      "material": {
        "type": "PhongMaterial",
        "ambient": [
          0.10000000149011612,
          0.10000000149011612,
          0.10000000149011612
        ],
        "diffuse": [
          0.5,
          0.5,
          0.5
        ],
        "specular": [
          1.0,
          1.0,
          1.0
        ],
        "shininess": 10.0
      }
    },
    {
      "type": "Sphere",
      "center": [
        2.7750000953674316,
        3.200000047683716,
        12.774999618530273
      ],
      "radius": 1.0,
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
          0.10000000149011612,
          0.10000000149011612,
          0.10000000149011612
        ],
        "diffuse": [
          0.5,
          0.5,
          0.5
        ],
        "specular": [
          1.0,
          1.0,
          1.0
        ],
        "shininess": 10.0
      }
    }
  ],
  "lights": [
    {
      "pos": [
        2.7750000953674316,
        5.550000190734863,
        2.7750000953674316
      ],
      "power": [
        150.0,
        150.0,
        150.0
      ]
    }
  ]
}
```

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.