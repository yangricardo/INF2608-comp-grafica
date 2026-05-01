# Relatorio Projeto 1 v5 - TODO

## Escopo e precedencia de fontes

Este arquivo gerencia o que ja foi avaliado, o que ainda precisa ser confirmado
e o que deve entrar no `relatorio-proj1.v5.md`.

Status atual: `relatorio-proj1.v5.md` redigido, validado sem erros no workspace e
com citacoes de codigo consolidadas. Documentacao secundaria principal tambem
alinhada ao estado real de `ray_tracing_2`.

Ordem de confianca obrigatoria durante a redacao:

1. `4.tracado_de_raios.pdf`, `5.tracado_de_raios2.pdf`, `6.estrutura_aceleracao.pdf`
2. Resumos em `materiais/traçado_de_raios/*.md`
3. Codigo e comentarios inline em `src/ray_tracing_2/`
4. Documentacao em `docs/*.md`

Legenda de status:

- `[ ]` ainda nao consolidado no relatorio
- `[~]` em analise / revisao
- `[x]` consolidado e revisado
- `[!]` teorico nos slides, mas parcial ou ausente na implementacao

## Matriz de topicos

| Status | Bloco   | Topico                                                                       | PDF / paginas ou intervalo                  | Complemento em `materiais/*.md`                                                 | Apoio PBRT 4e permitido                                                                                                           | Implementacao / observacoes                                                                |
| ------ | ------- | ---------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| [x]    | Slide 4 | Visao geral do algoritmo por pixel, visibilidade e sombreamento local        | `4.tracado_de_raios.pdf`, pp. 2-6           | `4.tracado_de_raiosv2.md`, sec. 1; `4.tracado_de_raiosv1.md`, sec. 1            | 1.2 `Photorealistic Rendering and the Ray-Tracing Algorithm`                                                                      | Consolidado no v5 com ancoragem em `main.py` e `scene.py::trace_ray`                       |
| [x]    | Slide 4 | Raio parametrico, interpretacao de `t`, hit `(p, n)` e orientacao de face    | `4.tracado_de_raios.pdf`, pp. 7-9           | `4.tracado_de_raiosv2.md`, sec. 2; `4.tracado_de_raiosv1.md`, sec. 1            | 3.5 `Normals`, 3.6 `Rays`, 3.11 `Interactions`                                                                                    | Consolidado com rastreio em `ray.py`, `hit.py`, `shape.py` e `scene.py`                    |
| [x]    | Slide 4 | Intersecao raio-plano                                                        | `4.tracado_de_raios.pdf`, pp. 10-13         | `4.tracado_de_raiosv2.md`, sec. 2; `4.tracado_de_raiosv1.md`, sec. 2            | 3.3 `Vectors`, 3.4 `Points`                                                                                                       | Consolidado com `shape.py::Plane.intersect`                                                |
| [x]    | Slide 4 | Intersecao raio-esfera, discriminante e raiz positiva mais proxima           | `4.tracado_de_raios.pdf`, pp. 14-18         | `4.tracado_de_raiosv2.md`, sec. 2; `4.tracado_de_raiosv1.md`, sec. 2            | 6.2 `Spheres`, 6.8 `Managing Rounding Error`                                                                                      | Consolidado com `shape.py::Sphere.intersect`                                               |
| [x]    | Slide 4 | Epsilon numerico e prevencao de auto-intersecao                              | `4.tracado_de_raios.pdf`, p. 18             | `4.tracado_de_raiosv1.md`, sec. 2; `4.tracado_de_raiosv2.md`, sec. 2            | 6.8 `Managing Rounding Error`                                                                                                     | Consolidado com `scene.py::offset_point` e limiares de intersecao                          |
| [x]    | Slide 4 | Camera pinhole, base ortonormal e parametros extrinsecos                     | `4.tracado_de_raios.pdf`, pp. 19-23         | `4.tracado_de_raiosv1.md`, sec. 3; `4.tracado_de_raiosv2.md`, secs. 3-4         | 5.1 `Camera Interface`, 5.2 `Projective Camera Models`, 3.9 `Transformations`                                                     | Consolidado com `camera.py::Camera.__init__`                                               |
| [x]    | Slide 4 | Filme, amostragem central do pixel e geracao de raios primarios              | `4.tracado_de_raios.pdf`, pp. 24-29         | `4.tracado_de_raiosv2.md`, secs. 3 e 5                                          | 5.4 `Film and Imaging`, 8.1 `Sampling Theory`                                                                                     | Consolidado com `film.py::get_sample`, `camera.py::generate_ray` e `film.py::render`       |
| [x]    | Slide 4 | Mudanca de base, matriz de visualizacao e espacos local/global               | `4.tracado_de_raios.pdf`, pp. 31-39         | `4.tracado_de_raiosv1.md`, sec. 3; `4.tracado_de_raiosv2.md`, sec. 4            | 3.9 `Transformations`, 3.10 `Applying Transformations`                                                                            | Consolidado com `camera.py::inv_view` e cenas ancora                                       |
| [x]    | Slide 4 | Luz pontual, termo ambiente e modelo de Phong                                | `4.tracado_de_raios.pdf`, pp. 40-43 e 54-55 | `4.tracado_de_raiosv1.md`, sec. 4; `4.tracado_de_raiosv2.md`, sec. 6            | 4.1 `Radiometry`, 4.3 `Surface Reflection`, 12.1 `Light Interface`, 12.2 `Point Lights`                                           | Consolidado com a ressalva do projeto: `PointLight` sem queda `1/r^2`                      |
| [x]    | Slide 4 | Raios de sombra, visibilidade direta e sombras duras                         | `4.tracado_de_raios.pdf`, pp. 51-53         | `4.tracado_de_raiosv1.md`, sec. 5                                               | 12.6 `Light Sampling`, 13.1 `The Light Transport Equation`                                                                        | Consolidado com `scene.py::transmittance` e `light.py::PointLight.radiance`                |
| [x]    | Slide 5 | Antialiasing como integracao Monte Carlo e reducao de aliasing               | `5.tracado_de_raios2.pdf`, pp. 4-9          | `5.tracado_de_raios2_1.md`, sec. I; `5.tracado_de_raios2_3.md`, sec. 2          | 2.1 `Monte Carlo: Basics`, 2.2 `Improving Efficiency`, 8.1 `Sampling Theory`, 8.4 `Independent Sampler`, 8.5 `Stratified Sampler` | Consolidado com `film.py::get_samples_for_pixel` e a extensao `stratified`                 |
| [x]    | Slide 5 | Instanciacao, coordenadas homogeneas e nao comutatividade de transformacoes  | `5.tracado_de_raios2.pdf`, pp. 10-20        | `5.tracado_de_raios2_1.md`, sec. II; `5.tracado_de_raios2_3.md`, sec. 3         | 3.9 `Transformations`, 3.10 `Applying Transformations`                                                                            | Consolidado com `shape.py::Instance` e cenas `main_box.py` / `main_triangles.py`           |
| [x]    | Slide 5 | Transformacao correta de normais por inversa transposta                      | `5.tracado_de_raios2.pdf`, pp. 10-20        | `5.tracado_de_raios2_1.md`, sec. II; `5.tracado_de_raios2_3.md`, sec. 3         | 3.5 `Normals`, 3.10 `Applying Transformations`                                                                                    | Consolidado com `shape.py::Instance.intersect`                                             |
| [x]    | Slide 5 | Luz de area, integracao sobre a fonte e penumbra                             | `5.tracado_de_raios2.pdf`, pp. 14-23        | `5.tracado_de_raios2_1.md`, sec. III; `5.tracado_de_raios2_3.md`, sec. 4        | 12.4 `Area Lights`, 12.6 `Light Sampling`                                                                                         | Consolidado com `light.py::AreaLight.sample_radiance` e `main_area_light.py`               |
| [x]    | Slide 5 | Caixa/AABB e metodo de slabs como primitiva e volume de contencao            | `5.tracado_de_raios2.pdf`, pp. 24-25        | `5.tracado_de_raios2_1.md`, sec. IV; `5.tracado_de_raios2_3.md`, sec. 5         | 3.7 `Bounding Boxes`                                                                                                              | Consolidado com `shape.py::Box.intersect` e `triangle_bvh.py::AABB.intersects`             |
| [x]    | Slide 5 | Transicao de tracador local para tracador recursivo e limite de profundidade | `5.tracado_de_raios2.pdf`, pp. 26-35        | `5.tracado_de_raios2_3.md`, secs. 6-7                                           | 1.2 `Photorealistic Rendering and the Ray-Tracing Algorithm`, 13.1 `The Light Transport Equation`                                 | Consolidado com `scene.py::can_spawn_ray` e `scene.py::trace_ray`                          |
| [x]    | Slide 5 | Reflexao especular com Fresnel-Schlick                                       | `5.tracado_de_raios2.pdf`, pp. 26-28        | `5.tracado_de_raios2_1.md`, sec. V; `5.tracado_de_raios2_3.md`, sec. 6          | 9.3 `Specular Reflection and Transmission`, 9.4 `Conductor BRDF`                                                                  | Consolidado com `material.py::ReflectiveMaterial.eval`                                     |
| [x]    | Slide 5 | Refracao dielétrica, Lei de Snell e reflexao interna total                   | `5.tracado_de_raios2.pdf`, pp. 29-36        | `5.tracado_de_raios2_1.md`, sec. VI; `5.tracado_de_raios2_3.md`, sec. 7         | 9.3 `Specular Reflection and Transmission`, 9.5 `Dielectric BSDF`                                                                 | Consolidado com `material.py::TransparentMaterial.eval`                                    |
| [x]    | Slide 5 | Lei de Beer-Lambert e transmitancia acumulada em raios de sombra             | `5.tracado_de_raios2.pdf`, pp. 33-35        | `5.tracado_de_raios2_1.md`, sec. VI; `5.tracado_de_raios2_3.md`, sec. 7         | 11.2 `Transmittance`, 12.6 `Light Sampling`                                                                                       | Consolidado com `TransparentMaterial.shadow_transmittance` e `scene.py::transmittance`     |
| [x]    | Slide 6 | Geometria do triangulo, area orientada e coordenadas baricentricas           | `6.estrutura_aceleracao.pdf`, pp. 3-4       | `6.estrutura_aceleracaov1.md`, sec. 2; `6.estrutura_aceleracaov2.md`, sec. 1    | 6.5 `Triangle Meshes`                                                                                                             | Consolidado com `shape.py::Triangle` e `main_triangles.py`                                 |
| [x]    | Slide 6 | Intersecao raio-triangulo por Moller-Trumbore e Regra de Cramer              | `6.estrutura_aceleracao.pdf`, pp. 5-12      | `6.estrutura_aceleracaov1.md`, sec. 3; `6.estrutura_aceleracaov2.md`, sec. 1    | 6.5 `Triangle Meshes`                                                                                                             | Consolidado com `shape.py::Triangle.intersect`                                             |
| [x]    | Slide 6 | Malhas triangulares, conectividade e carregamento de geometria               | `6.estrutura_aceleracao.pdf`, pp. 13-14     | `6.estrutura_aceleracaov1.md`, sec. 4; `6.estrutura_aceleracaov2.md`, sec. 2    | 6.5 `Triangle Meshes`, 7.1 `Primitive Interface and Geometric Primitives`                                                         | Consolidado com `shape.py::TriangleMesh` e `main_triangles.py`                             |
| [!]    | Slide 6 | Grade regular, SAT e percorrimento incremental                               | `6.estrutura_aceleracao.pdf`, pp. 15-21     | `6.estrutura_aceleracaov1.md`, sec. 5; `6.estrutura_aceleracaov2.md`, sec. 3    | 7.2 `Aggregates`                                                                                                                  | Nao implementado neste repositorio; tratar como conteudo teorico comparativo               |
| [x]    | Slide 6 | BVH, caixas envolventes, construcao e poda de subarvores                     | `6.estrutura_aceleracao.pdf`, pp. 22-36     | `6.estrutura_aceleracaov1.md`, secs. 5-6; `6.estrutura_aceleracaov2.md`, sec. 4 | 7.3 `Bounding Volume Hierarchies`, 3.7 `Bounding Boxes`                                                                           | Consolidado no v5 como BVH estatica local a `TriangleMesh`, com median split e poda AABB   |
| [!]    | Slide 6 | SAH, compactacao linear e percurso com pilha                                 | `6.estrutura_aceleracao.pdf`, pp. 30-36     | `6.estrutura_aceleracaov2.md`, sec. 4                                           | 7.3 `Bounding Volume Hierarchies`                                                                                                 | Implementacao parcial: ha median split e poda por AABB, mas nao ha SAH nem BVH linearizada |

## Checklist de comentarios e documentacao

### Python

- [x] `camera.py`: explicitar melhor a diferenca entre `focal_distance` no modelo pinhole e modelos de lente fina
- [x] `film.py`: uniformizar referencias de paginas e separar amostragem central de AA Monte Carlo
- [x] `material.py`: marcar `PhongMaterial.eval` como nucleo local reutilizado por materiais recursivos
- [x] `material.py`: documentar que o rateio entre termo local e reflexao recursiva e uma aproximacao energetica
- [x] `scene.py`: condensar e alinhar o comentario de `transmittance()` com Slide 5, sem perder o papel de Beer-Lambert
- [x] `triangle_bvh.py`: explicitar que a BVH e estatica, local a `TriangleMesh` e usa median split em vez de SAH

### Markdown secundario

- [x] `README.md`: revisar afirmacoes desatualizadas sobre `ray_tracing_1` versus `ray_tracing_2`
- [x] `docs/AA_IMPLEMENTATION.md`: conferir consistencia terminologica com os slides e o codigo atual
- [x] `docs/UNDOCUMENTED_FEATURES.md`: revisar onde a descricao fisica conflitar com o comportamento real do renderer

## Casos curtos para validacao experimental no v5

- [x] `main.py`: cena minima para pipeline basico do Slide 4
- [x] `main_area_light.py`: penumbra e amostragem de luz de area
- [x] `main_ellipse.py` ou `main_box.py`: instanciação, transformacoes e normais
- [x] `main_triangles.py`: malha triangular e BVH local
- [x] `cornell_box_pyramid.py`: reflexao/refracao em uma cena fechada com malhas triangulares

## Congelamento futuro das citacoes de codigo

Concluido apos o pass de comentarios e a redacao do v5.

- [x] `camera.py`: `Camera.__init__`, `Camera.generate_ray`
- [x] `film.py`: `SamplingMode`, `get_sample`, `get_samples_for_pixel`, `render`
- [x] `hit.py`: `Hit.__init__`, `Hit.set_face_normal`
- [x] `scene.py`: `compute_intersection`, `offset_point`, `can_spawn_ray`, `transmittance`, `trace_ray`
- [x] `light.py`: `PointLight.radiance`, `AreaLight.sample_radiance`, `AreaLight.radiance`, `Light.radiance`
- [x] `material.py`: `Material.shadow_transmittance`, `PhongMaterial.direct_lighting`, `PhongMaterial.eval`, `ReflectiveMaterial.eval`, `TransparentMaterial.shadow_transmittance`, `TransparentMaterial.eval`
- [x] `shape.py`: `Sphere.intersect`, `Plane.intersect`, `Box.intersect`, `Triangle.intersect`, `TriangleMesh`, `Instance`
- [x] `triangle_bvh.py`: `AABB.intersects`, `TriangleBVHNode.intersect`, `TriangleBVH._build`, `TriangleBVH._collect_stats`
- [x] Cenas ancora: `main.py`, `main_area_light.py`, `main_box.py`, `main_triangles.py`, `cornell_box_pyramid.py`
