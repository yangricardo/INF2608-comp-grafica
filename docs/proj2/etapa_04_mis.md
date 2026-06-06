# Etapa 04 — Multiple Importance Sampling (MIS)

## Objetivo

Combinar amostragem de BSDF e amostragem direta da luz com **pesos MIS** para reduzir viés do estimador one-sample, mantendo convergência não-viesada.

**Pontos:** **+1.0 pt** (extensão).

---

## Problema: One-Sample Bias

Cada estratégia de amostragem tem pontos cegos:

- **bsdf_only:** Direções especulares raramente amostram a luz diretamente → luz direta subamostra ada
- **nee_only:** Direções indiretas complexas (múltiplos bounces) subestimadas → falta iluminação global

Combinando ambas com pesos apropriados, reduzimos variância sem viés.

---

## Solução: Multiple Importance Sampling (MIS)

Amostramos de **múltiplas distribuições** e combinamos com pesos que dependem dos PDFs:

$$F_{\text{MIS}} = \sum_{i=1}^{n} w_i(X_i) \frac{f(X_i)}{p_i(X_i)}$$

onde $w_i$ satisfaz $\sum_i w_i(x) = 1$ para todo $x$ no suporte.

---

## Balance Heuristic (β=1)

$$w_s(x) = \frac{p_s(x)}{\sum_i p_i(x)}$$

Para duas estratégias (BSDF e luz):

$$w_{\text{BSDF}}(x) = \frac{p_{\text{BSDF}}(x)}{p_{\text{BSDF}}(x) + p_{\text{luz}}(x)}$$

$$w_{\text{luz}}(x) = \frac{p_{\text{luz}}(x)}{p_{\text{BSDF}}(x) + p_{\text{luz}}(x)}$$

---

## Power Heuristic (β=2) — Preferido

$$w_s(x) = \frac{(p_s(x))^2}{\sum_i (p_i(x))^2}$$

**Vantagem:** Reduz ainda mais a variância comparado a β=1, pois dá mais peso às estratégias melhores em cada região.

Ref: Veach & Guibas SIGGRAPH 1995, Equações 9 (balance) e 14 (power).

---

## Implementação: `mis.py`

```python
def balance_heuristic(pdf_a: float, pdf_b: float) -> float:
    """Peso para estratégia A com balance heuristic (β=1)."""
    denom = pdf_a + pdf_b
    if denom == 0.0:
        return 0.0
    return pdf_a / denom

def power_heuristic(pdf_a: float, pdf_b: float, beta: int = 2) -> float:
    """Peso para estratégia A com power heuristic (β=2 default)."""
    pdf_a_b = pdf_a ** beta
    pdf_b_b = pdf_b ** beta
    denom = pdf_a_b + pdf_b_b
    if denom == 0.0:
        return 0.0
    return pdf_a_b / denom
```

---

## Integrador `mis` Mode

```python
VALID_MODES = ('bsdf_only', 'nee_only', 'mis')

# Etapa 03: NEE com luz
if self.mode in ('nee_only', 'mis'):
    for light in scene.lights:
        # ... NEE sampling ...
        if self.mode == 'mis':
            # Calcular PDF da mesma direção via BSDF para MIS weight
            pdf_bsdf_for_nee = bsdf.pdf(wo_local, wi_nee_local)
            w_nee = mis.power_heuristic(pdf_nee, pdf_bsdf_for_nee)
        else:
            w_nee = 1.0
        L += beta * f_nee * Li_nee * cos_nee / pdf_nee * w_nee

# Etapa 02: BSDF com indirect
sample_result = bsdf.sample(wo_local, u_sample)
if self.mode == 'mis':
    # Calcular PDF da mesma direção via luz (MIS weight)
    pdf_light_for_bsdf = 0.0
    for light in scene.lights:
        pdf_light_for_bsdf += light.pdf_Li(hit.pos, wi_bsdf_global)
    w_bsdf = mis.power_heuristic(pdf_bsdf, pdf_light_for_bsdf)
else:
    w_bsdf = 1.0

L += beta * f_bsdf * Li_indirect * cos_bsdf / pdf_bsdf * w_bsdf
```

---

## Pseudocódigo MIS Combinado

```
// NEE (direct) com weight MIS
para cada luz:
    (wi_nee, pdf_nee, Li_nee) = amostra_luz(...)
    se não_ocluído(wi_nee):
        pdf_bsdf = bsdf.pdf(wo, wi_nee)  // avaliação extra!
        w_nee = power_heuristic(pdf_nee, pdf_bsdf)
        L += beta * bsdf.eval(...) * Li_nee * cos_nee * w_nee / pdf_nee

// BSDF (indirect) com weight MIS
(wi_bsdf, pdf_bsdf, f_bsdf) = amostra_bsdf(...)
se pdf_bsdf > 0:
    pdf_luz = 0
    para cada luz:
        pdf_luz += luz.pdf_Li(hit.pos, wi_bsdf)
    w_bsdf = power_heuristic(pdf_bsdf, pdf_luz)

    // Recursão / próximo vértice
    (hit2, L_indirect) = trace_ray(wi_bsdf)
    L += beta * f_bsdf * L_indirect * cos_bsdf * w_bsdf / pdf_bsdf
```

---

## Custo Computacional

MIS requer **duas avaliações de PDF a cada vértice** (uma por estratégia alternativa):

- **NEE:** `bsdf.pdf()` adicional para cada luz
- **BSDF:** `light.pdf_Li()` para cada luz

**Impacto:** ~2× shadow rays + ~nº_luzes × computação extra de PDF. Compensado por variância drasticamente reduzida.

---

## Resultado: Estimador Não-Viesado

A teoria MIS garante:

$$\mathbb{E}[F_{\text{MIS}}] = L_o$$

isto é, sem viés na expectativa, mesmo usando pesos não-uniformes.

---

## Galeria Comparativa

```bash
# bsdf_only (Etapa 02)
python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 32 --depth 6 --seed 42

# nee_only (Etapa 03)
python -m path_tracing.scripts.proj2_req2_nee --spp 32 --depth 6 --seed 42

# mis (Etapa 04) — a ser implementado
python -m path_tracing.scripts.proj2_req3_mis --spp 32 --depth 6 --seed 42
```

**Observações visuais:**

| Modo      | Fireflies  | Ruído uniforme | Convergência |
| --------- | ---------- | -------------- | ------------ |
| bsdf_only | Frequentes | Não-uniforme   | Lenta        |
| nee_only  | Poucas     | Uniforme       | Rápida       |
| mis       | Raras      | Suave          | Muito rápida |

---

## Referências Técnicas

- **Slide 9** "Traçado de Caminhos II" — seção _MIS / Multiple Importance Sampling_
- **PBRT 4e §2.2.3** "_Multiple Importance Sampling_"
- **PBRT 4e §13.4** "_A Better Path Tracer_" (com MIS integrado)
- **Veach & Guibas SIGGRAPH 1995** "_Optimally Combining Sampling Techniques for Monte Carlo Rendering_" — DOI: 10.1145/218380.218498
  - Equação 9: balance heuristic
  - Equação 14: power heuristic
