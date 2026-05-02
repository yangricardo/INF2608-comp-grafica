# Relatório Técnico-Científico: Traçador de Raios (Projeto 1)

## 1. Introdução

Este relatório documenta o desenvolvimento do traçador de raios implementado em `src/ray_tracing_2`, tomando como referência direta o enunciado em `proj1.pdf`, o arranjo de cena de `proj1-exemplo.pdf` e a progressão conceitual apresentada em `4.tracado_de_raios.pdf` e `5.tracado_de_raios2.pdf`.

O ponto central da implementação foi manter uma narrativa física coerente: primeiro construir o núcleo de um traçador local baseado em câmera pinhole, interseções geométricas, iluminação direta e sombras duras; depois estender esse núcleo com reflexão, refração, absorção volumétrica, fontes extensas e instanciação geométrica. Em termos de arquitetura, isso significa que o segundo conjunto de slides não substitui o primeiro. Ele reaproveita o pipeline inicial e o incrementa com novos fenômenos ópticos.

## 2. Evolução da Implementação: do Slide 4 ao Slide 5

### 2.1. Núcleo geométrico e fotométrico do Slide 4

#### 2.1.1. Câmera pinhole e formação dos raios primários

Referência teórica: `4.tracado_de_raios.pdf`, p. 14 e p. 25-29.

O primeiro bloco conceitual do projeto é a câmera pinhole. A cena é observada a partir de um ponto de vista `eye`, orientado por um alvo `center` e por um vetor `up`. A imagem final não é gerada diretamente no espaço 3D; ela nasce da projeção de cada amostra do pixel sobre uma janela de imagem situada a uma distância fixa do olho.

Essa formulação aparece em `camera.py`. A classe `Camera` calcula `inv_view` a partir de `glm.lookAt`, define a razão de aspecto e usa `fov_tan` para converter a amostra normalizada `(xn, yn)` em um ponto `p_cam` no plano de projeção. O método `generate_ray` constrói então o raio primário que sai de `self.eye` e atravessa esse ponto. Um detalhe importante para manutenção é que `focal_distance`, nesta implementação, representa apenas a distância geométrica até o plano da câmera no modelo pinhole. Não há lente fina nem profundidade de campo.

Em `film.py`, a discretização da imagem é tratada como uma aproximação numérica da integral da radiância sobre a área do pixel. `Film.get_samples_for_pixel` implementa dois esquemas: `jittered`, em que as amostras são aleatórias dentro do pixel, e `stratified`, em que o pixel é subdividido em subcélulas para reduzir variância. Essa escolha não altera a física da cena, mas altera a qualidade estatística da aproximação.

#### 2.1.2. Interseções geométricas e seleção do hit visível

Referência teórica: `4.tracado_de_raios.pdf`, p. 11-18, p. 35 e p. 47-48.

Uma vez gerado o raio primário, o problema central passa a ser determinar qual superfície ele atinge primeiro. A implementação segue a ideia de closest hit descrita nos slides: cada primitiva tenta atualizar um registro de interseção e, ao final, apenas a menor distância positiva permanece.

Em `shape.py`, a esfera resolve a interseção por meio da equação quadrática, escolhendo a primeira raiz positiva válida. O plano usa a forma analítica baseada em produto escalar entre a normal e a direção do raio. A caixa (`Box`) usa o método de slabs, isto é, a interseção sucessiva dos intervalos de entrada e saída em cada eixo cartesiano. Em `scene.py`, `Scene.compute_intersection` percorre a lista de objetos e retém apenas o hit mais próximo.

O arquivo `hit.py` concentra um detalhe que ganha importância apenas quando o Slide 5 entra em cena: além de `t`, posição e normal, o registro guarda `front_face` e `backfacing`. Essa informação codifica se o raio está entrando ou saindo do meio. No estágio básico do Slide 4, isso orienta a normal de sombreamento. No estágio avançado, essa mesma informação passa a controlar refração e absorção volumétrica.

#### 2.1.3. Iluminação direta com o modelo de Phong

Referência teórica: `4.tracado_de_raios.pdf`, p. 41-49 e `5.tracado_de_raios2.pdf`, p. 27.

O primeiro modelo de interação luz-matéria adotado foi o de Phong. Em termos físicos, ele ainda é um modelo local e simplificado, mas suficiente para representar três parcelas relevantes para o projeto: um termo ambiente residual, reflexão difusa dependente de `max(0, n . l)` e brilho especular dependente do alinhamento entre a direção de visão e a direção refletida.

Em `material.py`, `PhongMaterial.direct_lighting` calcula exatamente essa combinação. Para cada luz, o código obtém a radiância incidente `Li` e a direção `l`, soma a contribuição difusa `m_dif * Li * max(0, n . l)` e depois a contribuição especular `m_spe * Li * max(0, r . v)^shi`. A função `eval` de `PhongMaterial` devolve apenas essa iluminação direta. Esse ponto é estruturalmente importante: ele será reutilizado pelos materiais mais avançados como a parcela local da resposta óptica, em vez de ser descartado.

#### 2.1.4. Sombras duras e visibilidade direta da fonte

Referência teórica: `4.tracado_de_raios.pdf`, p. 40.

No núcleo do Slide 4, o problema da sombra é um problema de visibilidade entre o ponto sombreado e a fonte. A implementação segue essa lógica em `light.py` e `scene.py`. `PointLight.radiance` constrói o vetor da superfície até a luz, calcula a distância `dist` e consulta `Scene.transmittance`. Quando a cena é estritamente opaca, esse mecanismo se reduz à resposta binária esperada: ou a luz é visível, ou a contribuição é nula.

Há uma escolha importante de modelagem: a `PointLight` do projeto segue a convenção do enunciado, em que `Intensity` representa uma radiância constante da fonte, sem queda explícita por `1 / r^2` no próprio modelo da luz. Essa decisão foi mantida no código e documentada, porque difere da formulação física completa mais comum em cursos de computação gráfica.

### 2.2. Extensões do Slide 5 sobre o mesmo pipeline

#### 2.2.1. De traçador local para traçador recursivo

Referência teórica: `5.tracado_de_raios2.pdf`, p. 26-35.

O salto conceitual do segundo conjunto de slides não é reconstruir o renderizador do zero, mas permitir que o mesmo ponto de entrada `Scene.trace_ray` seja reutilizado por raios secundários. Em outras palavras, o raio primário continua chegando a um `hit`, e o material continua sendo responsável pela cor. A diferença é que agora certos materiais geram novos raios e pedem à cena uma nova avaliação.

Essa passagem está explícita em `scene.py`. `Scene.can_spawn_ray` impõe um limite finito de profundidade e controla o custo das cadeias de reflexão e refração. `Scene.trace_ray` permanece simples: encontra o hit e delega ao material. A recursividade não fica espalhada pela cena inteira; ela é encapsulada nos materiais que efetivamente precisam dela.

#### 2.2.2. Reflexão especular com Fresnel-Schlick

Referência teórica: `5.tracado_de_raios2.pdf`, p. 26-27.

`ReflectiveMaterial` implementa a extensão metálica do modelo local. A refletância não é constante: ela depende do ângulo de visão por meio da aproximação de Fresnel-Schlick,

$$
R(\theta, \lambda) = R_0(\lambda) + \left(1 - R_0(\lambda)\right) \left(1 - \cos\theta\right)^5.
$$

Em `material.py`, isso aparece no cálculo de `R` a partir de `self.reflectivity` e de `cos_theta = dot(v, n)`. O aspecto relevante é que a implementação não substitui Phong por reflexão pura. Ela reparte energia entre uma parcela local ponderada por `(1 - R)` e uma parcela recursiva ponderada por `R`. Assim, o Slide 5 preserva o comportamento básico do Slide 4 e apenas o complementa com dependência angular e raio refletido.

#### 2.2.3. Refração dielétrica, Snell, TIR e Beer-Lambert

Referência teórica: `5.tracado_de_raios2.pdf`, p. 29-34.

O material transparente é a extensão mais rica da arquitetura. Ele precisa decidir simultaneamente quanto da energia reflete, quanto refrata e quanto da parcela transmitida é absorvida ao percorrer o volume.

Em `material.py`, `TransparentMaterial.eval` encadeia três leis físicas:

1. Fresnel-Schlick para determinar a fração refletida.
2. Lei de Snell para determinar a direção refratada, via `glm.refract`.
3. Lei de Beer-Lambert para modelar a absorção ao longo da espessura atravessada.

O papel de `front_face` e `backfacing`, calculados em `hit.py`, torna-se essencial aqui. Quando o raio entra no objeto, a razão usada é `1 / ior`; quando sai, a razão passa a ser `ior / 1`. Essa troca é o equivalente discreto da mudança de meio ar -> vidro e vidro -> ar. Se `glm.refract` retorna o vetor nulo, a implementação reconhece implicitamente o caso de reflexão interna total.

Além disso, a atenuação `I = a^s` é aplicada com significados distintos em dois contextos diferentes:

1. Em `TransparentMaterial.eval`, a absorção atua sobre o raio refratado recursivo, modelando o percurso dentro do volume.
2. Em `TransparentMaterial.shadow_transmittance`, a mesma lei é usada para raios de sombra, de modo que uma fonte parcialmente visível através de um dielétrico não seja tratada como totalmente bloqueada.

#### 2.2.4. De sombra binária para transmitância acumulada

Referência teórica: `5.tracado_de_raios2.pdf`, p. 35.

Em um traçador estritamente opaco, a pergunta feita por um raio de sombra é binária. O Slide 5 refina isso: se o caminho até a fonte cruza meios transparentes, a energia deve ser atenuada progressivamente e não simplesmente anulada.

Essa transição está centralizada em `Scene.transmittance`, em `scene.py`. O método reutiliza `compute_intersection`, mas agora percorre vários hits sucessivos enquanto o caminho até a fonte não estiver totalmente bloqueado. Em cada interface transparente, ele consulta `shadow_transmittance`, atualiza o throughput acumulado e avança a origem do raio. Do ponto de vista conceitual, esta é uma das extensões mais importantes do projeto, porque ela transforma o antigo teste de visibilidade em uma estimativa de transmitância ao longo de um segmento.

Outro detalhe importante é `Scene.offset_point`. O deslocamento por `ray_epsilon` ao longo da normal evita auto-interseção em sombra, reflexão e refração. Sem essa separação numérica, o próprio objeto recém-intersectado poderia bloquear artificialmente o próximo raio, produzindo os artefatos conhecidos como `shadow acne`.

#### 2.2.5. Luz de área e penumbra

Referência teórica: `5.tracado_de_raios2.pdf`, p. 35.

Enquanto a `PointLight` representa uma fonte pontual idealizada, `AreaLight` representa uma fonte extensa retangular. A implementação em `light.py` aproxima a integral sobre a área emissiva por uma soma discreta de amostras distribuídas em uma malha `samples_u x samples_v`. Cada amostra gera uma direção levemente diferente até o ponto sombreado; por isso, regiões parcialmente ocluídas recebem apenas uma fração das contribuições e formam penumbra.

Diferentemente da `PointLight` adotada por convenção do enunciado, a `AreaLight` reparte a potência entre as subamostras e aplica queda com `1 / r^2`, o que aproxima melhor a distribuição geométrica de energia de uma fonte extensa.

#### 2.2.6. Instanciação geométrica e transformação correta de normais

Referência teórica: slides de instanciação e `5.tracado_de_raios2.pdf`, p. 12-13.

A classe `Instance`, em `shape.py`, evita duplicação da matemática de interseção. A estratégia é transformar o raio do espaço do mundo para o espaço local do objeto, resolver a interseção com a primitiva original e então transformar o ponto e a normal de volta. O ponto usa a matriz direta, mas a normal usa a inversa transposta. Essa distinção é indispensável quando há escala não uniforme, porque a normal precisa preservar perpendicularidade em relação à superfície transformada.

Essa solução permite reutilizar esfera, plano e caixa como blocos básicos para cenas mais complexas, como as montadas em `main_box.py` e `main_ellipse.py`.

## 3. Análise Experimental com Screenshots

Esta seção organiza os experimentos de modo compatível com a narrativa anterior. Em vez de apresentar apenas imagens soltas, cada renderização foi escolhida para evidenciar uma etapa distinta da evolução do traçador.

### 3.1. Cena-base do Slide 4: esfera, plano e sombra dura

Arquivo de referência: `src/ray_tracing_2/main.py`.

Na cena-base, uma esfera vermelha repousa sobre um plano e é iluminada por uma luz pontual. A imagem abaixo evidencia exatamente os fenômenos esperados do estágio inicial do projeto: projeção pinhole, interseção correta entre esfera e plano, parcela difusa dominante, highlight especular localizado e uma sombra dura coerente com a geometria da fonte pontual.

![Cena-base com PointLight](../outputs/main_scene_20260405_190325/render.png)

O valor experimental dessa imagem é que ela valida o núcleo do renderizador sem depender ainda de recursão. Se a câmera, a interseção, a orientação da normal ou o cálculo local de Phong estiverem incorretos, o erro costuma aparecer imediatamente nessa configuração mínima.

### 3.2. Extensão para fonte extensa: penumbra e integração espacial

Arquivo de referência: `src/ray_tracing_2/main_area_light.py`.

Ao substituir a luz pontual por uma luz de área retangular, a região de sombra deixa de apresentar uma transição abrupta. A imagem seguinte mostra exatamente essa mudança: o contorno escuro sob a esfera torna-se progressivo, porque diferentes subamostras da fonte permanecem visíveis ou ocultas dependendo da posição no plano.

![Penumbra com AreaLight](../outputs/main_area_light_20260405_204336/render.png)

Esse resultado confirma a implementação de `AreaLight.sample_radiance` como aproximação discreta da integral sobre uma fonte extensa. Também evidencia que o modelo de visibilidade já não é puramente binário quando a fonte tem área mensurável.

### 3.3. Cena Cornell-like: geometria instanciada e infraestrutura para ótica avançada

Arquivo de referência: `src/ray_tracing_2/main_box.py`.

Na cena inspirada na Cornell Box, o objetivo experimental muda. O foco deixa de ser apenas a interação de uma esfera com um plano e passa a incluir paredes coloridas, múltiplas superfícies, blocos instanciados e um arranjo geométrico fechado. A imagem abaixo mostra a validade geométrica desse arranjo: paredes laterais com materiais distintos, dois blocos internos e enquadramento frontal coerente com o enunciado.

![Cena Cornell-like](../outputs/main_box_20260412_162658/render.png)

Mesmo quando renderizada em uma configuração visual mais simples, essa cena é importante porque ela concentra os mecanismos que tornam viáveis as extensões do Slide 5: controle de profundidade recursiva, correção de normais transformadas, organização de materiais opacos, reflectivos e transparentes, e tratamento robusto de `ray_epsilon` em superfícies muito próximas.

## 4. Evidência Orientada por Requisitos do Enunciado

Esta seção complementa a análise técnica anterior com cenas produzidas especificamente para atender 1:1 aos requisitos do enunciado (`materiais/proj1.pdf`). A câmera é a mesma em todos os experimentos (eye=(2.775,3.2,12.775), center=(2.775,2.775,2.775), fov=50°), variando apenas objetos, materiais e luzes.

### 4.1. R1: Instanciação de esferas e caixas

Módulo: `src/ray_tracing_2/proj1_req1_geometry.py`

Sala Cornell com dois `Instance(Box)` rotacionados e uma `Sphere`. Iluminação exclusivamente por `AmbientLight` para evidenciar geometria sem dependência de fontes pontuais.

```bash
python -m ray_tracing_2.proj1_req1_geometry --width 800 --height 600 --spp 1
```

![R1 geometry](../outputs/proj1_req1_geometry_20260502_121509/render.png)

_800×600, spp=1, center, ~9.4 s._

### 4.2. R2: Uma ou mais fontes de luz pontuais

Módulo: `src/ray_tracing_2/proj1_req2_point_lights.py`

Três `PointLight` (key/fill/back) com posições e potências distintas; duas esferas Phong com `shininess` 20 e 96 para observar variação de highlight por material.

```bash
python -m ray_tracing_2.proj1_req2_point_lights --width 800 --height 600 --spp 1
```

![R2 point lights](../outputs/proj1_req2_point_lights_20260502_121731/render.png)

_800×600, spp=1, center, ~19.7 s._

### 4.3. R3: Iluminação direta com modelo de Phong e sombras duras

Módulo: `src/ray_tracing_2/proj1_req3_phong_shadows.py`

Dois materiais contrastantes: matte vermelho (`shininess=16`) e glossy azul (`shininess=120`, `specular=0.60`). Sombras duras via `Scene.transmittance()` com dois `PointLight` posicionados para gerar oclusão visível.

```bash
python -m ray_tracing_2.proj1_req3_phong_shadows --width 800 --height 600 --spp 1
```

![R3 Phong shadows](../outputs/proj1_req3_phong_shadows_20260502_121809/render.png)

_800×600, spp=1, center, ~20.1 s._

### 4.4. R4: Múltiplas amostras por pixel

Módulo: `src/ray_tracing_2/proj1_req4_sampling.py`

Geometria com arestas finas (caixa delgada) e esferas branca/preta para tornar aliasing visível. Comparar `center` (baseline) com `jittered`/`stratified` no mesmo enquadramento.

```bash
# baseline
python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 1 --sampling_mode center
# anti-aliasing
python -m ray_tracing_2.proj1_req4_sampling --width 800 --height 600 --spp 4 --sampling_mode jittered --seed 42
```

![R4 sampling baseline](../outputs/proj1_req4_sampling_20260502_122009/render.png)

_800×600, spp=1, center, ~20.7 s. Executar spp=4 para comparar AA._

### 4.5. Matriz de aderência

| Requisito                    | Status | Módulo                        |
| ---------------------------- | ------ | ----------------------------- |
| R1: esferas e caixas         | OK     | `proj1_req1_geometry.py`      |
| R2: luz pontual              | OK     | `proj1_req2_point_lights.py`  |
| R3: Phong + sombras          | OK     | `proj1_req3_phong_shadows.py` |
| R4: multiplas amostras/pixel | OK     | `proj1_req4_sampling.py`      |

---

## 5. Critérios Atendidos e Não Atendidos Integralmente

### 4.1. Critérios atendidos no escopo do projeto

- [x] Câmera pinhole com geração de raios primários a partir de amostras do pixel.
- [x] Interseção com primitivas básicas relevantes para o projeto: esfera, plano e caixa.
- [x] Seleção de interseção visível por closest hit.
- [x] Iluminação local no modelo de Phong com componentes ambiente, difusa e especular.
- [x] Sombreamento por visibilidade da fonte e suporte a sombras translúcidas.
- [x] Reflexão recursiva com ponderação angular por Fresnel-Schlick.
- [x] Refração dielétrica com Lei de Snell, detecção de reflexão interna total e absorção Beer-Lambert.
- [x] Luz de área com amostragem múltipla e formação de penumbra.
- [x] Instanciação geométrica por transformação de raio e correção de normais com inversa transposta.
- [x] Anti-aliasing por amostragem `jittered` e `stratified`.
- [x] Relatório com descrição técnica, análise experimental e screenshots de diferentes arranjos.

### 4.2. Itens não atendidos integralmente ou mantidos fora do escopo

- [ ] Iluminação global difusa completa ou múltiplos bounces estocásticos no sentido de path tracing. O projeto permanece centrado em iluminação direta mais raios secundários determinísticos de reflexão e refração.
- [ ] Modelo de câmera com lente fina e profundidade de campo. A câmera implementada é estritamente pinhole.
- [ ] Estruturas de aceleração como BVH ou kd-tree. A busca por interseções ainda é linear em `Scene.compute_intersection`.
- [ ] Calibração radiométrica estrita entre todas as fontes. O projeto preserva a convenção do enunciado para `PointLight`, mesmo quando ela não coincide com um modelo físico completo de queda por distância.

## 5. Conclusão

O resultado final mostra uma implementação coerente com a progressão didática dos materiais de referência. O Slide 4 fornece a espinha dorsal do traçador: câmera, amostragem, interseção, visibilidade e sombreamento local. O Slide 5 não rompe essa estrutura; ele a estende com recursão, fenômenos de interface e fontes extensas. Essa continuidade aparece de forma clara no código: `Scene.trace_ray` continua simples, `PhongMaterial` continua sendo a base local, e os materiais e luzes mais avançados apenas acrescentam novos mecanismos físicos sobre esse mesmo alicerce.

Do ponto de vista técnico-científico, a implementação é bem-sucedida porque cada novo efeito visual importante pode ser rastreado até uma escolha matemática explícita no código: Fresnel-Schlick para reflexão angular, Snell para desvio do raio transmitido, Beer-Lambert para absorção no volume, amostragem espacial para penumbra e inversa transposta para normais transformadas. Essa rastreabilidade entre teoria, implementação e imagem renderizada é precisamente o que caracteriza a maturidade do projeto entregue.
