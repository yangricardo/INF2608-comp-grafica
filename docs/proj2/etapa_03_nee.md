# Etapa 03 — Next Event Estimation (NEE)

## Objetivo

Implementar amostragem direta (direct lighting) em cada vértice do caminho, reduzindo drasticamente a variância comparado ao `bsdf_only`. O `nee_only` mode amostra **apenas** a luz diretamente, sem amostragem indireta de BSDF.

**Pontos:** suporte para Etapa 04+ (MIS depende disso).

---

## Comparação: NEE vs. Ray Tracer vs. BSDF-only

| Aspecto          | Ray Tracer (Proj1)             | Path Tracer `bsdf_only`     | Path Tracer `nee_only`                                              |
| ---------------- | ------------------------------ | --------------------------- | ------------------------------------------------------------------- |
| **Estratégia**   | `direct_lighting()` + recursão | Amostra um caminho via BSDF | Amostra **duas** estratégias: (1) direta (luz), (2) indireta (BSDF) |
| **Luz emissiva** | Não existe; tudo é PointLight  | EmissiveBSDF box no teto    | **RectAreaLight em `scene.lights`**                                 |
| **Variância**    | Controlada (determinística)    | Alta até SPP alto           | Baixa (convergência mais rápida)                                    |
| **Custo**        | Fixo por profundidade          | Linear em SPP               | Linear em SPP **e** nº luzes (shadow rays)                          |

---

## Arquitetura: Duas Representações da Luz

Para suportar ambos os modos simultaneamente:

1. **`scene.objects`** contém `Box` com material `EmissiveBSDF`
   - Usada por: `bsdf_only` (caminho bate no painel → acumula Le)
2. **`scene.lights`** contém `RectAreaLight`
   - Usada por: `nee_only` (shadow ray vê a luz)
   - Ignorada por: `bsdf_only`

**Bug corrigido:** Shadow ray passa pela EmissiveBSDF Box antes de atingir RectAreaLight. **Solução:** tratar EmissiveBSDF como transparente:

```python
if shadow_hit is not None and shadow_hit.t < dist_nee - 1e-3:
    is_light_panel = (
        shadow_hit.material is not None
        and isinstance(shadow_hit.material, EmissiveBSDF)
    )
    if not is_light_panel:
        continue  # Ocluído por objeto opaco
```

---

## Matemática — Conversão PDF: Área → Ângulo Sólido

Amostragem uniforme por **área** de paralelogramo:

$$p_{\text{area}}(p_L) = \frac{1}{A}$$

O Jacobiano geométrico converte para **ângulo sólido**:

$$p_{\text{solid angle}}(\omega_i) = \frac{1}{A} \cdot \frac{r^2}{|\cos\theta_L|}$$

onde:

- $r = |p - p_L|$ — distância até amostra de luz
- $\cos\theta_L = |\mathbf{n}_L \cdot \omega_i|$ — cosseno entre normal da luz e raio

---

## Pseudocódigo NEE a cada vértice

```
// Loop principal de path tracing
para cada luz em scene.lights:
    u_light = vec2(random(), random())
    sample = luz.sample_Li(hit.pos, u_light)
    se sample == null: continue

    wi_nee = sample['wi']
    Li_nee = sample['Le']
    pdf_nee = sample['pdf_solid_angle']

    // Verificar sombra (com transparência para EmissiveBSDF)
    shadow_ray = Ray(offset_point(...), wi_nee)
    shadow_hit = scene.intersect(shadow_ray)

    se shadow_hit != null e shadow_hit.t < dist_nee:
        se shadow_hit.material não é EmissiveBSDF:
            continue  // Ocluído

    // Avaliar BSDF
    wi_nee_local = onb.global_to_local(wi_nee)
    cos_nee = max(0, wi_nee_local.z)
    se cos_nee == 0: continue

    f_nee = bsdf.eval(wo_local, wi_nee_local)
    L += beta * f_nee * Li_nee * cos_nee / pdf_nee
```

---

## Referências Técnicas

- **Slide 9** "Traçado de Caminhos II" — seção _NEE / Next Event Estimation_
- **PBRT 4e §13.4** "_A Better Path Tracer_"
- **PBRT 4e §12.4, §12.6** "_Area Lights, Light Sampling_"

---

## Resultado

Comando:

```bash
python -m path_tracing.scripts.proj2_req2_nee --spp 16 --depth 6 --width 256 --height 256 --seed 42 --no-calibrate
```

**Antes do fix:** Imagem completamente escura (shadow ray bloqueado).
**Depois do fix:** Cornell Box bem iluminada com redução de ruído vs. `bsdf_only`.

| Métrica              | bsdf_only  | nee_only  |
| -------------------- | ---------- | --------- |
| **Variância**        | Alta       | Baixa     |
| **Fireflies**        | Frequentes | Reduzidas |
| **Convergência SPP** | Lenta      | Rápida    |
