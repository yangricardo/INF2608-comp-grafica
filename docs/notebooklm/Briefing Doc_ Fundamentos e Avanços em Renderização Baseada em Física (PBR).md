### Briefing Doc: Fundamentos e Avanços em Renderização Baseada em Física (PBR)

#### Sumário Executivo

Este documento sintetiza os princípios fundamentais e as inovações contemporâneas na computação gráfica, com foco em Renderização Baseada em Física (PBR). A renderização evoluiu de algoritmos locais simples para simulações complexas que utilizam o transporte de luz global, integrando métodos estatísticos como Monte Carlo e Metropolis. As principais conclusões indicam que a fidelidade visual depende da simulação precisa da interação luz-matéria (através de modelos de microfacetas e BSDFs) e do transporte em meios participantes (volumes). Avanços recentes, como o  *Monte Carlo Transport Scheduling*  (MCTS), propõem uma ponte entre a renderização física e modelos generativos de IA, utilizando a lei de convergência do limite central ( $1/\\sqrt{n}$ ) para criar um eixo contínuo de tempo-variância. Além disso, a implementação robusta desses sistemas exige práticas avançadas de programação em C++, especificamente no gerenciamento automático de memória e design orientado a objetos.

#### 1\. Fundamentos de Radiometria e Luz

A renderização foto-realista busca simular a física da luz e sua interação com a matéria. O espectro visível compreende comprimentos de onda entre 380 nm e 780 nm.

##### Grandezas Radiométricas Principais

A propagação da luz é descrita por quatro grandezas fundamentais:| Grandeza | Símbolo / Unidade | Definição || \------ | \------ | \------ || **Energia** | $Q$  (Joules, J) | Fótons emitidos por uma fonte. || **Fluxo Radiante** | $\\Phi$  (Watts, W) | Quantidade de energia por unidade de tempo ( $dQ/dt$ ). || **Irradiância** | $E$  (W/m²) | Fluxo por unidade de área. Obedece à Lei de Lambert ( $E \\propto \\cos \\theta$ ). || **Radiância** | $L$  (W/(m² sr)) | Fluxo por unidade de área perpendicular e unidade de ângulo sólido. É a grandeza principal na renderização. |

##### Propriedades da Luz e Modelagem

* **Linearidade:**  A combinação de efeitos é a soma dos efeitos individuais.  
* **Conservação de Energia:**  A luz dispersa não pode exceder a incidente.  
* **Modelos de Cor:**  O modelo  **XYZ**  cobre o espectro visível humano; o  **sRGB**  é o padrão para equipamentos, embora possua gama limitada.  
* **Ângulo Sólido (**  **$\\omega**$  **):**  Área projetada em um hemisfério unitário, medida em esferorradiano (sr). Um hemisfério possui  $2\\pi$  sr.

#### 2\. Interação Luz-Matéria: Modelos de Microfacetas

A reflexão em superfícies é modelada pela  **BRDF**  ( *Bidirectional Reflectance Distribution Function* ), que define a proporção de radiância refletida em uma direção de saída em relação à irradiância vinda de uma direção de entrada.

##### Modelo de Cook-Torrance

Este modelo estatístico aproxima superfícies reais através de microfacetas (espelhos perfeitos microscópicos). A função de BRDF é dividida em:

* **Parte Difusa (**  **$f\_d**$  **):**  Representa a luz que penetra na superfície e é dispersa.  
* **Parte Especular (**  **$f\_s**$  **):**  Representa a reflexão nas microfacetas, composta por três termos:  
* **Distribuição Normal (**  **$D**$  **):**  Fração de microfacetas alinhadas com o  *half-vector*  ( $h$ ). O modelo  **GGX/Walter**  é o padrão, onde a rugosidade ( $\\alpha$ ) define a dispersão.  
* **Termo Fresnel (**  **$F**$  **):**  Define quanta luz é refletida versus refratada. Metais refletem cor especular; dielétricos têm reflexão branca. A  **Aproximação de Schlick**  é amplamente utilizada pela eficiência computacional.  
* **Termo Geométrico (**  **$G**$  **):**  Modela o auto-sombreamento e o mascaramento entre microfacetas.

#### 3\. Algoritmos de Transporte de Luz

A renderização pode ser realizada por objeto (rasterização) ou por pixel (traçado de raios).

##### Traçado de Caminhos (Path Tracing)

Resolve a  **Equação de Renderização**  simulando caminhos de luz.

* **Traçado de Caminhos Bidirecional (BDPT):**  Traça sub-caminhos a partir da câmera e da fonte de luz, conectando-os. É superior ao  *path tracing*  convencional em cenas com iluminação complexa, pois reaproveita amostras.  
* **Múltipla Amostragem por Importância (MIS):**  Técnica para combinar diferentes estratégias de amostragem, reduzindo a variância.

##### Metropolis Light Transport (MLT)

Utiliza o algoritmo de Metropolis-Hastings para explorar o espaço de caminhos.

* **Vantagem:**  Excelente para situações de iluminação difícil (ex: luz passando por frestas).  
* **Mutação:**  Cria novos caminhos baseados em caminhos anteriores bem-sucedidos através de mutações locais ou grandes mudanças para cobrir o domínio.

#### 4\. Renderização de Volumes

Envolve a interação da luz com partículas suspensas (meios participantes).

* **Processos Físicos:**  
* **Absorção:**  Luz transformada em energia.  
* **Emissão:**  Partículas emitem luz.  
* **Dispersão (Scattering):**  Redirecionamento da luz (entrada ou saída).  
* **Transmitância (**  **$T\_r**$  **):**  Fração de luz que atravessa o volume sem interação. Em meios homogêneos, decai exponencialmente com a distância.  
* **Função de Fase:**  Define a distribuição direcional da dispersão (análoga à BRDF). O modelo  **Henyey-Greenstein**  permite simular dispersão para frente ou para trás.  
* **Monte Carlo em Volumes:**  Utiliza  *Tracking*  para estimar distâncias de colisão. O  *Delta Tracking*  (Woodcock) é aplicado a meios heterogêneos para "homogeneizar" o tratamento via colisões nulas.

#### 5\. Inovações: Renderização Inversa e IA

##### Monte Carlo Transport Scheduling (MCTS)

Apresenta uma nova perspectiva onde a renderização e modelos generativos (difusão) compartilham um substrato comum.

* **Conceito:**  O processo de  *Path Tracing*  progressivo é visto como um transporte contínuo de um estado ruidoso para um estado limpo.  
* **Eixo de Tempo-Variância (**  **$\\tau**$  **):**  Derivado da lei  $1/\\sqrt{n}$ , permite treinar redes neurais para prever o limite "limpo" de uma imagem a partir de estados de baixa amostragem (SPP).  
* **Aplicações:**  Refinamento de renderização estável e injeção de  *priors*  físicos em modelos generativos congelados.

##### 3D Surface Splatting (3DSS)

Um renderizador diferenciável para renderização inversa que utiliza  *surfels*  (amostras de superfície orientadas).

* Permite recuperar conjuntamente geometria, materiais (BRDF) e iluminação a partir de imagens multi-view.  
* Supera limitações de malhas tradicionais em fluxos de otimização complexos.

#### 6\. Implementação Técnica em C++

A eficiência e robustez de um motor de renderização dependem do uso correto da linguagem C++.

##### Gerenciamento de Memória e Objetos

* **Classes e Encapsulamento:**  Uso de arquivos .h para definições e .cpp para implementação. Métodos const garantem a imutabilidade do objeto em operações de leitura.  
* **Herança e Polimorfismo:**  Uso de classes abstratas (com métodos virtual \= 0\) para definir interfaces de figuras e materiais.  
* **Ponteiros Inteligentes (Smart Pointers):**  
* std::shared\_ptr: Gerenciamento por contagem de referência.  
* std::unique\_ptr: Propriedade exclusiva de um recurso.  
* std::weak\_ptr: Referência que não impede a deleção, essencial para evitar ciclos de referência em estruturas como "Pai-Filho" (ex: uma coleção de figuras).  
* **STL (Standard Template Library):**  Uso de std::vector para armazenamento dinâmico e std::string para cadeias de caracteres. O tipo auto e  *range-based for loops*  aumentam a legibilidade do código.

**Citação Chave:**"A renderização baseada em física não é apenas sobre imagens bonitas, mas sobre a simulação precisa da interação luz-matéria adequada à tecnologia disponível." —  *Waldemar Celes, INF2604.*  
