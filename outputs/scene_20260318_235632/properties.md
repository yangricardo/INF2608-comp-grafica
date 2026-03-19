# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Valores usados (numéricos)

```json
{
  "spheres": [
    {
      "center": [
        -6.0,
        0.0,
        0.0
      ],
      "radius": 1.0,
      "material": {
        "ambient": [
          0.02,
          0.02,
          0.02
        ],
        "diffuse": [
          0.9,
          0.9,
          0.1
        ],
        "specular": [
          0.1,
          0.1,
          0.1
        ],
        "shininess": 16
      }
    },
    {
      "center": [
        -2.5,
        0.0,
        0.5
      ],
      "radius": 0.9,
      "material": {
        "ambient": [
          0.02,
          0.02,
          0.02
        ],
        "diffuse": [
          0.1,
          0.7,
          0.1
        ],
        "specular": [
          0.1,
          0.1,
          0.1
        ],
        "shininess": 16
      }
    },
    {
      "center": [
        0.0,
        0.0,
        0.0
      ],
      "radius": 1.1,
      "material": {
        "ambient": [
          0.02,
          0.02,
          0.02
        ],
        "diffuse": [
          0.1,
          0.1,
          0.8
        ],
        "specular": [
          0.1,
          0.1,
          0.1
        ],
        "shininess": 16
      }
    },
    {
      "center": [
        3.0,
        0.0,
        -0.5
      ],
      "radius": 0.95,
      "material": {
        "ambient": [
          0.02,
          0.02,
          0.02
        ],
        "diffuse": [
          0.6,
          0.2,
          0.7
        ],
        "specular": [
          0.1,
          0.1,
          0.1
        ],
        "shininess": 16
      }
    },
    {
      "center": [
        7.0,
        0.0,
        0.0
      ],
      "radius": 1.0,
      "material": {
        "ambient": [
          0.02,
          0.02,
          0.02
        ],
        "diffuse": [
          0.8,
          0.1,
          0.1
        ],
        "specular": [
          0.1,
          0.1,
          0.1
        ],
        "shininess": 16
      }
    }
  ],
  "plane": {
    "y": -1.5,
    "material": {
      "ambient": [
        0.02,
        0.02,
        0.02
      ],
      "diffuse": [
        0.45,
        0.45,
        0.45
      ],
      "specular": [
        0.0,
        0.0,
        0.0
      ],
      "shininess": 1
    }
  },
  "lights": [
    {
      "pos": [
        -12.0,
        6.0,
        4.0
      ],
      "power": [
        500,
        500,
        500
      ]
    }
  ]
}
```

## O que significa cada valor (explicação para leigos)

- **Spheres**: lista de esferas; cada uma tem `center` (posição [x,y,z]) e `radius` (tamanho).
- **Plane - `y`**: altura do piso; valores menores colocam o piso mais abaixo.
- **Material - `ambient`**: iluminação ambiente (suave).
- **Material - `diffuse`**: cor principal sob luz direta.
- **Material - `specular`**: cor/intensidade do brilho (pequenos reflexos).
- **Material - `shininess`**: controla quão pequeno/afiado é o brilho especular.
- **Lights - `pos`**: posição da fonte; **power**: intensidade por canal (R,G,B).

> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.