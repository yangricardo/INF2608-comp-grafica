# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Objetos (detalhado)

### Objeto 1: Box
- **material**:
  - **ambient**: [0.10000000149011612, 0.10000000149011612, 0.10000000149011612]
  - **diffuse**: [0.7300000190734863, 0.7300000190734863, 0.7300000190734863]
  - **specular**: [0.5, 0.5, 0.5]
  - **shininess**: 50.0

### Objeto 2: Sphere
- **center**: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
- **radius**: 0.1
- **material**:
  - **ambient**: [1.0, 1.0, 1.0]
  - **diffuse**: [1.0, 1.0, 1.0]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 0.0

## Luzes (detalhado)

- **Light 1**:
  - pos: [0.699999988079071, 0.699999988079071, 0.699999988079071]
  - power: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]

## Debug (raw JSON)

```json
{
  "objects": [
    {
      "type": "Box",
      "p_min": [
        1.5,
        0.0,
        1.5
      ],
      "p_max": [
        4.0,
        2.5,
        4.0
      ],
      "material": {
        "ambient": [
          0.10000000149011612,
          0.10000000149011612,
          0.10000000149011612
        ],
        "diffuse": [
          0.7300000190734863,
          0.7300000190734863,
          0.7300000190734863
        ],
        "specular": [
          0.5,
          0.5,
          0.5
        ],
        "shininess": 50.0
      }
    },
    {
      "type": "Sphere",
      "center": [
        2.7750000953674316,
        5.550000190734863,
        2.7750000953674316
      ],
      "radius": 0.1,
      "material": {
        "ambient": [
          1.0,
          1.0,
          1.0
        ],
        "diffuse": [
          1.0,
          1.0,
          1.0
        ],
        "specular": [
          0.0,
          0.0,
          0.0
        ],
        "shininess": 0.0
      }
    }
  ],
  "lights": [
    {
      "pos": [
        0.699999988079071,
        0.699999988079071,
        0.699999988079071
      ],
      "power": [
        2.7750000953674316,
        5.550000190734863,
        2.7750000953674316
      ]
    }
  ]
}
```

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.