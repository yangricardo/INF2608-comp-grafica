# Etapa 01 — Boilerplate do pacote `path_tracing/`

## Objetivo

Criar o pacote `src/path_tracing/` espelhando a arquitetura de `src/ray_tracing_2`, sem ainda implementar o integrador. Garantir que todos os módulos importam sem erro e que `proj2_smoke` renderiza uma esfera com cor = (n+1)/2 (normal-as-color).

**Pontos:** infraestrutura — pré-requisito de todos os 7.0 pts.

---

## Árvore final de `path_tracing/`

```
src/path_tracing/
├── __init__.py
├── camera.py              # lookAt + generate_ray (idêntico ao ray_tracing_2)
├── cli.py                 # argparse helpers compartilhados (CommonRenderOptions)
├── film.py                # SamplingMode center/jittered/stratified
├── hit.py                 # HitInfo: t, pos, normal, geo_normal, material, front_face
├── light.py               # wrapper: re-exporta lights/ para compatibilidade legada
├── material.py            # wrapper: re-exporta materials/ para compatibilidade legada
├── mis.py                 # balance_heuristic, power_heuristic(β=2)  ← NOVO
├── obj_loader.py          # loader .obj (herdado)
├── onb.py                 # ONB + frisvad_branchless()                ← NOVO
├── ray.py                 # Ray(origin, direction)
├── render.py              # Render.render_core() orquestra Film + integrador
├── render_estimator.py    # RayCountEstimator + RenderEstimator + calibração
├── render_snapshot.py     # Snapshot JSON/MD completo
├── sampling.py            # uniform_samples_2d, stratified + cosine_hemisphere, uniform_triangle
├── scene.py               # Scene: objects, lights, compute_intersection, offset_point
├── shape.py               # Sphere, Plane, Box, Triangle, TriangleMesh, Instance
├── triangle_bvh.py        # BVH AABB+slab+median split
│
├── bsdf/
│   ├── __init__.py        # re-exporta LambertianBSDF, EmissiveBSDF
│   ├── base.py            # BSDF ABC: eval(wo,wi), sample(wo,u), pdf(wo,wi)
│   ├── emissive.py        # EmissiveBSDF — terminal emissivo (Etapa 02)
│   └── lambertian.py      # LambertianBSDF — Lambertiana cosseno-ponderada (Etapa 02)
│
├── integrators/
│   ├── __init__.py        # re-exporta PathIntegrator
│   ├── base.py            # Integrator ABC: Li(ray, scene, sampler)
│   └── path_tracer.py     # PathIntegrator: bsdf_only | nee_only | mis
│
├── lights/
│   ├── __init__.py        # re-exporta Light, PointLight, AreaLight, RectAreaLight
│   ├── area.py            # AreaLight (interface legada)
│   ├── area_rect.py       # RectAreaLight: sample_Li, pdf_Li (Etapa 03)
│   ├── base.py            # Light ABC: sample_Li, pdf_Li, Le
│   └── point.py           # PointLight (interface legada + nova)
│
├── materials/             # materiais do Proj1 (PhongMaterial etc)
│   └── ...
│
└── scenes/
    └── __init__.py        # build_proj2_cornell_basic_scene()
```

---

## Base Ortonormal de Frisvad (`onb.py`)

Para amostrar o hemisfério de forma cosseno-ponderada (Método de Malley), precisamos de um frame local alinhado com a normal da superfície. A classe `ONB` implementa isso via **algoritmo de Frisvad branchless** (2012):

```
se n.z < -0.9999999:
    t = (0, -1, 0),  b = (-1, 0, 0)
senão:
    a = 1/(1+n.z)
    k = -n.x · n.y · a
    t = (1 - n.x² · a,  k,        -n.x)
    b = (k,              1-n.y²·a, -n.y)
```

Verificação: `dot(t, b) = 0`, `dot(t, n) = 0`, `dot(b, n) = 0`, `|t| ≈ |b| ≈ 1`.

Propriedades:

- **Sem ramos** (salvo o singular `n.z ≈ -1`): evita instabilidade numérica do método Gram-Schmidt com `sqrt(1 - n.z²)` próximo de zero
- **Sem normalização final**: Frisvad prova que a norma é quasi-unitária por construção

Uso no `PathIntegrator`:

```python
onb = ONB(hit.normal)
wi_local  = onb.global_to_local(-ray.d)   # wo em frame local
wi_global = onb.local_to_global(wi_sampled)  # direção amostrada → global
```

---

## Differenças arquiteturais: `ray_tracing_2` → `path_tracing`

| Aspecto          | `ray_tracing_2` (Proj 1)                                       | `path_tracing` (Proj 2)                                   |
| ---------------- | -------------------------------------------------------------- | --------------------------------------------------------- |
| **Material API** | `Material.eval(scene, hit, ray, depth, max_depth)` — recursivo | `BSDF.eval(wo, wi)` + `BSDF.sample(wo, u)` — frame-local  |
| **Integrador**   | `Scene.trace_ray()` — recursão Whitted                         | `PathIntegrator.Li()` — loop iterativo com β acumulado    |
| **Luzes**        | `PointLight`/`AreaLight.radiance()` em `direct_lighting()`     | `EmissiveBSDF` em `objects` + `RectAreaLight` em `lights` |
| **Terminação**   | `max_depth` fixo                                               | `min_depth=4` + RR (Etapa 05) + Le ao atingir emissivo    |
| **ONB**          | Não existe (Phong dispensa)                                    | `frisvad_branchless()` — converte frame local ↔ global    |
| **Calibração**   | `scene.trace_ray()` mede raios/s                               | `integrator.Li()` mede caminhos completos/s               |

---

## Smoke test — normal-as-color

**Comando:**

```bash
python -m path_tracing.scripts.proj2_smoke --width 256 --height 256
```

**Técnica:** ray-cast primário; ao atingir a esfera, `cor = (n + 1) / 2`, mapeando a normal de `[-1,1]³` para `[0,1]³`.

**Resultado esperado:** esfera com faces coloridas em azul/ciano/verde/vermelho conforme a orientação da normal.

---

## Referências

- **Slide 9** "Traçado de Caminhos II" — seção _HemisphereToGlobal_
- **PBRT 4e §3.3** _Vectors and Normals_ — CoordinateSystem
- **Frisvad, J.R.**, "Building an Orthonormal Basis from a 3D Unit Vector Without Normalization", _Journal of Graphics Tools_ 16(3):151–159, 2012. **DOI: 10.1080/2165347X.2012.689606**
