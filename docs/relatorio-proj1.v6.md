# Relatorio Tecnico-Cientifico: Projeto 1 v6

## 1. Escopo e criterio de leitura

Esta versao reorganiza a analise por requisitos do enunciado (`materiais/proj1.pdf`),
com referencia secundaria aos slides e ao PBRT. O criterio principal e responder
cada requisito com uma cena dedicada, comando reproduzivel e evidencia visual.

Decisoes metodologicas desta versao:

- manter a mesma configuracao de camera entre as cenas principais;
- variar apenas objetos, materiais e luzes para isolar cada requisito;
- limitar os testes de validacao rapida a `800x600` com `--spp 1..4`.

## 2. Mapeamento requisito -> modulo

| Requisito                                  | Modulo                                          | Objetivo de validacao                                              |
| ------------------------------------------ | ----------------------------------------------- | ------------------------------------------------------------------ |
| R1: instanciacao de esferas e caixas       | `src/ray_tracing_2/proj1_req1_geometry.py`      | validar composicao geometrica basica sem depender de extras        |
| R2: uma ou mais fontes pontuais            | `src/ray_tracing_2/proj1_req2_point_lights.py`  | isolar contribuicao de multiplas `PointLight`                      |
| R3: iluminacao direta em Phong com sombras | `src/ray_tracing_2/proj1_req3_phong_shadows.py` | validar difusa/especular e sombras duras                           |
| R4: multiplas amostras por pixel           | `src/ray_tracing_2/proj1_req4_sampling.py`      | comparar `center` vs amostragem estocastica no mesmo enquadramento |

## 3. Requisito 1: instanciacao de esferas e caixas

Cena ancora: `proj1_req1_geometry.py`.

A cena usa a sala tipo Cornell e adiciona apenas primitivas requeridas:
caixas instanciadas (`Instance`) e esfera. Nao ha triangulos nem luz de area
neste requisito principal. A iluminacao e fornecida exclusivamente pelo
`AmbientLight` com intensidade elevada para revelar a geometria sem dependencia
de fontes pontuais.

Comando de validacao basica:

```bash
python -m ray_tracing_2.proj1_req1_geometry --width 800 --height 600 --spp 1 --sampling_mode center
```

Evidencia (800x600, spp=1, center, ~9.4 s):

![R1 geometry](../outputs/proj1_req1_geometry_20260502_121509/render.png)

Resultado: sala Cornell com dois `Instance(Box)` rotacionados e uma `Sphere`,
todos visiveis pela iluminacao ambiente; nenhuma fonte de luz pontual nesta cena.

## 4. Requisito 2: luz pontual

Cena ancora: `proj1_req2_point_lights.py`.

A cena preserva a mesma camera do requisito 1 e altera apenas configuracao de
luzes, usando tres `PointLight` para separar contribuicoes de key/fill/back
sem introduzir fonte extensa. Materiais Phong com componente especular variada
permitem observar que cada luz contribui de forma espacialmente distinta.

Comando de validacao basica:

```bash
python -m ray_tracing_2.proj1_req2_point_lights --width 800 --height 600 --spp 1 --sampling_mode center
```

Evidencia (800x600, spp=1, center, ~19.7 s):

![R2 point lights](../outputs/proj1_req2_point_lights_20260502_121731/render.png)

Resultado: tres `PointLight` com potencias e posicoes distintas; duas esferas
Phong com shininess diferente permitem comparar highlight angular entre materiais.

## 5. Requisito 3: Phong + sombras

Cena ancora: `proj1_req3_phong_shadows.py`.

Aqui a leitura principal e a resposta angular do modelo de Phong e a formacao
visivel de sombras duras via `Scene.transmittance()` para o caso opaco.
Dois materiais Phong distintos (matte vermelho e glossy azul) evidenciam a
diferenca entre alta e baixa shininess.

Comando de validacao basica:

```bash
python -m ray_tracing_2.proj1_req3_phong_shadows --width 800 --height 600 --spp 1 --sampling_mode center
```

Evidencia (800x600, spp=1, center, ~20.1 s):

![R3 Phong shadows](../outputs/proj1_req3_phong_shadows_20260502_121809/render.png)

Resultado: sombras duras visiveis; diferenca entre componente difusa lambertiana
e highlight especular focado observavel nos dois blocos de materiais distintos.

## 6. Requisito 4: multiplas amostras por pixel

Cena ancora: `proj1_req4_sampling.py`.

A geometria foi montada para enfatizar arestas e contraste (caixas finas e
esferas branca/preta), facilitando comparacoes entre configuracoes de amostragem
com o mesmo enquadramento.

Comandos recomendados:

```bash
python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 1 --sampling_mode center
python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 4 --sampling_mode jittered --seed 42
python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 4 --sampling_mode stratified --seed 42
```

Evidencia baseline (800x600, spp=1, center, ~20.7 s):

![R4 sampling center](../outputs/proj1_req4_sampling_20260502_122009/render.png)

Para comparar aliasing vs anti-aliasing execute os comandos `jittered` e
`stratified` acima (spp=4, ~80-85 s) e compare com o baseline `center`.

Nota de aderencia: na implementacao atual, a distribuicao uniforme aleatoria no
pixel e materializada internamente por `uniform_samples_2d()` e exposta no modo
publico `jittered`.
pixel e materializada internamente por `uniform_samples_2d()` e exposta no modo
publico `jittered`.

## 7. Requisitos adicionais e limites atuais

Itens como triangulos, BVH local de malha e luz de area ficam no bloco de
requisitos adicionais. Eles sao importantes para a analise tecnica, mas nao
substituem a evidencia principal dos requisitos 1-4.

Limitacoes relevantes mantidas da versao anterior:

- sem acelerador global de cena;
- camera estritamente pinhole;
- convencoes radiometricas simplificadas para `PointLight`.

## 8. Conclusao da rodada de implementacao

A estrutura `proj1_*` permite uma leitura 1:1 dos requisitos principais com
mesma camera e variacao controlada da cena. Essa organizacao melhora tanto a
clareza do relatorio quanto a reproducao experimental no workspace.
