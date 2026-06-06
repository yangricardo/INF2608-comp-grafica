# Etapa 12 — Relatório LaTeX (início)

**Status:** 🟡 início criado (esqueleto compilável).

Foi criado [`latex/inf2608-proj2.tex`](../../latex/inf2608-proj2.tex), espelhando
[`latex/inf2608-proj1.v3.tex`](../../latex/inf2608-proj1.v3.tex): mesma classe
`sbcreviews-2025`, mesmo preâmbulo/infra (`apalike-sol.bst`, `aas_macros.sty`,
`sectsty.sty`) e a **mesma** base bibliográfica [`latex/refs.bib`](../../latex/refs.bib)
(que já contém todas as chaves do proj2).

**Cobertura (apenas etapas implementadas):** Introdução; Núcleo unidirecional + Lambertiana
(02); NEE (03); MIS (04); Roleta Russa (05); Luzes retangular e poliédrica (03+06); BSDF
dielétrica com Snell/Fresnel/TIR/Beer-Lambert (07); Evidências Visuais (figuras de
`out/proj2/req*` com o comando gerador); Decisões e Limites; Conclusão.

**O que falta o autor completar:** análise quantitativa (tabelas MSE×SPP, tempos), substituir
a figura de req7 por um render pós-correções (refração/IOR/Beer-Lambert), e — se desejar —
anexos de rastreabilidade (conceito → slide → PBRT § → arquivo) no molde do proj1.

**Compilar:**

```bash
cd latex && latexmk -pdf inf2608-proj2.tex
```
