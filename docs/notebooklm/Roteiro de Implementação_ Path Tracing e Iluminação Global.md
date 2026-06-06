A análise do enunciado do **Projeto 2** (proj2.pdf) em comparação à sua implementação madura do Projeto 1 (src/ray\_tracing\_2) revela que você já possui uma excelente fundação estrutural. Sua base geométrica (instanciação de formas, malhas triangulares e aceleração BVH local) 1-3, sua câmera e sua estrutura de amostragem por pixel (filme com antialiasing) 4, 5 já atendem a muitos dos pré-requisitos físicos e operacionais exigidos.  
No entanto, o Projeto 2 exige uma transição de paradigma fotométrico: a passagem de um **modelo local e determinístico (Phong \+ recursão)** para um **modelo de Iluminação Global baseado em integração estocástica (Light Transport Equation \- LTE)** 6, 7\. Para a entrega em 30 de junho 8, você precisará substituir o acúmulo recursivo de cores pela avaliação de caminhos (paths) amostrados via Monte Carlo.  
Com base na teoria da disciplina (Aulas 7 a 11\) e nos requisitos de proj2.pdf, apresento abaixo o plano de implementação detalhado em passos sucessivos para o novo módulo src/path\_tracing. Este roteiro é estruturado para facilitar a geração de prompts e o uso de assistentes de IA (Copilot/Gemini).

### Análise de Requisitos (proj2.pdf) vs. Implementação Atual

* **Requisitos Básicos Cumpribles de Imediato:** Instanciação de caixas/esferas/planos 9, fontes de luz retangulares (você já tem AreaLight) 9, 10 e múltiplos caminhos por pixel (você já suporta múltiplos spp no Film) 5, 11\.  
* **Novos Requisitos Básicos:** Implementação de materiais puramente difusos usando integração estocástica (BRDF constante) e garantia de profundidade mínima de 4 vértices 9, 11\.  
* **Extensões Selecionadas para o Plano (3.0+ pontos):** Múltipla Amostragem por Importância (MIS) no último trecho (1.0 pt) 11, Roleta Russa (2.0 pts) 11, Microfacetas (1.0 pt) 12 e adequação de objetos refratários já existentes ao Path Tracing (2.0 pts) 12\.

### Plano Detalhado de Implementação para src/path\_tracing

#### Passo 1: Refatoração do Loop de Integração (O Integrador de Caminhos)

A diferença arquitetural primária é que o Path Tracing **não deve ser recursivo**, mas sim um loop iterativo que constrói o caminho construindo o "throughput" (atenuação) $\\beta$ 13\.

1. **Ação:** Duplique os módulos de src/ray\_tracing\_2. Em scene.py (ou crie um novo path\_integrator.py), substitua o método de iluminação direta pelo algoritmo iterativo TracePath.  
2. **Teoria:** Inicialize a radiância $L \= (0,0,0)$ e o throughput $\\beta \= (1,1,1)$ 13, 14\. Em um loop até max\_depth (mínimo de 4, conforme 11), em cada interseção:  
3. Verifique se o raio atingiu uma luz. Se sim, adicione ao $L$ a radiância emitida multiplicada pelo $\\beta$ atual (e encerre ou aplique MIS, se não for o primeiro raio) 14, 15\.  
4. Amostre a BRDF do material para obter a nova direção $\\omega\_i$ e seu PDF 16\.  
5. Atualize o throughput: $\\beta \= \\beta \* \\text{BRDF} \* \\cos(\\theta) / \\text{PDF}$ 15, 16\.  
6. Crie um novo raio partindo do ponto de interseção e repita 16\.

#### Passo 2: Implementação de Materiais Difusos (Monte Carlo)

No traçado de raios clássico, a cor difusa usa a posição exata da luz 17\. No traçado de caminhos, ela coleta luz do hemisfério.

* **Ação:** Refatorar a classe base de Material para incluir um método sample(normal, view\_dir) que retorne uma direção de espalhamento e o seu PDF.  
* **Teoria:** Para um material difuso ideal (Lambertiano), a BRDF é $f\_r \= \\rho / \\pi$, onde $\\rho$ é o albedo (cor) 13, 18\.  
* **Geração:** Peça ao Copilot para gerar uma **amostragem do hemisfério ponderada pelo cosseno** 19, 20\. O PDF para esta amostragem é $p(\\omega) \= \\cos(\\theta) / \\pi$ 20\.

#### Passo 3: Extensão \- Roleta Russa (Russian Roulette) Valor: 2.0 pontos

Para evitar que o programa avalie infinitos rebatimentos inviáveis de forma truncada e viesada, adota-se a Roleta Russa para caminhos profundos 11, 21\.

* **Ação:** Inserir a lógica de encerramento estocástico no final do loop iterativo TracePath, ativado apenas após uma profundidade mínima (por exemplo, depth \> 3\) 22, 23\.  
* **Teoria:** Calcule uma probabilidade de continuação $q$, geralmente baseada na refletância máxima do throughput $\\beta$ 23, 24\.  
* **Implementação:** Gere um número aleatório $\\xi$. Se $\\xi \> q$, quebre o loop. Se continuar, compense a perda dividindo o throughput pela probabilidade de sobrevivência: $\\beta \= \\beta / q$ 21, 25\.

#### Passo 4: Extensão \- Multiple Importance Sampling (MIS) Valor: 1.0 ponto

A amostragem puramente do hemisfério é péssima para luzes pequenas; a amostragem da luz falha em materiais muito especulares. O MIS combina as duas estratégias (Direct Light Sampling e BRDF Sampling) de forma robusta 11, 26, 27\.

1. **Ação:** Modificar o cálculo de iluminação de cada vértice para utilizar a heurística de balanço ou de potência de Veach 28, 29\.  
2. **Teoria/Passos:**  
3. Estime a luz direta amostrando a fonte de área ($L\_{d}$) e compute a probabilidade desta amostragem $p\_{light}$ e a probabilidade de amostrar a mesma direção pela BRDF $p\_{brdf}$ 15, 30\.  
4. Use o peso $w\_{light} \= \\frac{p\_{light}^2}{p\_{light}^2 \+ p\_{brdf}^2}$ (heurística da potência) para ponderar $L\_d$ 29\.  
5. Para o rebatimento contínuo do caminho (amostrando a BRDF), armazene os PDFs unidirecionais. Caso este raio colida com uma luz, aplique o inverso do peso MIS usando as probabilidades computadas retroativamente 22, 25\.

#### Passo 5: Extensão \- Material de Microfacetas (Cook-Torrance) Valor: 1.0 ponto

Substitua o modelo especular plástico e empírico de Phong pela simulação baseada em física (PBR) 12, 31\.

1. **Ação:** Criar a classe MicrofacetMaterial.  
2. **Teoria:** A BRDF é dada por $f\_r \= \\frac{D(h) F(v,h) G(l,v)}{4 (n \\cdot l)(n \\cdot v)}$ 32, 33\.  
3. **Componentes a implementar/gerar com IA:**  
4. **Fresnel $F$:** Você já tem a aproximação de Schlick em proj1\_rext\_reflective.py, pode reutilizar 32, 34, 35\.  
5. **Distribuição Normal (NDF) $D(h)$:** Implementar a distribuição **GGX** (Walter et al.): $D\_{GGX}(h) \= \\frac{\\alpha^2}{\\pi ((n \\cdot h)^2 (\\alpha^2 \- 1\) \+ 1)^2}$ 36, 37\. O parâmetro $\\alpha$ mapeia a rugosidade (roughness).  
6. **Mascaramento/Sombreamento $G(l,v)$:** Implementar o termo de geometria de Smith/Schlick: $G\_{Smith} \= G\_1(l) G\_1(v)$ 32, 38\.

#### Passo 6: Readequação dos Refratários e Reflexivos Valor: 2.0 pontos

Materiais como vidro (que você implementou perfeitamente via Snell e Beer-Lambert 39\) causam problemas no Path Tracing porque suas funções PDF são impulsos infinitos (Deltas de Dirac) 40\.

* **Ação:** Adaptar a classe transparente para a interface probabilística.  
* **Teoria e Código:** A probabilidade teórica de amostrar o raio refratado de um espelho ideal é 1\. No seu TracePath, ao avaliar um material reflexivo ou dielétrico, sinalize o integrador (is\_specular \= True) para que ele **ignore o cálculo de PDF do MIS (coloque $p\_{brdf} \= 0$)** para esse vértice específico 15, 41\. A cor pura refletida e atenuada será agregada no passo recursivo com probabilidade de $\\beta$ integral.

#### Estratégia Recomendada para o Fluxo com IA

1. Comece solicitando ao Github Copilot/Gemini: *"Escreva o esqueleto de um TracePath iterativo em Python para um Path Tracer simples, que substitua o clássico ray tracing recursivo, armazenando um acumulador de Radiância L e um vetor de throughput beta"*.  
2. Depois, insira a classe base dos materiais: *"No contexto deste Path Tracer, gere um Material Difuso Lambertiano com o método sample(normal, view\_dir) que retorne o raio rebatido (Cosine-Weighted Hemisphere Sampling) e o PDF"*.  
3. Quando tiver os diffuse nodes integrados com a sua AreaLight já existente, implemente MIS como uma evolução matemática local. Use a sintaxe limpa do seu framework experimental (cli.py e snapshots) 42 para rodar cenas-teste e observar a redução imediata da variância.

