# Revisão: Planejamento × Implementação (Projeto 2 — Path Tracer)

> Comparação entre os planejamentos iniciais
> ([`docs/proj2_plan.md`](../proj2_plan.md), [`docs/plano2_with_citacoes.md`](../plano2_with_citacoes.md))
> e o que foi efetivamente implementado em `src/path_tracing`.
> **Escopo desta revisão:** apenas as **etapas implementadas** (01–07).
> Data: 2026-06-06.

---

## 0. Sumário executivo

- O **núcleo exigido pelo enunciado** (cena com esferas/caixas/planos, luz retangular,
  material difuso de BRDF constante, múltiplos caminhos por pixel, profundidade ≥ 4) está
  **implementado e correto** — vale os **7.0 pts** base.
- Os **extras implementados** (MIS, Russian Roulette, mesh light, dielétrico) somam **6.0 pts**
  "brutos", **acima dos 3.0 exigidos**. Logo, as etapas não implementadas (08 GGX, 09 env,
  10 BDPT, 11 MLT) são "ir além" opcionais e **não afetam a nota**.
- Os **cálculos** (cancelamento cos/pdf difuso, fator geométrico no NEE, pesos MIS, Snell/
  Fresnel/TIR do dielétrico) foram **auditados e corrigidos** em sessão anterior; o **Beer-Lambert**
  do dielétrico foi **concluído agora** (Etapa 07 completa). Esta revisão foca em
  **completude vs. plano** e em **qualidade/manutenção**, não em recorrigir o que já está certo.

### Matriz plano × implementado

| Etapa | Tema | Planejado | Implementado | Observação |
|------:|------|:--------:|:------------:|------------|
| 01 | Boilerplate + ONB Frisvad | ✅ | ✅ | `onb.py` branchless; pacote `path_tracing/` montado |
| 02 | Path tracer core (Lambert, depth≥4) | ✅ | ✅ | 7.0 pts; estimador `β*=f·cosθ/pdf` correto |
| 03 | NEE em luz retangular | ✅ | ✅ | conversão área→ângulo sólido correta |
| 04 | MIS (balance + power β=2) | ✅ | ✅ | corrigido (peso não mais dobrado em β) |
| 05 | Russian Roulette | ✅ | ✅ | fórmula difere do plano (ver §5) |
| 06 | Mesh light (poliedro) | ✅ | ✅ | corrigido (amostragem uniforme + geometria) |
| 07 | Dielétrico (Snell+Fresnel+Beer) | ✅ | ✅ | **Beer-Lambert concluído nesta sessão** |
| 08–11 | GGX, env, BDPT, MLT | ✅ (plano) | ❌ | fora de escopo; opcionais |
| 12 | Relatório LaTeX | ✅ (plano) | 🟡 | **início** criado nesta sessão (`latex/inf2608-proj2.tex`) |

---

## 1. Pontos de melhoria transversais (arquitetura)

1. **`Shape.sample_area()` não existe.** O plano (§1.2/Etapa 06) previa um método único de
   amostragem por área nas formas, reutilizado pelas luzes. Hoje a amostragem está
   **duplicada** entre [`lights/area_rect.py`](../../src/path_tracing/lights/area_rect.py)
   e [`lights/area_mesh.py`](../../src/path_tracing/lights/area_mesh.py) (cada uma faz sua
   conversão área→ângulo sólido e seu teste de visibilidade/orientação).
   *Melhoria:* extrair um helper comum (conversão pdf e checagem unilateral) ou um
   `sample_area`/`pdf_area` em `Shape`.
2. **`sampling.py` incompleto vs. plano.** Tem `cosine_hemisphere` e `uniform_triangle`
   (este último agora usado pela mesh light), mas **não** tem `uniform_sphere` nem `ggx_vndf`
   (estes só seriam necessários para 08/esfera-luz). *Melhoria:* adicionar quando/se 08 for feito.
3. **CLI unificado ausente.** O plano previa `path_tracing/cli.py` com subcomandos
   `proj2_req*`/`proj2_ext*`. Na prática há **scripts soltos** em `scripts/` e o `cli.py`
   atende o estilo do Projeto 1. Além disso a numeração pula `req4` (MIS=`req3`, RR=`req5`).
   *Melhoria:* unificar entradas sob um só CLI e renumerar de forma consistente
   (`req1`..`req6`) — ou documentar explicitamente o mapeamento req→etapa.
4. **Coexistência de código legado.** `light.py` (Ambient/Area/Point do Projeto 1) e
   `materials/` convivem com os novos `lights/` e `bsdf/`. Usado pela calibração
   (`render_estimator`/`trace_ray`), então não é morto — mas confunde.
   *Melhoria:* documentar a fronteira “legado (ray tracer) × novo (path tracer)” num README do
   pacote, ou isolar o legado em submódulo `compat/`.

## 2. Documentação (consistência)

- **Nomenclatura inconsistente:** mistura de `etapa_0X_*.md` (minúsculo) e `ETAPA_0X_*.md`
  (maiúsculo); **duplicatas** (`etapa_04_mis.md` + `ETAPA_04_MIS_TESTING.md`;
  `ETAPA_05_RR_RESULTS.md` + `ETAPA_05_RUSSIAN_ROULETTE.md`); nome divergente do plano
  (`ETAPA_07_DIELECTRIC.md` vs. `etapa_07_refraction.md`).
  *Melhoria:* padronizar para `etapa_NN_shortname.md` (minúsculo) e fundir duplicatas.
- Vários `.md` começam com `"""` (resquício de docstring). *Melhoria:* remover.

## 3. Etapa 02 — núcleo

- **Default de modo:** `PathIntegrator(mode='bsdf_only')` enquanto o plano sugeria `mis` como
  default. Os scripts passam o modo explicitamente, então não há bug — só divergência de default.
- **Gamma desligada por padrão:** os scripts usam `--gamma` opt-in; o plano pedia gamma 2.2
  sempre no PNG. Sem gamma, a Cornell sai mais escura/“lavada” no gradiente.
  *Melhoria:* ligar gamma por padrão nos scripts do proj2 (ou aplicar tone mapping) e manter
  `--no-gamma` como escape.
- **Galeria SPP {4,16,64,256}** prometida no plano existe como descrição em
  `etapa_02_path_tracer_core.md`, mas **não** como render reproduzível/script. *Melhoria:* script
  que gera a grade e a tabela de tempo/ruído.

## 4. Etapas 03–04 — NEE e MIS

- **Corretos** após a auditoria: NEE com `pdf_solid_angle` (fator G embutido); MIS com
  `power_heuristic(β=2)` e peso aplicado **uma vez** à emissão direta (não dobrado em `β`).
- `pdf_Li` agora é **unilateral** (retângulo e malha) — consistente com `sample_Li`.
- *Melhoria (validação):* o plano pedia curvas **MSE×SPP log-log** e cenas “luz pequena vs.
  grande” mostrando o ganho do MIS; isso não existe como experimento reproduzível. Recomendado
  adicionar à suíte de validação (ver §7).

## 5. Etapa 05 — Russian Roulette

- **Implementado e não-viesado**, porém com fórmula **diferente do plano**:
  - *Implementado:* `p_continue = min(max(β.r,β.g,β.b), 1.0); if rand()>p: break; β/=p`
    (probabilidade de **sobrevivência** = throughput, **sem piso/clamp**).
  - *Plano:* `q = clamp(1−max(β), 0.05, 0.95); if rand()<q: break; β/=(1−q)`
    (probabilidade de **morte** com piso 0.05 e teto 0.95).
  Ambas são corretas; a do plano evita variância extrema garantindo `5% ≤ p_sobrevivência ≤ 95%`.
  *Melhoria:* adicionar um piso pequeno (ex.: `p_continue = clamp(max(β),0.05,1.0)`) para
  robustez em caminhos de throughput muito baixo.
- **RR vs. profundidade mínima 4:** a RR dispara em `iter_depth ≥ rr_min_depth` (default 4).
  Como o caminho já tem 4 vértices nesse ponto, a exigência do enunciado é respeitada; ainda
  assim, documentar (ou usar `rr_min_depth = min_depth+1`) deixa a relação explícita.

## 6. Etapa 06 — mesh light

- **Corrigido:** amostragem agora **uniforme por área** (usa `uniform_triangle`, com remapeamento
  de `u.x` para obter 2 dimensões independentes) e geometria do emissor reorientada (quad voltado
  para baixo, em vez da pirâmide que emitia para fora da sala).
- *Melhoria:* a seleção de triângulo é **linear** sobre a CDF (`O(n)` por amostra). Para malhas
  grandes, usar **alias method** (previsto no plano) ou busca binária na CDF.

## 7. Etapa 07 — dielétrico (agora completo)

- **Concluído nesta sessão:** Snell (η correto entrando=1/ior), Fresnel exato (média s/p), TIR,
  e **Beer-Lambert** (`T=exp(−σ·d)` com rastreio de meio no integrador). Validação numérica:
  razão de saída `(0.671,0.301,0.091) ≈ exp(−σ·2)`.
- *Limitações declaradas:* meio **não aninhado** (1 nível: dentro/fora) — suficiente para
  esfera/cubo convexos isolados; fator de radiância `1/η²` omitido (cancela em objeto fechado).
- *Melhoria futura:* pilha de índices p/ objetos sobrepostos; Schlick como opção rápida de Fresnel.

## 8. Validações ausentes (recomendação de suíte)

O plano define vários critérios de aceitação que **não existem como código reproduzível**:

- **Furnace test** (paredes brancas sob luz uniforme → energia conservada).
- **Não-viés cross-mode** (`L1 ≤ 1%` entre `bsdf_only/nee_only/mis(+rr)` a SPP alto) —
  hoje só validado ad-hoc (média converge em ~1.8%).
- **MSE × SPP** (log-log, slope ≈ 1) para 02→03→04.
- **Beer-Lambert** quantitativo (já temos o teste; faltaria fixá-lo como regressão).

*Melhoria:* criar `src/path_tracing/validation/` (ou `tests/`) com esses checks rodáveis e
um alvo único (`python -m path_tracing.validation`), gerando as tabelas que o relatório precisa.

---

## 9. Itens acionáveis priorizados

| Prioridade | Item | Esforço |
|:---:|------|:---:|
| Alta | Gamma/tone mapping padrão nos scripts proj2 (§3) | baixo |
| Alta | Suíte de validação reproduzível: furnace, não-viés, MSE×SPP (§8) | médio |
| Média | Padronizar nomes/fundir docs duplicadas (§2) | baixo |
| Média | Piso na RR + documentar relação com min_depth (§5) | baixo |
| Média | Unificar CLI e renumerar req1..req6 (§1.3) | médio |
| Baixa | Extrair `sample_area`/helper comum das luzes (§1.1) | médio |
| Baixa | Alias method na mesh light (§6) | baixo |

> Estes itens são **recomendações**; nesta sessão foram executados apenas: conclusão do
> dielétrico (Beer-Lambert) e o **início do relatório LaTeX**.
