# INF2608 — Fundamentos da Computação Gráfica (2026.1) — PUC-Rio

> **Aluno:** Yang Miranda

## Visão Geral

Este repositório concentra a implementação do projeto de traçado de raios em `src/ray_tracing_2`. O renderer segue a progressão dos slides de aula: começa com câmera pinhole, interseções geométricas e sombreamento local de Phong, e depois adiciona anti-aliasing, instanciação, luz de área, reflexão, refração, transmitância em raios de sombra, malhas triangulares e uma BVH local para `TriangleMesh`.

O pipeline principal é:

1. gerar amostras no pixel;
2. converter cada amostra em um raio primário pela câmera;
3. encontrar o `closest hit` na cena;
4. delegar a cor ao material atingido;
5. salvar a imagem e um `properties.md` em uma pasta timestamped dentro de `outputs/`.

O material teórico principal do projeto está em `4.tracado_de_raios.pdf`, `5.tracado_de_raios2.pdf` e `6.estrutura_aceleracao.pdf`. O relatório técnico mais recente está em `docs/relatorio-proj1.v5.md`.

## Funcionalidades Atuais

- câmera pinhole com base derivada de `eye`, `center` e `up`
- interseções com esfera, plano, caixa alinhada aos eixos e triângulo
- materiais `PhongMaterial`, `ReflectiveMaterial` e `TransparentMaterial`
- sombras duras e transmitância acumulada para materiais transparentes
- anti-aliasing por `jittered` e `stratified`
- luz pontual e luz de área retangular amostrada
- instanciação por transformação afim com normal por inversa transposta
- malhas triangulares com `TriangleMesh`
- BVH estática local a `TriangleMesh`, com poda por AABB
- geração automática de `render.png` e `properties.md` em `outputs/`

## Convenções Importantes

- `PointLight` **não** aplica queda explícita de $1/r^2$ no próprio modelo da fonte. Nesta base, `power` é tratado como radiância constante da luz, conforme a convenção adotada no projeto.
- `AreaLight` já usa amostragem sobre um emissor retangular com decaimento geométrico explícito por distância.
- A aceleração por BVH é **local à malha triangular**. O nível superior da cena ainda percorre `scene.objects` linearmente.
- `focal_distance` em `Camera` controla apenas a distância geométrica do plano de projeção no modelo pinhole; não há lente fina nem profundidade de campo.

## Setup

### Opção 1: script do projeto

```bash
./scripts/setup_dev.sh
source .venv/bin/activate
```

O script cria `.venv`, instala `requirements.txt` e roda `pip install -e .`.

### Opção 2: setup manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Execução

Depois de ativar o ambiente e instalar o pacote em modo editável, execute como módulo:

```bash
python -m ray_tracing_2
```

Ou escolha explicitamente uma cena. Para uma validação rápida e reprodutível, os exemplos abaixo usam `800x600` e `--spp 1`:

```bash
python -m ray_tracing_2.main --width 800 --height 600 --spp 1
python -m ray_tracing_2.main_area_light --width 800 --height 600 --spp 1 --sampling_mode stratified --light_sampling_mode regular
python -m ray_tracing_2.cornell_box --width 800 --height 600 --spp 1 --sampling_mode jittered --light_sampling_mode uniform
python -m ray_tracing_2.main_triangles --width 800 --height 600 --spp 1 --scene inputs/triangle_pyramid.json --accelerator bvh
python -m ray_tracing_2.generate_scene --input inputs/example_scene.json --width 800 --height 600 --spp 1
```

Nos entrypoints com `AreaLight`, os controles públicos de amostragem permanecem separados:

- `--sampling_mode` controla apenas o anti-aliasing do filme
- `--light_sampling_mode` controla apenas o padrão 2D usado na integração sobre a fonte de área

Se preferir não instalar o pacote, use `PYTHONPATH=src` na raiz do repositório:

```bash
PYTHONPATH=src python -m ray_tracing_2.main_area_light --width 800 --height 600 --spp 1 --sampling_mode jittered --light_sampling_mode stratified
```

Cada execução produz uma nova pasta em `outputs/` contendo pelo menos:

- `render.png`
- `properties.md`

## Estrutura Relevante

| Caminho                             | Papel                                                          |
| ----------------------------------- | -------------------------------------------------------------- |
| `src/ray_tracing_2/camera.py`       | câmera pinhole e geração de raios primários                    |
| `src/ray_tracing_2/film.py`         | amostragem por pixel, buffer e gravação da imagem              |
| `src/ray_tracing_2/scene.py`        | interseção global, offset, transmitância e recursão            |
| `src/ray_tracing_2/material.py`     | Phong local, reflexão e refração                               |
| `src/ray_tracing_2/light.py`        | `PointLight`, `AreaLight` e `AmbientLight`                     |
| `src/ray_tracing_2/shape.py`        | primitivas analíticas, triângulos, `TriangleMesh` e `Instance` |
| `src/ray_tracing_2/triangle_bvh.py` | BVH local para malhas triangulares                             |
| `src/ray_tracing_2/render.py`       | criação de pasta de saída e serialização de metadados          |
| `docs/relatorio-proj1.v5.md`        | relatório técnico-científico consolidado                       |
| `docs/AA_IMPLEMENTATION.md`         | nota específica sobre anti-aliasing                            |
| `docs/UNDOCUMENTED_FEATURES.md`     | nuances e limitações não expandidas no README                  |

## Scripts de Cena

| Módulo                              | Uso principal                                 |
| ----------------------------------- | --------------------------------------------- |
| `ray_tracing_2.main`                | cena mínima para o núcleo do Slide 4          |
| `ray_tracing_2.main_area_light`     | penumbra com `AreaLight`                      |
| `ray_tracing_2.main_ellipse`        | instanciação com escala não uniforme          |
| `ray_tracing_2.main_box`            | cena tipo Cornell com blocos instanciados     |
| `ray_tracing_2.main_triangles`      | malha triangular e BVH local                  |
| `ray_tracing_2.cornell_box_pyramid` | integração de triângulos, reflexão e refração |
| `ray_tracing_2.generate_scene`      | cena dirigida por JSON                        |
| `ray_tracing_2.random_scene`        | geração de cenas aleatórias com documentação  |

## Referências do Curso

- `materiais/traçado_de_raios/4.tracado_de_raios.pdf`
- `materiais/traçado_de_raios/5.tracado_de_raios2.pdf`
- `materiais/traçado_de_raios/6.estrutura_aceleracao.pdf`
- `docs/relatorio-proj1.v5.md`

## Limitações Atuais

- não há lente fina, profundidade de campo nem path tracing global
- `PointLight` e `AreaLight` seguem convenções radiométricas diferentes nesta base
- não há grade regular, SAH, BVH linearizada ou acelerador global da cena
- algumas cenas auxiliares antigas ainda servem mais como laboratório do que como interface final do projeto
