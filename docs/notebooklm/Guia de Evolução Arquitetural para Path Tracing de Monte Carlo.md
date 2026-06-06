**Mapa de Evolução Arquitetural: Path Tracing Estocástico de Monte Carlo**  
A fim de garantir rastreabilidade acadêmica completa, a implementação do traçador de caminhos deve fundir o paradigma estrutural do *Physically Based Rendering* (PBRT) com as aulas da disciplina INF2608 e a literatura primária do estado da arte 1, 2\. A seguir, detalha-se o roadmap consolidado com prompts prontos para injeção na IA, mapeando rigorosamente os capítulos do PBRT, os intervalos de páginas dos slides e as citações dos artigos originais de referência.

### 🛠️ Fase 0: Contexto Global e Preservação do Projeto 1

A transição para o Path Tracing exige o reaproveitamento das estruturas determinísticas consolidadas no traçado de raios 3\.

* **Referências PUC-Rio Herdadas:**  
* 4.tracado\_de\_raios.pdf: Preservam-se as interseções geométricas, o tratamento de *front/back faces*, e o modelo canônico de câmera *pinhole* 4, 5\.  
* 5.tracado\_de\_raios2.pdf (pp. 26-35): Base óptica para Leis de Snell e a refletância de Fresnel-Schlick 6\.  
* 6.estrutura\_aceleracao.pdf (pp. 22-36): Estruturas AABB e hierarquia de volumes limitantes (BVH) com heurística SAH, fundamentais para a performance da integração estocástica 7-9.

**Prompt de Setup do Sistema:**  
"Atue como um Engenheiro Especialista em Renderização Baseada em Física (PBR). O nosso projeto em Python (src/path\_tracing) já possui uma base sólida de ray tracing com BVH (6.estrutura\_aceleracao.pdf), câmera pinhole (4.tracado\_de\_raios.pdf) e materiais refratários baseados nas Leis de Snell e Beer-Lambert (5.tracado\_de\_raios2.pdf). Agora, implementaremos um Path Tracer de Monte Carlo para resolver a Equação de Renderização original formulada por Kajiya (1986). A arquitetura deve seguir estritamente o livro *Physically Based Rendering (PBRT 4e)*, especificamente o 'Light Transport I: Surface Reflection'. Use tipagem estática e vetores glm, e garanta que o código gerado contenha comentários explícitos referenciando as equações matemáticas das fontes."

### 📍 Fase 1: O Integrador Iterativo (Equação de Transporte de Luz)

A recursão clássica do modelo local de Phong, que gera um custo exponencial $O(N^d)$, deve ser substituída por uma avaliação linear unidimensional 10\.

* **Referências PUC-Rio:** 8.tracado\_de\_caminhos.pdf (pp. 20-21) ilustra o pseudo-código iterativo acumulando radiância em L e atenuação em beta 11\. 9.tracado\_de\_caminhos2.pdf (pp. 7-8) expande a contribuição do caminho ponderada pela PDF 12, 13\.  
* **Referências PBRT:** *A Simple Path Tracer* 14\.  
* **Artigos Auxiliares:** Kajiya, J. T. (1986). *The Rendering Equation* 15\.

**Prompt para a IA (Contexto: scene.py):**  
"Refatore o método principal de avaliação de raios implementando o algoritmo TracePath iterativo de Monte Carlo (Kajiya, 1986).Siga o pseudocódigo do slide 8.tracado\_de\_caminhos.pdf (pág 21\) e o Cap. 13 do PBRT 4e ('A Simple Path Tracer'):

1. Receba um raio primário e itere em um loop até max\_depth.  
2. Inicialize o acumulador de radiância L \= glm.vec3(0.0) e o throughput de atenuação beta \= glm.vec3(1.0).  
3. Na interseção, se atingir um emissor, acumule L \+= beta \* L\_e (apenas se for o primeiro salto) e encerre.  
4. Para superfícies opacas, chame material.sample(wo, normal) para obter a nova direção wi, a BRDF e a PDF.  
5. Atualize o throughput estritamente pela Equação de Transporte: beta \*= BRDF \* max(0.0, glm.dot(normal, wi)) / PDF. Adicione o comentário \# \[Celes 2026, 8.tracado\_de\_caminhos, p. 21\] e \[PBRT 4e\] Atualização do throughput LTE na linha do código correspondente."

### 📍 Fase 2: Amostragem e Material Difuso Ideal (Lambert)

A integração de Monte Carlo para materiais difusos requer a amostragem em um hemisfério para avaliar os raios secundários com estabilidade estatística 16, 17\.

* **Referências PUC-Rio:** 7.montecarlo.pdf (pp. 43-46) detalha a Amostragem do Hemisfério Ponderada pelo Cosseno via Método de Malley 17\. A BRDF de materiais difusos (albedo / $\\pi$) é consolidada em 8.tracado\_de\_caminhos.pdf (pág. 20\) 11\.  
* **Referências PBRT:** *Sampling Using the Inversion Method* 18\.

**Prompt para a IA (Contexto: material.py / sampling.py):**  
"Crie a classe DiffuseMaterial e seu método sample(wo, normal).

1. A constante da BRDF Lambertiana será o albedo / math.pi (ref: 8.tracado\_de\_caminhos.pdf, pág. 20).  
2. Sorteie a direção wi utilizando a Amostragem do Hemisfério Ponderada pelo Cosseno (Método de Malley, 7.montecarlo.pdf pág. 43-46 e PBRT Cap 2). Sorteie dois números, mapeie para o disco unitário e projete no hemisfério local.  
3. A PDF teórica deve ser obrigatoriamente max(0, glm.dot(normal, wi)) / math.pi.  
4. Retorne a tupla: (wi, brdf\_value, pdf, is\_specular=False). Comente a fórmula do Método de Malley no código."

### 📍 Fase 3: Múltipla Amostragem por Importância (MIS)

O estimador da luz direta atinge altíssima variância se não combinar a probabilidade da área da fonte de luz com o hemisfério da BRDF 19, 20\.

* **Referências PUC-Rio:** 9.tracado\_de\_caminhos2.pdf (pp. 16-22) aborda a heurística balanceada e a heurística da potência 21-23.  
* **Artigos Auxiliares:** Veach, E., & Guibas, L. J. (1995). *Optimally Combining Sampling Techniques for Monte Carlo Rendering* 24\.

**Prompt para a IA (Contexto: scene.py):**  
"Aprimore a estimativa de iluminação direta no TracePath através da Múltipla Amostragem por Importância (MIS) usando a Heurística da Potência de Veach (1995) com exponente beta=2, conforme 9.tracado\_de\_caminhos2.pdf (pág. 21).

1. Se is\_specular \== False, ative o *Next Event Estimation* (NEE): sorteie um ponto explícito na AreaLight, lance o raio de sombra de verificação de visibilidade, e obtenha L\_d e PDF\_light em ângulo sólido.  
2. Analise a probabilidade da BRDF apontar para a mesma direção da fonte (PDF\_brdf).  
3. Compute o peso MIS: weight\_light \= (PDF\_light\*\*2) / (PDF\_light\*\*2 \+ PDF\_brdf\*\*2). Acumule L \+= beta \* weight\_light \* BRDF \* L\_d \* cos(theta) / PDF\_light.  
4. Continue o Path Tracing com a direção wi da BRDF. Caso este próximo salto atinja emissão na iteração subsequente, calcule o weight\_brdf inverso e aplique a ele. Adicione o comentário \# \[Veach 1995\] e \[Celes 2026, 9.tracado\_de\_caminhos2, p. 21\] Heurística da Potência no cálculo do peso."

### 📍 Fase 4: Terminação Estocástica de Caminhos \- Roleta Russa

O rastreamento de saltos infinitos incorre em viés caso truncado em profundidade fixa. A técnica da Roleta Russa preserva o valor esperado do estimador de Monte Carlo enquanto minimiza os custos computacionais 25\.

* **Referências PUC-Rio:** 9.tracado\_de\_caminhos2.pdf (pp. 12-14) fundamenta a probabilidade de terminação escalada em função de um estado sobrevivente 26, 27\.  
* **Artigos Auxiliares:** Misso et al. (2022). *Unbiased and consistent rendering using biased estimators* para fundamentação de viés analítico 28, creditado historicamente a Arvo & Kirk (1990) no PBRT.

**Prompt para a IA (Contexto: scene.py):**  
"Integre a técnica de Roleta Russa ao laço iterativo TracePath para encerrar o transporte da luz de forma sem viés (unbiased), referenciado em 9.tracado\_de\_caminhos2.pdf (pág. 13-14).

1. Só ative a avaliação se depth \>= 3 (garantindo os 4 vértices mínimos do seu enunciado).  
2. A probabilidade de sobrevivência q deverá espelhar a refletância limite do beta (throughput): q \= max(0.05, min(1.0, max(beta.x, beta.y, beta.z))).  
3. Sorteie xi. Se xi \> q, efetue break. Se sobreviver, divida o throughput mantendo a consistência do estimador: beta /= q. Comente o código com \# Roleta Russa \[Celes 2026, 9.tracado\_de\_caminhos2, p. 13\]."

### 📍 Fase 5: BRDF de Microfacetas (Cook-Torrance)

Para substituir os especulares empíricos, os materiais do motor de física devem operar sobre as estatísticas microgeométricas 29\.

* **Referências PUC-Rio:** 11.microfaceta.pdf (pp. 9-18). Derivações de reflectância de Fresnel por Schlick (p. 13), distribuição Normal GGX (p. 15), e o mascaramento geométrico Variante Smith-Schlick (p. 17\) 29-32.  
* **Referências PBRT:** *Roughness Using Microfacet Theory* 33\.  
* **Artigos Auxiliares:** Cook & Torrance (1982) *A Reflectance Model for Computer Graphics* 34\. Walter et al. (2007) *Microfacet Models for Refraction through Rough Surfaces* 35\.

**Prompt para a IA (Contexto: material.py):**  
"Construa a classe MicrofacetMaterial que calcule a BRDF exata de Cook-Torrance (1982), fundamentada em 11.microfaceta.pdf (pág. 8-18) e PBRT Cap 9\.

1. A função de Distribuição Normal (NDF) D(h) será **GGX** (Walter et al., 2007, pág. 15), convertendo a rugosidade via alpha \= roughness\*\*2.  
2. O fator Geométrico G\_Smith(l, v) utilizará a aproximação de Schlick com k \= alpha / 2 (pág. 17).  
3. O termo de refletância F(v,h) será avaliado por Schlick com controle paramétrico por albedo (metálicos) e F0 base de dielétricos (pág. 13).  
4. O denominador do estimador é estritamente 4 \* abs(dot(n, wi)) \* abs(dot(n, wo)).  
5. A amostragem deve sortear sobre a NDF para recuperar o half-vector (h). Documente cada equação citando a pág do slide correspondente."

### 🌟 Opcional Avançado: Traçado Bidirecional ou Metropolis Light Transport (MLT)

Caso o projeto demande integração de iluminação global severamente ocluída ou focada em cáusticos.

* **BDPT:** Referência direta a 10.metodos\_bidirecionais.pdf (pp. 4-11). Traça-se sub-caminhos independentes partindo da lente da câmera e da fonte emissora simultaneamente, unindo-se por regras rígidas de visibilidade e expandindo consideravelmente a formulação da heurística balanceada MIS de Veach para $(k+2)$ combinações 36-39.  
* **MLT:** Referência direta a 11.metropolis.pdf (pp. 20-29). Rejeita o preceito fundamental de amostragem estocástica independente. Operando via cadeia de Markov no Espaço de Amostragem Primário (conforme Kelemen et al., 2002), perturba sistematicamente os vetores $u$ preexistentes para concentrar-se nas densidades radiantes altas do *film* através de um índice de aceitação Metropolis-Hastings e mutações combinadas pequenas/grandes 40-42.

Ao compor seu documento em LaTeX para a universidade, cite textualmente o modelo matemático exato exigido por cada fase para alinhar sua engenharia de software com as equações íntegras do framework PBRT.  
