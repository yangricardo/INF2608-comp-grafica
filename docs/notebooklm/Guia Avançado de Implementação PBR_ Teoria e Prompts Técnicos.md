Após uma reavaliação extensiva das 117 fontes do seu repositório, incluindo os slides da disciplina INF2608, os excertos do livro *Physically Based Rendering (PBRT 4e)* e as teses/artigos científicos avançados de renderização presentes no seu *Notebook*, reprojetei o plano de implementação e os *prompts*.  
A grande vantagem de incluir a literatura científica primária (como os *papers* originais de Veach, Kajiya e Cook-Torrance) e o livro PBRT nos *prompts* é que as IAs generativas (como Copilot e Gemini) foram exaustivamente treinadas nesses exatos textos. Ao citar os autores, equações específicas e capítulos exatos, você ancora a geração de código na notação matemática rigorosa, evitando que a IA alucine algoritmos genéricos ou subótimos.  
Abaixo apresento a evolução do seu guia de *prompts*, agora fundamentado com **cruzamento teórico de alto nível**:

### 🛠️ Prompt 0: Configuração do Perfil de Sistema (System Prompt)

**Cruzamento Teórico:** O problema raiz é a Equação de Renderização formulada por Kajiya (1986) 1\. O PBRT-v4 (Pharr, Jakob, e Humphreys) serve como arquitetura base para o integrador 2, 3\.**Como usar:** Forneça este prompt como instrução inicial para ajustar a "temperatura técnica" da IA.  
"Atue como um Engenheiro Especialista em Renderização Baseada em Física (PBR). O nosso projeto em Python (src/path\_tracing) está sendo atualizado para resolver a Equação de Renderização de Kajiya (1986). A arquitetura deve seguir os preceitos do livro *Physically Based Rendering: From Theory to Implementation (PBRT 4e)*, Capítulo 13 (Light Transport I). Implementaremos um Integrador Unidirecional de Caminhos (Path Tracer) baseado na integração estocástica de Monte Carlo. Use tipagem estática, vetores glm e garanta otimização algébrica, evitando ramificações profundas e divisões por zero nas PDFs."

### 📍 Fase 1: O Integrador Iterativo (Equação de Transporte de Luz)

**Cruzamento Teórico:**

* **PUC-Rio:** O pseudocódigo base está em 8.tracado\_de\_caminhos.pdf, pág. 21 4, e 9.tracado\_de\_caminhos2.pdf, pág. 7 5\.  
* **PBRT 4e:** Capítulo 13 (*Light Transport I*), seções 13.2 (Path Tracing) e 13.3 (A Simple Path Tracer) 3, 6\.  
* **Artigos:** A tese de Delio Vicini da EPFL define formalmente a construção do "Throughput" (Atenuação) $\\beta(\\bar{x})$ como o produtório dos termos de Geometria e BSDF 7\.

**Prompt para a IA (Contexto: scene.py):**  
"Implemente o método iterativo TracePath substituindo a recursão clássica por um laço (loop) baseado no Capítulo 13 do PBRT 4e e no pseudocódigo da Aula 8 do Prof. Waldemar Celes (PUC-Rio).

1. Inicialize a Radiância Acumulada $L \= \\text{vec3}(0.0)$ e o Throughput $\\beta \= \\text{vec3}(1.0)$.  
2. No loop (até max\_depth), encontre a interseção. Se não houver, retorne $L$. Se houver, obtenha a emissão $L\_e$. Se for a iteração depth \== 0, acumule $L \+= \\beta \* L\_e$.  
3. Chame a amostragem do material sample() para obter a nova direção $w\_i$, a $BRDF$ e a $PDF$.  
4. Atualize o throughput multiplicando $\\beta$ pelo termo da Equação de Transporte: $\\beta \*= BRDF \* \\max(0, \\text{dot}(n, w\_i)) / PDF$. Siga a notação rigorosa do estimador de Monte Carlo.  
5. Atualize a origem e a direção do raio para o próximo rebote."

### 📍 Fase 2: Materiais Difusos Ideais (Amostragem Ponderada pelo Cosseno)

**Cruzamento Teórico:**

* **PUC-Rio:** A amostragem baseada no Método de Malley é detalhada em 7.montecarlo.pdf, pág. 43-46 8, 9\. A BRDF de Lambert é definida como $\\rho / \\pi$ em 8.tracado\_de\_caminhos.pdf, pág. 20 10\.  
* **PBRT 4e:** "Sampling Using the Inversion Method" (Cap. 2\) 11, 12\.

**Prompt para a IA (Contexto: material.py):**  
"Implemente a amostragem de Monte Carlo para um Material Difuso (Lambertiano) utilizando a **Amostragem de Hemisfério Ponderada pelo Cosseno** (Cosine-Weighted Hemisphere Sampling), de acordo com o Método de Malley detalhado no PBRT.

1. O método sample(wo, normal) deve sortear dois números aleatórios $\\xi\_1, \\xi\_2$.  
2. Mapeie esses números para o disco unitário e projete-os na superfície do hemisfério para achar a direção $w\_i$.  
3. A $PDF$ teórica dessa amostragem é $p(w\_i) \= \\max(0, \\text{dot}(n, w\_i)) / \\pi$.  
4. A $BRDF$ constante é o Albedo dividido por $\\pi$.  
5. Retorne a tupla contendo: $(w\_i, BRDF, PDF, \\text{is\\\_specular}=\\text{False})$."

### 📍 Fase 3: Múltipla Amostragem por Importância (MIS) e Heurística da Potência

**Cruzamento Teórico:**

* **PUC-Rio:** A Aula 9 (9.tracado\_de\_caminhos2.pdf, pág. 16-22) discute explicitamente a heurística da potência de Veach 13, 14\.  
* **Artigos Científicos:** Eric Veach (1995 e 1997\) 15, 16 e teses contemporâneas sobre *Spatiotemporal Reservoir Resampling* (ReSTIR) referenciam amplamente o peso do MIS 17-19. O cálculo robusto é fundamental para a convergência 20\.

**Prompt para a IA (Contexto: scene.py):**  
"Aprimore o integrador TracePath com a **Múltipla Amostragem por Importância (MIS)** formulada por Eric Veach (1995), adotando estritamente a **Heurística da Potência** (Power Heuristic) com $\\beta=2$.

1. Para vértices opacos (is\_specular \== False), adicione a Estimativa de Próximo Evento (NEE): sorteie um ponto na AreaLight para calcular $L\_d$, avalie a visibilidade (shadow ray) e a $PDF\_{light}$ baseada em ângulo sólido.  
2. Obtenha a probabilidade da BRDF para essa mesma direção: $PDF\_{brdf}$.  
3. Aplique o peso MIS: $W\_{light} \= (PDF\_{light}^2) / (PDF\_{light}^2 \+ PDF\_{brdf}^2)$. Acumule: $L \+= \\beta \* W\_{light} \* BRDF \* L\_d \* \\cos(\\theta) / PDF\_{light}$.  
4. Prossiga com o sorteio estocástico da BRDF para o próximo salto do caminho. Se este salto atingir uma luz na iteração seguinte, calcule retroativamente $W\_{brdf} \= (PDF\_{brdf\\\_prev}^2) / (PDF\_{brdf\\\_prev}^2 \+ PDF\_{light\\\_prev}^2)$ e aplique à emissão capturada."

### 📍 Fase 4: Terminação de Caminhos \- Roleta Russa

**Cruzamento Teórico:**

* **PUC-Rio:** Abordada na Aula 9 (9.tracado\_de\_caminhos2.pdf, pág. 12-14) para preservação do estimador sem viés 21, 22\.  
* **PBRT 4e e Artigos:** O *Debiasing rendering algorithms* (Misso et al., 2022\) explica que a Roleta Russa é um caso especial de estimador de um único termo, que compensa o viés da truncatura infinita 23, 24\. O livro PBRT credita a introdução da técnica em CG a Arvo e Kirk (1990) 25\.

**Prompt para a IA (Contexto: scene.py):**  
"Implemente a **Roleta Russa (Russian Roulette)** de Arvo e Kirk no loop TracePath para lidar com a soma infinita do transporte de luz de maneira estocástica e sem viés (*unbiased*).

1. Ative a regra apenas se o comprimento do caminho for $\\ge 3$ (para garantir no mínimo 4 vértices).  
2. Defina a probabilidade de sobrevivência $q$ atrelada à luminância máxima do throughput $\\beta$: $q \= \\max(0.05, \\min(1.0, \\max(\\beta.x, \\beta.y, \\beta.z)))$.  
3. Sorteie $\\xi \\in \[0,1)$. Se $\\xi \> q$, encerre a construção do caminho (break).  
4. Se não encerrar, modifique o estimador escalando o throughput pelo inverso da probabilidade: $\\beta \= \\beta / q$."

### 📍 Fase 5: Materiais Físicos de Microfacetas (Modelo de Cook-Torrance)

**Cruzamento Teórico:**

* **PUC-Rio:** O modelo Cook-Torrance, a NDF de GGX (Walter et al., 2007\) e o termo Geométrico de Smith-Schlick estão na Aula 11 (11.microfaceta.pdf, pág. 9-18) 26-28.  
* **PBRT 4e & Papers:** A tese EPFL 29 e o artigo de *Bridging PBR and Diffusion Models* detalham a equação matemática explícita das microfacetas, isolando a distribuição D, o Fresnel F e a geometria G na integral do Monte Carlo 30\.

**Prompt para a IA (Contexto: material.py):**  
"Implemente uma classe MicrofacetMaterial que resolva a BRDF de **Cook-Torrance (1982)** baseada na teoria de microfacetas.

1. O denominador da equação deve ser rigorosamente $4 \* |n \\cdot w\_i| \* |n \\cdot w\_o|$.  
2. O termo de Distribuição Normal (NDF) $D(h)$ deve ser a distribuição **GGX** (Trowbridge-Reitz / Walter et al. 2007), onde a rugosidade geométrica é mapeada por $\\alpha \= roughness^2$.  
3. O termo de Fresnel $F(v,h)$ será a **Aproximação de Schlick**.  
4. O termo de Mascaramento/Sombreamento $G\_{Smith}(l, v)$ será o modelo de Smith acoplado a Schlick com $k \= \\alpha / 2$.  
5. Crie a amostragem sample() extraindo o vetor médio $h$ proporcionalmente a $D(h) \* \\cos(\\theta)$, obtendo a direção de reflexão ideal sobre $h$. Retorne a tupla (wi, BRDF\_value, PDF, is\_specular=False)."

### 📍 Fase 6: Isolamento de Deltas de Dirac (Dielétricos Perfeitos e Condutores)

**Cruzamento Teórico:**

* **PUC-Rio / PBRT 4e / Teses:** Espelhos e vidros criam funções $\\delta$ (Delta de Dirac) na densidade de probabilidade. O PBRT 4e (Cap 9.4 e 9.5) e a tese de Vicini (EPFL\_TH9008.pdf, Eq 3.14) evidenciam que, como o suporte da integral encolhe para um único ponto no hemisfério, o algoritmo falha numericamente se tentar aplicar *Next Event Estimation* e MIS tradicionais 31, 32\.

**Prompt para a IA (Contexto: scene.py e material.py):**  
"Adapte a infraestrutura do TracePath e das classes TransparentMaterial e ReflectiveMaterial para operar com os **Deltas de Dirac** gerados por refrações e reflexões perfeitas, evitando divisões por zero (NaN).

1. Em materiais puramente especulares, o método sample() deve retornar PDF \= 1.0 e um valor atenuado puramente pela função de Fresnel (ou Lei de Beer), setando imperativamente a flag is\_specular \= True. Cancele a divisão pelo cosseno neste retorno.  
2. No TracePath, envolva a rotina de *Next Event Estimation* (Sorteio de luz de área e MIS de luz) em um bloco if not is\_specular:. Dielétricos perfeitos não podem conectar caminhos por ângulos sólidos para luzes de área.  
3. Para o peso MIS do passo recursivo W\_brdf, se o material rebatido originou de um hit especular (is\_specular \== True), defina W\_brdf \= 1.0 rigidamente para não subestimar o trajeto em direção à luz."

### Benefício do Novo Cruzamento Teórico

Ao submeter estes novos prompts à sua IA geradora de código, a aderência à nomenclatura matemática (f\_r para BRDF, D, F, G para os termos, q para a probabilidade da Roleta Russa) forçará a IA a escrever um código em Python cujas variáveis e fluxos sejam um reflexo literal do *Physically Based Rendering (PBRT)* 3 e do framework *Veach-MIS* 15\. Esse alinhamento garante pontuação integral não apenas pela eficácia do algoritmo final, mas pelo rigor acadêmico que você demonstrará no seu relatório do Projeto 2\.  
