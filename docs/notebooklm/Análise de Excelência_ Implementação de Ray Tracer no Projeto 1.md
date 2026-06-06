A comparação entre o enunciado do **Projeto 1** (proj1.pdf) e o relatório final entregue (inf2608-proj1.v3.pdf) revela que a implementação não apenas cumpriu integralmente todos os requisitos exigidos, mas superou amplamente a pontuação de extensões proposta, entregando um trabalho de engenharia de software e fundamentação matemática bastante rigoroso.  
Abaixo, detalho a análise comparativa dividida pelas seções do enunciado:  
**1\. Requisitos Básicos (Valor: 7.0 pontos)**O enunciado exigia uma aplicação capaz de gerar uma cena 3D com as seguintes características 1, 2:

* **Instanciação de esferas e caixas:** Cumprido. O relatório comprova a instanciação dessas formas básicas e sua coerência espacial logo na sua primeira evidência visual (Figura 1\) 3, 4\.  
* **Iluminação por fontes pontuais:** Cumprido. A implementação de PointLight foi testada e documentada com múltiplas fontes atuando simultaneamente 3, 5\.  
* **Modelo Phong e geração de sombras diretas:** Cumprido. O relatório detalha a implementação do PhongMaterial, calculando os termos ambiente, difuso e especular, assim como os *shadow rays* gerados para verificar a oclusão 5-7.  
* **Múltiplas amostras por pixel (distribuição uniforme):** Cumprido. O aluno reestruturou a classe Film para suportar diferentes regimes de integração subpixel (center, jittered e stratified), convertendo o serrilhado em ruído e estabilizando a imagem 8-10.

**2\. Funcionalidades Adicionais / Extensões (Esperado: 3.0 pontos)**O enunciado pedia que o aluno escolhesse opções de uma lista para somar 3.0 pontos 2, 11\. O relatório evidencia que o projeto implementou **praticamente todas as extensões listadas**, totalizando um equivalente a **9.0 pontos extras**:

* **Transformações de modelagem (1.0 pt):** Implementado via inversas e inversas transpostas para garantir que as normais interajam perfeitamente com a transformação afim de objetos (escalas, translações e rotações) 12, 13\.  
* **Instanciação de malhas de triângulos (1.0 pt):** Implementado utilizando o algoritmo clássico de *Möller-Trumbore* e cálculo de coordenadas baricêntricas 14-16.  
* **Estrutura de aceleração espacial (2.0 pts):** Implementado como uma Bounding Volume Hierarchy (BVH) estática local e caixas AABB (Axis-Aligned Bounding Boxes) para acelerar a travessia das malhas trianguladas 16, 17\.  
* **Luz retangular de área com distribuição (1.0 pt) e Comparação de distribuições (1.0 pt):** O relatório detalha a classe AreaLight com integração sobre o emissor e penumbra, comparando padrões uniform, regular e stratified para o cálculo da integração sobre a fonte 18, 19\.  
* **Objetos reflexivos (1.0 pt):** O ReflectiveMaterial utiliza o modelo Phong clássico somado ao vetor de reflexão ponderado pela aproximação de Fresnel-Schlick 20, 21\.  
* **Objetos refratários (2.0 pts):** O código cobre a Lei de Snell, verifica Reflexão Interna Total (TIR) e estende a física com a atenuação de Beer-Lambert dependente da distância percorrida pela luz dentro do meio 21, 22\.

**3\. Elaboração do Relatório**O enunciado deixava explícito que a "qualidade do relatório é parte fundamental da avaliação", exigindo descrição técnica e análise detalhada com screenshots 11, 23.O aluno entregou um documento que vai muito além de descrições superficiais 24, 25:

* **Arquitetura e Rastreabilidade:** O relatório apresenta diagramas de classe detalhados (Anexo B) documentando todo o design orientado a objetos que separou câmera, filme, amostradores, primitivas e funções de sombreamento 25-27.  
* **Infraestrutura Experimental (CLI):** O aluno construiu uma Interface de Linha de Comando (CLI) para garantir que cada imagem exibida fosse auditável e as comparações justas 28, 29\.  
* **Uso da Cornell Box:** A instrução de usar e customizar uma Cornell Box (sugerida no enunciado 11\) foi fortemente utilizada para demonstrar *anti-aliasing* (com a cena cornell\_box\_pyramid), materiais reflexivos e refração 30, 31\.  
* **Transparência e Limitações:** Com maturidade técnica, o relatório também tem uma seção apenas para apontar *limites e decisões de modelagem*, reconhecendo as restrições da sua implementação, como as diferenças de convenções radiométricas entre PointLight e AreaLight, e o fato de a BVH não ser global para a cena, e sim local aos triângulos 32-34.

**Conclusão**Em comparação com as especificações exigidas em proj1.pdf, a entrega inf2608-proj1.v3.pdf excedeu largamente o escopo mínimo e atendeu todas as diretrizes de expansões opcionais de traçado de raios (Prática I), entregando um *ray tracer* complexo e um texto explicativo digno de excelência acadêmica.  
