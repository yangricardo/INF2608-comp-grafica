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
def balance_heuristic(n_a, pdf_a, n_b, pdf_b) -> float:
    """Peso para estratégia A com balance heuristic (β=1)."""
    denom = n_a * pdf_a + n_b * pdf_b
    if denom <= 0.0:
        return 0.0
    return (n_a * pdf_a) / denom

def power_heuristic(n_a, pdf_a, n_b, pdf_b, beta: float = 2.0) -> float:
    """Peso para estratégia A com power heuristic (β=2 default)."""
    a = (n_a * pdf_a) ** beta
    b = (n_b * pdf_b) ** beta
    denom = a + b
    if denom <= 0.0:
        return 0.0
    return a / denom
```

> As assinaturas incluem a contagem de amostras `n_a`/`n_b` (tipicamente 1 cada),
> conforme PBRT 4e Eq. 2.14/2.15. Uso no integrador:
> `power_heuristic(1, pdf_luz, 1, pdf_bsdf, beta=2.0)`.

---

## Integrador `mis` Mode

⚠️ **Onde o peso BSDF incide (correção importante).** O peso da estratégia "BSDF
amostrou a luz" deve incidir **apenas** sobre a emissão `Le` vista **diretamente** no
vértice seguinte — **não** pode ser dobrado em `beta`. Se for dobrado, `beta` (que persiste
ao longo do caminho) carrega o peso para **todas** as contribuições posteriores (NEE e
emissão de vértices mais profundos), enviesando o estimador (imagem mais escura na
iluminação indireta). A versão anterior tinha esse bug.

Solução: `beta` permanece **throughput puro** (`f·cosθ/pdf`); o peso é guardado em
`pending_mis_weight` e aplicado **uma única vez** quando o raio de BSDF atinge um emissor.

```python
VALID_MODES = ('bsdf_only', 'nee_only', 'mis')
pending_mis_weight = 1.0   # peso para a Le vista no PRÓXIMO vértice (1.0 = primário/especular)

for iter_depth in 1..max_depth:
    hit = intersect(ray)
    if hit é emissivo:
        # peso aplicado SÓ aqui, à emissão direta; beta é throughput puro
        L += beta * Le * pending_mis_weight
        break

    # NEE (pulado se bsdf.is_specular()): peso é local a este termo
    if mode in ('nee_only','mis') and not bsdf.is_specular():
        for light in scene.lights:
            ... sample_Li ...
            w_nee = power_heuristic(1, pdf_nee, 1, bsdf.pdf(wo,wi_nee)) if mode=='mis' else 1.0
            L += beta * f_nee * Li_nee * cos_nee / pdf_nee * w_nee

    # Amostra BSDF
    (wi, pdf_bsdf, f) = bsdf.sample(wo, u)
    if bsdf.is_specular():
        beta *= f / pdf_bsdf            # sem cosseno; delta
        pending_mis_weight = 1.0        # NEE não alcança a direção delta
    else:
        beta *= f * cos_theta / pdf_bsdf   # THROUGHPUT PURO (sem w_bsdf!)
        if mode == 'mis':
            pdf_luz = sum(light.pdf_Li(hit.pos, wi_global) for light in scene.lights)
            pending_mis_weight = power_heuristic(1, pdf_bsdf, 1, pdf_luz)
        else:
            pending_mis_weight = 1.0
    ray = Ray(offset(hit.pos), wi_global)
```

---

## Pseudocódigo MIS Combinado

```
// NEE (direct) — peso local ao termo, beta puro
para cada luz (se não especular):
    (wi_nee, pdf_nee, Li_nee) = amostra_luz(...)
    se não_ocluído(wi_nee):
        pdf_bsdf = bsdf.pdf(wo, wi_nee)
        w_nee = power_heuristic(1, pdf_nee, 1, pdf_bsdf)
        L += beta * bsdf.eval(...) * Li_nee * cos_nee * w_nee / pdf_nee

// BSDF — calcula o peso para a Le do PRÓXIMO vértice, mas NÃO o dobra em beta
(wi_bsdf, pdf_bsdf, f_bsdf) = amostra_bsdf(...)
pdf_luz = Σ luz.pdf_Li(hit.pos, wi_bsdf)
pending_mis_weight = power_heuristic(1, pdf_bsdf, 1, pdf_luz)
beta *= f_bsdf * cos_bsdf / pdf_bsdf            // throughput puro

// no próximo vértice, se for emissor:
//   L += beta * Le * pending_mis_weight        // peso aplicado UMA vez
```

Validação: nas três variantes (`bsdf_only`, `nee_only`, `mis`) a média da imagem converge
ao mesmo valor (teste cruzado: diferença bsdf↔mis ≈ 1.8% em 128 spp, limitada por ruído),
confirmando estimador não-viesado.

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
