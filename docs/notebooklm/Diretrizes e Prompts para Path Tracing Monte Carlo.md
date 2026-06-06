Aqui está a proposta refinada e altamente detalhada dos prompts, agora ancorada diretamente nos slides e páginas do material da disciplina ministrada pelo Prof. Waldemar Celes, bem como em referências clássicas como o PBRT.  
Essa estrutura não apenas instrui a IA (Copilot/Gemini) sobre *o que* fazer, mas dá a ela a base matemática e a referência exata para que os geradores de código sigam as mesmas convenções usadas no curso.

### 🛠️ Prompt 0: Configuração de Contexto Global (Opcional, mas recomendado)

**Referências Teóricas:** 2.introducao.pdf (Equação de Renderização) 1, *A Simple Path Tracer \- PBR Book* 2, 3\.**Como usar:** Envie este prompt antes de qualquer outro para configurar o "cérebro" da IA.  
"Atue como um engenheiro especialista em Computação Gráfica. Estamos migrando um Ray Tracer clássico em Python (yangricardo/INF2608-comp-grafica/src/path\_tracing) para um Path Tracer de Monte Carlo estocástico baseado na Equação de Renderização e no livro PBRT. Nossos raios transportam radiância e usaremos um loop iterativo com acumulador L e throughput beta, abandonando a recursão pura. O código utiliza vetores glm. Respeite a tipagem estática e mantenha o código modular."

### 📍 Fase 1: O Integrador Iterativo (TracePath)

**Referências Teóricas:**

* 8.tracado\_de\_caminhos.pdf, pág. 20-21 (Pseudo código do TracePath) 4, 5\.  
* 9.tracado\_de\_caminhos2.pdf, pág. 7-8 (Atualização do pseudo código com avaliação da luz) 6, 7\.

**Prompt para a IA (Contexto: scene.py):**  
"Refatore o método principal de avaliação de raios (trace\_ray ou crie TracePath) para usar a abordagem iterativa de Path Tracing.Siga rigorosamente o pseudo código da Aula 8 (Traçado de Caminhos, pág 21\) e Aula 9 (pág 8\) do Prof. Waldemar Celes:

1. Receba um raio e itere até max\_depth.  
2. Inicialize L \= glm.vec3(0.0) e beta \= glm.vec3(1.0).  
3. Ao atingir uma luz, se for a primeira iteração (depth \== 0), retorne a radiância emitida pela luz L\_e ponderada pelo beta. Caso contrário, quebre o laço (encerre o caminho).  
4. Se atingir um material, chame mat.sample() para obter: direção rebatida wi, valor da BRDF e a probabilidade pdf.  
5. Atualize o throughput exatamente como na teoria: beta \*= BRDF \* max(0.0, glm.dot(normal, wi)) / pdf.  
6. Atualize o raio para o próximo salto a partir do ponto de interseção na direção wi."

### 📍 Fase 2: Amostragem e Material Difuso (Lambert)

**Referências Teóricas:**

* 8.tracado\_de\_caminhos.pdf, pág. 20 (BRDF do material difuso $f\_r \= \\rho/\\pi$) 4\.  
* 7.montecarlo.pdf, pág. 43 a 46 (Amostragem do hemisfério ponderada pelo cosseno e Método de Malley) 8-10.

**Prompt para a IA (Contexto: material.py / sampling.py):**  
"Implemente a amostragem estocástica para materiais difusos (Lambert).

1. Na classe DiffuseMaterial, a função de BRDF ($f\_r$) é constante e igual ao albedo dividido por PI (conforme Aula 8, pág 20).  
2. Crie um método sample(wo, normal) que sorteie a direção de espalhamento wi usando **Amostragem do Hemisfério Ponderada pelo Cosseno** (Cosine-Weighted Hemisphere Sampling), referenciada na Aula 7 (Integração Monte Carlo, pág 43-46) utilizando o Método de Malley (pontos no disco unitário projetados para a esfera).  
3. O valor do pdf resultante para essa amostragem direcional deverá ser max(0, dot(normal, wi)) / PI.  
4. O retorno de sample deve ser a tupla: (wi, brdf\_value, pdf, is\_specular=False)."

### 📍 Fase 3: Múltipla Amostragem por Importância (MIS)

**Referências Teóricas:**

* 9.tracado\_de\_caminhos2.pdf, pág. 16 a 22 (Amostragem por importância, MIS e Heurística da Potência com $\\beta=2$) 11-14.

**Prompt para a IA (Contexto: scene.py / novo loop iterativo):**  
"Expanda o loop de TracePath para incorporar Múltipla Amostragem por Importância (MIS) para iluminação direta, visando resolver o problema de alta variância descrito na Aula 9 (pág 16-22).

1. Em cada vértice não-especular (is\_specular \== False), amostre explicitamente a fonte de luz de área (Next Event Estimation).  
2. Obtenha a direção wi\_light, radiância L\_d e a pdf\_light (em ângulo sólido). Teste a oclusão com um raio de sombra.  
3. Avalie a pdf\_brdf para essa mesma direção wi\_light.  
4. Calcule o peso usando a **Heurística da Potência de Veach** (Aula 9, pág 21\) com $\\beta=2$: weight\_light \= (pdf\_light\*\*2) / (pdf\_light\*\*2 \+ pdf\_brdf\*\*2).  
5. Acumule no valor global L \+= beta \* weight\_light \* (BRDF \* L\_d \* cos\_theta / pdf\_light).  
6. Adapte a amostragem contínua do caminho (via BRDF) para que, se atingir a luz de área no próximo salto, a emissão seja ponderada pelo peso MIS inverso."

### 📍 Fase 4: Otimização de Caminhos via Roleta Russa

**Referências Teóricas:**

* 9.tracado\_de\_caminhos2.pdf, pág. 12 a 14 (Estratégia Roleta Russa para aumentar eficiência sem gerar viés) 15-17.

**Prompt para a IA (Contexto: scene.py / TracePath):**  
"Implemente a terminação estocástica de caminhos (Roleta Russa) no TracePath, baseando-se na Aula 9 (pág 13-14).

1. Para garantir o requisito mínimo do projeto, a roleta russa só deve ser ativada após profundidade \>= 3 (assegurando um mínimo de 4 vértices).  
2. Calcule a probabilidade de continuação q com base no throughput atual (ex: valor máximo do canal RGB de beta).  
3. Gere um número aleatório uniforme $\\xi$. Se $\\xi \> q$, termine o loop break.  
4. Se continuar o caminho, divida o throughput pela probabilidade de sobrevivência q (beta /= q) para que o estimador de Monte Carlo permaneça não viesado ($EF' \= EF$)."

### 📍 Fase 5: Materiais PBR Microfacetas (Cook-Torrance)

**Referências Teóricas:**

* 11.microfaceta.pdf, pág. 9 (Fórmula Cook-Torrance) 18\.  
* 11.microfaceta.pdf, pág. 10 a 14 (Termo de Fresnel/Schlick e tabelas $F\_0$) 19-21.  
* 11.microfaceta.pdf, pág. 15 (Distribuição Normal GGX de Walter et al.) 22, 23\.  
* 11.microfaceta.pdf, pág. 16 a 18 (Termo Geométrico de Mascaramento de Smith/Schlick) 24-26.

**Prompt para a IA (Contexto: material.py):**  
"Crie a classe MicrofacetMaterial que implementa o modelo realista de Cook-Torrance (Aula 11 de Microfacetas).

1. A fórmula base da BRDF é f\_r \= (D \* F \* G) / (4 \* dot(n, wi) \* dot(n, wo)) (pág 9).  
2. Implemente o termo D(h) como a função de distribuição **GGX** (Walter et al., pág 15\) onde $\\alpha \= r^2$.  
3. Implemente o Fresnel F(v,h) pela aproximação de Schlick (pág 14), interpolando entre 0.04 (dielétricos) e o albedo para metais dependendo de um parâmetro metallic.  
4. Implemente o termo geométrico G\_{Smith}(l, v) \= G1(l) \* G1(v) usando a variante de Schlick com $k \= \\alpha/2$ (pág 17).  
5. Crie a amostragem baseada na NDF para este material e retorne a flag is\_specular \= False."

### 📍 Fase 6: Readequação de Vidros e Espelhos

**Referências Teóricas:**

* Livro base PBRT (citado no curso): Ao lidar com Deltas de Dirac (Espelhos perfeitos e Dielétricos limpos), a avaliação de MIS falha pois a função de densidade de probabilidade $p(w)$ explode para infinito. Tratamento: isolamento especular 27, 28\.  
* 5.tracado\_de\_raios2.pdf, pág. 26 e 29 (Leis de Snell, Reflexão/Refração de materiais transparentes) 29, 30\.

**Prompt para a IA (Contexto: material.py e scene.py):**  
"Adapte as classes puramente especulares do Projeto 1 (ReflectiveMaterial e TransparentMaterial baseadas em Snell/Beer-Lambert, Aula 5, pág 29\) para o Path Tracer.

1. Na função sample(), espelhos perfeitos e refrações puras devem definir a flag is\_specular \= True e retornar pdf \= 1.0. O valor de retorno da 'BRDF' será a cor diretamente avaliada por Fresnel atenuada sem divisão pelo cosseno.  
2. No TracePath, o MIS não pode amostrar luzes (Next Event Estimation) se o vértice atual for originado de um material especular, pois a PDF teórica é um Delta de Dirac.  
3. Quando um raio disparado por um material especular colidir com a fonte de luz no próximo passo da iteração, acumule a emissão em L com peso MIS forçado a 1.0 (já que $p\_{brdf}$ é tecnicamente impossível de ser comparada com a área da luz nesse salto)."

Esses prompts capturam fielmente o jargão, as equações explícitas e a filosofia de ensino apresentados nas aulas (como na derivação do termo geométrico de Smith ou a Heurística da Potência no MIS) 13, 14, 25, garantindo que o seu repositório de Path Tracing reflita um profundo alinhamento com a PUC-Rio e o material do projeto.  
