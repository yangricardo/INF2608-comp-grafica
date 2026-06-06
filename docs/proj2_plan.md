# Plano Mestre de Execução — Projeto 2 (INF2608): Path Tracer em Python

> **Curso:** INF2608 — Fundamentos de Computação Gráfica (PUC-Rio, Prof. Waldemar Celes)
> **Projeto:** Projeto 2 — Renderizador por Path Tracing
> **Linguagem/Bibliotecas obrigatórias:** Python ≥ 3.11, `pyglm` (`from pyglm import glm`), `pillow` (PIL). Nenhuma outra dependência pesada de renderização.
> **Base de código:** este projeto **estende** o pacote `src/ray_tracing_2` (ray tracer recursivo existente). O path tracer mora em um **novo** pacote `path_tracing/`.
> **Objetivo deste documento:** unificar todas as tentativas anteriores (incluindo `merge.md` e `path_tracing_plan.md`) em um único plano coerente, ordenado do mais simples ao mais complexo, com prompts prontos para cada etapa e referências técnicas precisas (slides do Prof. Celes, PBRT 4ª edição e três artigos de referência).

---

## TL;DR

- O Projeto 2 é entregue em **12 etapas independentes** (cada uma com um markdown próprio `etapa_NN_*.md` em `docs/proj2/`), começando pelo núcleo unidirecional (Etapa 02, que sozinha vale os 7.0 pts base) e progredindo por todos os extras possíveis (MIS, Russian Roulette, mesh light, refração, GGX, environment), culminando em BDPT (Etapa 10) e MLT/PSSMLT (Etapa 11) como “ir além”, com consolidação em LaTeX (Etapa 12) no mesmo molde do relatório do Projeto 1.
- Toda a arquitetura nova vive em `path_tracing/` (réplica adaptada de `src/ray_tracing_2` + módulos novos: `bsdf/`, `lights/`, `integrators/`, `mis.py`, `onb.py`), preservando o sistema de snapshots/CLI/render-estimator do Projeto 1 para garantir reprodutibilidade e auditabilidade — cada figura do relatório aponta para um diretório `out/proj2/etapa_NN_xxx/` com `image.png`, `properties.json`, `properties.md` e `command.txt`.
- As citações são precisas: PBRT 4e §2.2.3 (MIS), §2.2.4 (RR), §6.5 (triangle area sampling), §9.2 (Lambert), §9.5 (Dielectric), §9.6.1–9.6.5 (GGX/Torrance–Sparrow), §12.4–§12.6 (luzes), §13.1–§13.4 (path tracing), §A.5 (Malley); BDPT/MLT vêm de PBRT **3ª edição §16.3 e §16.4** (removidos do 4ed); papers: Veach & Guibas SIGGRAPH 1995 (DOI 10.1145/218380.218498), Misso et al. ACM TOG 2022 (DOI 10.1145/3528223.3530160), Seyb et al. ACM TOG 2024 (DOI 10.1145/3658121).

---

## Key Findings

1. **A 4ª edição do PBRT removeu o capítulo de métodos bidirecionais e MLT.** Portanto, as etapas 10 (BDPT) e 11 (MLT) devem ser citadas a partir do PBRT 3ª edição (§16.3 e §16.4 respectivamente), explicitando essa diferença no apêndice do relatório.
2. **A pontuação cumulativa dos extras simples já ultrapassa em muito os 3.0 pts esperados** (1.0 MIS + 2.0 RR + 1.0 mesh light + 2.0 refração + 1.0 GGX + 1.0 envmap = 8.0 “pts brutos” se somados, embora o enunciado limite extras a 3.0). BDPT+MLT são o “além”.
3. **A ordenação simples→complexa otimiza pré-requisitos**: NEE (Etapa 03) precede MIS (04), que precede RR (05); BDPT (10) precisa de luz por mesh (06), refração (07) e MIS (04); MLT (11) é construído sobre BDPT.
4. **A passagem do ray tracer recursivo do Projeto 1 para o path tracer é uma reescrita conceitual do integrador** (não da geometria): toda a infra de câmera/BVH/instancing/film/snapshot é reaproveitada; o que muda é `Scene.trace_ray()` → `Integrator.Li()` com throughput β.
5. **Validação de não-viés entre estimadores** (`bsdf_only`, `nee_only`, `mis`, `mis+rr`, `bdpt`, `mlt`) é o teste de regressão central — todos devem convergir para a mesma imagem em alto SPP.

---

## Details

### 1. Visão Geral e Arquitetura

#### 1.1 Layout proposto do pacote `path_tracing/`

```
path_tracing/
├── __init__.py
├── camera.py              # cópia adaptada de ray_tracing_2.camera (pinhole, lookAt, generate_ray)
├── ray.py                 # idem (Ray com origem e direção)
├── hit.py                 # idem (Hit com t, pos, normal, geo_normal, material, front_face)
├── shape.py               # Sphere/Plane/Box/Triangle/TriangleMesh/Instance + sample_area() novo
├── triangle_bvh.py        # idem (BVH local AABB+slab+median split)
├── sampling.py            # estendido: cosine_hemisphere(), uniform_triangle(), uniform_sphere(), VNDF-GGX
├── onb.py                 # NOVO: base ortonormal local (HemisphereToGlobal) — Frisvad JGT 2012
├── film.py                # idem (SamplingMode center/jittered/stratified) + acumulador robusto
├── scene.py               # adaptado: compute_intersection, offset_point, lista de luzes/emissivos
├── render.py              # adaptado: orquestra integrator + film + snapshot
├── render_estimator.py    # idem (estimador de raios e calibração)
├── render_snapshot.py     # idem + extensões (PathTracerSnapshot)
├── cli.py                 # subcomandos por cena (proj2_req*, proj2_ext*)
│
├── bsdf/                  # NOVO — BSDFs separadas do conceito de "Material" do Projeto 1
│   ├── __init__.py
│   ├── base.py            # interface BSDF.eval/sample/pdf
│   ├── lambertian.py      # f = rho/pi, amostragem cosseno
│   ├── dielectric.py      # Snell + Fresnel + Beer-Lambert
│   ├── microfacet_ggx.py  # Cook-Torrance, GGX (Walter 2007), Smith, Schlick
│   └── emissive.py        # luz como BSDF terminal
│
├── lights/                # NOVO
│   ├── __init__.py
│   ├── base.py            # interface Light.sample_Li / pdf_Li / Le
│   ├── area_rect.py       # luz retangular (cópia adaptada de AreaLight)
│   ├── area_mesh.py       # luz como malha (Etapa 06)
│   └── infinite.py        # environment light (Etapa 09)
│
├── integrators/           # NOVO — coração do projeto
│   ├── __init__.py
│   ├── base.py            # interface Integrator.Li(ray, scene, sampler)
│   ├── path_tracer.py     # Etapa 02 + 03 + 04 + 05 acumuladas
│   ├── bdpt.py            # Etapa 10
│   └── mlt.py             # Etapa 11 (PSSMLT)
│
└── mis.py                 # NOVO — balance_heuristic, power_heuristic(β=2)
```

#### 1.2 O que é copiado de `src/ray_tracing_2`

`ray.py`, `hit.py`, `triangle_bvh.py` e o esqueleto de `camera.py`, `film.py`, `render_estimator.py`, `render_snapshot.py` são copiados quase ipsis literis. Os arquivos `shape.py` e `sampling.py` são **estendidos** com:

- `Shape.sample_area(u: glm.vec2) -> (point, normal, area_pdf)` (Sphere, Triangle, TriangleMesh, Plane retangular finito).
- `sampling.cosine_hemisphere(u: glm.vec2) -> (glm.vec3, pdf)` — Método de Malley (PBRT 4e Apêndice A.5 *Sampling Multidimensional Functions*).
- `sampling.uniform_triangle(u) -> bary` com `b0 = 1−sqrt(u1)`, `b1 = sqrt(u1)·(1−u2)`, `b2 = sqrt(u1)·u2`.
- `sampling.uniform_sphere(u)` e `sampling.ggx_vndf(u, wo, alpha)` (Etapa 08).

#### 1.3 O que é **novo**

- `bsdf/` (separa o conceito de **BRDF físico** da reflexão recursiva do Projeto 1).
- `integrators/` (substitui o `Scene.trace_ray()` recursivo do Projeto 1 por um estimador Monte Carlo iterativo com acumulador `β`).
- `mis.py`, `onb.py`, `lights/area_mesh.py`, `lights/infinite.py`.

#### 1.4 Diferença conceitual: ray tracer recursivo × path tracer

| Aspecto | Ray Tracer (Projeto 1) | Path Tracer (Projeto 2) |
|---|---|---|
| **Equação resolvida** | Avaliação analítica de Phong + termo de reflexão/refração recursivo (Whitted) | Estimador Monte Carlo da Light Transport Equation / Path Integral (Kajiya, "The Rendering Equation", SIGGRAPH 1986; PBRT 4e §13.1–13.2) |
| **Iluminação direta** | Loop sobre luzes com `direct_lighting()` analítico | Amostra **uma** direção via BSDF e/ou luz, com pdf, e estima L_o pela média de N caminhos |
| **Iluminação indireta** | Inexistente (só reflexão especular) | Construção incremental do caminho com **throughput β** acumulado |
| **Terminação** | `max_depth` fixo (≈3–5) | `min_depth=4` (exigência do enunciado) + Russian Roulette (Etapa 05) |
| **Sombreamento** | Função analítica do material | Avaliação probabilística: `β *= f * |cos θ| / pdf` |
| **Convergência** | Determinística por pixel | Estocástica — mais SPP ⇒ menos ruído (variância ∝ 1/N) |
| **Saída** | Imagem nítida com baixíssimo SPP | Imagem ruidosa até SPP alto; o ruído é o sintoma central a controlar |

#### 1.5 Convenções de entregáveis

- **Cada etapa produz seu próprio markdown** com nome `etapa_NN_shortname.md` em `docs/proj2/`, contendo:
  1. Objetivo, requisitos atendidos, pontos.
  2. Arquivos/funções/classes implementados ou modificados.
  3. Fórmulas matemáticas explícitas.
  4. Citações precisas (slide com páginas, PBRT 4e §+título+URL, artigo com DOI).
  5. Cenas de validação + comandos CLI exatos (`python -m path_tracing.cli proj2_req2_lambert --spp 64 --depth 6 --out out/proj2/req2`).
  6. Critério de aceitação (imagem esperada, métrica esperada).
  7. Snapshot JSON/MD com hash da cena para reprodutibilidade.
- **Comentários do código** devem citar a referência primária no docstring: `# Ref: Slide 7 "Monte Carlo", pp. 12-18; PBRT 4e §2.2.3 Multiple Importance Sampling; Veach & Guibas SIGGRAPH 1995, Eq. 9 (DOI 10.1145/218380.218498).`
- O **CLI** segue o padrão do Projeto 1 (`proj1_req*_*`), agora com `proj2_req*_*` para os requisitos básicos e `proj2_ext*_*` para os extras.

---

### 2. Etapas de Execução

> Convenção: cada etapa lista **(a) objetivo**, **(b) deliverables de código**, **(c) matemática**, **(d) referências**, **(e) requisitos/pontos**, **(f) validação**, **(g) prompt copiável**.

---

#### Etapa 01 — Boilerplate do pacote `path_tracing/`

**(a) Objetivo.** Criar o pacote `path_tracing/` espelhando a arquitetura de `src/ray_tracing_2`, sem ainda implementar o integrador. Garantir que `python -m path_tracing.cli --help` lista subcomandos vazios e que `python -m path_tracing.cli proj2_smoke` renderiza uma esfera contra fundo cinza usando apenas o ray-cast primário (normal-as-color).

**(b) Deliverables.**
- `path_tracing/{ray,hit,camera,shape,triangle_bvh,sampling,film,scene,render_snapshot,render,render_estimator,cli}.py` (cópias adaptadas).
- `path_tracing/onb.py` com `class ONB` e função `frisvad_branchless(n) -> (t, b)`.
- Esqueletos vazios de `bsdf/`, `lights/`, `integrators/`, `mis.py`.
- `tests/test_pkg_imports.py` (carrega tudo sem ImportError).

**(c) Matemática.** Base ortonormal de Frisvad (sem ramos):
```
if n.z < -0.9999999: t = (0,-1,0), b = (-1,0,0)
else: a = 1/(1+n.z); k = -n.x*n.y*a; 
      t = (1 - n.x²*a, k, -n.x); b = (k, 1 - n.y²*a, -n.y)
```

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**", seção *HemisphereToGlobal*.
- PBRT 4e §3.3 *Vectors* (CoordinateSystem) — https://pbr-book.org/4ed/Geometry_and_Transformations/Vectors.
- Frisvad, J.R., "Building an Orthonormal Basis from a 3D Unit Vector Without Normalization", *Journal of Graphics Tools* 16(3):151–159, August 2012, **DOI: 10.1080/2165347X.2012.689606**.

**(e) Requisitos atendidos.** Infra-estrutura — pré-requisito de todos os 7.0 pts.

**(f) Validação.** Saída PNG de uma esfera com cor = (n+1)/2; comparar visualmente com o mesmo cast em `ray_tracing_2`.

**(g) Prompt copiável.**

````text
Você é o programador implementando a Etapa 01 do Projeto 2 de INF2608.
Crie o pacote `path_tracing/` em Python, espelhando a arquitetura de `src/ray_tracing_2`.

Requisitos:
- Use exclusivamente `from pyglm import glm` e `from PIL import Image` para matemática vetorial e I/O.
- Copie e adapte para `path_tracing/`: ray.py, hit.py, camera.py, shape.py (sem material — esse vem depois),
  triangle_bvh.py, sampling.py, film.py, scene.py, render_snapshot.py, render.py, render_estimator.py, cli.py.
- Crie diretórios vazios com __init__.py: bsdf/, lights/, integrators/.
- Crie `path_tracing/onb.py` com `class ONB` e `frisvad_branchless(n: glm.vec3) -> Tuple[glm.vec3, glm.vec3]`.
- Crie `path_tracing/mis.py` vazio (pass).
- Adicione um subcomando `proj2_smoke` no CLI que renderiza uma esfera unitária na origem,
  câmera em (0,0,3) olhando para a origem, fov=60°, 256x256 px, com cor = (n+1)/2 (normal-as-color).
- O snapshot/JSON+MD deve ser gerado em `out/proj2/etapa_01_smoke/` exatamente como o Projeto 1.

Entregável de documentação:
- Crie `docs/proj2/etapa_01_boilerplate.md` com:
  (i) objetivo, (ii) árvore final de path_tracing/, (iii) explicação do ONB de Frisvad com a fórmula,
  (iv) referências: Slide 9 (HemisphereToGlobal), PBRT 4e §3.3 "Vectors",
       Frisvad J.R., "Building an Orthonormal Basis from a 3D Unit Vector Without Normalization",
       JGT 16(3):151–159, 2012 (DOI 10.1080/2165347X.2012.689606),
  (v) o comando CLI exato que gera o smoke test e a imagem gerada.

Comentários no código DEVEM citar a referência (e.g. `# Ref: PBRT 4e §3.3 Vectors; Frisvad JGT 2012, DOI 10.1080/2165347X.2012.689606`).
````

---

#### Etapa 02 — Núcleo do Path Tracer Unidirecional (Aplicação Básica, 7.0 pts)

**(a) Objetivo.** Implementar o `PathIntegrator` unidirecional capaz de renderizar uma cena **Cornell-box-like** (planos como paredes, esferas/caixas com instancing, **uma** luz retangular emissiva) com **BSDF Lambertiana**, **N caminhos/pixel**, **profundidade mínima 4**, sem NEE ainda — apenas amostragem do BSDF (cosseno).

**(b) Deliverables.**
- `bsdf/lambertian.py`: `class LambertianBSDF` com `eval(wo, wi) = rho/π`, `sample(wo, u) -> (wi, pdf, f)` por Malley, `pdf(wo, wi) = max(0, cosθ_i)/π`.
- `bsdf/emissive.py`: `class EmissiveBSDF` (`eval=0`, marcação `is_emissive`, `Le`).
- `lights/area_rect.py`: luz retangular (geometria + emissão Le constante, normal lado-emissivo).
- `integrators/path_tracer.py`: integrador unidirecional **BSDF-sampling only** (sem NEE), respeitando `min_depth=4`.
- `cli.py`: subcomando `proj2_req1_lambert_basic`.

**(c) Matemática.**

Estimador de path tracing puro com amostragem de BSDF:

```
β ← (1,1,1);  L ← (0,0,0);  ray ← câmera.generate_ray(x_n, y_n)
para depth = 1, 2, ...:
   hit ← scene.intersect(ray)
   se !hit: L += β * background; break
   se hit.emissivo: 
      se (depth == 1) ou (modo == "bsdf_only"): L += β * Le
      break
   wo = -ray.d (frame local)
   (wi, pdf, f) = bsdf.sample(wo, u)
   se pdf == 0 ou f == 0: break
   β *= f * |cosθ_i| / pdf
   ray = Ray(offset_point(hit.p, hit.n), wi_global)
   se depth >= max_depth: break   ;; respeitar min_depth (=4) antes de qualquer term. anticipada
```

Para a Lambertiana com amostragem cosseno-ponderada: `β *= (ρ/π) · cosθ / (cosθ/π) = ρ` (cancela cosθ e π). PBRT 4e §9.2 *Diffuse Reflection*: "*By incorporating the cosine factor in the light transport equation’s integrand, cosine-weighted hemisphere sampling improves MSE by a factor of 2.34 for this test scene, without additional computational cost.*"

**Profundidade mínima 4** (exigência do enunciado): o caminho `câmera → x1 → x2 → x3 → luz` tem 4 vértices na superfície.

**(d) Referências.**
- Slide "**7. Integração de Monte Carlo**": PDF/CDF, inversion method, estimador MC, importance sampling, hemisfério cosseno (Malley).
- Slide "**8. Traçado de Caminhos**": LTE, formulação por integral de caminhos (Kajiya), throughput, TracePath, BRDF Lambertiana ρ/π.
- PBRT 4e §2.1 *Monte Carlo: Basics*, §2.2.2 *Importance Sampling*, §2.3 *Sampling Using the Inversion Method*, §2.4 *Transforming between Distributions*.
- PBRT 4e §9.2 *Diffuse Reflection* (https://pbr-book.org/4ed/Reflection_Models/Diffuse_Reflection).
- PBRT 4e §13.1 *The Light Transport Equation*, §13.2 *Path Tracing*, §13.3 *A Simple Path Tracer* (https://pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/A_Simple_Path_Tracer).
- PBRT 4e Apêndice A.5 *Sampling Multidimensional Functions* (Malley para cosseno).
- Kajiya, J.T., "The Rendering Equation", SIGGRAPH 1986, DOI: 10.1145/15922.15902.

**(e) Pontos.** Atende **toda a aplicação básica = 7.0 pts**.

**(f) Validação.**
- Cornell-like com 1 luz no teto, 2 caixas no chão; renderizar com **spp ∈ {4, 16, 64, 256}** e mostrar a redução de ruído (∝ 1/√N).
- Verificar que o teto perto da luz fica iluminado (bleeding indireto).
- Furnace test: cena com paredes brancas (ρ=0.8) → brilho médio coerente.

**(g) Prompt copiável.**

````text
Implemente a Etapa 02 do Projeto 2 — núcleo unidirecional do Path Tracer.
Pré-requisito: Etapa 01 concluída. Use pyglm e PIL exclusivamente.

1) Em `path_tracing/bsdf/lambertian.py`:
   - LambertianBSDF(rho: glm.vec3).
   - eval(wo, wi) = rho/π (frame local, n=(0,0,1)).
   - sample(wo, u: glm.vec2) -> (wi, pdf, f) via Malley:
       phi = 2π u.x; r = sqrt(u.y); x = r cos(phi), y = r sin(phi), z = sqrt(max(0,1-r²))
       wi = (x,y,z); pdf = z/π; f = rho/π.
   - pdf(wo, wi) = max(0, wi.z)/π.

2) Em `path_tracing/bsdf/emissive.py`:
   - EmissiveBSDF(Le: glm.vec3); is_emissive=True; eval/pdf=0.

3) Em `path_tracing/lights/area_rect.py`:
   - RectAreaLight(corner, edge_u, edge_v, Le) com normal=normalize(cross(edge_u,edge_v)),
     área=|cross|, emissão lado único, uniform-area sample.

4) Em `path_tracing/integrators/path_tracer.py`:
   - PathIntegrator(min_depth=4, max_depth=8, mode="bsdf_only").
   - Li(ray, scene, sampler) iterativo com throughput beta acumulado.
   - Respeitar min_depth: nenhuma terminação antes do 4º vértice.

5) Em `path_tracing/render.py`: chamar Integrator.Li N=spp vezes por pixel; gamma 2.2 no PNG.

6) Cena `path_tracing/scenes/proj2_req1_lambert_basic.py`: Cornell-like 5 planos + 2 caixas + 1 luz retangular no teto. 512×512.

7) CLI `proj2_req1_lambert_basic --spp N --depth D --out OUT` com snapshot completo.

8) Entregável `docs/proj2/etapa_02_path_tracer_core.md`:
   - Pseudocódigo do integrador (versão simplificada de PBRT 4e §13.3).
   - Fórmula explícita do estimador beta *= f * cosθ / pdf e a simplificação Lambertiana.
   - Galeria SPP = {4,16,64,256} com tabela de tempo e ruído.
   - Referências: Slide 7 (Monte Carlo), Slide 8 (Path Tracing);
     PBRT 4e §2.1, §2.2.2, §9.2, §13.1, §13.2, §13.3, §A.5;
     Kajiya, "The Rendering Equation", SIGGRAPH 1986, DOI 10.1145/15922.15902.

Comentários no código devem citar a referência acima de cada bloco-chave.
````

---

#### Etapa 03 — Next Event Estimation (NEE) em luzes retangulares

**(a) Objetivo.** Amostragem direta da luz a cada vértice do caminho. Reduz drasticamente a variância vs. Etapa 02. Sem MIS ainda.

**(b) Deliverables.**
- `lights/area_rect.py`: `sample_Li(ref_point, u) -> (wi, Li, pdf_solid_angle, p_on_light)`.
- `integrators/path_tracer.py`: novo modo `"nee_only"` que em cada vértice computa o termo direto via amostragem da luz, suprimindo o termo emissivo no próximo hit (exceto na primeira interseção).
- CLI `proj2_req2_nee`.

**(c) Matemática.**

Para uma luz retangular de área A com normal `n_L`:
```
pdf_area(p_L) = 1/A
r = |p - p_L|, ω_i = (p_L - p)/r
cosθ_L = max(0, -dot(ω_i, n_L)); cosθ_x = max(0, dot(ω_i, n))
pdf_solid_angle = pdf_area * r² / cosθ_L
L_direct = V · f(ω_o, ω_i) · Le · cosθ_x / pdf_solid_angle
         = V · f · Le · cosθ_x · cosθ_L · A / r²       (G = cosθ_x · cosθ_L / r²)
```
PBRT 4e §13.1.1 e §13.4.

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**", seção NEE.
- PBRT 4e §12.4 *Area Lights* e §12.6 *Light Sampling*.
- PBRT 4e §13.4 *A Better Path Tracer* (https://pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/A_Better_Path_Tracer).

**(e) Pontos.** Reforça os 7.0 pts base; pré-requisito do MIS da Etapa 04.

**(f) Validação.** Mesma cena de Etapa 02 com spp=16 → variância visivelmente menor. Comparação lado-a-lado com MSE relativo.

**(g) Prompt copiável.**

````text
Implemente a Etapa 03 — NEE em luzes retangulares.

1) Em `path_tracing/lights/area_rect.py`:
   - sample_Li(ref_point, u: glm.vec2) -> dict {p_on_light, wi, Li, pdf_solid_angle, distance, cos_at_light}.
   - pdf_Li(ref_point, wi) -> float (para uso em MIS na Etapa 04).

2) Em `path_tracing/integrators/path_tracer.py`:
   - Suporte mode in {"bsdf_only","nee_only"}.
   - No modo "nee_only", em cada vértice não-especular:
       L += beta * f(wo,wi_NEE) * Li * cosθ_x / pdf_solid_angle * V.
   - Suprimir Le do próximo hit (evita dupla contagem), exceto hit primário.

3) Cena: a mesma do Etapa 02. Subcomando `proj2_req2_nee`.

4) Entregável `docs/proj2/etapa_03_nee.md`:
   - Derivação da conversão pdf_area → pdf_solid_angle = pdf_area·r²/cosθ_L (PBRT 4e §13.1.1).
   - Imagem comparativa Etapa 02 vs Etapa 03 em SPP=16, tabela de MSE por canal.
   - Comando CLI exato. Referências: Slide 9 (NEE); PBRT 4e §12.4, §12.6, §13.4.
````

---

#### Etapa 04 — MIS (Multiple Importance Sampling) no último segmento

**(a) Objetivo.** No vértice antes da conexão com a luz, combinar duas estimativas: amostragem do BSDF e amostragem direta da luz (NEE). Usar **balance heuristic** e **power heuristic com β=2**.

**(b) Deliverables.**
- `mis.py`:
  ```python
  def balance_heuristic(n_a, pdf_a, n_b, pdf_b):
      return (n_a*pdf_a) / (n_a*pdf_a + n_b*pdf_b)
  def power_heuristic(n_a, pdf_a, n_b, pdf_b, beta=2.0):
      a = (n_a*pdf_a)**beta; b = (n_b*pdf_b)**beta
      return a / (a + b)
  ```
- `integrators/path_tracer.py`: novo modo `"mis"` (default). Em cada vértice:
  - Amostra luz: pdf_light, pdf_bsdf(ω_i_light), peso `w_light = power(1, pdf_light, 1, pdf_bsdf)`.
  - Amostra BSDF: pdf_bsdf, pdf_light(ω_i_bsdf), peso `w_bsdf = power(1, pdf_bsdf, 1, pdf_light)`.
- CLI `proj2_ext_mis`.

**(c) Matemática.**

Estimador MIS one-sample (PBRT 4e §2.2.3 *Multiple Importance Sampling*, Eqs. 2.14/2.15):
```
F_MIS = (1/n_a) Σ w_a(X_a) f(X_a)/p_a(X_a)  +  (1/n_b) Σ w_b(X_b) f(X_b)/p_b(X_b)
w_s(x) = (n_s p_s(x))^β / Σ_i (n_i p_i(x))^β   (β=1: balance; β=2: power)
```

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**", seção MIS.
- PBRT 4e §2.2.3 *Multiple Importance Sampling* — "*In practice, a good choice for the weighting functions is given by the balance heuristic… In practice, the power heuristic often reduces variance even further.*" URL: https://pbr-book.org/4ed/Monte_Carlo_Integration/Improving_Efficiency.html#MultipleImportanceSampling.
- PBRT 4e §13.4 *A Better Path Tracer*.
- **Veach, E. & Guibas, L.J., "Optimally Combining Sampling Techniques for Monte Carlo Rendering", SIGGRAPH '95, pp. 419–428, DOI: 10.1145/218380.218498.**

**(e) Pontos.** **+1.0 pt**.

**(f) Validação.** Cenas com luz pequena (alta variância para BSDF puro) e luz grande (alta variância para NEE puro); MIS deve **vencer** ambas. Plotar MSE × SPP em log-log com slope ≈ 1.

**(g) Prompt copiável.**

````text
Implemente a Etapa 04 — MIS no último segmento.

1) Em `path_tracing/mis.py`: balance_heuristic e power_heuristic(beta=2.0).
   Docstring deve citar Veach & Guibas SIGGRAPH 1995 (DOI 10.1145/218380.218498), Eq. 9 e 14;
   e PBRT 4e §2.2.3 (URL pbr-book.org/4ed/Monte_Carlo_Integration/Improving_Efficiency.html#MultipleImportanceSampling).

2) Em `path_tracing/integrators/path_tracer.py`:
   - Adicione mode=="mis".
   - Em cada vértice não-especular, combine:
     (a) Sample-light com peso w_L = power_heuristic(1, pdf_L, 1, pdf_B).
     (b) Sample-BSDF com peso w_B = power_heuristic(1, pdf_B, 1, pdf_L).
   - Especulares NÃO usam MIS (pdf delta) — apenas BSDF.

3) CLI `proj2_ext_mis` com flag `--heuristic={balance,power}`.

4) Entregável `docs/proj2/etapa_04_mis.md`:
   - Tabela MSE × spp para 3 cenas (luz pequena, grande, mista) + curvas log-log.
   - Referências: Slide 9 (MIS);
     PBRT 4e §2.2.3 (URL ...#MultipleImportanceSampling) e §13.4;
     Veach & Guibas SIGGRAPH 1995, pp. 419–428, DOI 10.1145/218380.218498.
````

---

#### Etapa 05 — Russian Roulette

**(a) Objetivo.** Terminar caminhos profundos probabilisticamente sem viés, com prob. de continuação baseada na magnitude do throughput.

**(b) Deliverables.** Modificação no `PathIntegrator`:
```python
if depth >= rr_min_depth:   # >= min_depth = 4 (exigência do enunciado)
    q = clamp(1.0 - max(beta.r, beta.g, beta.b), 0.05, 0.95)
    if random() < q: break
    beta /= (1 - q)
```
CLI flag `--rr/--no-rr`.

**(c) Matemática.**

Estimador F com RR (PBRT 4e §2.2.4 *Russian Roulette*):
```
F' = (F − q·c) / (1 − q)  com probabilidade (1 − q),
     c                    com probabilidade q
E[F'] = E[F]      (não viesado se q < 1; tipicamente c=0)
```

Interpretação telescópica (Misso et al. 2022): path tracing pode ser visto como série telescópica `T = Σ (T_n − T_{n−1})` e a RR aplicada faz cada caminho estimar um termo dessa série — tornando soma infinita estimável com amostras finitas.

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**", Russian Roulette.
- PBRT 4e §2.2.4 *Russian Roulette* — "*Russian roulette is a technique that can improve the efficiency of Monte Carlo estimates by skipping the evaluation of samples that would make a small contribution to the final result.*" URL: https://pbr-book.org/4ed/Monte_Carlo_Integration/Improving_Efficiency.html#RussianRoulette.
- PBRT 4e §13.4 *A Better Path Tracer*.
- **Misso, Z., Bitterli, B., Georgiev, I. & Jarosz, W., "Unbiased and consistent rendering using biased estimators", ACM Trans. Graph. 41(4), Article 48, July 2022, DOI: 10.1145/3528223.3530160.**

**(e) Pontos.** **+2.0 pts**.

**(f) Validação.**
- Média da imagem **não muda** estatisticamente entre `--rr=off` e `--rr=on` em SPP alto.
- **Tempo** cai em cenas reflexivas. `min_depth=4` é obrigatório; RR só ativa a partir do 5º vértice.

**(g) Prompt copiável.**

````text
Implemente a Etapa 05 — Russian Roulette.

1) Em `path_tracing/integrators/path_tracer.py`:
   - parâmetros `russian_roulette: bool = True`, `rr_min_depth: int = 4`.
   - Estratégia Hall–Greenberg (PBRT 4e §2.2.4):
       q = clamp(1 - max(beta.r, beta.g, beta.b), 0.05, 0.95)
       if random() < q: break
       beta /= (1 - q)
   - Aplicar somente quando depth >= rr_min_depth.

2) Testes: para SPP=1024 com cena de validação, RR on/off com L1 médio < 1% (não-viés empírico).
   Medir tempo via render_estimator.

3) CLI: flag `--rr/--no-rr`.

4) Entregável `docs/proj2/etapa_05_russian_roulette.md`:
   - Derivação E[F'] = E[F].
   - Tabela: cena, SPP, tempo on/off, ruído on/off, ganho de eficiência.
   - Discussão teórica curta citando Misso, Bitterli, Georgiev, Jarosz, "Unbiased and consistent rendering using biased estimators", ACM TOG 41(4):Article 48, July 2022, DOI 10.1145/3528223.3530160 — RR como instância de telescoping debiasing.
   - Referências: Slide 9 (RR); PBRT 4e §2.2.4 (URL ...#RussianRoulette); §13.4.
````

---

#### Etapa 06 — Luz de Área Poliédrica (Triangle Mesh) com Amostragem Uniforme por Área

**(a) Objetivo.** Permitir que **qualquer** triangle mesh seja luz (icosaedro suspenso, neon ring triangulado, etc.).

**(b) Deliverables.**
- `lights/area_mesh.py`: `MeshAreaLight(mesh, Le)` com pré-cálculo de CDF discreta sobre áreas dos triângulos.
- `sampling.py`: `uniform_triangle(u: glm.vec2) -> (b0, b1, b2)`.
- `shape.py`: `TriangleMesh.area()`, `TriangleMesh.sample_area(u, u_tri) -> (point, normal, pdf_area)`.

**(c) Matemática.**

Amostragem uniforme em um triângulo (PBRT 4e §6.5 *Triangle Meshes*): "*The uniform area triangle sampling method is based on mapping the provided random sample u to barycentric coordinates that are uniformly distributed over the triangle.*"
```
b0 = 1 − sqrt(u.x); b1 = sqrt(u.x) · (1 − u.y); b2 = sqrt(u.x) · u.y
p = b0 P0 + b1 P1 + b2 P2; n = normalize(cross(P1−P0, P2−P0))
pdf_area_triângulo = 1 / area(triângulo)
```
Para a mesh inteira proporcional à área: amostrar triângulo `i` ~ CDF de `area(t_i)/total_area`; depois amostrar dentro do triângulo. pdf_area_global(p) = 1/total_area.

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**" (área-sampling).
- PBRT 4e §6.5 *Triangle Meshes* (https://pbr-book.org/4ed/Shapes/Triangle_Meshes).
- PBRT 4e §12.4 *Area Lights*, §12.6 *Light Sampling*.
- PBRT 4e Apêndice A.5 *Sampling Multidimensional Functions* (alias method opcional).

**(e) Pontos.** **+1.0 pt**.

**(f) Validação.** Cena com luz icosaédrica vs. quadrada de mesma área e mesma `Le` total — distribuição de luminância no fundo difuso semelhante. Verificar `∫ pdf_Li dω = 1` empiricamente.

**(g) Prompt copiável.**

````text
Implemente a Etapa 06 — Luz como malha de triângulos.

1) Em `path_tracing/sampling.py`:
   - uniform_triangle(u) usando b0=1-sqrt(u.x); b1=sqrt(u.x)*(1-u.y); b2=sqrt(u.x)*u.y.
   - alias_table(weights) ou cdf_inverse() para discreta proporcional à área.

2) Em `path_tracing/shape.py` (TriangleMesh):
   - Pré-calcule total_area, áreas e CDF.
   - sample_area(u, u_disc) -> (p, n, pdf_area=1/total_area).

3) Em `path_tracing/lights/area_mesh.py`:
   - MeshAreaLight(mesh, Le) com sample_Li/pdf_Li análogos a RectAreaLight, convertendo área→ângulo sólido.

4) Cena `proj2_ext_mesh_light`: Cornell-like com luz icosaédrica suspensa.

5) Entregável `docs/proj2/etapa_06_mesh_light.md`:
   - Fórmula barycentric com sqrt(u.x), prova de uniformidade.
   - Imagem icosaedro vs retângulo de mesma área.
   - Referências: Slide 9; PBRT 4e §6.5 Triangle Meshes; §12.4, §12.6; §A.5.
````

---

#### Etapa 07 — BSDF Dielétrica Refrativa (Snell + Fresnel + Beer-Lambert)

**(a) Objetivo.** Objetos refrativos (vidro, água): Snell, Fresnel real para reflexão vs refração estocástica, e Beer-Lambert para atenuação interna.

**(b) Deliverables.**
- `bsdf/dielectric.py`: `DielectricBSDF(eta, sigma_t)` — `is_delta=True`. Fresnel real PBRT 4e §9.5; TIR; escala η_t/η_i; Beer-Lambert.

**(c) Matemática.**

Snell: `η_i sinθ_i = η_t sinθ_t` → `cos²θ_t = 1 − (η_i/η_t)² sin²θ_i`.

Fresnel dielétrico (PBRT 4e §9.5, eq. 9.6):
```
r_∥ = (η_t cosθ_i - η_i cosθ_t)/(η_t cosθ_i + η_i cosθ_t)
r_⊥ = (η_i cosθ_i - η_t cosθ_t)/(η_i cosθ_i + η_t cosθ_t)
F   = (r_∥² + r_⊥²) / 2
```
Beer-Lambert (PBRT 4e §11.2 *Transmittance*): `T(r) = exp(−σ_t · r)`.

**(d) Referências.**
- Slide "**8. Traçado de Caminhos**" + Slide "**11. Microfaceta**" (Fresnel).
- PBRT 4e §9.3 *Specular Reflection and Transmission*.
- PBRT 4e §9.5 *Dielectric BSDF* (https://www.pbr-book.org/4ed/Reflection_Models/Dielectric_BSDF).
- PBRT 4e §11.2 *Transmittance*.
- Implementação interna em `ray_tracing_2/material.py::TransparentMaterial` (referência interna).

**(e) Pontos.** **+2.0 pts**.

**(f) Validação.**
- Esfera de vidro (η=1.5) sobre plano difuso → cáustica visível (motivação para Etapa 10).
- Esfera com `σ_t = (0.5, 0.1, 0.1)` mostrando atenuação avermelhada.

**(g) Prompt copiável.**

````text
Implemente a Etapa 07 — BSDF Dielétrica.

1) Em `path_tracing/bsdf/dielectric.py`:
   - DielectricBSDF(eta: float, sigma_t: glm.vec3 = glm.vec3(0)); is_delta=True.
   - FresnelDielectric(cos_theta_i, eta_i, eta_t) -> F (eq. 9.6 PBRT 4e).
   - sample(wo, u: float) -> (wi, pdf, f):
       compute cos_theta_i, eta_ratio (front/back).
       handle TIR (F=1).
       if u < F: reflect; else refract com fator (η_t/η_i)².

2) No PathIntegrator:
   - Especular: pular NEE+MIS, apenas propagar.
   - Beer-Lambert quando dentro do meio: beta *= exp(-sigma_t * hit.t).

3) Cenas: `proj2_ext_glass` e `proj2_ext_beer`.

4) Entregável `docs/proj2/etapa_07_refraction.md`:
   - Snell, Fresnel eq. 9.6, TIR, fator η_t/η_i.
   - Beer-Lambert.
   - Limitação: cáusticas ruidosas — Etapa 10 resolverá.
   - Referências: Slide 8 + Slide 11 (Fresnel); PBRT 4e §9.3, §9.5, §11.2.
````

---

#### Etapa 08 — BSDF Microfacetada Cook-Torrance / GGX

**(a) Objetivo.** Materiais não-difusos com rugosidade controlável (workflow metalness/roughness/baseColor).

**(b) Deliverables.**
- `bsdf/microfacet_ggx.py` (`CookTorranceGGX(baseColor, metallic, roughness)`):
  - `D(ω_h)` — Trowbridge–Reitz (GGX); `G` — Smith height-correlated; `F` — Schlick com `F0 = mix(vec3(0.04), baseColor, metallic)`.
  - `eval(wo, wi) = D F G / (4 |n·ω_o| |n·ω_i|)` — PBRT 4e §9.6.5 Eq. 9.33.
  - `sample(wo, u)` via VNDF — PBRT 4e §9.6.4.

**(c) Matemática.**

Com `α = roughness²`:
```
GGX:   D(ω_h) = α² / (π · ((n·ω_h)²(α²−1) + 1)²)
Smith: Λ_GGX(ω) = (−1 + √(1 + α² tan²θ)) / 2 ; G1(ω) = 1/(1+Λ(ω))
       G(ω_o, ω_i) = 1 / (1 + Λ(ω_o) + Λ(ω_i))    (height-correlated)
F (Schlick): F(cosθ) = F0 + (1 − F0)(1 − cosθ)^5
Half-vector: ω_h = normalize(ω_o + ω_i)
f_r = D · F · G / (4 · |n·ω_o| · |n·ω_i|)         (Eq. 9.33 PBRT 4e §9.6.5)
```

**(d) Referências.**
- Slide "**11. Microfaceta**" (Cook-Torrance, GGX, Smith-Schlick).
- PBRT 4e §9.6 *Roughness Using Microfacet Theory* (https://www.pbr-book.org/4ed/Reflection_Models/Roughness_Using_Microfacet_Theory):
  - §9.6.1 *The Microfacet Distribution* (D GGX).
  - §9.6.2 *The Masking Function* (Λ).
  - §9.6.3 *The Masking-Shadowing Function* (G).
  - §9.6.4 *Sampling the Distribution of Visible Normals*.
  - §9.6.5 *The Torrance–Sparrow Model* (Eq. 9.33).
- PBRT 4e §9.4 *Conductor BRDF*, §9.7 *Rough Dielectric BSDF*.
- **Walter, B., Marschner, S.R., Li, H. & Torrance, K.E., "Microfacet Models for Refraction through Rough Surfaces", EGSR'07 (18th Eurographics Symposium on Rendering), pp. 195–206, DOI: 10.2312/EGWR/EGSR07/195-206.**
- Contexto teórico avançado (citar na conclusão e docstring): **Seyb, D., d'Eon, E., Bitterli, B. & Jarosz, W., "From microfacets to participating media: A unified theory of light transport with stochastic geometry", ACM Trans. Graph. 43(4), Article 112, July 2024, DOI: 10.1145/3658121.**

**(e) Pontos.** **+1.0 pt**.

**(f) Validação.**
- Grid de esferas com `roughness ∈ {0.05, 0.2, 0.5, 1.0}` × `metallic ∈ {0, 1}`.
- Furnace test: BSDF metálico puro sob luz uniforme → albedo recuperado ≈ baseColor (energy-preservation).

**(g) Prompt copiável.**

````text
Implemente a Etapa 08 — BSDF Cook-Torrance/GGX.

1) Em `path_tracing/bsdf/microfacet_ggx.py`:
   - CookTorranceGGX(base_color: glm.vec3, metallic: float, roughness: float).
   - alpha = roughness**2; F0 = mix(vec3(0.04), base_color, metallic).
   - Funções D_ggx, Lambda_ggx, G_smith_correlated, F_schlick.
   - eval(wo, wi) implementa Eq. 9.33 de PBRT 4e §9.6.5.
   - sample(wo, u) via VNDF (PBRT 4e §9.6.4).

2) Layered: LayeredBSDF(diffuse, specular, weight=1-metallic).

3) Cena `proj2_ext_ggx_grid` 5×2.

4) Entregável `docs/proj2/etapa_08_microfacet.md`:
   - Equações D, G, F, eval explícitas.
   - Imagem 5×2 + furnace test.
   - VNDF discussão.
   - Referências: Slide 11 (Microfaceta);
     PBRT 4e §9.6.1, §9.6.2, §9.6.3, §9.6.4, §9.6.5; §9.4;
     Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces",
       EGSR'07, pp. 195–206, DOI 10.2312/EGWR/EGSR07/195-206;
     Seyb, d'Eon, Bitterli, Jarosz, "From microfacets to participating media: A unified theory of light transport with stochastic geometry",
       ACM TOG 43(4):Article 112, July 2024, DOI 10.1145/3658121.
````

---

#### Etapa 09 — Luz Infinita / Environment Light

**(a) Objetivo.** Iluminação ambiente direcional vinda de environment map (lat-long HDR) ou sky uniforme.

**(b) Deliverables.**
- `lights/infinite.py`:
  - `UniformInfiniteLight(Le_const)` — sample uniforme da esfera; pdf = 1/(4π).
  - `ImageInfiniteLight(env_map)` — 2D CDF de luminance · sinθ; amostragem por inversão.

**(c) Matemática.**

PBRT 4e §12.5 *Infinite Area Lights*:
- Peso por linha: `f_v = Σ_u L[u,v] · sin(π·v/H)`.
- CDF marginal em v; condicional em u dado v.
- pdf direcional: `pdf_dir(ω) = pdf_uv / (2π² sinθ)` (Jacobiano lat-long → sphere).

**(d) Referências.**
- Slide "**9. Traçado de Caminhos II**" (luzes infinitas).
- PBRT 4e §12.5 *Infinite Area Lights* (https://www.pbr-book.org/4ed/Light_Sources/Infinite_Area_Lights), §12.6 *Light Sampling*.
- PBRT 4e Apêndice A.5.

**(e) Pontos.** **+1.0 pt**.

**(f) Validação.** Modelo glossy sob HDRi com 64 spp + MIS → reflexões coerentes. Comparar uniform × image-importance sampling.

**(g) Prompt copiável.**

````text
Implemente a Etapa 09 — Environment/Infinite area light.

1) Em `path_tracing/lights/infinite.py`:
   - UniformInfiniteLight(Le, scene_radius).
   - ImageInfiniteLight:
       carregue HDR/EXR; pré-compute 2D piecewise-constant distribution;
       sample_Li(u) -> {wi, Li, pdf_solid_angle, distance=inf};
       pdf_Li(wi).

2) No path_tracer: env.Le(ray.d) no miss; MIS sample-BSDF × sample-env.

3) Cena `proj2_ext_envmap`: esfera de cobre (CookTorrance metallic=1) sob HDRi.

4) Entregável `docs/proj2/etapa_09_envmap.md`:
   - Derivação pdf_dir via Jacobiano sinθ.
   - Uniform vs image-IS (MSE).
   - Referências: Slide 9; PBRT 4e §12.5 Infinite Area Lights, §12.6 Light Sampling, §A.5.
````

---

#### Etapa 10 — Bidirectional Path Tracing (BDPT)

**(a) Objetivo.** Subcaminho da luz + subcaminho da câmera; conectar todos pares (s, t); pesar por MIS. Resolve cáusticas/SDS.

**(b) Deliverables.**
- `integrators/bdpt.py`: `generate_camera_subpath`, `generate_light_subpath`, `connect_bdpt(s, t)`, `mis_weight_bdpt`. Casos `s=0` (PT puro), `t=0` (light tracing direto na câmera com splatting).

**(c) Matemática.**

Path integral (PBRT 4e §13.1.2):
```
I_j = ∫_Ω f_j(x̄) dμ(x̄)
f_j(x̄) = L_e(x_0→x_1) · ∏_{i=1..k-1} f_s(x_{i-1}→x_i→x_{i+1}) · G(x_i↔x_{i+1}) · W_e(x_{k-1}→x_k)
```
BDPT amostra cada caminho de comprimento k pela soma sobre estratégias (s+t=k+1):
```
F = Σ_{s+t=k+1} w_{s,t}(x̄) · C_{s,t}(x̄) / p_{s,t}(x̄)
w_{s,t} = (p_{s,t})^β / Σ_i (p_i)^β       (power heuristic, β=2)
```

**(d) Referências.**
- Slide "**10. Métodos Bidirecionais e Renderização de Volumes**".
- **PBRT 4e NÃO contém capítulo BDPT** — removido. Referência primária: **PBRT 3ª ed. §16.3 *Bidirectional Path Tracing*** (https://pbr-book.org/3ed-2018/Light_Transport_III_Bidirectional_Methods/Bidirectional_Path_Tracing).
- **Veach, E. & Guibas, L.J., "Optimally Combining Sampling Techniques for Monte Carlo Rendering", SIGGRAPH '95, pp. 419–428, DOI: 10.1145/218380.218498.**
- Veach, E., PhD thesis, Stanford, 1997 ("Robust Monte Carlo Methods for Light Transport Simulation").

**(e) Pontos.** **+3.0 pts equivalentes** (alternativa avançada — o usuário implementa AMBOS BDPT e MLT como "ir além").

**(f) Validação.** Cena com vidro iluminado por janela → cáustica do vidro no chão. MSE muito menor que Etapa 04 em mesmo SPP onde há cáusticas.

**(g) Prompt copiável.**

````text
Implemente a Etapa 10 — Bidirectional Path Tracing.

1) Em `path_tracing/integrators/bdpt.py`:
   - Vertex: (pos, normal, geo_normal, bsdf, beta, pdf_fwd, pdf_rev, kind in {camera, surface, light}).
   - generate_camera_subpath(ray, scene, max_t).
   - generate_light_subpath(scene, max_s) começando por sample_Le.
   - connect_bdpt(camera_path, light_path, s, t) -> SampledSpectrum (G-term + shadow ray + throughput).
   - mis_weight_bdpt com pdfs reversas e power heuristic beta=2.
   - Caso t=0 (light tracing): conexão direta com câmera via splatting.

2) Cena `proj2_ext_bdpt_caustic`: vidro sobre plano + luz retangular.

3) Entregável `docs/proj2/etapa_10_bdpt.md`:
   - Diagrama (s,t) com casos PT (s=0), light tracing (t=0), conexões internas.
   - Fórmula MIS BDPT explícita.
   - Comparação visual + MSE × tempo com Etapa 04+05.
   - Limitação SDS — motivar Etapa 11.
   - Referências: Slide 10 (BDPT);
     PBRT 3ª ed. §16.3 Bidirectional Path Tracing (URL pbr-book.org/3ed-2018/Light_Transport_III_Bidirectional_Methods/Bidirectional_Path_Tracing) — removido do 4ed;
     Veach & Guibas, "Optimally Combining Sampling Techniques for Monte Carlo Rendering",
       SIGGRAPH '95, pp. 419–428, DOI 10.1145/218380.218498;
     Veach, PhD Thesis, Stanford 1997.
````

---

#### Etapa 11 — Metropolis Light Transport em Primary Sample Space (PSSMLT / Kelemen)

**(a) Objetivo.** MCMC no espaço de variáveis aleatórias primárias: small/large mutations nos `u_i` que parametrizam um caminho BDPT; aceitação Metropolis–Hastings; MIS entre mutações pequenas e grandes.

**(b) Deliverables.**
- `integrators/mlt.py`: `PSSampler` com small-step (Kelemen exp-tail) e large-step; bootstrap para normalização `b`; loop principal Metropolis-Hastings; opcionalmente Multiplexed (Hachisuka 2014).

**(c) Matemática.**

Distribuição-alvo `π(x̄) ∝ |f(x̄)|`. Mutação small (Kelemen, s1=1/1024, s2=1/64):
```
ξ = uniforme[0,1]; sign uniforme {-1,+1};
Δ = s2 * exp(-log(s2/s1) * ξ);
u' = (u + sign * Δ) mod 1
```
Mutação large: `u' = uniforme[0,1]` por componente, com prob. p_large ≈ 0.3.

Aceitação:
```
α = min(1, |f(y)|/|f(x)|)
splat(y) += α · b · f(y)/|f(y)|
splat(x) += (1−α) · b · f(x)/|f(x)|
x ← y se rand < α
```
`b = (1/K) Σ |f(x_k)|` estimado no bootstrap.

**(d) Referências.**
- Slide "**11. Metropolis (MLT)**" (mutação, balanço detalhado, MH, warm-up bias, PSS, Kelemen, Multiplexed).
- **PBRT 4e NÃO contém capítulo MLT** — removido. Referência primária: **PBRT 3ª ed. §16.4 *Metropolis Light Transport*** (https://pbr-book.org/3ed-2018/Light_Transport_III_Bidirectional_Methods/Metropolis_Light_Transport).
- **Veach, E. & Guibas, L.J., "Metropolis Light Transport", SIGGRAPH '97, pp. 65–76, DOI: 10.1145/258734.258775.**
- **Kelemen, C., Szirmay-Kalos, L., Antal, G. & Csonka, F., "A Simple and Robust Mutation Strategy for the Metropolis Light Transport Algorithm", Computer Graphics Forum 21(3):531–540, September 2002, DOI: 10.1111/1467-8659.t01-1-00703.**
- **Hachisuka, T., Kaplanyan, A.S. & Dachsbacher, C., "Multiplexed Metropolis Light Transport", ACM Trans. Graph. 33(4), Article 100, July 2014, DOI: 10.1145/2601097.2601138** (opcional).

**(e) Pontos.** **+3.0 pts equivalentes** (alternativa avançada).

**(f) Validação.**
- Cena difícil (SDS path: porta de vidro entre câmera e luz) — comparar PT, BDPT, PSSMLT em mesmo tempo de parede.
- Não-viés: com `n_bootstrap` grande, média estimada coincide com BDPT puro.
- Documentar **bias de warm-up** (Slide 11) e estratégia de descarte de iniciações.

**(g) Prompt copiável.**

````text
Implemente a Etapa 11 — PSSMLT.

1) Em `path_tracing/integrators/mlt.py`:
   - PSSampler com small-step Kelemen (s1=1/1024, s2=1/64) e large-step p_large=0.3.
   - bootstrap(K_boot=100_000) computando b e selecionando seed por CDF de |f|.
   - Loop por chain de M iterações:
       y ← mutate(x);
       compute f(y) via BDPT usando PSSampler;
       alpha = min(1, |f(y)|/|f(x)|);
       splat(film, y_path, alpha * b * f_y/|f_y|);
       splat(film, x_path, (1-alpha) * b * f_x/|f_x|);
       if rand() < alpha: x ← y.
   - Opcional: Multiplexed (estratégia (s,t) como primary sample).

2) Cena `proj2_ext_mlt_sds`: Cornell com vidro fino entre luz e câmera.

3) Entregável `docs/proj2/etapa_11_mlt.md`:
   - Markov chain, detailed balance, MH.
   - Mutação Kelemen com fórmula e parâmetros.
   - Warm-up bias discussão.
   - Comparação PT × BDPT × MLT em tempo de parede.
   - Referências: Slide 11 (Metropolis);
     PBRT 3ª ed. §16.4 Metropolis Light Transport (URL pbr-book.org/3ed-2018/Light_Transport_III_Bidirectional_Methods/Metropolis_Light_Transport) — removido do 4ed;
     Veach & Guibas, "Metropolis Light Transport", SIGGRAPH '97, pp. 65–76, DOI 10.1145/258734.258775;
     Kelemen, Szirmay-Kalos, Antal, Csonka, "A Simple and Robust Mutation Strategy for the Metropolis Light Transport Algorithm",
       Computer Graphics Forum 21(3):531–540, Sep. 2002, DOI 10.1111/1467-8659.t01-1-00703;
     Hachisuka, Kaplanyan, Dachsbacher, "Multiplexed Metropolis Light Transport",
       ACM TOG 33(4):Article 100, July 2014, DOI 10.1145/2601097.2601138.
````

---

#### Etapa 12 — Consolidação: Relatório LaTeX

**(a) Objetivo.** Produzir `inf2608-proj2.pdf` no molde de `inf2608-proj1.v3.pdf`: artigo técnico-científico com abstract PT+EN, introdução, seções por técnica, evidência visual com comandos geradores, decisões e limites, conclusão, referências, apêndices.

**(b) Deliverables.**
- `report/proj2.tex`.
- `report/figures/` populado a partir dos snapshots (script `make_report_figures.py`).
- `report/refs.bib` com **todas** as referências:
  - Slides (7, 8, 9, 10, 11, "Microfaceta") do Prof. Celes.
  - PBRT 4e §§2.2.3, 2.2.4, 6.5, 9.2, 9.3, 9.4, 9.5, 9.6.1–9.6.5, 11.2, 12.4–12.6, 13.1–13.4, A.5.
  - PBRT 3ª ed. §16.3, §16.4.
  - Veach & Guibas 1995, SIGGRAPH, pp. 419–428, DOI 10.1145/218380.218498.
  - Veach & Guibas 1997, SIGGRAPH, pp. 65–76, DOI 10.1145/258734.258775.
  - Misso et al. 2022, ACM TOG 41(4):Article 48, DOI 10.1145/3528223.3530160.
  - Seyb et al. 2024, ACM TOG 43(4):Article 112, DOI 10.1145/3658121.
  - Walter et al. EGSR 2007, pp. 195–206, DOI 10.2312/EGWR/EGSR07/195-206.
  - Kelemen et al. CGF 21(3):531–540, 2002, DOI 10.1111/1467-8659.t01-1-00703.
  - Hachisuka et al. ACM TOG 33(4):Article 100, 2014, DOI 10.1145/2601097.2601138.
  - Frisvad 2012, JGT 16(3):151–159, DOI 10.1080/2165347X.2012.689606.
  - Kajiya, "The Rendering Equation", SIGGRAPH 1986, DOI 10.1145/15922.15902.
- Tabelas-apêndice mapeando "conceito → slide → PBRT § → arquivo:linha".

**(c) Estrutura do LaTeX.**

1. Título, autor, data.
2. **Resumo (PT)** e **Abstract (EN)** + keywords.
3. **1. Introdução** — LTE, motivação, organização.
4. **2. Pipeline e Geometria** — câmera, BVH, instancing (referenciar Projeto 1).
5. **3. Monte Carlo & Path Tracing Unidirecional** — Etapas 02–03.
6. **4. MIS** — Etapa 04.
7. **5. Russian Roulette** — Etapa 05.
8. **6. Luzes de Área (retangular e poliédrica)** — Etapa 06.
9. **7. BSDFs: Lambertiano, Dielétrico, GGX** — Etapas 07–08.
10. **8. Luz Infinita / Environment** — Etapa 09.
11. **9. Métodos Bidirecionais e MLT** — Etapas 10–11.
12. **10. Evidência Visual** — galeria com comandos CLI exatos abaixo de cada figura.
13. **11. Decisões de Modelagem e Limites**.
14. **12. Conclusão e Trabalhos Futuros** — citar Seyb et al. 2024 (volumes), Misso et al. 2022 (estimadores enviesados unbiasable).
15. **Referências** (bibtex).
16. **Apêndices**: A. Rastreabilidade (conceito → slide → PBRT § → arquivo:linha); B. Evidência (figura → comando → snapshot); C. Diagramas de classe (PlantUML/TikZ-UML) atualizados.

**(d) Prompt copiável.**

````text
Gere o relatório final do Projeto 2 (INF2608) em LaTeX em `report/proj2.tex`,
seguindo a estrutura idêntica à de `inf2608-proj1.v3.pdf`.

1) Estrutura obrigatória de seções (na ordem):
   Resumo (PT), Abstract (EN), Palavras-chave/Keywords,
   1. Introdução
   2. Pipeline e Geometria (recapitular ray_tracing_2)
   3. Integração Monte Carlo & Path Tracing Unidirecional (Etapas 02–03)
   4. Multiple Importance Sampling (Etapa 04)
   5. Russian Roulette (Etapa 05)
   6. Luzes de Área Retangular e Poliédrica (Etapas 03+06)
   7. BSDFs: Lambertiano, Dielétrico, GGX (Etapas 02+07+08)
   8. Environment Light (Etapa 09)
   9. Métodos Bidirecionais (BDPT) e MLT (Etapas 10–11)
   10. Evidência Visual (galeria com comandos geradores)
   11. Decisões de Modelagem e Limites
   12. Conclusão e Trabalhos Futuros
   Referências, Apêndices A/B/C.

2) Para CADA figura na seção 10, imprima abaixo o COMANDO CLI EXATO que a gerou,
   no mesmo padrão visual do Projeto 1, e cite o snapshot JSON correspondente.

3) Cite explicitamente, com biblatex:
   - Slides do Prof. Celes (7, 8, 9, 10, 11 + "Microfaceta").
   - PBRT 4ª ed.: §2.1, §2.2.2, §2.2.3 Multiple Importance Sampling, §2.2.4 Russian Roulette,
     §6.5 Triangle Meshes, §9.2 Diffuse Reflection, §9.3 Specular, §9.5 Dielectric BSDF,
     §9.6 Roughness Using Microfacet Theory (9.6.1–9.6.5), §9.4 Conductor BRDF,
     §11.2 Transmittance, §12.4 Area Lights, §12.5 Infinite Area Lights, §12.6 Light Sampling,
     §13.1 The Light Transport Equation, §13.2 Path Tracing, §13.3 A Simple Path Tracer, §13.4 A Better Path Tracer,
     Apêndice A.5 Sampling Multidimensional Functions.
   - PBRT 3ª ed.: §16.3 Bidirectional Path Tracing, §16.4 Metropolis Light Transport (removidos do 4ed).
   - Veach & Guibas, "Optimally Combining Sampling Techniques for Monte Carlo Rendering",
     SIGGRAPH '95, pp. 419–428, DOI 10.1145/218380.218498.
   - Veach & Guibas, "Metropolis Light Transport",
     SIGGRAPH '97, pp. 65–76, DOI 10.1145/258734.258775.
   - Misso, Bitterli, Georgiev, Jarosz, "Unbiased and consistent rendering using biased estimators",
     ACM TOG 41(4):Article 48, July 2022, DOI 10.1145/3528223.3530160.
   - Seyb, d'Eon, Bitterli, Jarosz, "From microfacets to participating media: A unified theory of light transport with stochastic geometry",
     ACM TOG 43(4):Article 112, July 2024, DOI 10.1145/3658121.
   - Kelemen, Szirmay-Kalos, Antal, Csonka,
     "A Simple and Robust Mutation Strategy for the Metropolis Light Transport Algorithm",
     CGF 21(3):531–540, Sep. 2002, DOI 10.1111/1467-8659.t01-1-00703.
   - Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces",
     EGSR'07, pp. 195–206, DOI 10.2312/EGWR/EGSR07/195-206.
   - Hachisuka, Kaplanyan, Dachsbacher, "Multiplexed Metropolis Light Transport",
     ACM TOG 33(4):Article 100, July 2014, DOI 10.1145/2601097.2601138.
   - Frisvad, "Building an Orthonormal Basis from a 3D Unit Vector Without Normalization",
     JGT 16(3):151–159, August 2012, DOI 10.1080/2165347X.2012.689606.
   - Kajiya, "The Rendering Equation", SIGGRAPH 1986, DOI 10.1145/15922.15902.

4) Apêndice A — tabela CSV-convertida-em-tabular com colunas:
   | Conceito | Slide:pp | PBRT 4e § | Artigo (DOI) | path_tracing/arquivo:linhas |
   Pelo menos 30 linhas cobrindo as Etapas 02–11.

5) Apêndice B — tabela:
   | Figura | Cena | SPP | Tempo | Comando CLI | snapshot/dir |

6) Apêndice C — diagramas de classe (TikZ-UML ou PlantUML compilado como PDF),
   focando em: BSDF hierarchy, Light hierarchy, Integrator hierarchy.

7) Saída: `report/proj2.pdf` compilável com `latexmk -pdf report/proj2.tex`.

8) Crie também `docs/proj2/etapa_12_relatorio.md` (1 página) descrevendo o processo
   de consolidação a partir dos snapshots das etapas anteriores.
````

---

### 3. Tabela-Síntese (Etapa × Pontos × Slide × PBRT 4e × Artigo × Markdown)

| Etapa | Tema | Pontos | Slide primário (Celes) | PBRT § primária | Artigo (DOI) | Markdown |
|---|---|---|---|---|---|---|
| 01 | Boilerplate `path_tracing/` | infra | 9 (HemisphereToGlobal) | 4e §3.3; A.5 | Frisvad 2012 JGT 16(3):151–159, DOI 10.1080/2165347X.2012.689606 | `etapa_01_boilerplate.md` |
| 02 | Path tracer Lambertiano, depth≥4 | **7.0** | 7 (Monte Carlo) + 8 (Path Tracing) | 4e §13.1, §13.2, §13.3, §9.2, §A.5 | Kajiya SIGGRAPH 1986, DOI 10.1145/15922.15902 | `etapa_02_path_tracer_core.md` |
| 03 | NEE em luz retangular | — (suporte) | 9 (NEE) | 4e §12.4, §12.6, §13.4 | — | `etapa_03_nee.md` |
| 04 | MIS (balance + power β=2) | **+1.0** | 9 (MIS) | 4e §2.2.3; §13.4 | Veach & Guibas SIGGRAPH '95 pp. 419–428, DOI 10.1145/218380.218498 | `etapa_04_mis.md` |
| 05 | Russian Roulette | **+2.0** | 9 (RR) | 4e §2.2.4; §13.4 | Misso et al. ACM TOG 41(4):Art. 48 (2022), DOI 10.1145/3528223.3530160 | `etapa_05_russian_roulette.md` |
| 06 | Mesh light (poliedro) | **+1.0** | 9 (área-sampling) | 4e §6.5; §12.4; §A.5 | — | `etapa_06_mesh_light.md` |
| 07 | Dielétrico refrativo | **+2.0** | 8 + 11 (Fresnel) | 4e §9.3, §9.5, §11.2 | — | `etapa_07_refraction.md` |
| 08 | Microfaceta Cook-Torrance/GGX | **+1.0** | 11 (Microfaceta) | 4e §9.6.1–9.6.5; §9.4 | Walter et al. EGSR'07 pp. 195–206, DOI 10.2312/EGWR/EGSR07/195-206; Seyb et al. ACM TOG 43(4):Art. 112 (2024), DOI 10.1145/3658121 | `etapa_08_microfacet.md` |
| 09 | Environment / luz infinita | **+1.0** | 9 (luzes infinitas) | 4e §12.5, §12.6, §A.5 | — | `etapa_09_envmap.md` |
| 10 | BDPT | **+3.0** (alt.) | 10 (Bidirecionais) | 3e §16.3 (removido do 4e) | Veach & Guibas SIGGRAPH '95 DOI 10.1145/218380.218498; Veach Thesis 1997 | `etapa_10_bdpt.md` |
| 11 | MLT (PSSMLT) | **+3.0** (alt.) | 11 (Metropolis) | 3e §16.4 (removido do 4e) | Veach & Guibas SIGGRAPH '97 pp. 65–76, DOI 10.1145/258734.258775; Kelemen et al. CGF 21(3):531–540 (2002), DOI 10.1111/1467-8659.t01-1-00703; Hachisuka et al. ACM TOG 33(4):Art. 100 (2014), DOI 10.1145/2601097.2601138 | `etapa_11_mlt.md` |
| 12 | Relatório LaTeX | entrega | todos | todos | todos | `etapa_12_relatorio.md` + `report/proj2.tex` |

**Soma teórica de pontos** (extras simples): Base 7.0 + MIS 1.0 + RR 2.0 + Mesh light 1.0 + Refração 2.0 + GGX 1.0 + Envmap 1.0 = **15.0 pts** equivalentes em escala teórica (o enunciado limita extras a 3.0; o usuário pediu para implementar todos e ir além). BDPT + MLT são o "além" solicitado.

---

### 4. Observações de Implementação Transversais

- **Reprodutibilidade.** Cada etapa registra `seed` no snapshot e expõe `--seed`. O `render_snapshot` é estendido com: `integrator`, `min_depth`, `max_depth`, `spp`, `russian_roulette`, `mis_heuristic`, `bsdf_list`, `light_list`, `bdpt_max_s_t`, `mlt_bootstrap_K`.
- **Snapshots auditáveis.** Cada figura aponta para `out/proj2/etapa_NN_xxx/` com `image.png`, `properties.json`, `properties.md`, `command.txt`.
- **Comentários de código padronizados.** Cabeçalho exemplo:
  ```python
  # Ref: Slide "9. Traçado de Caminhos II", seção MIS;
  #      PBRT 4e §2.2.3 Multiple Importance Sampling
  #        (pbr-book.org/4ed/Monte_Carlo_Integration/Improving_Efficiency.html#MultipleImportanceSampling);
  #      Veach & Guibas, SIGGRAPH 1995, pp. 419-428 (DOI 10.1145/218380.218498),
  #        Eq. 9 (balance heuristic) e Eq. 14 (power heuristic, β=2).
  ```
- **Convenção de unidades.** Toda radiância em RGB linear (gamma=2.2 só no PNG). `Le` e `rho` são `glm.vec3` ∈ [0, ∞).
- **Limites declarados.** O sistema **não** implementa espectros contínuos, BSSRDF, volumes participativos (apenas Beer-Lambert), photon mapping, GPU.
- **Validação do não-viés.** Pelo menos uma cena com `spp=2048` deve produzir L1 ≤ 1% entre `{bsdf_only, nee_only, mis, mis+rr, bdpt, mlt}` — convergência para a mesma imagem.

---

## Recommendations

**Sequenciamento recomendado de execução (próximas duas semanas):**

1. **Dia 1–2 (sprint núcleo)**: executar Etapa 01 + Etapa 02. *Threshold de avanço*: smoke test renderiza a Cornell-like com SPP=64 em < 5 min e produz snapshot completo. Se Python puro for inviavelmente lento (> 30 min/imagem em 512² × 64 spp), considere `numba` ou portar o kernel inner-loop para `cython`/`mypyc` — mas **só** após Etapa 02 funcionar.
2. **Dia 3 (NEE + MIS)**: Etapas 03 e 04 juntas. *Threshold*: MSE da cena de validação cai ≥ 4× ao ativar MIS contra NEE-only no mesmo SPP.
3. **Dia 4 (Russian Roulette)**: Etapa 05. *Threshold*: tempo cai ≥ 25% sem mudar a média global em cena reflexiva.
4. **Dia 5–6 (extras médios)**: Etapas 06 (mesh light), 07 (dielétrico), 08 (GGX), 09 (envmap). *Threshold*: galeria GGX 5×2 nítida; cáustica visível na cena de vidro (mesmo ruidosa).
5. **Dia 7–10 (avançado)**: Etapa 10 (BDPT). *Threshold*: cáustica do vidro converge com SPP modesto e BDPT vence PT+MIS no MSE.
6. **Dia 11–12 (MLT)**: Etapa 11. *Threshold*: PSSMLT renderiza cena SDS onde BDPT falha; aceitar variância maior por iteração desde que a imagem média convirja.
7. **Dia 13–14**: Etapa 12 — gerar relatório, validar tabela de rastreabilidade, conferir bibliografia.

**Critérios de parada de cada etapa antes de avançar:**
- Imagem produzida (PNG).
- Snapshot JSON+MD válido com comando CLI.
- Pelo menos uma figura comparativa no markdown da etapa.
- Citações com DOI/URL completos.

**O que mudaria meus conselhos:**
- Se Python puro for absurdamente lento (> 1 h/imagem em 512² × 256 spp), **integre numba imediatamente após a Etapa 02**, antes de qualquer extra. Isso é única dependência adicional aceitável.
- Se BDPT for difícil de fazer convergir em 2 dias (provável em Python puro), entregue apenas a versão com `s=1` (NEE direto na light subpath) e `t≥1`, deixando `s≥2` para trabalho futuro — ainda capta o ponto principal e satisfaz o enunciado.
- Se MLT não couber no cronograma, MANTENHA apenas BDPT — BDPT já é uma alternativa válida ao bloco de extras simples e a soma dos extras simples + BDPT ultrapassa a nota máxima possível.

---

## Caveats

- **Desempenho do Python puro é o principal risco.** Path tracing puro em Python é tipicamente 10–100× mais lento que C++. Trabalhe em resoluções ≤ 512² e SPP ≤ 256 no pipeline rápido; reserve renderizações finais ≤ 1024² @ ≤ 1024 spp (horas). Use `render_estimator` para anunciar tempo previsto antes de cada batch.
- **MLT é frágil.** Em Python puro pode ser muito lento; bootstrap pequeno (K ~ 10⁴) e cadeias curtas. Foco em correção (não-viés) mais que velocidade.
- **PBRT 4e ≠ PBRT 3e nas seções de bidirecional.** BDPT e MLT foram removidos do livro 4ª edição (o capítulo "Light Transport III: Bidirectional Methods" da 3ª edição desapareceu). Cite **3ª edição** explicitamente nas Etapas 10–11 e marque essa diferença em apêndice do relatório (importante para o avaliador).
- **MIS para superfícies especulares.** BSDFs com pdf delta (Etapa 07 dielétrico ideal) **não** participam de MIS — apenas amostragem BSDF. Documentar claramente no código.
- **Cáusticas em PT puro = fireflies.** Esperado e desejado: a Etapa 10 (BDPT) existe justamente para isso e o contraste é cobrado visualmente no relatório.
- **Warm-up bias em MLT.** A média estimada nas primeiras iterações da cadeia é viciada (cadeia ainda não estacionária). Descarte primeiras N iterações (Slide 11 — Celes discute) ou aceite o bias e documente.
- **Citações de DOIs.** Todas as DOIs neste plano foram extraídas dos metadados das publicações originais; algumas (Veach 1995/1997, Kelemen 2002, Walter 2007, Hachisuka 2014) são as versões finais publicadas pelos editores (ACM, Eurographics, Wiley). A DOI Eurographics da Walter et al. 2007 (`10.2312/EGWR/EGSR07/195-206`) segue o esquema de DOIs do Eurographics Digital Library; alguns mirrors podem usar o formato alternativo `10.2312/EGWR.07.195-206` — ambos resolvem para o mesmo paper.
- **Slides "Microfaceta" do Prof. Celes** são citados na lista oficial como "11. Microfaceta" (numeração da disciplina); confira que o número/letra da apostila do semestre vigente coincide com este — se na entrega o slide deck tiver mudado de numeração, atualize todas as referências.