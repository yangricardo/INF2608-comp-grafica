Compreendo perfeitamente o seu objetivo. Para a entrega do **Projeto 2** até o dia 30 de junho, você precisará migrar de um traçador de raios recursivo clássico para um traçador de caminhos estocástico iterativo (Path Tracing), apoiado na Equação de Renderização 1\.  
Abaixo apresento o plano de implementação detalhado, transformando a teoria das Aulas 7 a 11 e do PBRT 1-40 em pacotes de trabalho incrementais. Este roteiro foi desenhado especificamente para você copiar e colar como **instruções de contexto (prompts)** no GitHub Copilot ou Gemini, garantindo que a IA gere os algoritmos matematicamente corretos na sua arquitetura em Python.

### Fase 0: Setup e Duplicação da Arquitetura (Dia 1\)

**Objetivo:** Criar o ambiente base sem quebrar o Projeto 1\.

1. Duplique a pasta src/ray\_tracing\_2/ e renomeie para src/path\_tracing/.  
2. Atualize todos os imports internos (arquivos como \_\_main\_\_.py, cli.py, render.py) para apontarem para o novo pacote path\_tracing.  
3. Garanta que a sua infraestrutura experimental (snapshots, RenderEstimator, CommonRenderOptions 41, 42\) continue operando para as saídas na pasta outputs/.

### Fase 1: O Integrador de Caminhos Interativo (TracePath)

**Objetivo:** Substituir a recursão da classe Scene por um laço iterativo de transporte de luz.

* **Fundamento:** Em vez de recursão, o Path Tracer usa um acumulador de radiância (L) e um fator de atenuação/throughput (beta) 43\. O raio viaja pela cena iterativamente 44, 45\.  
* **Prompt para IA (Inserir em scene.py ou novo integrator.py):**  
* "Atue como um especialista em Computação Gráfica. Refatore a função de traçado de raios local para implementar um TracePath iterativo de Monte Carlo (Path Tracing).O algoritmo deve receber o raio primário da câmera e iterar até max\_depth.Inicialize L \= vec3(0.0) e beta \= vec3(1.0).Em cada laço: calcule a interseção (hit). Se não atingir nada, adicione a cor de fundo vezes beta e quebre o laço. Se atingir um emissor de luz, adicione a radiância da luz vezes beta e quebre o laço. Em seguida, chame material.sample(wo, normal) para obter a nova direção wi, a avaliação da BRDF e o valor da probabilidade pdf.Atualize o throughput: beta \*= BRDF \* max(0, dot(normal, wi)) / pdf. Em seguida, gere o próximo raio a partir do ponto de interseção na direção wi."

### Fase 2: Amostragem e Materiais Difusos Ideais (Lambert)

**Objetivo:** Implementar o espalhamento estocástico nos materiais básicos.

* **Fundamento:** A BRDF de um material difuso é constante, $\\rho / \\pi$, onde $\\rho$ é o albedo (cor) 46\. Para otimizar a integração, usa-se a Amostragem do Hemisfério Ponderada pelo Cosseno 47, 48, cuja função de densidade de probabilidade (PDF) é $\\cos(\\theta) / \\pi$ 48\.  
* **Prompt para IA (Inserir em material.py):**  
* "Adicione uma interface estocástica baseada no PBR para a classe Material com o método sample(wo, normal).Para a classe DiffuseMaterial (Lambertiano), implemente o sample usando Amostragem Ponderada pelo Cosseno (Cosine-Weighted Hemisphere Sampling).O método deve retornar 4 valores: a nova direção wi, o valor da BRDF (albedo / $\\pi$), o valor da pdf ($\\max(0, dot(normal, wi)) / \\pi$), e uma flag booleana is\_specular \= False. Lembre-se de transformar a direção amostrada do espaço tangente local (Z para cima) para o espaço global da normal."

### Fase 3: Múltipla Amostragem por Importância (MIS) para Luz Direta

**Objetivo:** Adicionar a "Estimativa de Próximo Evento" (Next Event Estimation) balanceada com a heurística de Veach.

1. **Fundamento:** Amostrar aleatoriamente o hemisfério pode nunca encontrar luzes pequenas. O MIS combina a amostragem sobre a área da luz e a amostragem da BRDF, ponderando os pesos pela *Power Heuristic* ($w \= p\_1^2 / (p\_1^2 \+ p\_2^2)$) 49, 50\.  
2. **Prompt para IA (Expandir o TracePath criado na Fase 1):**  
3. "Melhore o laço do integrador para incluir Múltipla Amostragem por Importância (MIS) avaliando a iluminação direta.Em cada interseção com material opaco (is\_specular \== False), realize os seguintes passos:  
4. Sorteie um ponto na AreaLight para obter wi\_light, a distância, e pdf\_light em relação ao ângulo sólido (solid angle).  
5. Lance um raio de sombra (shadow ray). Se não houver oclusão, calcule o peso MIS: weight\_light \= (pdf\_light\*\*2) / (pdf\_light\*\*2 \+ pdf\_brdf\_light\_dir\*\*2).  
6. Acumule no L principal: L \+= beta \* weight\_light \* (BRDF \* L\_d \* cos\_theta / pdf\_light).  
7. Quando o raio quicar rebatido pela amostragem da BRDF e atingir a luz de área no passo seguinte do laço iterativo, calcule o weight\_brdf \= (pdf\_brdf\_prev\*\*2) / (pdf\_brdf\_prev\*\*2 \+ pdf\_light\_prev\*\*2) e pondere a emissão antes de adicioná-la a L."

### Fase 4: Otimização de Caminhos via Roleta Russa

**Objetivo:** Permitir que o algoritmo rastreie rebatimentos longos sem custo infinito, terminando caminhos improváveis estatisticamente de forma correta.

* **Fundamento:** A Roleta Russa cancela caminhos de forma justa dividindo o throughput pela probabilidade de continuação (sobrevivência) 51, 52\. O enunciado exige profundidade mínima de 4\.  
* **Prompt para IA (Inserir no final do laço de TracePath):**  
* "Adicione uma Roleta Russa ao integrador TracePath para encerrar caminhos de baixa contribuição de forma sem viés (unbiased).Esta lógica só deve ser ativada se depth \>= 3 (garantindo o mínimo de 4 vértices do enunciado).Calcule a probabilidade de continuação q \= max(beta.r, beta.g, beta.b).Gere um número aleatório uniforme xi. Se xi \> q, dê break no laço de integração.Caso contrário, compense a energia fazendo beta \= beta / q."

### Fase 5: Materiais Físicos de Microfacetas (Cook-Torrance)

**Objetivo:** Substituir o modelo empírico de Phong pelo modelo realista PBR baseado na distribuição GGX para renderizar metais ou superfícies rugosas 26, 28\.

* **Fundamento:** A BRDF microfacetada exige as funções Distribuição $D\_{GGX}$, Reflexão de Fresnel (Schlick) e Mascaramento-Sombreamento $G\_{Smith}$ 37-39.  
* **Prompt para IA (Em material.py):**  
* "Crie a classe MicrofacetMaterial que substitua o modelo Phong usando a teoria Cook-Torrance.A BRDF será calculada por f \= (D \* F \* G) / (4 \* dot(n, wi) \* dot(n, wo)).Implemente a Distribuição Normal de Walter et al. ($D\_{GGX}$) dependente da rugosidade alpha \= roughness\*\*2.Implemente o termo de geometria $G\_{Smith}(wi, wo) \= G\_{Schlick}(wi) \* G\_{Schlick}(wo)$ onde $k \= alpha / 2$.Implemente o Fresnel $F$ pela aproximação de Schlick dependente do vetor médio (half-vector h).Crie o método de amostragem (sample) deste material, sorteando a normal da microfaceta usando a densidade de probabilidade de GGX, e retornando o raio refletido perfeitamente sobre a normal sorteada."

### Fase 6: Adequação da Geometria Refratária (Vidros/Espelhos)

**Objetivo:** Garantir que dielétricos/vidros implementados no Projeto 1 funcionem no Path Tracer sem explodir as equações com divisões por zero.

1. **Fundamento:** Refrações e espelhos perfeitos geram Delstas de Dirac matemáticos, o que significa que sua PDF clássica é infinita e eles não podem ser avaliados por amostragem de luz direta (Next Event Estimation) 3-21.  
2. **Prompt para IA (Em material.py e integrador):**  
3. "Ajuste os materiais TransparentMaterial (Lei de Snell e Beer-Lambert) e ReflectiveMaterial (Espelhos) para o Path Tracing.No retorno do seu método sample(), defina a flag is\_specular \= True e coloque a pdf \= 1.0.Modifique o integrador TracePath para que, ao cruzar vértices onde is\_specular \== True:  
4. Ele IGNORE o sorteio de luz direta (MIS com as luzes) para aquele salto.  
5. Se o raio de um espelho/vidro atingir uma luz, o peso do MIS weight\_brdf do passo anterior seja forçado a 1.0."

### Check-list Executivo até 30 de Junho:

1. **Até 10/Junho:** Completar as Fases 0, 1 e 2\. Valide que cenas inteiramente difusas (Apenas Lambert) com 64 spp geram uma imagem escura, porém fotorealista, na sua infraestrutura.  
2. **Até 15/Junho:** Completar Fase 3 e 4\. O uso de MIS com AreaLight fará o ruído da imagem cair drasticamente e o renderizador ficará rápido em áreas sombreadas.  
3. **Até 22/Junho:** Adicionar e testar as microfacetas (Fase 5\) e vidro adaptado (Fase 6). Você usará os testes da *Cornell Box* 53 que já possui no seu repositório para confirmar a convergência física dos cáusticos.  
4. **Restante do tempo:** Redigir o PDF focado em demonstrar a queda do ruído por causa do MIS e a diferença do sombreamento PBR vs. Phong, reaproveitando a força da sua CLI e de saídas properties.json/md 41, 42\.

