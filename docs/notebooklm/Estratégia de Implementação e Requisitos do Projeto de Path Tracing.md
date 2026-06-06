O plano anterior **cobre todos os requisitos básicos**, mas **deliberadamente não cobre todos os pontos extras possíveis**. O enunciado do Projeto 2 (proj2.pdf) exige a implementação de 100% dos requisitos básicos (valendo 7.0 pontos) e a escolha de algumas extensões que somem **3.0 pontos** 1-3.  
O plano que elaborei cobriu todos os básicos e selecionou uma combinação de extras que já soma **6.0 pontos** (o dobro do exigido), garantindo uma implementação extremamente madura sem sobrecarregar com extensões redundantes para a avaliação.  
Aqui está o detalhamento de como o plano se alinha aos requisitos do proj2.pdf:

### 1\. Requisitos Básicos (100% Cobertos) \- 7.0 pontos

O plano garante a entrega total desta seção 1, 2:

* **Cena com esferas, caixas e/ou planos:** Já herdado da sua infraestrutura do Projeto 1 e mantido na Fase 0\.  
* **Iluminação por fontes retangulares:** Você já possui a AreaLight do Projeto 1, que foi integrada na Fase 3\.  
* **Materiais difusos (BRDF constante):** Coberto na **Fase 2** (Amostragem ponderada pelo cosseno para Lambert).  
* **Múltiplos caminhos por pixel:** Coberto na **Fase 1** (estrutura iterativa do TracePath interagindo com o Film herdado).  
* **Profundidade mínima de 4 vértices:** Coberto na **Fase 4** (A Roleta Russa só é ativada após depth \>= 3, forçando o caminho a ter o comprimento mínimo exigido).

### 2\. Extensões / Extras (6.0 pontos cobertos de 3.0 exigidos)

O enunciado pede que você escolha opções de uma lista para somar 3.0 pontos 2, 3\. O plano anterior sugeriu as seguintes:

* **Múltipla Amostragem por Importância (MIS) (1.0 pt):** Coberto na **Fase 3**.  
* **Roleta Russa (2.0 pts):** Coberto na **Fase 4**.  
* **Microfacetas / Objetos não difusos (1.0 pt):** Coberto na **Fase 5**.  
* **Objetos refratários (2.0 pts):** Coberto na **Fase 6** (Aproveitando sua física do Projeto 1 adaptada para gerar Delstas de Dirac no Monte Carlo).

### 3\. O que ficou de fora (Extras não cobertos)

Como a meta era criar o traçador de caminhos mais robusto e direto, deixei as seguintes opções de fora 3, 4:

* **Fonte de luz infinita / Environment Map (1.0 pt):** Não incluí para poupar a necessidade de carregar mapas HDRI e criar amostradores esféricos.  
* **Luz de área em malha de triângulos (1.0 pt):** Não incluí porque você já tem a luz de área retangular funcional e o MIS foi focado nela.  
* **Métodos Alternativos de Iluminação Global (Traçado Bidirecional ou Metrópolis) (3.0 pts cada):** O enunciado permite que você troque todos os pequenos extras por um desses integradores complexos 3, 4\. Não recomendei isso para o plano inicial porque alterar do Path Tracing unidirecional direto para Metrópolis Light Transport (MLT) ou Bidirectional Path Tracing exigiria uma refatoração massiva da sua arquitetura que levaria muito mais tempo do que as 3 semanas restantes.

**Em resumo:** O plano está estrategicamente superdimensionado para a nota máxima, focando nas adições que geram a maior qualidade visual (MIS e Microfacetas PBR) aliadas ao reuso do seu código (Refratários).  
Você gostaria que eu substituísse algum dos passos do plano (por exemplo, trocar as microfacetas pela implementação de **Luz Infinita** ou **Luzes Triangulares**)?  
