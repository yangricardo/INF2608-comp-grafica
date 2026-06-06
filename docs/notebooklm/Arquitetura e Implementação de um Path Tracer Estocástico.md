Com base na revisão exaustiva da arquitetura do seu repositório atual (especificamente os módulos em src/ray\_tracing\_2/ 1\) e no arcabouço teórico da disciplina (Aulas 7 a 11 do Prof. Waldemar Celes 2\) cruzado com a literatura do *Physically Based Rendering* (PBRT 4e) e teses associadas (como a de Delio Vicini da EPFL 3), apresento a estrutura de *prompts* e fases detalhadas.  
Esta versão foca exatamente em **quais arquivos alterar**, **quais classes criar** e as **referências teóricas cruzadas** que devem ser passadas para a IA geradora de código.

### 🛠️ Fase 0: Setup e Duplicação de Módulos

O primeiro passo não usa prompt, mas prepara a base arquitetural para que o Path Tracer seja construído de forma limpa, preservando o Projeto 1 4\.

* **O que criar/alterar:** Duplique a pasta src/ray\_tracing\_2/ e renomeie-a para src/path\_tracing/. Em arquivos como \_\_main\_\_.py, cli.py e render.py, atualize todos os *imports* internos de ray\_tracing\_2 para path\_tracing 4\. Sua infraestrutura de RenderSnapshot e RenderEstimator deve ser mantida intacta 5\.

### 📍 Fase 1: O Integrador Iterativo (Equação de Transporte de Luz)

* **Módulo a alterar:** scene.py (ou criar path\_integrator.py).  
* **O que mudar no código:** Substituir o método recursivo trace\_ray() por um laço (loop) iterativo TracePath() que resolva a Equação de Renderização original de Kajiya 6\. A função não deve mais empilhar chamadas, mas manter as variáveis de estado: Radiância Acumulada (L) e Atenuação (beta ou throughput) 7-9.  
* **Referências para a IA:** Slides Aula 8 (pág. 21\) 7; Aula 9 (pág. 8\) 10; PBRT 4e Cap. 13 (SimplePathIntegrator) 11, 12\.

**Prompt para a IA (Forneça o arquivo scene.py como contexto):**  
"Reescreva o método principal de avaliação de raios na classe Scene implementando o algoritmo TracePath iterativo, abandonando a recursão pura (baseado no PBRT 4e Cap 13 e no pseudo-código da Aula 8 do Prof. Waldemar Celes).

1. Receba um raio e itere em um for ou while até max\_depth.  
2. Inicialize o acumulador L \= glm.vec3(0.0) e o throughput beta \= glm.vec3(1.0).  
3. Na interseção (Hit), verifique se atingiu um emissor (AreaLight ou material emissivo). Se sim, e for a primeira iteração (depth \== 0), adicione ao acumulador L \+= beta \* L\_e e encerre o laço.  
4. Se atingir um material opaco, chame um método material.sample(wo, normal) (que criaremos depois) para obter a direção rebatida wi, o valor da BRDF e a PDF.  
5. Atualize o throughput estritamente pela Equação de Transporte: beta \*= BRDF \* max(0.0, glm.dot(normal, wi)) / PDF.  
6. Atualize a origem e direção do raio do laço para o próximo rebote partindo do ponto de interseção."

### 📍 Fase 2: Amostragem e Material Difuso (Lambert)

* **Módulos a alterar:** material.py e sampling.py.  
* **O que mudar no código:** Na classe base Material, adicionar o contrato do método sample(wo, normal). Em DiffuseMaterial (ou PhongMaterial simplificado), implementar o espalhamento estocástico usando o Método de Malley (Amostragem Ponderada pelo Cosseno) gerando padrões no disco unitário projetados na esfera 13, 14\.  
* **Referências para a IA:** Slides Aula 7 (pág. 43-46) 13, 15; Aula 8 (pág. 20\) 7\.

**Prompt para a IA (Forneça os arquivos material.py e sampling.py):**  
"Atualize a classe DiffuseMaterial (Lambertiano) para o contexto de Path Tracing estocástico.

1. A BRDF (f\_r) constante é igual ao albedo do material dividido por PI.  
2. Implemente o método sample(wo, normal) que utilize a Amostragem do Hemisfério Ponderada pelo Cosseno (Método de Malley).  
3. Sorteie dois valores uniformes xi\_1, xi\_2, mapeie para o disco e projete para o hemisfério local. Use matrizes glm para transformar essa direção wi do espaço tangente para o espaço global alinhado à normal.  
4. A densidade de probabilidade (PDF) dessa amostragem é max(0, glm.dot(normal, wi)) / PI.  
5. O método deve retornar uma tupla ou dicionário: (wi, BRDF\_value, PDF\_value, is\_specular=False)."

### 📍 Fase 3: Múltipla Amostragem por Importância (MIS) para Luz Direta

* **Módulos a alterar:** scene.py (laço TracePath) e light.py (classe AreaLight).  
* **O que mudar no código:** Introduzir a Estimativa de Próximo Evento (NEE) dentro do laço TracePath para materiais não-especulares. É necessário chamar a amostragem explícita da AreaLight (que já existe na sua base 16, 17\) e ponderá-la pela Heurística da Potência de Veach junto com o sorteio da BRDF 18-20.  
* **Referências para a IA:** Slides Aula 9 (pág. 16-22) 19, 21; Veach (1995).

**Prompt para a IA (Forneça o arquivo scene.py e light.py atualizados):**  
"Aprimore o integrador TracePath em scene.py com Múltipla Amostragem por Importância (MIS), utilizando estritamente a Heurística da Potência (Power Heuristic) com expoente beta=2, conforme proposto por Veach (1995).

1. Em superfícies opacas (is\_specular \== False), isole a etapa de Next Event Estimation (NEE): sorteie um ponto na luz de área, lance um raio de oclusão e calcule a radiância L\_d e a PDF\_light em ângulo sólido.  
2. Calcule a probabilidade da BRDF apontar para a mesma direção: PDF\_brdf.  
3. Calcule o peso MIS da luz: w\_light \= (PDF\_light\*\*2) / (PDF\_light\*\*2 \+ PDF\_brdf\*\*2) e acumule em L \+= beta \* w\_light \* BRDF \* L\_d \* cos(theta) / PDF\_light.  
4. Após acumular a luz direta, prossiga no laço: faça a amostragem da BRDF (material.sample()) para o próximo salto contínuo do caminho.  
5. Se o raio desse salto atingir a luz de área na iteração seguinte, calcule retroativamente o w\_brdf \= (PDF\_brdf\_prev\*\*2) / (PDF\_brdf\_prev\*\*2 \+ PDF\_light\_prev\*\*2) e pondere a emissão dessa luz usando esse peso inverso."

### 📍 Fase 4: Terminação de Caminhos (Roleta Russa)

* **Módulo a alterar:** scene.py.  
* **O que mudar no código:** No final do laço iterativo em TracePath, implementar a quebra sem viés de caminhos que já não possuem muita energia (throughput baixo). O enunciado exige 4 vértices mínimos, então ative após depth \>= 3 22, 23\.  
* **Referências para a IA:** Slides Aula 9 (pág. 13-14) 24, 25; Arvo & Kirk (1990).

**Prompt para a IA (Forneça scene.py):**  
"No laço de integração TracePath, implemente a técnica de Roleta Russa (Russian Roulette) de Arvo e Kirk para terminação sem viés do transporte de luz.

1. A regra deve ser ativada unicamente se depth \>= 3\.  
2. Calcule a probabilidade de sobrevivência q atrelada à energia restante no throughput (ex.: q \= max(0.05, min(1.0, max(beta.x, beta.y, beta.z)))).  
3. Gere o número aleatório xi. Se xi \> q, efetue break finalizando o caminho.  
4. Se o raio não for terminado, escale o estimador dividindo o vetor beta por q (beta /= q) para assegurar a compensação correta de Monte Carlo."

### 📍 Fase 5: Materiais Físicos de Microfacetas (Modelo de Cook-Torrance)

* **Módulo a alterar:** material.py (Adicionar nova classe).  
* **O que mudar no código:** Criar a classe MicrofacetMaterial. Ela substituirá modelos analíticos empíricos e necessita implementar os três termos do modelo PBR: Distribuição ($D$), Geometria ($G$) e Fresnel ($F$) 26, 27\.  
* **Referências para a IA:** Slides Aula 11 (pág. 9-18) 28, 29; Walter et al. (2007) 29; PBRT Cap. 9 (Reflection Models) 30\.

**Prompt para a IA (Forneça material.py):**  
"Crie uma nova classe MicrofacetMaterial que resolva a BRDF de Cook-Torrance baseada em microgeometria e adicione seu método sample(wo, normal).

1. A equação base da BRDF é f \= (D \* F \* G) / (4 \* abs(dot(n, wi)) \* abs(dot(n, wo))).  
2. Implemente a função de Distribuição Normal (NDF) D(h) com o modelo GGX (Trowbridge-Reitz) de Walter et al., onde a rugosidade geométrica seja mapeada por alpha \= roughness\*\*2.  
3. O termo de Fresnel F(v,h) será a Aproximação de Schlick, interpolando a cor de dielétricos (vec3(0.04)) ao albedo para metais, via parâmetro de controle metallic.  
4. O Mascaramento G(l, v) será a função de Smith/Schlick com k \= alpha / 2\.  
5. A amostragem sample() extrai o half-vector h proporcionalmente a D(h) \* cos(theta), calculando o raio perfeitamente refletido wi sobre h. O método deve devolver is\_specular \= False."

### 📍 Fase 6: Isolamento de Deltas de Dirac (Dielétricos Perfeitos e Condutores)

* **Módulos a alterar:** material.py e scene.py.  
* **O que mudar no código:** Ajustar as lógicas do TransparentMaterial (vidro que já contém as leis de Snell e Beer-Lambert 31, 32\) e do ReflectiveMaterial. Em um traçador estocástico com MIS, reflexões puras falham pois geram uma PDF impulsiva infinita (Deltas de Dirac) e causam erro de divisão por zero 3, 33, 34\.  
* **Referências para a IA:** PBRT 4e Cap. 9 (Specular Reflection and Transmission) 30; Tese EPFL\_TH9008 de Delio Vicini 3\.

**Prompt para a IA (Forneça scene.py e material.py):**  
"Modifique as classes puramente especulares (ReflectiveMaterial e TransparentMaterial) e a lógica do TracePath para tratar os Deltas de Dirac, suportando assim refrações perfeitas sem quebrar a matemática do estimador.

1. Nas classes especulares, o método sample() deve forçar PDF \= 1.0 e is\_specular \= True. O valor devolvido pela BRDF deve ser o cálculo de Fresnel exato (e Beer-Lambert se refratado) sem divisão pelo cosseno (já que a densidade anula esse termo analiticamente).  
2. No loop TracePath, englobe o processo de amostragem de luz direta (NEE com AreaLights) dentro de um bloco condicional if not is\_specular:. Reflexões perfeitas são fisicamente impedidas de criar conexões implícitas com fontes de luz via MIS.  
3. Na iteração subsequente do laço recursivo, caso um raio oriundo de uma colisão onde is\_specular \== True acerte fortuitamente a fonte de área, assegure que o peso MIS w\_brdf retroativo seja rigidamente travado em 1.0, coletando integralmente a energia da fonte de luz com L \+= beta \* L\_e."

