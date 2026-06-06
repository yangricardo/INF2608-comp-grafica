# Plano Mestre de Execução — Projeto 2 (INF2608): Path Tracer em Python
## Versão com Citações Bibliográficas Integradas

> **Curso:** INF2608 — Fundamentos de Computação Gráfica (PUC-Rio, Prof. Waldemar Celes)
> **Projeto:** Projeto 2 — Renderizador por Path Tracing
> **Linguagem/Bibliotecas obrigatórias:** Python ≥ 3.11, `pyglm` (`from pyglm import glm`), `pillow` (PIL). Nenhuma outra dependência pesada de renderização.
> **Base de código:** este projeto **estende** o pacote `src/ray_tracing_2` (ray tracer recursivo existente). O path tracer mora em um **novo** pacote `path_tracing/`.

---

## TL;DR — Visão Geral Executiva

O Projeto 2 é entregue em **12 etapas independentes** (cada uma com um markdown próprio `etapa_NN_*.md` em `docs/proj2/`), começando pelo núcleo unidirecional \cite{inf2608slides08} \cite{pharr2023pbrt} \cite{kajiya1986rendering} (Etapa 02, que sozinha vale os 7.0 pts base) e progredindo por todos os extras possíveis: MIS \cite{veach1995optimallycombin}, Russian Roulette \cite{misso2022unbiased}, mesh light, refração, GGX \cite{walter2007microfacet}, environment, culminando em BDPT \cite{veach1995optimallycombin} (Etapa 10) e MLT/PSSMLT \cite{kelemen2002simple} (Etapa 11) como "ir além", com consolidação em LaTeX (Etapa 12).

Toda a arquitetura nova vive em `path_tracing/` (réplica adaptada de `src/ray_tracing_2` + módulos novos: `bsdf/`, `lights/`, `integrators/`, `mis.py`, `onb.py`), preservando o sistema de snapshots/CLI/render-estimator do Projeto 1 para garantir reprodutibilidade.

As citações são precisas: PBRT 4e \cite{pharr2023pbrt} §2.2.3 (MIS), §2.2.4 (RR), §6.5 (triangle area sampling), §9.2 (Lambert), §9.5 (Dielectric), §9.6.1–9.6.5 (GGX/Torrance–Sparrow), §12.4–§12.6 (luzes), §13.1–§13.4 (path tracing), §A.5 (Malley); BDPT/MLT vêm de PBRT **3ª edição** \cite{pharr2018pbrt3e} §16.3 e §16.4 (removidos do 4ed); papers: \cite{kajiya1986rendering}, \cite{veach1995optimallycombin}, \cite{veach1997metropolis}, \cite{misso2022unbiased}, \cite{seyb2024microfacets}, \cite{walter2007microfacet}, \cite{kelemen2002simple}, \cite{hachisuka2014multiplexed}, \cite{frisvad2012orthonormal}.

---

## 1. Visão Geral e Arquitetura

### 1.1 Layout proposto do pacote `path_tracing/`

```
path_tracing/
├── __init__.py
├── camera.py              # cópia adaptada de ray_tracing_2.camera
├── ray.py                 # idem
├── hit.py                 # idem
├── shape.py               # estendido com sample_area()
├── triangle_bvh.py        # idem
├── sampling.py            # estendido: cosine_hemisphere(), uniform_triangle(), VNDF-GGX
├── onb.py                 # NOVO: base ortonormal local (Frisvad)
├── film.py                # idem
├── scene.py               # adaptado
├── render.py              # adaptado
├── render_estimator.py    # idem
├── render_snapshot.py     # idem
├── cli.py                 # subcomandos por cena
│
├── bsdf/
│   ├── __init__.py
│   ├── base.py
│   ├── lambertian.py      # f = rho/pi
│   ├── dielectric.py      # Snell + Fresnel + Beer-Lambert
│   ├── microfacet_ggx.py  # Cook-Torrance/GGX
│   └── emissive.py
│
├── lights/
│   ├── __init__.py
│   ├── base.py
│   ├── area_rect.py       # luz retangular
│   ├── area_mesh.py       # luz como malha
│   └── infinite.py        # environment light
│
├── integrators/
│   ├── __init__.py
│   ├── base.py
│   ├── path_tracer.py     # unidirecional
│   ├── bdpt.py            # bidirecional
│   └── mlt.py             # Metropolis
│
└── mis.py                 # NOVO — balance_heuristic, power_heuristic
```

### 1.2 Diferença conceitual: ray tracer recursivo × path tracer

A transição do Projeto 1 para o Projeto 2 é uma reescrita conceitual do **integrador**, não da geometria. O ray tracer recursivo resolve a Equação de Renderização \cite{kajiya1986rendering} analiticamente via recursão (Whitted ray tracing com Phong); o path tracer resolve a mesma equação **estocasticamente** via Monte Carlo \cite{pharr2023pbrt} \cite{inf2608slides07}, acumulando **throughput β** e construindo caminhos incrementalmente \cite{inf2608slides08}.

| Aspecto | Ray Tracer (Projeto 1) | Path Tracer (Projeto 2) |
|---|---|---|
| **Equação** | Phong analítico + reflexão recursiva | Light Transport Equation (LTE) / Path Integral \cite{kajiya1986rendering} |
| **Iluminação direta** | Loop sobre luzes com `direct_lighting()` | Amostra uma direção via BSDF e/ou luz com pdf |
| **Iluminação indireta** | Apenas reflexão especular | Construção incremental com throughput β \cite{inf2608slides08} |
| **Amostragem** | Determinística (Phong specular) | Probabilística via distribuições de importância \cite{pharr2023pbrt} |
| **Convergência** | Nítida com baixo SPP | Ruidosa até SPP alto (σ ∝ 1/√N) |

---

## 2. Etapas de Execução

### Etapa 01 — Boilerplate do pacote `path_tracing/`

**Objetivo:** Criar o pacote `path_tracing/` espelhando a arquitetura de `src/ray_tracing_2`, sem ainda implementar o integrador.

**Referências técnicas:**
- **Slide:** \cite{inf2608slides09} — seção *HemisphereToGlobal* (base ortonormal local)
- **PBRT 4e:** \cite{pharr2023pbrt} §3.3 *Vectors* e CoordinateSystem
- **Paper:** \cite{frisvad2012orthonormal} — "*Building an Orthonormal Basis from a 3D Unit Vector Without Normalization*" (branchless ONB)

**Matemática — Base ortonormal de Frisvad:**

```
if n.z < -0.9999999: t = (0,-1,0), b = (-1,0,0)
else: a = 1/(1+n.z); k = -n.x*n.y*a; 
      t = (1 - n.x²*a, k, -n.x); 
      b = (k, 1 - n.y²*a, -n.y)
```

**Deliverables:**
- `path_tracing/{ray,hit,camera,shape,triangle_bvh,sampling,film,scene,render_snapshot,render,render_estimator,cli}.py`
- `path_tracing/onb.py` com `frisvad_branchless(n) -> (t, b)`
- Esqueletos vazios: `bsdf/`, `lights/`, `integrators/`, `mis.py`

---

### Etapa 02 — Núcleo do Path Tracer Unidirecional (Aplicação Básica, 7.0 pts)

**Objetivo:** Implementar o `PathIntegrator` unidirecional capaz de renderizar uma cena Cornell-box-like com **BSDF Lambertiana** \cite{pharr2023pbrt}, **N caminhos/pixel**, **profundidade mínima 4**, amostragem de BSDF com método de Malley \cite{inf2608slides07}.

**Referências técnicas:**
- **Slides:** \cite{inf2608slides07} (Monte Carlo, PDF, CDF, importance sampling, hemisfério cosseno); \cite{inf2608slides08} (LTE, path integral \cite{kajiya1986rendering}, throughput, BRDF Lambertiana ρ/π, TracePath)
- **PBRT 4e:** \cite{pharr2023pbrt} §2.1 *Monte Carlo: Basics*, §2.2.2 *Importance Sampling*, §9.2 *Diffuse Reflection*, §13.1 *The Light Transport Equation*, §13.2 *Path Tracing*, §13.3 *A Simple Path Tracer*, §A.5 *Sampling Multidimensional Functions*
- **Paper:** \cite{kajiya1986rendering} — "*The Rendering Equation*" (SIGGRAPH 1986)

**Matemática — Estimador de path tracing com amostragem de BSDF:**

O estimador Monte Carlo do path integral é:
```
β ← (1,1,1);  L ← (0,0,0)
para depth = 1, 2, ..., max_depth:
   hit ← scene.intersect(ray)
   se !hit: L += β · background; break
   se hit.emissivo: L += β · Le; break          [apenas se modo ≠ "nee"]
   wo = -ray.d (frame local)
   (wi, pdf, f) = bsdf.sample(wo, u)
   se pdf ≈ 0: break
   β *= f · |cosθ_i| / pdf
   ray ← Ray(offset_point(hit.p, hit.n), wi_global)
   se depth >= max_depth: break
```

Para a Lambertiana \cite{pharr2023pbrt} com amostragem cosseno-ponderada (Método de Malley \cite{inf2608slides07}):
```
f(ω_o, ω_i) = ρ/π
pdf(ω_o, ω_i) = cosθ_i/π
β *= (ρ/π) · cosθ_i / (cosθ_i/π) = ρ    [cosθ e π cancelam]
```

**Profundidade mínima:** O enunciado exige que o caminho tenha no mínimo **4 vértices na superfície** (câmera → x₁ → x₂ → x₃ → luz), garantindo interações significativas. Nenhuma terminação antecipada (RR) antes da profundidade mínima.

**Pontos:** Atende **toda a aplicação básica = 7.0 pts**.

**Validação:**
- Cornell-like com 1 luz no teto, 2 caixas no chão
- Renderizar com **spp ∈ {4, 16, 64, 256}** e verificar redução de ruído
- Furnace test: paredes brancas (ρ=0.8) → brilho médio coerente

**Prompt copiável:**

```
Implemente a Etapa 02 do Projeto 2 — núcleo unidirecional do Path Tracer.

Referências obrigatórias (citar em docstrings):
- Slide 7 (Integração de Monte Carlo) — PDF, CDF, inversion method, importance sampling, Método de Malley
- Slide 8 (Traçado de Caminhos) — LTE, path integral, throughput β, TracePath, BRDF Lambertiana ρ/π
- PBRT 4e §2.1, §2.2.2, §9.2, §13.1, §13.2, §13.3, §A.5
- Kajiya, "The Rendering Equation", SIGGRAPH 1986, DOI 10.1145/15922.15902

Implementação:

1) Em `path_tracing/bsdf/lambertian.py`:
   class LambertianBSDF(rho: glm.vec3):
   - eval(wo, wi) = rho/π
   - sample(wo, u) via Método de Malley (sqrt + circulo)
   - pdf(wo, wi) = max(0, wi.z)/π

2) Em `path_tracing/bsdf/emissive.py`:
   class EmissiveBSDF(Le: glm.vec3):
   - is_emissive = True
   - eval/pdf = 0

3) Em `path_tracing/lights/area_rect.py`:
   class RectAreaLight(corner, edge_u, edge_v, Le)

4) Em `path_tracing/integrators/path_tracer.py`:
   class PathIntegrator(min_depth=4, max_depth=8, mode="bsdf_only")
   def Li(ray, scene, sampler) -> iterativo com throughput beta

5) Cena `path_tracing/scenes/proj2_req1_lambert_basic.py`: Cornell-like 5 planos + 2 caixas + 1 luz retangular

6) CLI: `proj2_req1_lambert_basic --spp N --depth D --out OUT` com snapshot completo

7) Entregável `docs/proj2/etapa_02_path_tracer_core.md`:
   - Pseudocódigo do integrador
   - Fórmula explícita β *= f · cosθ / pdf
   - Galeria SPP = {4,16,64,256}
   - Citações: Slide 7, 8; PBRT 4e §2.1, §2.2.2, §9.2, §13.1-13.3, §A.5; Kajiya SIGGRAPH 1986
```

---

### Etapa 03 — Next Event Estimation (NEE) em luzes retangulares

**Objetivo:** Amostragem direta da luz a cada vértice, reduzindo drasticamente a variância.

**Referências técnicas:**
- **Slide:** \cite{inf2608slides09} — seção *NEE / Next Event Estimation*
- **PBRT 4e:** \cite{pharr2023pbrt} §12.4 *Area Lights*, §12.6 *Light Sampling*, §13.4 *A Better Path Tracer*

**Matemática — Conversão pdf_area → pdf_solid_angle:**

```
pdf_area(p_L) = 1/A
r = |p - p_L|
cosθ_L = max(0, -dot(ω_i, n_L))
pdf_solid_angle = pdf_area · r² / cosθ_L
L_direct = f(ω_o, ω_i) · Le · cosθ_x · cosθ_L · A / r²
```

---

### Etapa 04 — MIS (Multiple Importance Sampling) no último segmento

**Objetivo:** Combinar amostragem do BSDF e amostragem direta da luz com **balance heuristic** e **power heuristic com β=2**.

**Referências técnicas:**
- **Slide:** \cite{inf2608slides09} — seção *MIS / Multiple Importance Sampling*
- **PBRT 4e:** \cite{pharr2023pbrt} §2.2.3 *Multiple Importance Sampling*
- **Paper:** \cite{veach1995optimallycombin} — "*Optimally Combining Sampling Techniques for Monte Carlo Rendering*" (SIGGRAPH 1995, Eq. 9 balance heuristic, Eq. 14 power heuristic)

**Matemática — Estimador MIS one-sample:**

```
F_MIS = (1/n_a) Σ w_a(X_a) f(X_a)/p_a(X_a)  +  (1/n_b) Σ w_b(X_b) f(X_b)/p_b(X_b)

w_s(x) = (n_s p_s(x))^β / Σ_i (n_i p_i(x))^β

β=1: balance heuristic
β=2: power heuristic (preferido)
```

**Pontos:** **+1.0 pt** (extensão)

---

### Etapa 05 — Russian Roulette

**Objetivo:** Terminar caminhos profundos probabilisticamente sem viés.

**Referências técnicas:**
- **Slide:** \cite{inf2608slides09} — *Russian Roulette*
- **PBRT 4e:** \cite{pharr2023pbrt} §2.2.4 *Russian Roulette*
- **Paper:** \cite{misso2022unbiased} — "*Unbiased and consistent rendering using biased estimators*" (ACM TOG 2022); path tracing visto como série telescópica

**Matemática — Estimador F com RR:**

```
q = clamp(1.0 - max(β.r, β.g, β.b), 0.05, 0.95)
if random() < q: break
β /= (1 - q)
E[F'] = E[F]  (não viesado)
```

**Pontos:** **+2.0 pts** (extensão)

**Limitação:** Apenas aplicar RR **após** `min_depth=4` obrigatório (exigência do enunciado).

---

### Etapa 06 — Luz de Área Poliédrica (Triangle Mesh)

**Objetivo:** Permitir que **qualquer** triangle mesh seja luz com amostragem uniforme por área.

**Referências técnicas:**
- **PBRT 4e:** \cite{pharr2023pbrt} §6.5 *Triangle Meshes*, §12.4 *Area Lights*, §12.6 *Light Sampling*, §A.5 *Sampling Multidimensional Functions*

**Matemática — Amostragem uniforme em triângulo:**

```
b0 = 1 − sqrt(u.x)
b1 = sqrt(u.x) · (1 − u.y)
b2 = sqrt(u.x) · u.y
p = b0 P0 + b1 P1 + b2 P2
pdf_area = 1 / total_area
```

**Pontos:** **+1.0 pt** (extensão)

---

### Etapa 07 — BSDF Dielétrica Refrativa

**Objetivo:** Objetos refrativos com Snell, Fresnel real, e Beer-Lambert.

**Referências técnicas:**
- **PBRT 4e:** \cite{pharr2023pbrt} §9.3 *Specular Reflection and Transmission*, §9.5 *Dielectric BSDF*, §11.2 *Transmittance*

**Matemática — Fresnel dielétrico e Snell:**

```
η_i sinθ_i = η_t sinθ_t  (Lei de Snell)
cosθ_t = √(1 − (η_i/η_t)² sin²θ_i)
F_dielétrico (eq. 9.6 PBRT 4e) [fórmulas de Fresnel por componentes r∥ e r⊥]
T(r) = exp(−σ_t · r)  (Beer-Lambert)
```

**Pontos:** **+2.0 pts** (extensão)

---

### Etapa 08 — BSDF Microfacetada Cook-Torrance / GGX

**Objetivo:** Materiais com rugosidade controlável (workflow metalness/roughness/baseColor).

**Referências técnicas:**
- **Slide:** \cite{inf2608slides11microfaceta} — Cook-Torrance, GGX, Smith-Schlick
- **PBRT 4e:** \cite{pharr2023pbrt} §9.6 *Roughness Using Microfacet Theory* (§9.6.1 Distribution D, §9.6.2 Masking Λ, §9.6.3 G, §9.6.4 VNDF, §9.6.5 Torrance–Sparrow)
- **Paper:** \cite{walter2007microfacet} — "*Microfacet Models for Refraction through Rough Surfaces*" (EGSR 2007, GGX/Trowbridge-Reitz, Smith, Schlick)
- **Contexto teórico avançado:** \cite{seyb2024microfacets} — "*From microfacets to participating media: A unified theory of light transport with stochastic geometry*" (ACM TOG 2024)

**Matemática — Cook-Torrance com α = roughness²:**

```
D(ω_h) = α² / (π · ((n·ω_h)²(α²−1) + 1)²)  (GGX/Trowbridge-Reitz)
G_smith_height_correlated(ω_o, ω_i, α)      (Smith com correlação)
F(cosθ) = F0 + (1 − F0)(1 − cosθ)^5         (Schlick)
f_r = D · F · G / (4 · |n·ω_o| · |n·ω_i|)   (Eq. 9.33)
```

**Pontos:** **+1.0 pt** (extensão)

---

### Etapa 09 — Luz Infinita / Environment Light

**Objetivo:** Iluminação ambiente direcional via environment map ou sky uniforme.

**Referências técnicas:**
- **PBRT 4e:** \cite{pharr2023pbrt} §12.5 *Infinite Area Lights*, §12.6 *Light Sampling*

**Matemática — Amostragem lat-long com Jacobiano:**

```
pdf_dir(ω) = pdf_uv / (2π² sinθ)  [conversão área → ângulo sólido]
```

**Pontos:** **+1.0 pt** (extensão)

---

### Etapa 10 — Bidirectional Path Tracing (BDPT)

**Objetivo:** Subcaminho da câmera + subcaminho da luz; conectar todos pares (s, t) com MIS. Resolve cáusticas e padrões SDS (Specular-Diffuse-Specular).

**Referências técnicas:**
- **Slide:** \cite{inf2608slides10} — *Métodos Bidirecionais*
- **PBRT 3e (removido do 4ed!):** \cite{pharr2018pbrt3e} §16.3 *Bidirectional Path Tracing*
- **Paper:** \cite{veach1995optimallycombin} — SIGGRAPH 1995 (estratégias BDPT com MIS); \cite{veach1997metropolis} — SIGGRAPH 1997; \cite{veach1997thesis} — tese Stanford 1997 (detalhes completos)

**⚠️ Nota crítica:** A 4ª edição do PBRT **removeu integralmente o capítulo sobre métodos bidirecionais**. A Etapa 10 deve **citar PBRT 3ª edição** \cite{pharr2018pbrt3e} §16.3 e explicitamente mencionar essa remoção no apêndice do relatório final.

**Pontos:** **+3.0 pts** (alternativa avançada)

---

### Etapa 11 — Metropolis Light Transport em Primary Sample Space (PSSMLT)

**Objetivo:** MCMC no espaço de variáveis aleatórias primárias com small/large mutations e aceitação Metropolis–Hastings.

**Referências técnicas:**
- **Slide:** \cite{inf2608slides11metropolis} — *Metropolis, MLT, PSSMLT, Kelemen*
- **PBRT 3e (removido do 4ed!):** \cite{pharr2018pbrt3e} §16.4 *Metropolis Light Transport*
- **Papers:**
  - \cite{veach1997metropolis} — SIGGRAPH 1997 (MLT original)
  - \cite{kelemen2002simple} — CGF 2002 (mutação Kelemen: small-step exponencial + large-step uniforme)
  - \cite{hachisuka2014multiplexed} — ACM TOG 2014 (Multiplexed MLT com MIS)

**⚠️ Nota crítica:** PBRT 4ª edição removeu este capítulo também. Cite **PBRT 3ª edição** \cite{pharr2018pbrt3e} §16.4.

**Pontos:** **+3.0 pts** (alternativa avançada)

**Limitação esperada:** Warm-up bias (cadeia não-estacionária nas primeiras iterações); documentar descarte de burn-in conforme \cite{inf2608slides11metropolis}.

---

### Etapa 12 — Consolidação: Relatório LaTeX

**Objetivo:** Produzir `inf2608-proj2.pdf` no molde de `inf2608-proj1.v3.pdf`.

**Estrutura obrigatória:**

1. **Título, autor, data, resumo (PT)** e **abstract (EN) + keywords**
2. **1. Introdução** — LTE \cite{kajiya1986rendering}, motivação, organização
3. **2. Pipeline e Geometria** — câmera, BVH, instancing (referência Projeto 1)
4. **3. Monte Carlo & Path Tracing Unidirecional** — Etapas 02–03 (\cite{inf2608slides07}, \cite{inf2608slides08}, \cite{pharr2023pbrt})
5. **4. MIS** — Etapa 04 (\cite{veach1995optimallycombin}, \cite{pharr2023pbrt})
6. **5. Russian Roulette** — Etapa 05 (\cite{misso2022unbiased}, \cite{pharr2023pbrt})
7. **6. Luzes de Área (retangular e poliédrica)** — Etapa 06 (\cite{pharr2023pbrt})
8. **7. BSDFs: Lambertiano, Dielétrico, GGX** — Etapas 07–08 (\cite{pharr2023pbrt}, \cite{walter2007microfacet}, \cite{seyb2024microfacets})
9. **8. Luz Infinita / Environment** — Etapa 09 (\cite{pharr2023pbrt})
10. **9. Métodos Bidirecionais e MLT** — Etapas 10–11 (\cite{pharr2018pbrt3e}, \cite{veach1995optimallycombin}, \cite{veach1997metropolis}, \cite{kelemen2002simple}, \cite{hachisuka2014multiplexed})
11. **10. Evidência Visual** — galeria com comandos CLI exatos
12. **11. Decisões de Modelagem e Limites**
13. **12. Conclusão e Trabalhos Futuros** — citar \cite{seyb2024microfacets} (volumes), \cite{misso2022unbiased} (estimadores enviesados)
14. **Referências** — arquivo `refs.bib` completo
15. **Apêndices:**
    - **A. Rastreabilidade** (conceito → slide → PBRT § → arquivo:linha)
    - **B. Evidência** (figura → comando → snapshot)
    - **C. Diagramas de classe** (BSDF hierarchy, Light hierarchy, Integrator hierarchy)

---

## 3. Tabela-Síntese Final

| Etapa | Tema | Pontos | Slide(s) | PBRT § | Paper(s) | Markdown |
|---|---|---|---|---|---|---|
| 01 | Boilerplate | infra | \cite{inf2608slides09} | 4e §3.3; A.5 | \cite{frisvad2012orthonormal} | `etapa_01_boilerplate.md` |
| 02 | Path tracer core | **7.0** | \cite{inf2608slides07}, \cite{inf2608slides08} | 4e §2.1, §2.2.2, §9.2, §13.1-13.3, §A.5 | \cite{kajiya1986rendering} | `etapa_02_path_tracer_core.md` |
| 03 | NEE | suporte | \cite{inf2608slides09} | 4e §12.4, §12.6, §13.4 | — | `etapa_03_nee.md` |
| 04 | MIS | **+1.0** | \cite{inf2608slides09} | 4e §2.2.3, §13.4 | \cite{veach1995optimallycombin} | `etapa_04_mis.md` |
| 05 | Russian Roulette | **+2.0** | \cite{inf2608slides09} | 4e §2.2.4, §13.4 | \cite{misso2022unbiased} | `etapa_05_russian_roulette.md` |
| 06 | Mesh light | **+1.0** | \cite{inf2608slides09} | 4e §6.5, §12.4, §A.5 | — | `etapa_06_mesh_light.md` |
| 07 | Dielétrico | **+2.0** | \cite{inf2608slides08} | 4e §9.3, §9.5, §11.2 | — | `etapa_07_refraction.md` |
| 08 | Microfaceta/GGX | **+1.0** | \cite{inf2608slides11microfaceta} | 4e §9.6.1-9.6.5 | \cite{walter2007microfacet}, \cite{seyb2024microfacets} | `etapa_08_microfacet.md` |
| 09 | Environment | **+1.0** | \cite{inf2608slides09} | 4e §12.5, §12.6, §A.5 | — | `etapa_09_envmap.md` |
| 10 | BDPT | **+3.0** (alt.) | \cite{inf2608slides10} | 3e §16.3 | \cite{veach1995optimallycombin}, \cite{veach1997thesis} | `etapa_10_bdpt.md` |
| 11 | MLT/PSSMLT | **+3.0** (alt.) | \cite{inf2608slides11metropolis} | 3e §16.4 | \cite{veach1997metropolis}, \cite{kelemen2002simple}, \cite{hachisuka2014multiplexed} | `etapa_11_mlt.md` |
| 12 | Relatório LaTeX | entrega | todos | todos | todos | `etapa_12_relatorio.md` + `report/proj2.tex` |

---

## 4. Observações Transversais Importantes

### 4.1 Reprodutibilidade e Snapshots

Cada etapa registra `seed` no snapshot. O `render_snapshot` é estendido com:
- `integrator`: nome do integrador (PathTracer, BDPT, MLT)
- `min_depth`, `max_depth`, `spp`
- `russian_roulette`: bool
- `mis_heuristic`: "balance" ou "power"
- `bsdf_list`: lista de BSDFs na cena
- `light_list`: lista de luzes
- Para BDPT: `max_s`, `max_t`
- Para MLT: `bootstrap_K`, `chain_length`, `burn_in`

### 4.2 Validação do Não-Viés

Cene com `spp=2048` devem produzir L1 ≤ 1% entre todos os modos `{bsdf_only, nee_only, mis, mis+rr, bdpt, mlt}`. **Convergência para a mesma imagem média é a garantia de corretude.**

### 4.3 PBRT 4e vs 3e

A 4ª edição (2023) **removeu integralmente** o capítulo 16 "Light Transport III: Bidirectional Methods" que continha §16.3 (BDPT) e §16.4 (MLT). Etapas 10 e 11 devem citar **PBRT 3ª edição** \cite{pharr2018pbrt3e} e **explicitamente marcar essa diferença em apêndice** do relatório final.

### 4.4 Especulares não usam MIS

BSDFs com pdf delta (Etapa 07 dielétrico ideal, Etapa 08 GGX especular puro) **não** participam de MIS — apenas amostragem de BSDF. Documentar isso claramente no código e no relatório.

### 4.5 Cáusticas em PT puro = esperado

Fireflies são esperados e desejados em path tracing puro. A Etapa 10 (BDPT) existe justamente para reduzir esse ruído. O contraste visual é cobrado no relatório.

### 4.6 Warm-up Bias em MLT

Cadeia MCMC nas primeiras iterações é viciada (não-estacionária). Descartar primeiras N iterações (burn-in) ou aceitar o bias e documentar, conforme \cite{inf2608slides11metropolis}.

---

## 5. Cronograma Recomendado (2 semanas)

| Dias | Etapas | Threshold de avanço |
|---|---|---|
| 1–2 | 01 + 02 | Smoke test com SPP=64 em < 5 min; snapshot completo |
| 3 | 03 + 04 | MSE cai ≥ 4× ao ativar MIS contra NEE-only |
| 4 | 05 | Tempo cai ≥ 25% sem mudar média (em cena reflexiva) |
| 5–6 | 06 + 07 + 08 + 09 | Galeria GGX 5×2; cáustica visível (mesmo ruidosa) |
| 7–10 | 10 | BDPT converge com SPP modesto; vence PT+MIS em cenas SDS |
| 11–12 | 11 | PSSMLT renderiza cena SDS; aceitar variância maior se média converte |
| 13–14 | 12 | Relatório com tabela rastreabilidade e bibliografia completa |

---

## Referências Completas

Todas as referências citadas neste documento estão em `refs.bib`:

- Slides INF2608 (Prof. W. Celes): \cite{inf2608slides07}, \cite{inf2608slides08}, \cite{inf2608slides09}, \cite{inf2608slides10}, \cite{inf2608slides11metropolis}, \cite{inf2608slides11microfaceta}
- Physically Based Rendering: \cite{pharr2023pbrt} (4ª ed.), \cite{pharr2018pbrt3e} (3ª ed.)
- Papers seminais: \cite{kajiya1986rendering}, \cite{veach1995optimallycombin}, \cite{veach1997metropolis}, \cite{veach1997thesis}
- Técnicas avançadas: \cite{misso2022unbiased}, \cite{seyb2024microfacets}, \cite{walter2007microfacet}, \cite{kelemen2002simple}, \cite{hachisuka2014multiplexed}, \cite{frisvad2012orthonormal}
- Repositório: \cite{inf2608projectrepo}

---

*Fim do Plano Mestre (versão com citações integradas)*
