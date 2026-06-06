# Guia Prático de Citações em BibLaTeX para o Relatório INF2608 Projeto 2

> Este documento explica como usar as referências do arquivo `refs.bib` no relatório LaTeX final (`proj2.tex`).

---

## 1. Configuração do LaTeX (preâmbulo)

Para usar BibLaTeX com o arquivo `refs.bib`, adicione no preâmbulo do seu documento LaTeX:

```latex
\usepackage[backend=biber,style=alphabetic,maxcitenames=999,abbreviate=false]{biblatex}
\addbibresource{refs.bib}
```

**Nota sobre o backend:** O backend `biber` é moderno e recomendado. Alternativamente, use `backend=bibtex8` ou `backend=bibtex`, mas `biber` oferece melhor suporte a Unicode e características avançadas de BibLaTeX.

**Estilos alternativos:** 
- `alphabetic` — citações por [ABC99], referências alfabetizadas
- `numeric` — citações por [1], referências por ordem de aparição
- `authoryear` — citações por (Autor, Ano)
- `authoryear-comp` — idem, mas comprime múltiplas citações

Para este projeto, recomendamos **`alphabetic`** (semelhante ao Projeto 1).

---

## 2. Tipos de Comando de Citação

### 2.1 `\cite{key}` — Citação entre parênteses

**Uso:** Citação em linha, inserida entre parênteses ou como nota de rodapé conforme o estilo.

**Exemplos:**

```latex
% Citação simples
A Equação de Renderização foi definida por \cite{kajiya1986rendering}.

% Múltiplas citações
Path tracing é baseado em Monte Carlo \cite{pharr2023pbrt} e amostragem de importância
\cite{inf2608slides07}.

% Shorthand: cite curto
O artigo seminal \cite{veach1995optimallycombin} introduz MIS.
```

### 2.2 `\textcite{key}` — Citação textual

**Uso:** O nome do autor(a) aparece no texto; a referência fica ao lado ou em nota.

**Exemplos:**

```latex
% Nome + ano/ref no texto
\textcite{kajiya1986rendering} definiu a Equação de Renderização.

% Múltiplos autores
\textcite{pharr2023pbrt} (Pharr, Jakob, Humphreys) detalham a implementação de um path tracer.
```

### 2.3 `\parencite{key}` — Citação entre parênteses (explícita)

**Uso:** Força a citação entre parênteses, mesmo que o estilo padrão seja diferente.

**Exemplos:**

```latex
% Para clareza quando há ambiguidade
A amostragem cosseno-ponderada \parencite{inf2608slides07} é eficiente.
```

### 2.4 `\cite[pp. 123]{key}` — Citação com página específica

**Uso:** Indica a página ou seção exata da referência.

**Exemplos:**

```latex
% Citação com página
Sobre MIS, veja \cite[pp. 419--428]{veach1995optimallycombin}.

% Para capítulo/seção de livro
PBRT detalha o path tracer em \cite[§13.3]{pharr2023pbrt}.
```

---

## 3. Padrão de Citação Recomendado para cada Tipo de Referência

### 3.1 Slides da Disciplina

**Entrada BibTeX:**
```bibtex
@misc{inf2608slides08,
  author={Celes, Waldemar},
  title={Traçado de Caminhos},
  year={2026},
  ...
}
```

**No texto LaTeX:**

```latex
% Referência básica
Como explicado no \cite{inf2608slides08}, o path tracing...

% Com nome do autor
\textcite{inf2608slides08} descreve a formulação de integral de caminhos.

% Se for citar uma seção específica do slide
O método de Malley está explicado em \cite{inf2608slides07} (Integração de Monte Carlo).
```

### 3.2 Livros (PBRT 4e e 3e)

**Entrada BibTeX:**
```bibtex
@book{pharr2023pbrt,
  title={Physically Based Rendering: From Theory to Implementation},
  author={Pharr, Matt and Jakob, Wenzel and Humphreys, Greg},
  edition={4},
  year={2023},
  ...
}
```

**No texto LaTeX:**

```latex
% Referência ao livro em geral
PBRT \cite{pharr2023pbrt} é a referência padrão da indústria.

% Referência específica a um capítulo/seção
A integração Monte Carlo é discutida em \cite[§2]{pharr2023pbrt}.

% Referência a um capítulo nomeado
Para Monte Carlo, consulte \cite[Cap. 2, ``Monte Carlo Integration'']{pharr2023pbrt}.

% PBRT 3ª edição (especificar porque há removals)
BDPT está em \cite{pharr2018pbrt3e}, capítulo que foi removido da 4ª edição.
```

### 3.3 Artigos de Conferência (SIGGRAPH, Eurographics, etc.)

**Entrada BibTeX:**
```bibtex
@inproceedings{veach1995optimallycombin,
  author={Veach, Eric and Guibas, Leonidas J.},
  title={Optimally Combining Sampling Techniques for Monte Carlo Rendering},
  booktitle={Proceedings of the 22nd Annual Conference on Computer Graphics 
            and Interactive Techniques (SIGGRAPH)},
  year={1995},
  pages={419--428},
  doi={10.1145/218380.218498},
  ...
}
```

**No texto LaTeX:**

```latex
% Referência básica
MIS foi introduzido por \cite{veach1995optimallycombin}.

% Nome + ano
\textcite{veach1995optimallycombin} propõem as heurísticas balance e power.

% Com página específica
A heurística da potência (β=2) está em \cite[pp. 425]{veach1995optimallycombin}.

% Com DOI (se quiser mencionar)
Veja \cite{veach1995optimallycombin} (DOI: 10.1145/218380.218498) para detalhes.
```

### 3.4 Artigos de Periódico (ACM TOG, CGF, JGT, etc.)

**Entrada BibTeX:**
```bibtex
@article{misso2022unbiased,
  author={Misso, Zackary and Bitterli, Benedikt and Georgiev, Iliyan and Jarosz, Wojciech},
  title={Unbiased and Consistent Rendering Using Biased Estimators},
  journal={ACM Transactions on Graphics},
  volume={41},
  number={4},
  article={48},
  year={2022},
  doi={10.1145/3528223.3530160},
  ...
}
```

**No texto LaTeX:**

```latex
% Referência básica
Path tracing pode ser visto como série telescópica \cite{misso2022unbiased}.

% Nome + journal
\textcite{misso2022unbiased} mostram que Russian Roulette é uma instância de debiasing.

% Com volume/número (se relevante)
Publicado em ACM TOG 41(4), artigo 48 \cite{misso2022unbiased}.
```

### 3.5 Teses (PhD Thesis)

**Entrada BibTeX:**
```bibtex
@phdthesis{veach1997thesis,
  author={Veach, Eric},
  title={Robust Monte Carlo Methods for Light Transport Simulation},
  school={Stanford University},
  year={1997},
  ...
}
```

**No texto LaTeX:**

```latex
% Referência básica
Os detalhes completos estão na tese de \cite{veach1997thesis}.

% Com nome
\textcite{veach1997thesis} oferece a fundamentação matemática rigorosa para BDPT e MLT.
```

---

## 4. Estrutura de Seções Recomendada no relatório LaTeX

Aqui está como estruturar as seções do relatório para ciências com uma boa prática de citações:

### 4.1 Seção de Introdução

```latex
\section{Introdução}

Este projeto implementa um renderizador baseado em \emph{path tracing}, 
uma técnica de renderização global que resolve a Equação de Renderização 
\cite{kajiya1986rendering} de forma estocástica usando integração de Monte Carlo.

O path tracing é a fundação de muitos renderizadores modernos 
\cite{pharr2023pbrt, inf2608slides08}. Para este projeto, estendemos 
um ray tracer educacional \cite{inf2608projectrepo} com as técnicas 
mais importantes de redução de variância em Monte Carlo, incluindo...
```

### 4.2 Seção de Método/Técnica

```latex
\subsection{Multiple Importance Sampling}

A Amostragem Múltipla de Importância (MIS) foi proposta por 
\cite{veach1995optimallycombin} como forma de combinar otimamente 
dois ou mais estimadores Monte Carlo. A ideia fundamental é que, 
para cada amostra, calculamos qual estimador teria sido melhor 
(em termos de pdf) e ponderamos a amostra de acordo.

\cite[p. 420]{veach1995optimallycombin} demonstram que a heurística 
da potência com expoente $\beta=2$ produz variância menor em muitos casos 
práticos em relação à heurística balance (isto é, $\beta=1$).

Para implementação, referimos a \cite{pharr2023pbrt} (§2.2.3) 
e aos slides da disciplina \cite{inf2608slides09}.
```

### 4.3 Seção de Resultados

```latex
\section{Evidência Visual}

A figura \ref{fig:cornell_spp} mostra a cena Cornell renderizada com 
diferentes números de amostras por pixel (SPP). Como esperado de um 
estimador Monte Carlo \cite{pharr2023pbrt}, a variância diminui 
aproximadamente como $1/\sqrt{\text{SPP}}$.

A renderização com MIS \cite{veach1995optimallycombin} (Figura \ref{fig:cornell_mis}) 
mostra convergência mais rápida em comparação com amostragem de BSDF puro 
(Figura \ref{fig:cornell_bsdf_only}).
```

### 4.4 Seção de Discussão/Conclusão

```latex
\section{Discussão}

A implementação de path tracing unidirecional com MIS demonstra a importância 
de técnicas de redução de variância em Monte Carlo \cite{pharr2023pbrt, inf2608slides07}. 
Para cenas com padrões de iluminação complexos (como cáusticas), técnicas 
bidirecionais \cite{pharr2018pbrt3e} ou Metropolis \cite{veach1997metropolis} 
são necessárias — deixamos isso como trabalho futuro.

Finalmente, observamos que a formulação telescópica do path tracing 
\cite{misso2022unbiased} oferece uma perspectiva teórica profunda que 
unifica várias técnicas aparentemente díspares.
```

---

## 5. Exemplo Completo: Trecho de Código LaTeX com Citações

```latex
\documentclass[12pt,a4paper]{article}

\usepackage[brazilian]{babel}
\usepackage[utf8]{inputenc}
\usepackage[backend=biber,style=alphabetic]{biblatex}
\addbibresource{refs.bib}

\usepackage{graphicx}
\usepackage{hyperref}

\title{Projeto 2: Path Tracer Educacional para INF2608}
\author{Yang Ricardo Barcellos Miranda}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Este relatório descreve a implementação de um renderizador por path tracing 
em Python, estendendo um ray tracer educacional \cite{inf2608projectrepo}. 
O path tracer resolve a Equação de Renderização \cite{kajiya1986rendering} 
usando Monte Carlo \cite{pharr2023pbrt} com técnicas de redução de variância 
incluindo Multiple Importance Sampling \cite{veach1995optimallycombin} e 
Russian Roulette \cite{misso2022unbiased}. Etapas avançadas incluem 
Bidirectional Path Tracing \cite{pharr2018pbrt3e} e Metropolis Light Transport 
\cite{veach1997metropolis}.
\end{abstract}

\section{Introdução}

O caminho da luz através de uma cena 3D é descrito matematicamente pela 
Equação de Renderização, proposta por \cite{kajiya1986rendering}. 
A resolução numérica dessa integral é o fundamento de todo rendering realista.

Este projeto implementa várias abordagens para estimar essa integral, 
começando com path tracing unidirecional \cite{inf2608slides08, pharr2023pbrt} 
e progredindo para técnicas mais sofisticadas como BDPT 
\cite{veach1995optimallycombin, pharr2018pbrt3e} e MLT 
\cite{veach1997metropolis, kelemen2002simple}.

\section{Monte Carlo e Path Tracing}

\cite{inf2608slides07} descreve os princípios fundamentais da integração 
Monte Carlo: variáveis aleatórias, funções de distribuição de probabilidade (PDF), 
e amostragem por inversão.

O método de Malley \cite{pharr2023pbrt} (§A.5) fornece uma forma elegante 
de amostrar uniformemente a esfera unitária usando um círculo: $\theta = \arcsin(\sqrt{u_1})$, 
$\phi = 2\pi u_2$.

\section{Resultados}

A Figura \ref{fig:cornell} mostra a cena Cornell renderizada com path tracing 
unidirecional e MIS \cite{veach1995optimallycombin}. A convergência é visível 
com aumento de SPP.

\begin{figure}
\centering
\includegraphics[width=0.8\textwidth]{figures/cornell_spp_comparison.png}
\caption{Cornell box: path tracing com SPP = \{4, 16, 64, 256\}. 
Convergência visível conforme esperado da teoria Monte Carlo \cite{pharr2023pbrt}.}
\label{fig:cornell}
\end{figure}

\section{Conclusão}

Este projeto demonstra a importância de técnicas de redução de variância 
em Monte Carlo \cite{pharr2023pbrt, inf2608slides07}. MIS 
\cite{veach1995optimallycombin} reduziu o MSE em até 4× em algumas cenas.

Para trabalhos futuros, a implementação de BDPT \cite{pharr2018pbrt3e} 
ofereceria ainda melhores resultados em cenas com cáusticas.

% ============================================================
% BIBLIOGRAFIA — Comando obrigatório no final do documento
% ============================================================

\printbibliography

\end{document}
```

**Para compilar:**

```bash
pdflatex proj2.tex
biber proj2
pdflatex proj2.tex
pdflatex proj2.tex
```

---

## 6. Checklist de Citações para o Relatório Final

Use este checklist para garantir que todas as referências esperadas estão citadas no relatório:

- [ ] **Slides INF2608:**
  - [ ] Slide 7 (Monte Carlo) — \cite{inf2608slides07}
  - [ ] Slide 8 (Path Tracing) — \cite{inf2608slides08}
  - [ ] Slide 9 (Path Tracing II) — \cite{inf2608slides09}
  - [ ] Slide 10 (Métodos Bidirecionais) — \cite{inf2608slides10}
  - [ ] Slide 11 (Metropolis) — \cite{inf2608slides11metropolis}
  - [ ] Slide 11 (Microfaceta) — \cite{inf2608slides11microfaceta}

- [ ] **PBRT:**
  - [ ] PBRT 4ª edição — \cite{pharr2023pbrt}
  - [ ] PBRT 3ª edição (BDPT/MLT) — \cite{pharr2018pbrt3e}

- [ ] **Papers Seminais:**
  - [ ] Kajiya 1986 (Rendering Equation) — \cite{kajiya1986rendering}
  - [ ] Veach & Guibas 1995 (MIS) — \cite{veach1995optimallycombin}
  - [ ] Veach & Guibas 1997 (MLT) — \cite{veach1997metropolis}
  - [ ] Veach Thesis 1997 — \cite{veach1997thesis}

- [ ] **Técnicas Específicas:**
  - [ ] Misso 2022 (Debiasing, RR) — \cite{misso2022unbiased}
  - [ ] Seyb 2024 (Microfacetas teoria) — \cite{seyb2024microfacets}
  - [ ] Walter 2007 (Microfacet GGX) — \cite{walter2007microfacet}
  - [ ] Kelemen 2002 (PSSMLT) — \cite{kelemen2002simple}
  - [ ] Hachisuka 2014 (Multiplexed MLT) — \cite{hachisuka2014multiplexed}
  - [ ] Frisvad 2012 (ONB) — \cite{frisvad2012orthonormal}

- [ ] **Repositório:**
  - [ ] GitHub INF2608 — \cite{inf2608projectrepo}

---

## 7. Notas Adicionais

### 7.1 DOIs e URLs

As entradas no `refs.bib` incluem DOIs e URLs completos. No arquivo LaTeX compilado, BibLaTeX renderizará automaticamente links clicáveis (com `\usepackage{hyperref}`).

### 7.2 Estilos de Citação Alternativos

Se preferir um estilo diferente, altere a opção `style=` no preâmbulo:

```latex
\usepackage[backend=biber,style=ieee]{biblatex}      % IEEE numeric
\usepackage[backend=biber,style=authoryear]{biblatex} % Chicago author-year
```

### 7.3 Abreviações de Periódicos

BibLaTeX pode abreviar nomes de periódicos automaticamente se você fornecer um arquivo de abreviações. Para este projeto, mantemos nomes completos para clareza (e.g., "ACM Transactions on Graphics" e não "ACM TOG").

---

*Fim do Guia de Citações em BibLaTeX*
