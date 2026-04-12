# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Objetos (detalhado)

### Objeto 1: Sphere
- **center**: [0.0, 0.0, 0.0]
- **radius**: 1.0
- **material**:
  - **ambient**: [0.07999999821186066, 0.0, 0.0]
  - **diffuse**: [0.75, 0.05000000074505806, 0.05000000074505806]
  - **specular**: [0.0, 0.0, 0.0]
  - **shininess**: 1.0

## Luzes (detalhado)

- **Light 1**:
  - pos: [0.0, 5.0, 5.0]
  - power: [150.0, 150.0, 150.0]

- **Light 2**:
  - pos: [2.7750000953674316, 5.550000190734863, 2.7750000953674316]
  - power: [250.0, 250.0, 250.0]

## Debug (raw JSON)

```json
{
  "objects": [
    {
      "type": "Sphere",
      "center": [
        0.0,
        0.0,
        0.0
      ],
      "radius": 1.0,
      "material": {
        "ambient": [
          0.07999999821186066,
          0.0,
          0.0
        ],
        "diffuse": [
          0.75,
          0.05000000074505806,
          0.05000000074505806
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
        0.0,
        5.0,
        5.0
      ],
      "power": [
        150.0,
        150.0,
        150.0
      ]
    },
    {
      "pos": [
        2.7750000953674316,
        5.550000190734863,
        2.7750000953674316
      ],
      "power": [
        250.0,
        250.0,
        250.0
      ]
    }
  ]
}
```

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.