# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Objetos (detalhado)

### Objeto 1: Rotate

### Objeto 2: Sphere
- **center**: [2.7750000953674316, 3.200000047683716, 12.774999618530273]
- **radius**: 1.0
- **material**:
  - **ambient**: [0.10000000149011612, 0.0, 0.0]
  - **diffuse**: [0.699999988079071, 0.0, 0.0]
  - **specular**: [1.0, 1.0, 1.0]
  - **shininess**: 50.0

### Objeto 3: Plane
- **pos**: [0.0, -1.0, 0.0]
- **normal**: [0.0, 1.0, 0.0]
- **material**:
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
  "objects": [
    {
      "type": "Rotate"
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