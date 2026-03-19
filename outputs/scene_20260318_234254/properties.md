# Propriedades da Simulação

![Imagem da Simulação](render.png)

## Valores usados (numéricos)

```json
{
  "spheres": [
    {
      "center": [
        -2.5,
        0.0,
        -0.3
      ],
      "radius": 0.8,
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
          0.3,
          0.3,
          0.3
        ],
        "shininess": 32
      }
    },
    {
      "center": [
        0.0,
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
          0.1,
          0.7,
          0.1
        ],
        "specular": [
          0.3,
          0.3,
          0.3
        ],
        "shininess": 32
      }
    },
    {
      "center": [
        2.5,
        0.0,
        0.3
      ],
      "radius": 0.8,
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
          0.3,
          0.3,
          0.3
        ],
        "shininess": 32
      }
    }
  ],
  "plane": {
    "y": -1.2,
    "material": {
      "ambient": [
        0.02,
        0.02,
        0.02
      ],
      "diffuse": [
        0.4,
        0.4,
        0.4
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
        0.0,
        0.75,
        3.0
      ],
      "power": [
        200,
        200,
        200
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