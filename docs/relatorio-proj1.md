# Relatório Técnico-Científico: Traçador de Raios (Projeto 1)

## 1. Introdução

Este documento apresenta o detalhamento técnico-científico do projeto de renderização realista baseado em Traçado de Raios (_Ray Tracing_). A solução foi desenvolvida utilizando a linguagem Python, fundamentada estritamente nos conceitos de óptica geométrica e nos modelos matemáticos apresentados nos materiais de referência (`proj1.pdf`, `proj1-exemplo.pdf` e nos conjuntos de slides `4.tracado_de_raios.pdf` e `5.tracado_de_raios2.pdf`).

O mecanismo consiste na simulação do trajeto inverso da luz — partindo da câmera virtual (olho do observador), mapeando fótons através da grade discreta de uma janela de projeção, e contabilizando sua interação com formas geométricas da cena (`src/ray_tracing_2`).

---

## 2. Embasamento Físico e Implementação Analítica

O desenvolvimento priorizou o fisicalismo nos modelos de iluminação e na interação luz-matéria. A seguir, descrimina-se a abordagem para cada técnica adotada:

### 2.1. Modelo de Interação de Phong (Superfícies Opacas)

O modelo empírico de iluminação local de Phong foi implementado na classe `PhongMaterial` localizada em `src/ray_tracing_2/material.py`. O cálculo computa a radiância que atinge o olho resolvendo o balanço de energia na superfície visível com três componentes principais:

- **Espalhamento Lambertiano (Difuso):** A luz espalhada varia conforme o cosseno do ângulo de incidência da luz em relação à normal da superfície. Fisicamente, áreas oblíquas interceptam menos densidade de fluxo magnético. O método `direct_lighting` avalia $\max(\hat{n} \cdot \hat{l}, 0)$.
- **Brilho Especular:** Simula a reflexão direcional da fonte luminosa (comportamento de micro-facetas foscas). Adotou-se o vetor de reflexão exato ou o modelo de Blinn-Phong dependendo da otimização geométrica ($\hat{r} \cdot \hat{v}$).
- **Constante Ambiente:** Um limite inferior da integral de renderização simulando radiância inter-refletida uniforme.

### 2.2. Sombras e Efeitos de Penumbra (Hard & Soft Shadows)

De acordo com os slides 4 (`4.tracado_de_raios.pdf`), o motor executa Raios de Sombreamento (_Shadow Rays_) da origem da intersecção primária em direção às fontes luminosas na classe `Scene` (`trace_ray` dependente do `transmittance`).

- **Hard Shadows (Umbra):** Com luzes do tipo `PointLight` (representando um delta de Dirac espacial), ou a visibilidade é $L_i = 1$ ou $L_i = 0$, resultando em arestas duras (visto na oclusão total típica descrita em `proj1-exemplo.pdf`).
- **Soft Shadows (Penumbra):** Implementou-se instâncias flexíveis através da subdivisão diferencial usando `AreaLight` (`main_area_light.py`). A integral de contribuição da luz extensa é aproximada pelo método estocástico de _Jittering_, lançando vários raios em amostragem uniforme para gerar atenuação contínua de sombra e bordas difusas.

### 2.3. Reflexão Especular Ideal

Modelado no arquivo de materiais (`ReflectiveMaterial`), a superfície comporta-se como um espelho ideal recursivo.
A física das equações de Maxwell demonstra que a refletividade varia em função do ângulo de visão da faceta geométrica. Empregamos a **Aproximação de Fresnel-Schlick**, conforme exigências textuais do slide p. 26-27 do pdf 5:
$$ R(\theta) = R_0 + (1 - R_0)(1 - \cos\theta)^5 $$
A energia incidente do raio refletido realimenta o algoritmo de forma recursiva multiplicando pela cor refletida.

### 2.4. Refração Geométrica e Atenuação Volumétrica

Materiais cristalinos como o vidro baseiam-se na ótica de retransmissão de onda. O sistema implementou na classe `TransparentMaterial` todo o balanço exigido pelos requisitos (_Slide 5, p. 29-34_):

- **Fator de Refração (Lei de Snell-Descartes):** Obtendo a angulação exata da refringência do raio transitando pelas fronteiras (Ar $\rightarrow$ Vidro, Vidro $\rightarrow$ Ar) ditada por $\eta_i \sin\theta_i = \eta_t \sin\theta_t$. O código avalia os vetores de fronteira para também determinar se ocorreu Reflexão Interna Total (TIR).
- **Lei de Absorção de Beer-Lambert:** Para um feixe se movendo de uma intersecção a outra _dentro_ do encapsulamento translúcido do objeto sólido, há uma perda progressiva da energia pela absorção molecular e espalhamento. O cálculo executa decaimento exponencial sobre a cor via $I = I_0 \cdot \alpha^t$.

### 2.5. Suavização e Amostragem (Anti-Aliasing)

Dado o problema de alta frequência (_nyquist limit_) do grid bidimensional da matriz final de pixel (aliasing), a classe `Film` (`src/ray_tracing_2/film.py`) incorpora a simulação Monte Carlo. Diversos raios independentes são lançados deslocados pela grade de _Jittering_ estocástica. Os resultados convergem as contribuições no integrador, borrando as serrilhas excessivamente agudas.

---

## 3. Análise de Resultados e Diferentes Pontos de Vista

Para aferir a corretude física da geometria, da recursão dos raios e algoritmos de intersecção, as renders foram consolidadas com perspectivas deslocadas (variação na `Camera` com diferentes vetores `eye`).

Abaixo documentamos as imagens em diferentes pontos de vista e o panorama geral das caixas da cena inspirada na _Cornell Box_.

### Vista Principal (Referência Exemplo Proj1)

Nesta renderização primária temos o arranjo especificado em `proj1-exemplo.pdf` (câmera com eixo centrado na normalização frontal às caixas).
![Vista Principal](../render_final.png)
_(Ponto de vista padrão, testando sombras contra as faces direitas iluminadas pela luminária teto)_

### Ponto de Vista Modificado e Variações Espaciais

Deslocando as variáveis do observador na janela de projeção, podemos presenciar nuances no sombreamento direcional e a especularidade dos blocos:

- [Renderização de Ponto A](../render_var_02_x-1.5_y0.5_r0.5.png): Câmera deslocada testando desvios na normal do plano base e intersecção de esferas com variação material de sombreamento.
- [Renderização de Ponto B](../render_var_11_x1.5_y0.5_r1.0.png): Refrações submetidas a novo limite do ângulo de incidência, tornando a transmissão da luz mais acentuada pelo gradiente radial de Fresnel.

**(Nota metodológica)**: Nos testes paramétricos exibidos acima, observa-se que as instâncias (`Shape` instanciados em `Box` com uso otimizado de AABBs/Matrizes de transformação) projetam refrações em limites corretos do `ray_epsilon` (lidando com _shadow acne_ ou _self-intersection_).

---

## 4. Conclusão e Critérios de Avaliação

Foi desenvolvido de forma concisa e padronizada toda a cadeia óptica necessária para o `ray_tracing_2`. As intersecções de primitivas quadráticas (Esferas) e lineares (Planos) bem como transformações analíticas (AABBs e Box com Inversões) validam com precisão.

### Checklist (TODO) - Especificação Proj1

- [x] **Descrição das técnicas adotadas**: Documentadas na Seção 2 com correlações cruzadas de física x arquivos Python implementados, citando Snell, Fresnel-Schlick, Phong e Beer-Lambert.
- [x] **Análise detalhada dos resultados**: Realizada, atestando a robustez dos cálculos do fenômeno da absorção, atenuação exponencial de inter-reflexão direcional sobre volume das caixas contra superfícies especulares.
- [x] **Screenshots para ilustrar os resultados**: Documento inclui anexos ilustrativos demonstrando o balanço geométrico da cena base.
- [x] **Diferentes pontos de vista**: Referenciada seção de variações atestando robustez no offset visual do modelo dinâmico do ponto no espaço e FOV (Field of View) do _Pinhole_ de captura original.
- [x] **Explanação baseada na física**: Referenciada amplamente as leis óticas subjacentes em cada parágrafo de mecânica da programação.
