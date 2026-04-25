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

Em `film.py`, a discretização da imagem é tratada como uma aproximação numérica da integral da radiância sobre a área do pixel. `Film.get_samples_for_pixel` implementa dois esquemas de anti-aliasing:

- **Jittered:** $N$ amostras independentes e uniformemente aleatórias dentro do pixel. Simples de gerar, mas permite que amostras se concentrem casualmente na mesma sub-região, aumentando a variância local do estimador.
- **Stratified:** o pixel é subdividido em uma grade $G \times G$ de subcélulas (com $G = \lceil\sqrt{N}\rceil$) e cada subcélula contribui com exatamente uma amostra com jitter interno. Essa cobertura espacial mínima garante que todo o pixel seja representado, reduzindo a variância em comparação ao jitter puro ao custo de um laço aninhado e de impor uma estrutura de grade.

Essa escolha não altera a física da cena nem o modelo de câmera; ela altera apenas a qualidade estatística da estimativa da cor do pixel. Em cenas com gradientes de cor lentos, a diferença é imperceptível. Em bordas de objetos ou em penumbra suave, o `stratified` reduz o ruído perceptível para o mesmo número de amostras.

#### 2.1.2. Interseções geométricas e seleção do hit visível

Referência teórica: `4.tracado_de_raios.pdf`, p. 11-18, p. 35 e p. 47-48.

Uma vez gerado o raio primário, o problema central passa a ser determinar qual superfície ele atinge primeiro. A implementação segue a ideia de closest hit descrita nos slides: cada primitiva tenta atualizar um registro de interseção e, ao final, apenas a menor distância positiva permanece.

**Esfera.** Para um raio $\mathbf{r}(t) = \mathbf{o} + t\,\mathbf{d}$ e uma esfera centrada em $\mathbf{c}$ com raio $r$, substitui-se na equação $\|\mathbf{r}(t) - \mathbf{c}\|^2 = r^2$ e obtém-se a forma quadrática

$$
a\,t^2 + b\,t + c = 0, \quad a = \mathbf{d}\cdot\mathbf{d},\quad b = 2\,\mathbf{d}\cdot(\mathbf{o}-\mathbf{c}),\quad c = (\mathbf{o}-\mathbf{c})\cdot(\mathbf{o}-\mathbf{c}) - r^2.
$$

Se $\Delta = b^2 - 4ac < 0$, o raio não atinge a esfera. Caso contrário, as raízes são $t_{1,2} = (-b \mp \sqrt{\Delta})/(2a)$ e a implementação em `shape.py` escolhe a menor raiz positiva válida, com limiar $t > 0{,}001$ para evitar auto-interseção.

**Plano.** Para um plano definido por um ponto $\mathbf{p}_0$ e uma normal unitária $\hat{\mathbf{n}}$, a condição $(\mathbf{r}(t) - \mathbf{p}_0)\cdot\hat{\mathbf{n}} = 0$ resolve-se diretamente em

$$
t = \frac{(\mathbf{p}_0 - \mathbf{o})\cdot\hat{\mathbf{n}}}{\mathbf{d}\cdot\hat{\mathbf{n}}}.
$$

O denominador $\mathbf{d}\cdot\hat{\mathbf{n}}$ deve ser não-nulo; caso contrário, o raio é paralelo ao plano e não há interseção.

**Caixa por slabs.** Uma caixa alinhada aos eixos é a interseção de três pares de planos. Para cada eixo $k$, calculam-se os tempos de entrada $t_{k,\text{near}}$ e saída $t_{k,\text{far}}$. O intervalo de interseção válido é então

$$
t_{\text{near}} = \max_k(t_{k,\text{near}}), \qquad t_{\text{far}} = \min_k(t_{k,\text{far}}).
$$

Se $t_{\text{near}} > t_{\text{far}}$, o raio não intersecta a caixa. A normal da face atingida é determinada pelo eixo que produziu o maior $t_{k,\text{near}}$.

Em `scene.py`, `Scene.compute_intersection` percorre a lista de objetos e retém apenas o hit mais próximo. O limiar inferior $t > 0{,}001$ (igual ao `ray_epsilon` de `Scene`) tem um papel numérico importante: ele evita que o ponto recém-calculado se "auto-intersecte" com a própria superfície por erros de ponto flutuante — um artefato conhecido como _shadow acne_ que seria visível como pontos negros na imagem.

O arquivo `hit.py` concentra um detalhe que ganha importância apenas quando o Slide 5 entra em cena: além de `t`, posição e normal, o registro guarda `front_face` e `backfacing`. Essa informação codifica se o raio está entrando ou saindo do meio. No estágio básico do Slide 4, isso orienta a normal de sombreamento. No estágio avançado, essa mesma informação passa a controlar refração e absorção volumétrica.

#### 2.1.3. Iluminação direta com o modelo de Phong

Referência teórica: `4.tracado_de_raios.pdf`, p. 41-49 e `5.tracado_de_raios2.pdf`, p. 27.

O primeiro modelo de interação luz-matéria adotado foi o de Phong. Em termos físicos, ele ainda é um modelo local e simplificado, mas suficiente para representar três parcelas relevantes para o projeto: um termo ambiente residual, reflexão difusa dependente de `max(0, n . l)` e brilho especular dependente do alinhamento entre a direção de visão e a direção refletida.

Em `material.py`, `PhongMaterial.direct_lighting` calcula exatamente essa combinação. Para cada luz, o código obtém a radiância incidente `Li` e a direção `l`, soma a contribuição difusa `m_dif * Li * max(0, n . l)` e depois a contribuição especular `m_spe * Li * max(0, r . v)^shi`. A função `eval` de `PhongMaterial` devolve apenas essa iluminação direta. Esse ponto é estruturalmente importante: ele será reutilizado pelos materiais mais avançados como a parcela local da resposta óptica, em vez de ser descartado.

#### 2.1.4. Sombras duras e visibilidade direta da fonte

Referência teórica: `4.tracado_de_raios.pdf`, p. 40.

No núcleo do Slide 4, o problema da sombra é um problema de visibilidade entre o ponto sombreado e a fonte. A implementação segue essa lógica em `light.py` e `scene.py`. `PointLight.radiance` constrói o vetor da superfície até a luz, calcula a distância `dist` e consulta `Scene.transmittance`. Quando a cena é estritamente opaca, esse mecanismo se reduz à resposta binária esperada: ou a luz é visível, ou a contribuição é nula.

Há uma escolha importante de modelagem: a `PointLight` do projeto segue a convenção do enunciado, em que `Intensity` representa uma radiância constante da fonte, sem queda explícita por $1/r^2$ no próprio modelo da luz. Essa decisão foi mantida no código e documentada, porque difere da formulação física completa mais comum em cursos de computação gráfica.

Uma segunda decisão de engenharia que impacta sombras, reflexão e refração é o parâmetro `ray_epsilon = 0.001` em `Scene`. Quando um raio de sombra é disparado a partir do ponto de interseção, o ponto de origem está, por definição, sobre a superfície do objeto. Erros de arredondamento em ponto flutuante fazem com que esse ponto possa estar ligeiramente abaixo ou acima da superfície na representação numérica. Sem um deslocamento mínimo, o próprio objeto seria o primeiro hit do raio de sombra, reportando uma falsa oclusão — o que produz manchas escuras aleatórias na imagem. A função `Scene.offset_point` resolve isso ao mover a origem do novo raio por `ray_epsilon` ao longo da normal antes de enviar qualquer raio secundário. O valor `0.001` é suficientemente grande para absorver erros de ponto flutuante em coordenadas da ordem de unidade e suficientemente pequeno para não deslocar o ponto perceptivelmente.

### 2.2. Extensões do Slide 5 sobre o mesmo pipeline

#### 2.2.1. De traçador local para traçador recursivo

Referência teórica: `5.tracado_de_raios2.pdf`, p. 26-35.

O salto conceitual do segundo conjunto de slides não é reconstruir o renderizador do zero, mas permitir que o mesmo ponto de entrada `Scene.trace_ray` seja reutilizado por raios secundários. Em outras palavras, o raio primário continua chegando a um `hit`, e o material continua sendo responsável pela cor. A diferença é que agora certos materiais geram novos raios e pedem à cena uma nova avaliação.

Essa passagem está explícita em `scene.py`. `Scene.can_spawn_ray` impõe um limite finito de profundidade `max_depth` e controla o custo das cadeias de reflexão e refração. A justificativa física é que cada salto multiplica a energia pelo coeficiente de refletância ou transmitância correspondente — valores que, na prática, são sempre menores que 1 para materiais físicos. A contribuição de um raio de profundidade $k$ é ponderada por um produto de refletâncias $R_1 \cdot R_2 \cdots R_k$, que converge para zero rapidamente. Por isso, truncar a recursão a `max_depth = 4` (padrão em `Scene`) elimina contribuições que seriam numericamente desprezíveis, sem impacto visual significativo. Do ponto de vista de custo, o número de raios por pixel cresce como $O(2^k)$ no pior caso (cada superfície gera reflexão e refração), de modo que limitar $k$ é indispensável para manter o tempo de renderização controlado. `Scene.trace_ray` permanece simples: encontra o hit e delega ao material. A recursividade não fica espalhada pela cena inteira; ela é encapsulada nos materiais que efetivamente precisam dela.

#### 2.2.2. Reflexão especular com Fresnel-Schlick

Referência teórica: `5.tracado_de_raios2.pdf`, p. 26-27.

`ReflectiveMaterial` implementa a extensão metálica do modelo local. A refletância não é constante: ela depende do ângulo de visão por meio da aproximação de Fresnel-Schlick,

$$
R(\theta, \lambda) = R_0(\lambda) + \left(1 - R_0(\lambda)\right) \left(1 - \cos\theta\right)^5.
$$

Em `material.py`, isso aparece no cálculo de `R` a partir de `self.reflectivity` e de `cos_theta = dot(v, n)`. O aspecto relevante é que a implementação não substitui Phong por reflexão pura. Ela reparte energia entre uma parcela local ponderada por $(1 - R)$ e uma parcela recursiva ponderada por $R$:

$$
c = (1 - R(\theta))\,\cdot\,\text{PhongDireto} + R(\theta)\,\cdot\,\text{TraceRay}(\hat{r}).
$$

Esse rateio é uma aproximação fisicamente plausível para metais: quando o ângulo $\theta$ aumenta (visão rasante), $R(\theta) \to 1$ e o brilho especular do Phong é suprimido em favor da reflexão pura. Notar, porém, que a soma $(1-R)\,\text{Phong} + R\,\text{Reflexão}$ não é uma conservação de energia estrita, porque o termo de Phong por si só já pode exceder o fluxo incidente em configurações de brilho alto. É uma aproximação amplamente usada em traçadores não-physically-based e adequada ao escopo deste projeto. Assim, o Slide 5 preserva o comportamento básico do Slide 4 e apenas o complementa com dependência angular e raio refletido.

#### 2.2.3. Refração dielétrica, Snell, TIR e Beer-Lambert

Referência teórica: `5.tracado_de_raios2.pdf`, p. 29-34.

O material transparente é a extensão mais rica da arquitetura. Ele precisa decidir simultaneamente quanto da energia reflete, quanto refrata e quanto da parcela transmitida é absorvida ao percorrer o volume.

Em `material.py`, `TransparentMaterial.eval` encadeia quatro decisões físicas distintas:

**1. Fresnel-Schlick — fração refletida.**
A refletância basal $R_0 = \left(\frac{\eta-1}{\eta+1}\right)^2$ é calculada a partir do índice de refração `ior` e usada para estimar a fração que reflete em função do ângulo:

$$
R(\theta) = R_0 + (1 - R_0)(1 - \cos\theta)^5.
$$

**2. Lei de Snell — direção refratada.**
A direção do raio transmitido é obtida via `glm.refract(incident, n, ratio)`, onde `ratio = 1/η` ao entrar no material ($\eta_i = 1$, $\eta_t = \eta$) e `ratio = η/1` ao sair ($\eta_i = \eta$, $\eta_t = 1$). A função implementa numericamente a lei de Snell $\eta_i \sin\theta_i = \eta_t \sin\theta_t$.

**3. Reflexão interna total (TIR).**
Quando o ângulo de incidência interno supera o ângulo crítico $\theta_c = \arcsin(1/\eta)$, não existe raio refratado. `glm.refract` retorna o vetor nulo nesse caso. A implementação detecta isso pela condição `dot(refracted, refracted) < 0.5` e omite o raio transmitido, restando apenas a componente refletida.

**4. Lei de Beer-Lambert — absorção volumétrica.**
A atenuação ao longo da espessura percorrida é calculada como

$$
I(\lambda) = I_0(\lambda)\cdot a(\lambda)^{s},
$$

onde $a(\lambda)$ é a constante de atenuação por canal de cor (`attenuation`) e $s$ é a distância percorrida dentro do volume. Em `eval`, $s = \|\mathbf{o} - \mathbf{p}\|$ é a distância do ponto de origem do raio refratado até a face de saída do objeto. Em `shadow_transmittance`, $s = \texttt{hit.t}$ é a espessura que o raio de sombra percorreu dentro do material. O papel de `front_face` e `backfacing`, calculados em `hit.py`, é justamente distinguir quando o raio está entrando (sem absorção ainda) de quando está saindo (absorção acumulada pela espessura).

Quando $\mathbf{glm.refract}$ retorna um vetor não-nulo, o raio transmitido é disparado recursivamente com $c \mathrel{+}= (1-R)\,\cdot\,\text{TraceRay}(\hat{r}_t)$, e o resultado final é $I \cdot c$.

#### 2.2.4. De sombra binária para transmitância acumulada

Referência teórica: `5.tracado_de_raios2.pdf`, p. 35.

Em um traçador estritamente opaco, a pergunta feita por um raio de sombra é binária. O Slide 5 refina isso: se o caminho até a fonte cruza meios transparentes, a energia deve ser atenuada progressivamente e não simplesmente anulada.

Essa transição está centralizada em `Scene.transmittance`, em `scene.py`. O método reutiliza `compute_intersection`, mas agora percorre vários hits sucessivos enquanto o caminho até a fonte não estiver totalmente bloqueado. Em cada interface transparente, ele consulta `shadow_transmittance`, atualiza o throughput acumulado e avança a origem do raio. O loop tem três condições distintas de parada:

1. **Nenhum hit encontrado, ou hit além da fonte:** o raio de sombra chegou à luz sem ser bloqueado — retorna o `throughput` acumulado até aqui.
2. **Material opaco:** `shadow_transmittance` retorna `vec3(0)` e o throughput cai a zero — retorna bloqueio total.
3. **Throughput colapsa:** se o produto acumulado de atenuações fica abaixo de $10^{-4}$ (verificado via `dot(throughput, throughput) ≤ 1e-8`), o raio é tratado como extinto numericamente.

O parâmetro `max_steps = 16` limita o número de iterações para evitar loops infindáveis em cenas com muitos objetos sobrepostos. O `remaining` é decrementado a cada passo para impedir que objetos além da posição da fonte sejam consultados desnecessariamente. Do ponto de vista conceitual, esta é uma das extensões mais importantes do projeto, porque ela transforma o antigo teste binário de visibilidade em uma estimativa iterativa de transmitância ao longo de um segmento.

Outro detalhe importante é `Scene.offset_point`. O deslocamento por `ray_epsilon` ao longo da normal evita auto-interseção em sombra, reflexão e refração. Sem essa separação numérica, o próprio objeto recém-intersectado poderia bloquear artificialmente o próximo raio, produzindo os artefatos conhecidos como _shadow acne_.

#### 2.2.5. Luz de área e penumbra

Referência teórica: `5.tracado_de_raios2.pdf`, p. 35.

Enquanto a `PointLight` representa uma fonte pontual idealizada, `AreaLight` representa uma fonte extensa retangular. A aproximação discreta implementada em `light.py` pode ser vista como uma quadratura Monte Carlo da integral

$$
L_i = \int_{A} f(\mathbf{p}, \hat{\mathbf{l}}(\mathbf{q}))\,\frac{\cos\theta_s\,\cos\theta_r}{r^2}\,dA(\mathbf{q}),
$$

em que $\mathbf{q}$ varia sobre a área emissiva. A implementação substitui essa integral por uma soma sobre uma malha regular `samples_u × samples_v` de pontos uniformemente espaçados na superfície da fonte:

$$
L_i \approx \frac{1}{N}\sum_{k=1}^{N} f(\mathbf{p}, \hat{\mathbf{l}}_k)\,\frac{\text{intensity}}{r_k^2},
$$

onde $N = \text{samples\_u} \times \text{samples\_v}$ e $r_k$ é a distância do ponto sombreado à $k$-ésima amostra. Cada amostra gera uma direção levemente diferente até o ponto sombreado; por isso, regiões parcialmente ocluídas recebem apenas uma fração das contribuições e formam penumbra. A nitidez da penumbra é diretamente proporcional ao número de amostras: poucas amostras produzem penumbra granulada; muitas amostras suavizam a transição. Diferentemente da `PointLight` adotada por convenção do enunciado, a `AreaLight` aplica queda com $1/r^2$, o que aproxima melhor a distribuição geométrica de energia de uma fonte extensa.

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

É importante notar o que esta cena demonstra e o que ela não demonstra diretamente. Em sua configuração padrão, `main_box.py` atribui `PhongMaterial` aos dois blocos internos, tornando-os opacos. Por isso, a imagem acima é evidência experimental de: câmera pinhole com enquadramento correto, interseção de múltiplas caixas instanciadas via `Instance` com normais corretamente transformadas pela inversa transposta, materiais difusos com cores distintas por objeto, e robustez do `ray_epsilon` em um arranjo com superfícies muito próximas.

Ela **não** comprova diretamente reflexão ou refração recursiva nos blocos, pois os materiais padrão não as ativam. A evidência óptica avançada — reflexão com Fresnel-Schlick e refração com Beer-Lambert — pode ser obtida substituindo os materiais dos blocos por `ReflectiveMaterial` ou `TransparentMaterial` na mesma cena, ou observando a cena carregada via `src/ray_tracing_2/cornell_box.py`, que usa esses materiais por definição. A importância desta cena para o projeto é, portanto, infraestrutural: ela valida que todos os mecanismos de suporte às extensões do Slide 5 estão corretamente montados.

### 3.4. Geometria triangulada: malha JSON com BVH

Arquivo de referência: `src/ray_tracing_2/main_triangles.py`.

Para atender ao requisito de geometria representada por triângulos, a implementação adiciona uma especificação JSON simples carregada como cena e convertida em uma coleção de triângulos. A versão atual da cena ativa uma BVH sobre a malha triangulada via `accelerator: "bvh"`, e o executável ainda aceita o override `--accelerator linear` quando se quer comparar o caminho sem aceleração. A cena foi ajustada para usar dois materiais Phong distintos, vermelho e azul, além do plano cinza, porque a versão anterior ficava visualmente lavada e a sombra não aparecia com clareza suficiente. Isso não indicava falha no caminho de sombras: o problema era a encenação da cena, com luz muito central e ambiente alto. A versão final reposiciona a esfera para que ela projete uma sombra visível sobre a própria malha triangulada e adiciona uma segunda luz no lado oposto para equilibrar a iluminação. A figura abaixo mostra uma pequena pirâmide triangulada, descrita em `inputs/triangle_pyramid.json` e renderizada com a mesma infraestrutura de câmera, luz, materiais e aceleração usada nas demais cenas.

Do ponto de vista matemático, a BVH não altera a interseção do triângulo em si: o teste local continua sendo o Möller-Trumbore do Slide 4, p. 35 e p. 47-48, enquanto a instância da malha continua dependendo da transformação inversa transposta discutida no Slide 5, p. 12-13. O que a BVH acrescenta é apenas uma camada de poda baseada em AABB para reduzir quantas faces chegam ao teste exato.

![Malha triangulada com BVH](../outputs/main_triangles_20260424_233034/render.png)

O valor dessa cena é estritamente geométrico: ela valida a interseção raio-triângulo, a triangulação de faces poligonais no carregador e a compatibilidade da nova malha com o pipeline existente de `Scene`, `Hit` e `Instance`. O arquivo `properties.md` gerado para essa renderização registra 5 vértices e 6 triângulos, além de expor o uso da BVH com `bvh_node_count`, `bvh_leaf_count` e `bvh_max_depth`, o que facilita a conferência da malha carregada. As anotações no código indicam as páginas dos slides usadas como base para câmera, Phong, interseções, instanciação e o raciocínio de sombra.

## 4. Critérios, Extensões e Limitações

### 4.1. Requisitos básicos atendidos

- [x] Câmera pinhole com geração de raios primários a partir de amostras do pixel.
- [x] Cena com esferas e caixas instanciadas.
- [x] Uma ou mais luzes pontuais.
- [x] Iluminação direta com modelo de Phong e geração de sombras.
- [x] Múltiplas amostras por pixel com distribuição uniforme.
- [x] Relatório técnico-científico com descrição das técnicas adotadas e screenshots das cenas renderizadas.

### 4.2. Extensões opcionais implementadas

- [x] Transformações de modelagem na instanciação geométrica, com `Translate`, `Rotate` e `Instance`.
- [x] Luz de área retangular com amostragem discreta e formação de penumbra.
- [x] Geometria representada por triângulos, com interseção raio-triângulo e carregamento de malha via JSON/OBJ.
- [x] Estrutura espacial de aceleração por BVH na malha triangulada, configurável por JSON ou linha de comando.
- [x] Objetos reflexivos com ponderação angular por Fresnel-Schlick.
- [x] Objetos refratários com Lei de Snell, reflexão interna total, absorção Beer-Lambert e sombras translúcidas.

### 4.3. Extensões opcionais não implementadas

- [ ] Comparação de diferentes distribuições de amostras na fonte retangular.

### 4.4. Lacunas da BVH

A BVH adicionada para a malha triangulada é intencionalmente conservadora e ainda não cobre o conjunto completo de técnicas que aparecem na literatura de aceleração espacial. Ela preserva a matemática dos slides para a interseção exata e para a instanciação, mas ainda deixa as seguintes lacunas de implementação:

- [ ] O particionamento usa mediana no eixo dominante; ainda não há SAH nem split espacial.
- [ ] A estrutura é estática e não faz refit ou rebuild incremental para malhas deformáveis.
- [ ] A aceleração está restrita à malha triangulada da cena de demonstração, não ao `Scene.compute_intersection` inteiro.
- [ ] Ainda não há benchmark comparando baseline linear e BVH com métricas de tempo ou número de testes de triângulo.
- [ ] A malha ainda não expõe normais de vértice, UVs ou materiais por face.

### 4.5. Limitações adicionais e trabalhos futuros

- [ ] Câmera com lente fina e profundidade de campo. A câmera implementada é estritamente pinhole.
- [ ] Calibração radiométrica estrita entre todas as fontes. O projeto preserva a convenção do enunciado para `PointLight` e mantém a `AreaLight` com queda por $1/r^2$.
- [ ] Renderização global estocástica, como `path tracing`, como possível extensão futura fora da rubrica atual.

## 5. Conclusão

O resultado final mostra uma implementação coerente com a progressão didática dos materiais de referência. O Slide 4 fornece a espinha dorsal do traçador: câmera, amostragem, interseção, visibilidade e sombreamento local. O Slide 5 não rompe essa estrutura; ele a estende com recursão, fenômenos de interface e fontes extensas. Essa continuidade aparece de forma clara no código: `Scene.trace_ray` continua simples, `PhongMaterial` continua sendo a base local, e os materiais e luzes mais avançados apenas acrescentam novos mecanismos físicos sobre esse mesmo alicerce.

Do ponto de vista técnico-científico, a implementação é bem-sucedida porque cada novo efeito visual importante pode ser rastreado até uma escolha matemática explícita no código: Fresnel-Schlick para reflexão angular, Snell para desvio do raio transmitido, Beer-Lambert para absorção no volume, amostragem espacial para penumbra e inversa transposta para normais transformadas. Essa rastreabilidade entre teoria, implementação e imagem renderizada é precisamente o que caracteriza a maturidade do projeto entregue.
