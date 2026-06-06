Aqui está o mapa de prompts detalhado, projetado especificamente para ser copiado e colado em assistentes como GitHub Copilot Chat, Cursor ou Gemini.  
Esses prompts foram desenhados considerando que a IA precisará entender a sua base de código em Python (yangricardo/INF2608-comp-grafica/src/path\_tracing) e as equações matemáticas do PBRT e das aulas do Prof. Waldemar Celes.  
Para obter os melhores resultados, **sempre forneça os arquivos atuais como contexto** para a IA antes de enviar o prompt (por exemplo, usando o comando @workspace ou anexando os arquivos no chat).

### 🛠️ Prompt 0: Configuração de Contexto Global (Opcional, mas recomendado)

**Onde usar:** No início da sua sessão de chat com a IA.  
"Atue como um engenheiro especialista em Computação Gráfica e renderização baseada em física (PBR). Estamos evoluindo um Ray Tracer clássico escrito em Python (orientado a objetos, usando glm) para um Path Tracer de Monte Carlo estocástico, baseado no livro 'Physically Based Rendering' (PBRT) e na Equação de Transporte de Luz. Nossos raios agora transportam radiância e usam integração numérica em vez de recursão direta. O código utiliza vetores da biblioteca glm. Mantenha a tipagem estática do Python e o código limpo."

### 📍 Passo 1: O Integrador Iterativo (Path Tracing)

**Arquivo de Contexto:** scene.py (ou crie path\_integrator.py) e ray.py.**Objetivo:** Substituir a recursão por um laço iterativo de acúmulo de radiância e atenuação.  
**Prompt:**  
"Refatore o método principal de traçado de raios (ex: trace\_ray) para usar a abordagem iterativa de Path Tracing (Monte Carlo).

1. Receba um raio primário e estabeleça um loop iterativo até um limite de max\_depth (ex: 5).  
2. Inicialize o acumulador de radiância L \= glm.vec3(0.0) e o fator de atenuação (throughput) beta \= glm.vec3(1.0).  
3. Em cada iteração do loop, calcule a interseção com a cena. Se não houver hit, adicione a cor de fundo vezes beta ao L e dê break.  
4. Se houver hit com um material emissivo, acumule no L a emissão vezes beta e dê break.  
5. Chame um método abstrato material.sample(wo, normal) que deve retornar a nova direção wi, a avaliação da BRDF, o valor da pdf e uma flag booleana is\_specular.  
6. Atualize o throughput: beta \*= BRDF \* max(0.0, glm.dot(normal, wi)) / pdf.  
7. Atualize a origem e direção do raio para o próximo salto."

### 📍 Passo 2: Material Difuso de Lambert (Amostragem de Hemisfério)

**Arquivo de Contexto:** material.py e métodos de amostragem no sampling.py (se existirem).**Objetivo:** Implementar o espalhamento estocástico para materiais foscos.  
**Prompt:**  
"Crie a classe DiffuseMaterial (ou refatore o material fosco atual) adaptada para Path Tracing.

1. Implemente o método sample(wo, normal) que será chamado pelo Path Integrator.  
2. Este método deve gerar uma direção wi aleatória usando **Amostragem do Hemisfério Ponderada pelo Cosseno** (Cosine-Weighted Hemisphere Sampling).  
3. O método deve retornar 4 valores: a direção amostrada wi (no espaço global, convertida a partir da normal), o valor da BRDF (albedo / math.pi), o valor da pdf (que neste caso é max(0.0, glm.dot(normal, wi)) / math.pi), e a flag is\_specular \= False.Lembre-se de fornecer a função matemática em Python para converter a amostra 2D local para uma direção hemisférica no espaço da normal fornecida."

### 📍 Passo 3: Múltipla Amostragem por Importância (MIS)

**Arquivos de Contexto:** scene.py (seu novo TracePath), light.py (especialmente AreaLight).**Objetivo:** Combinar a amostragem da luz (Next Event Estimation) com a amostragem da BRDF para reduzir o ruído vertiginosamente.  
**Prompt:**  
"Quero adicionar Múltipla Amostragem por Importância (MIS) usando a heurística de potência (Power Heuristic) ao nosso loop de TracePath criado anteriormente.Modifique a etapa de interseção em superfícies opacas (is\_specular \== False):

1. **Amostragem da Luz (NEE):** Escolha uma fonte de luz, sorteie um ponto sobre ela, obtenha a radiância Ld, a direção para a luz wi\_light, a distância e a pdf\_light (em ângulo sólido).  
2. Lance um shadow ray. Se não houver oclusão, calcule a probabilidade da BRDF gerar essa mesma direção: pdf\_brdf\_light \= material.pdf(wo, normal, wi\_light).  
3. Calcule o peso MIS da luz: weight\_light \= (pdf\_light\*\*2) / (pdf\_light\*\*2 \+ pdf\_brdf\_light\*\*2).  
4. Acumule: L \+= beta \* weight\_light \* BRDF \* Ld \* cos\_theta / pdf\_light.  
5. **Amostragem da BRDF:** Gere o próximo trecho do caminho através do material.sample como antes. Guarde o pdf\_brdf desse sorteio.  
6. Se o raio desse rebatimento atingir uma luz de área na iteração *seguinte*, avalie o MIS retroativamente: force o cálculo da pdf\_light para a direção anterior e pondere a emissão antes de adicionar a L usando weight\_brdf \= (pdf\_brdf\*\*2) / (pdf\_brdf\*\*2 \+ pdf\_light\*\*2). Assuma que AreaLight já existe."

### 📍 Passo 4: Roleta Russa (Russian Roulette)

**Arquivo de Contexto:** scene.py (o loop iterativo TracePath).**Objetivo:** Finalizar caminhos profundos sem gerar viés, focando apenas nos raios promissores.  
**Prompt:**  
"No loop do iterador TracePath, adicione a técnica de Roleta Russa (Russian Roulette) para terminação de caminhos.A lógica deve ser aplicada apenas após o caminho atingir uma profundidade mínima, especificamente depth \>= 3 (garantindo os 4 vértices do requisito do projeto).

1. Calcule a probabilidade de continuação q com base no valor máximo do vetor de throughput beta: q \= max(0.05, min(1.0, max(beta.x, beta.y, beta.z))).  
2. Sorteie um número aleatório xi entre 0 e 1\.  
3. Se xi \> q, termine o loop imediatamente (break).  
4. Se o raio sobreviver, divida o throughput pela probabilidade de sobrevivência para manter o estimador não viesado: beta /= q."

### 📍 Passo 5: Materiais PBR de Microfacetas (Cook-Torrance)

**Arquivo de Contexto:** material.py.**Objetivo:** Renderização física correta de metais e plásticos com rugosidade.  
**Prompt:**  
"Crie uma nova classe MicrofacetMaterial que implementa o modelo de refletância de Cook-Torrance (PBR).O material possui os parâmetros albedo (vec3), metallic (float 0 a 1\) e roughness (float 0 a 1).

1. Implemente a função de Distribuição Normal (NDF) **GGX** de Walter et al, dependendo de alpha \= roughness\*\*2.  
2. Implemente o termo Geométrico de **Smith-Schlick** ($G\_1(v) \* G\_1(l)$).  
3. Implemente a aproximação de Fresnel de **Schlick**. O $F\_0$ deve interpolar entre vec3(0.04) para dielétricos e o albedo para metais com base no parâmetro metallic.  
4. Implemente o método sample(wo, normal) que sorteie o half-vector h na distribuição GGX, reflita wo sobre h para achar wi, calcule a BRDF completa e retorne (wi, brdf\_value, pdf, is\_specular=False). Crie também o método pdf(wo, normal, wi) correspondente para ser usado pelo MIS."

### 📍 Passo 6: Transparência e Reflexão Pura (Deltas de Dirac)

**Arquivo de Contexto:** material.py e scene.py.**Objetivo:** Adaptar vidros e espelhos já existentes para não quebrarem o pipeline numérico do MIS (evitando divisões por zero).  
**Prompt:**  
"Precisamos adaptar nossos materiais espelhados (ReflectiveMaterial) e vidros refratários perfeitos (TransparentMaterial) para o Path Tracing.

1. Nesses materiais ideais, no método sample(wo, normal), retorne sempre pdf \= 1.0 e a flag is\_specular \= True. O retorno da BRDF será a cor atenuada (usando Fresnel e Beer-Lambert, se for vidro) dividida pelo cosseno, para cancelar o termo de cosseno no integrador.  
2. Atualize o TracePath para que, na etapa do MIS, **VERIFIQUE:** if is\_specular:. Se o material do vértice atual for especular puro, **pule a amostragem de luz direta (NEE)** para este vértice.  
3. Além disso, se o raio rebatido por esse material especular cruzar uma fonte de luz na próxima iteração, certifique-se de que o peso MIS weight\_brdf dessa emissão seja forçado a 1.0 (ou seja, consideraremos 100% da contribuição, já que a luz direta não conseguiu amostrar esse vértice)."

### Dicas de Execução:

* Cole um prompt por vez e revise o código gerado.  
* Teste a renderização logo após a **Fase 2** com objetos puramente foscose valide se consegue ver uma cena escurecida com bastante ruído (isso é normal no Path Tracing puro).  
* Teste novamente após a **Fase 3** (MIS); a cena deve saltar para uma qualidade incrivelmente limpa na mesma quantidade de spp.

