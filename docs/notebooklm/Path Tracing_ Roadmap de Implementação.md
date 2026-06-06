# **Mapa de Evolução Arquitetural: Path Tracing Estocástico de Monte Carlo**

A modelagem de imagens fotorrealistas por meio de simulação física baseada em computador avançou significativamente através da transição de métodos de iluminação local e determinísticos para abordagens estocásticas capazes de resolver globalmente o transporte de radiação luminosa.1 Este relatório técnico apresenta o projeto detalhado e a fundamentação matemática para a evolução arquitetural de um traçador de raios clássico (Whitted) — estruturado no módulo src/ray\_tracing\_2/ 2 — para um integrador estocástico de Monte Carlo iterativo (Path Tracer), a ser consolidado no módulo src/path\_tracing/.1  
A proposta aqui delineada estabelece uma ponte conceitual entre a herança geométrica e de aceleração do projeto anterior, as aulas expositivas de computação gráfica da PUC-Rio e a literatura fundamental de síntese de imagens físicas, com destaque para a obra *Physically Based Rendering (PBRT 4e)* e artigos clássicos do estado da arte.1

## **Seção 1: Arquitetura de Transição e Preservação de Componentes (Fase 0\)**

A transição para o algoritmo de *Path Tracing* estocástico não exige a reconstrução completa do núcleo geométrico desenvolvido no Projeto 1\.1 A engenharia do novo integrador baseia-se no reaproveitamento de componentes determinísticos consolidados, isolando as modificações nos módulos de amostragem, avaliação de materiais e na malha iterativa de transporte de radiância.1  
Para garantir a integridade estrutural e evitar regressões numéricas, os arquivos de infraestrutura matemática, interseção e aceleração espacial são importados diretamente ou replicados no novo diretório com adaptações marginais de assinatura.1  
A Tabela 1 detalha o mapeamento de herança de software do módulo src/ray\_tracing\_2/ para o módulo src/path\_tracing/.1

### **Tabela 1: Mapeamento e Estratégia de Migração de Módulos**

| Arquivo de Origem (src/ray\_tracing\_2/) | Arquivo de Destino (src/path\_tracing/) | Estratégia de Software e Acoplamento | Referência Teórica e Conceito Associado |
| :---- | :---- | :---- | :---- |
| camera.py | camera.py | Preservação total. Fornece o modelo canônico de câmera *pinhole* e a geração do primary\_ray.1 | 4.tracado\_de\_raios.pdf (pp. 19-39): Transformação de visão via lookAt.2 |
| triangle\_bvh.py | triangle\_bvh.py | Preservação total. Mantém a aceleração local por malha usando caixas AABB e a heurística de partição.1 | 6.estrutura\_aceleracao.pdf (pp. 22-36): Hierarquia de volumes limitantes com redução de custo para ![][image1].1 |
| film.py | film.py | Preservação total. Gerencia a distribuição de subpixels e filtros para reconstrução de pixel com antialiasing estocástico.1 | 5.tracado\_de\_raios2.pdf (pp. 4-6): Amostragem estratificada e tratamento de aliasing.1 |
| shape.py | shape.py | Preservação das interseções analíticas (Plano, Esfera, Caixa) e do nó Instance com transformações afins inversas de raios e inversas transpostas de normais.2 | 4.tracado\_de\_raios.pdf (pp. 7-18) e 5.tracado\_de\_raios2.pdf (pp. 9-13): Mudança de base e ortogonalidade de normais.1 |
| light.py | light.py | Extensão estrutural. Reutilização de AreaLight para fornecer amostragem de pontos em sua superfície através de padrões estratificados.2 | 5.tracado\_de\_raios2.pdf (pp. 14-23): Geometria de fontes extensas e cálculo de penumbra.2 |
| material.py | material.py | Refatoração completa. Transição de avaliação puramente local (Phong) para uma interface de amostragem estocástica com cálculo de BRDF e PDF direcional.1 | 8.tracado\_de\_caminhos.pdf (p. 20\) e 11.microfaceta.pdf (pp. 9-18).1 |
| scene.py | scene.py | Substituição do método recursivo trace\_ray pelo laço estocástico linear unificado TracePath.1 | 8.tracado\_de\_caminhos.pdf (pp. 20-21) e 9.tracado\_de\_caminhos2.pdf (pp. 7-8).1 |

### **Prompt de Configuração Global do Sistema (Prompt 0\)**

"Atue como um Engenheiro Especialista em Renderização Baseada em Física (PBR). O nosso projeto em Python (src/path\_tracing) já possui uma base sólida de ray tracing com BVH (6.estrutura\_aceleracao.pdf), câmera pinhole (4.tracado\_de\_raios.pdf) e materiais refratários baseados nas Leis de Snell e Beer-Lambert (5.tracado\_de\_raios2.pdf). Agora, implementaremos um Path Tracer de Monte Carlo para resolver a Equação de Renderização original formulada por Kajiya (1986). A arquitetura deve seguir estritamente o livro *Physically Based Rendering (PBRT 4e)*, especificamente o 'Light Transport I: Surface Reflection'. Use tipagem estática e vetores glm, e garanta que o código gerado contenha comentários explícitos referenciando as equações matemáticas das fontes." 1

## **Seção 2: O Integrador Iterativo e a Equação de Transporte de Luz (Fase 1\)**

O objetivo central de um pipeline estocástico maduro consiste em resolver numericamente a Equação de Transporte de Luz (LTE), formulada originalmente por James Kajiya em 1986\.1 A formulação analítica contínua define a radiância espectral de saída ![][image2] a partir de um ponto de superfície ![][image3] ao longo de uma direção de visualização ![][image4] como o somatório da radiância emitida pela superfície ![][image5] e a integral da radiância incidente ![][image6] sobre a semiesfera tangente ![][image7], ponderada pela BRDF ![][image8] e pelo cosseno geométrico local 1:  
![][image9]  
A recursão clássica presente em traçadores de raios Whitted ou distribucionais produz uma árvore de caminhos de custo computacional exponencial ![][image10], onde ![][image11] é o número de amostras locais e ![][image12] é a profundidade recursiva.1 Para tornar o cálculo computacionalmente viável, o algoritmo de *Path Tracing* de Monte Carlo colapsa a árvore de decisão ao amostrar uma única direção estocástica por impacto geométrico (![][image13]), convertendo a recursão em uma série linear de caminhos unidimensionais.1  
Para manter a conformidade física ao longo de múltiplos saltos, o integrador acumula os fatores de atenuação espectral em uma variável de estado denominada *throughput* (![][image14]).1 A cada intersecção, ![][image14] é atualizado multiplicativamente pela BRDF e pelo cosseno geométrico, e escalado de forma inversa pela densidade de probabilidade (PDF) da direção de espalhamento amostrada 1:  
![][image15]  
Se o caminho estocástico interceptar um emissor ativo de luz no vértice ![][image16], a contribuição de radiância direta é acumulada ponderando a emissão intrínseca pelo *throughput* cumulativo naquele instante: ![][image17].1 Esta formulação iterativa previne o estouro da pilha de chamadas e mantém estável o consumo de memória do motor de renderização.1

### **Prompt para a IA (Contexto: scene.py / TracePath)**

"Refatore o método principal de avaliação de raios implementando o algoritmo TracePath iterativo de Monte Carlo (Kajiya, 1986). Siga o pseudocódigo do slide 8.tracado\_de\_caminhos.pdf (pág 21\) e o Cap. 13 do PBRT 4e ('A Simple Path Tracer'):

1. Receba um raio primário e itere em um loop até max\_depth.  
2. Inicialize o acumulador de radiância L \= glm.vec3(0.0) e o throughput de atenuação beta \= glm.vec3(1.0).  
3. Na interseção, se atingir um emissor, acumule L \+= beta \* L\_e (apenas se for o primeiro salto) e encerre.  
4. Para superfícies opacas, chame material.sample(wo, normal) para obter a nova direção wi, a BRDF e a PDF.  
5. Atualize o throughput estritamente pela Equação de Transporte: beta \*= BRDF \* max(0.0, glm.dot(normal, wi)) / PDF. Adicione o comentário \# \[Celes 2026, 8.tracado\_de\_caminhos, p. 21\] e Atualização do throughput LTE na linha do código correspondente." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/scene.py  
import glm  
import math  
import random  
from typing import Optional, List  
from shape import HitRecord, Ray

class Scene:  
    def \_\_init\_\_(self, bvh: any, lights: List\[any\], background: glm.vec3 \= glm.vec3(0.0)) \-\> None:  
        self.triangle\_bvh \= bvh  
        self.lights \= lights  
        self.background \= background

    def TracePath(self, primary\_ray: Ray, max\_depth: int) \-\> glm.vec3:  
        """  
        \[Celes 2026, 8.tracado\_de\_caminhos.pdf, p. 21\] e  
        Implementação iterativa do estimador de transporte de luz de Monte Carlo (Kajiya 1986).  
        """  
        L \= glm.vec3(0.0)  
        beta \= glm.vec3(1.0)  
        current\_ray \= primary\_ray  
        last\_specular \= True  \# Mantido para compatibilidade com emissores diretos

        for depth in range(max\_depth):  
            hit: Optional \= self.triangle\_bvh.Intersect(current\_ray)  
              
            \# Se o raio escapar para o infinito, acumula a cor de fundo (ambiente)  
            if not hit:  
                L \+= beta \* self.background  
                break

            hit.wo \= \-current\_ray.d

            \# Se atingir um emissor diretamente  
            if hit.material.is\_emissive:  
                Le \= hit.material.Le(hit.wo)  
                \# Acumula emissão direta se for o primeiro salto ou se o salto anterior foi especular  
                if depth \== 0 or last\_specular:  
                    L \+= beta \* Le  
                break

            \# Amostragem estocástica baseada na BRDF do material  
            wi, brdf\_val, pdf, is\_specular \= hit.material.sample(hit.wo, hit.normal)  
              
            if pdf \<= 1e-6 or math.isnan(pdf):  
                break

            \# \[Celes 2026, 8.tracado\_de\_caminhos, p. 21\] e Atualização do throughput LTE  
            cos\_theta \= max(0.0, glm.dot(hit.normal, wi))  
            beta \*= (brdf\_val \* cos\_theta) / pdf

            \# Atualização do estado do raio para a próxima iteração  
            last\_specular \= is\_specular  
            offset\_origin \= hit.p \+ (hit.normal \* 1e-4 if glm.dot(wi, hit.normal) \> 0.0 else \-hit.normal \* 1e-4)  
            current\_ray \= Ray(offset\_origin, wi)

        return L

### **Resultados Esperados**

A eliminação do estouro de pilha por recursão direta e estabilização do pipeline de execução.1 Espera-se a convergência estocástica para uma imagem fisicamente realista, onde o ruído decai a uma taxa de ![][image18], na qual ![][image11] corresponde ao número de caminhos processados por pixel (spp).1

## **Seção 3: Amostragem e Material Difuso Ideal de Lambert (Fase 2\)**

Superfícies difusas Lambertianas puras espalham energia de forma idêntica sobre todas as direções do hemisfério.1 O princípio da conservação de energia impõe que a BRDF correspondente seja constante em relação ao domínio direcional, correlacionando-se ao albedo espectral do material ![][image19] e à constante de normalização da projeção esférica 1:  
![][image20]  
A amostragem uniforme sobre a semiesfera unitária gera alta variância, uma vez que distribui raios excessivos em direções rasas (tangenciais), nas quais o fluxo é fortemente atenuado pelo termo geométrico ![][image21].1 Para minimizar o erro quadrático médio, utiliza-se a Amostragem do Hemisfério Ponderada pelo Cosseno.1 A PDF teórica associada deve alinhar-se perfeitamente com a distribuição física 1:  
![][image22]  
A técnica de geração robusta dessas amostras é formalizada pelo Método de Malley.1 O procedimento consiste em mapear uniformemente duas variáveis independentes ![][image23] sobre a superfície de um disco unitário bidimensional e projetá-las verticalmente em direção à calota do hemisfério tangente de raio unitário.1 O mapeamento de área uniforme no disco em coordenadas polares é estabelecido por 1:  
![][image24]  
A projeção ortogonal estende essas coordenadas bidimensionais para o espaço cartesiano tridimensional local da semiesfera unitária 1:  
![][image25]  
Pelo teorema de Malley, a densidade diferencial resultante é ![][image26].1 A substituição desta densidade e da BRDF Lambertiana na equação de atualização de *throughput* promove um cancelamento analítico perfeito, zerando a variância local decorrente dos termos cosseno e pi 1:  
![][image27]

### **Prompt para a IA (Contexto: material.py / sampling.py)**

"Crie a classe DiffuseMaterial e seu método sample(wo, normal).

1. A constante da BRDF Lambertiana será o albedo / math.pi (ref: 8.tracado\_de\_caminhos.pdf, pág. 20).  
2. Sorteie a direção wi utilizando a Amostragem do Hemisfério Ponderada pelo Cosseno (Método de Malley, 7.montecarlo.pdf pág. 43-46 e PBRT Cap 2). Sorteie dois números, mapeie para o disco unitário e projete no hemisfério local.  
3. A PDF teórica deve ser obrigatoriamente max(0, glm.dot(normal, wi)) / math.pi.  
4. Retorne a tupla: (wi, brdf\_value, pdf, is\_specular=False). Comente a fórmula do Método de Malley no código." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/sampling.py  
import math  
import glm  
from typing import Tuple

def SampleCosineHemisphere(u1: float, u2: float) \-\> Tuple\[glm.vec3, float\]:  
    """  
    \[Celes 2026, 7.montecarlo.pdf, pág. 45-46\] Método de Malley.  
    Gera direções na semiesfera local (normal ao longo do eixo \+Z) ponderadas pelo cosseno.  
    """  
    \# Mapeamento uniforme sobre a área de um disco unitário (Malley 2D)  
    r \= math.sqrt(u1)  
    phi \= 2.0 \* math.pi \* u2  
    x \= r \* math.cos(phi)  
    y \= r \* math.sin(phi)  
      
    \# Projeção ortogonal vertical em direção à casca do hemisfério unitário  
    z \= math.sqrt(max(0.0, 1.0 \- (x \* x \+ y \* y)))  
      
    \# PDF em relação ao ângulo sólido: cos(theta) / pi. No espaço local, cos(theta) é a coordenada z.  
    pdf \= z / math.pi  
    return glm.vec3(x, y, z), pdf

def LocalToWorldONB(local\_v: glm.vec3, normal: glm.vec3) \-\> glm.vec3:  
    """  
    \[Celes 2026, 9.tracado\_de\_caminhos2.pdf, pág. 11\]  
    Muda a base de um vetor do espaço tangente local (+Z como normal) para o espaço de coordenadas global do mundo.  
    """  
    up \= glm.vec3(1.0, 0.0, 0.0) if abs(normal.x) \< 0.9 else glm.vec3(0.0, 1.0, 0.0)  
    tangent \= glm.normalize(glm.cross(normal, up))  
    bitangent \= glm.cross(normal, tangent)  
      
    \# Transformação linear por rotação pura utilizando matriz de mudança de base  
    onb \= glm.mat3(tangent, bitangent, normal)  
    return glm.normalize(onb \* local\_v)

\# Contexto: src/path\_tracing/material.py  
from material import Material  
from sampling import SampleCosineHemisphere, LocalToWorldONB

class DiffuseMaterial(Material):  
    def \_\_init\_\_(self, albedo: glm.vec3) \-\> None:  
        super().\_\_init\_\_()  
        self.albedo \= albedo  
        self.is\_specular \= False  
        self.is\_emissive \= False

    def sample(self, wo: glm.vec3, normal: glm.vec3) \-\> Tuple\[glm.vec3, glm.vec3, float, bool\]:  
        """  
        \[Celes 2026, 8.tracado\_de\_caminhos.pdf, pág. 20\]  
        Avalia o espalhamento estocástico de um material Lambertiano ideal.  
        """  
        u1 \= random.random()  
        u2 \= random.random()  
        local\_wi, local\_pdf \= SampleCosineHemisphere(u1, u2)  
        wi \= LocalToWorldONB(local\_wi, normal)  
          
        brdf\_val \= self.albedo / math.pi  
        cos\_theta \= max(0.0, glm.dot(normal, wi))  
        pdf \= cos\_theta / math.pi  
          
        return wi, brdf\_val, pdf, False

    def pdf(self, wo: glm.vec3, wi: glm.vec3, normal: glm.vec3) \-\> float:  
        cos\_theta \= max(0.0, glm.dot(normal, wi))  
        return cos\_theta / math.pi

    def eval(self, wo: glm.vec3, wi: glm.vec3, normal: glm.vec3) \-\> glm.vec3:  
        return self.albedo / math.pi

### **Resultados Esperados**

Distribuição direcional fisicamente correta em superfícies foscas (mate).1 Comparado ao sorteio esférico ou hemisférico uniforme convencional, a amostragem de Malley elimina ruído estridentes em penumbras e garante taxas de convergência notavelmente superiores com menor amostragem total por pixel.1

## **Seção 4: Múltipla Amostragem por Importância (MIS) (Fase 3\)**

Integrar unicamente com base na amostragem estocástica da BRDF resulta em variância inaceitável se o ambiente for iluminado por fontes de luz extremamente pequenas ou distantes, pois a probabilidade de um raio arbitrário interceptar o emissor de forma passiva aproxima-se de zero.1 Para contornar essa deficiência, o integrador acopla a técnica de Iluminação Direta de Próximo Evento (Next Event Estimation \- NEE), gerando caminhos específicos em direção à geometria dos emissores ativos.1  
Ao amostrar uniformemente a superfície da luz retangular, a PDF baseada em área é ![][image28].1 Para integrar essa contribuição à LTE, a densidade de área deve ser transposta para densidade de ângulo sólido sob a ótica do ponto sombreado ![][image3] 1:  
![][image29]  
Onde ![][image30] é a distância euclidiana, e ![][image31] corresponde à normal intrínseca da fonte de luz no ponto ![][image32].1  
Ponderar as duas estimativas (NEE e amostragem de BRDF) separadamente pode induzir picos catastróficos de variância se o material for altamente especular.1 O formalismo de Múltipla Amostragem por Importância (MIS), proposto por Eric Veach em 1995, combina ambas as técnicas de amostragem sem introduzir viés matemático, ponderando as respectivas PDFs pela Heurística da Potência com expoente ![][image33] 1:  
![][image34]  
Onde as probabilidades em ângulo sólido são avaliadas para a mesma direção de avaliação ![][image35].1

### **Prompt para a IA (Contexto: scene.py / TracePath)**

"Aprimore a estimativa de iluminação direta no TracePath através da Múltipla Amostragem por Importância (MIS) usando a Heurística da Potência de Veach (1995) com exponente beta=2, conforme 9.tracado\_de\_caminhos2.pdf (pág. 21).

1. Se is\_specular \== False, ative o *Next Event Estimation* (NEE): sorteie um ponto explícito na AreaLight, lance o raio de sombra de verificação de visibilidade, e obtenha L\_d e PDF\_light em ângulo sólido.  
2. Analise a probabilidade da BRDF apontar para a mesma direção da fonte (PDF\_brdf).  
3. Compute o peso MIS: weight\_light \= (PDF\_light\*\*2) / (PDF\_light\*\*2 \+ PDF\_brdf\*\*2). Acumule L \+= beta \* weight\_light \* BRDF \* L\_d \* cos(theta) / PDF\_light.  
4. Continue o Path Tracing com a direção wi da BRDF. Caso este próximo salto atinja emissão na iteração subsequente, calcule o weight\_brdf inverso e aplique a ele. Adicione o comentário \# \[Veach 1995\] e \[Celes 2026, 9.tracado\_de\_caminhos2, p. 21\] Heurística da Potência no cálculo do peso." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/scene.py (Extensão dos métodos de Scene)  
    def SampleDirectLight(self, hit: HitRecord, beta: glm.vec3) \-\> glm.vec3:  
        """  
        \[Celes 2026, 9.tracado\_de\_caminhos2.pdf, pág. 16, 21\] e \[Veach 1995\]  
        Estima a radiância direta baseada em Next Event Estimation (NEE) com balanceamento MIS.  
        """  
        if not self.lights:  
            return glm.vec3(0.0)

        \# Seleciona aleatoriamente um emissor da cena para a estimativa de iluminação direta  
        light \= random.choice(self.lights)  
        p\_light, normal\_light, pdf\_area \= light.SampleSurface()  
          
        wi\_light \= p\_light \- hit.p  
        dist2 \= glm.length2(wi\_light)  
        dist \= math.sqrt(dist2)  
        wi\_light \= glm.normalize(wi\_light)

        \# Dispara o raio de sombra (Shadow Ray) de verificação de visibilidade  
        shadow\_ray \= Ray(hit.p \+ hit.normal \* 1e-4, wi\_light)  
        shadow\_hit \= self.triangle\_bvh.Intersect(shadow\_ray)  
          
        \# Se houver oclusão prévia ao emissor sorteado  
        if shadow\_hit and (shadow\_hit.t \< dist \- 1e-4):  
            return glm.vec3(0.0)

        cos\_theta\_light \= abs(glm.dot(normal\_light, \-wi\_light))  
        if cos\_theta\_light \< 1e-6:  
            return glm.vec3(0.0)

        \# Conversão analítica da PDF de área para ângulo sólido  
        pdf\_light\_sa \= (pdf\_area \* dist2) / cos\_theta\_light  
        pdf\_brdf \= hit.material.pdf(hit.wo, wi\_light, hit.normal)

        \# \[Veach 1995\] e \[Celes 2026, 9.tracado\_de\_caminhos2, p. 21\] Heurística da Potência  
        weight\_light \= (pdf\_light\_sa\*\*2) / (pdf\_light\_sa\*\*2 \+ pdf\_brdf\*\*2 \+ 1e-10)

        brdf\_eval \= hit.material.eval(hit.wo, wi\_light, hit.normal)  
        cos\_theta\_local \= max(0.0, glm.dot(hit.normal, wi\_light))  
        Le \= light.GetRadiance()

        num\_lights \= float(len(self.lights))  
        return (weight\_light \* brdf\_eval \* Le \* cos\_theta\_local) / (pdf\_light\_sa \* num\_lights)

    def EvaluateLightPDF\_SolidAngle(self, hit: HitRecord, ray: Ray) \-\> float:  
        """  
        Calcula a PDF em ângulo sólido de uma colisão passiva com um emissor retangular.  
        """  
        light\_inst \= hit.material  
        pdf\_area \= 1.0 / light\_inst.GetArea()  
        dist2 \= hit.t \*\* 2  
        cos\_theta\_light \= abs(glm.dot(hit.normal, \-ray.d))  
        if cos\_theta\_light \< 1e-6:  
            return 0.0  
        return (pdf\_area \* dist2) / cos\_theta\_light

### **Resultados Esperados**

Completa atenuação de ruído estrutural de alta frequência nas penumbras geradas por fontes de luz de qualquer tamanho.1 O integrador equilibra suavemente a amostragem de luz direta e o mapeamento estocástico da BRDF, preservando o realismo energético físico sem introduzir viés nas bordas de sombra.1

## **Seção 5: Terminação Estocástica de Caminhos \- Roleta Russa (Fase 4\)**

Truncar arbitrariamente o transporte estocástico de luz a uma profundidade estática introduz sérios vieses energéticos na cena, visto que elimina as trajetórias físicas de reflexão indireta de alta frequência.1 Para mitigar esta barreira sem incorrer em loops infinitos de custo computacional insustentável, aplica-se a terminação probabilística por Roleta Russa.1  
A Roleta Russa avalia a contribuição energética relativa do caminho a partir de uma probabilidade de continuação ![][image36] baseada na refletância remanescente do *throughput* espectral ![][image14].1 Sorteia-se uma variável uniforme independente ![][image37].1 Se o teste falhar (![][image38]), a cadeia estocástica de transporte de luz é encerrada.1 Se o caminho sobreviver (![][image39]), o *throughput* é reescalado pelo inverso da probabilidade sobrevivente 1:  
![][image40]  
Analiticamente, demonstra-se que a esperança matemática do estimador sob Roleta Russa preserva o valor de expectativa original da integral (assumindo valor de interrupção nulo ![][image41]) 1:  
![][image42]  
Para manter a aderência estrita às exigências da disciplina, o pipeline garante que cada caminho estocástico avalie, no mínimo, 4 vértices completos antes de submeter-se ao crivo de terminação estocástica.1 Sabendo que a contagem de profundidade iterativa inicia-se em zero (sendo depth \= 0 o vértice primário na lente, depth \= 1 o vértice secundário na superfície opaca, e assim sucessivamente), a roleta estocástica é rigidamente condicionada a operar apenas quando depth \>= 3\.1 Isso impede encerramentos prematuros e preserva os caminhos mínimos do enunciado.1

### **Prompt para a IA (Contexto: scene.py / TracePath)**

"Integre a técnica de Roleta Russa ao laço iterativo TracePath para encerrar o transporte da luz de forma sem viés (unbiased), referenciado em 9.tracado\_de\_caminhos2.pdf (pág. 13-14).

1. Só ative a avaliação se depth \>= 3 (garantindo os 4 vértices mínimos do seu enunciado).  
2. A probabilidade de sobrevivência q deverá espelhar a refletância limite do beta (throughput): q \= max(0.05, min(1.0, max(beta.x, beta.y, beta.z))).  
3. Sorteie xi. Se xi \> q, efetue break. Se sobreviver, divida o throughput mantendo a consistência do estimador: beta /= q. Comente o código com \# Roleta Russa \[Celes 2026, 9.tracado\_de\_caminhos2, p. 13\]." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/scene.py (Segmento interno do loop de TracePath)  
            \#... processamento dos passos 1 a 4 (LTE, NEE, amostragem de material)  
              
            \# \-------------------------------------------------------------  
            \# 5\. Terminação Estocástica por Roleta Russa  
            \# \[Arvo & Kirk, 1990\] e \[Celes 2026, 9.tracado\_de\_caminhos2.pdf, pág. 13\]  
            \# Roleta Russa ativada somente para depth \>= 3 (4 vértices mínimos exigidos)  
            \# \-------------------------------------------------------------  
            if depth \>= 3:  
                q \= max(0.05, min(0.95, max(beta.x, max(beta.y, beta.z))))  
                if random.random() \> q:  
                    \# Terminação sem viés matemático  
                    break  
                \# Preservação da expectativa matemática do estimador de Monte Carlo  
                beta /= q \# Roleta Russa \[Celes 2026, 9.tracado\_de\_caminhos2, p. 13\]

### **Resultados Esperados**

Redução imediata no tempo médio de processamento da cena sem prejuízo ou desvio energético.1 Caminhos pouco expressivos em oclusões profundas são eliminados de forma não viesada, concentrando a computação nos raios de alta contribuição espectral.1

## **Seção 6: BRDF de Microfacetas (Cook-Torrance) (Fase 5\)**

A representação física de superfícies ásperas, condutoras (metais) e dielétricos opacos de rugosidade ajustável é modelada pela BRDF microgeométrica de Cook-Torrance.1 O modelo assume que a superfície microscópica é constituída por um arranjo estatístico de microespelhos ideais cujas normais individuais estão dispostas ao redor do vetor de meia-direção (half-vector) ![][image43].1 A componente especular de Cook-Torrance é definida analiticamente por 1:  
![][image44]

* **Distribuição de Normais GGX (![][image45]):** Walter et al. (2007) definem a probabilidade de orientação microgeométrica do half-vector ![][image46] a partir da conversão da rugosidade linear em espalhamento angular ![][image47] 1:

![][image48]

* **Fator de Mascaramento Geométrico (![][image49]):** Utiliza o sombreamento bidirecional de Smith, subdividido em duas componentes independentes com aproximação linear de Schlick (![][image50]) 1:

![][image51]

* **Fator de Fresnel Schlick (![][image52]):** Quantifica o nível de refletância em função do albedo metálico ![][image53] para condutores ou do índice básico para dielétricos 1:

![][image54]  
A amostragem de microfacetas sorteia estocasticamente a orientação de ![][image46] proporcionalmente à distribuição de normais GGX multiplicada pelo cosseno local.1 Os ângulos locais do half-vector ![][image46] são determinados a partir de variáveis uniformes independentes ![][image23] 1:  
![][image55]  
A PDF direcional do espalhamento físico final deve incorporar o Jacobiano de transformação de variáveis para mapear o espaço do half-vector para a direção incidente 1:  
![][image56]

### **Prompt para a IA (Contexto: material.py)**

"Construa a classe MicrofacetMaterial que calcule a BRDF exata de Cook-Torrance (1982), fundamentada em 11.microfaceta.pdf (pág. 8-18) e PBRT Cap 9\.

1. A função de Distribuição Normal (NDF) D(h) será **GGX** (Walter et al., 2007, pág. 15), convertendo a rugosidade via alpha \= roughness\*\*2.  
2. O fator Geométrico G\_Smith(l, v) utilizará a aproximação de Schlick com k \= alpha / 2 (pág. 17).  
3. O termo de refletância F(v,h) será avaliado por Schlick com controle paramétrico por albedo (metálicos) e F0 base de dielétricos (pág. 13).  
4. O denominador do estimador é estritamente 4 \* abs(dot(n, wi)) \* abs(dot(n, wo)).  
5. A amostragem deve sortear sobre a NDF para recuperar o half-vector (h). Documente cada equação citando a pág do slide correspondente." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/material.py (Adição de MicrofacetMaterial)  
class MicrofacetMaterial(Material):  
    def \_\_init\_\_(self, albedo: glm.vec3, roughness: float) \-\> None:  
        super().\_\_init\_\_()  
        self.albedo \= albedo  
        \# \[Celes 2026, 11.microfaceta.pdf, pág. 15\] Mapeamento de rugosidade linear para GGX  
        self.alpha \= max(1e-4, roughness \*\* 2)  
        self.is\_specular \= False  
        self.is\_emissive \= False

    def sample(self, wo: glm.vec3, normal: glm.vec3) \-\> Tuple\[glm.vec3, glm.vec3, float, bool\]:  
        """  
        \[Celes 2026, 11.microfaceta.pdf, pág. 18\]  
        Amostragem de importância da NDF GGX para geração do half-vector h.  
        """  
        u1 \= random.random()  
        u2 \= random.random()  
          
        \# Sorteio do ângulo polar e azimutal proporcional à GGX  
        theta\_h \= math.acos(math.sqrt((1.0 \- u1) / (u1 \* (self.alpha\*\*2 \- 1.0) \+ 1.0)))  
        phi\_h \= 2.0 \* math.pi \* u2

        local\_h \= glm.vec3(  
            math.sin(theta\_h) \* math.cos(phi\_h),  
            math.sin(theta\_h) \* math.sin(phi\_h),  
            math.cos(theta\_h)  
        )  
        h \= LocalToWorldONB(local\_h, normal)  
          
        \# Reflete o vetor de visualização wo sobre o half-vector estocástico h  
        wi \= glm.normalize(2.0 \* glm.dot(wo, h) \* h \- wo)

        \# Rejeita direções que penetrem o plano geométrico interno  
        if glm.dot(normal, wi) \<= 1e-6:  
            return glm.vec3(0.0), glm.vec3(0.0), 0.0, False

        pdf\_val \= self.pdf(wo, wi, normal)  
        brdf\_val \= self.eval(wo, wi, normal)  
        return wi, brdf\_val, pdf\_val, False

    def pdf(self, wo: glm.vec3, wi: glm.vec3, normal: glm.vec3) \-\> float:  
        h \= glm.normalize(wo \+ wi)  
        cos\_theta\_h \= max(1e-6, glm.dot(normal, h))  
          
        \# NDF GGX  
        d\_denom \= cos\_theta\_h\*\*2 \* (self.alpha\*\*2 \- 1.0) \+ 1.0  
        D \= self.alpha\*\*2 / (math.pi \* d\_denom\*\*2)  
          
        \# Transformação do Jacobiano de half-vector para direção incidente  
        h\_dot\_wo \= max(1e-6, glm.dot(h, wo))  
        return D \* cos\_theta\_h / (4.0 \* h\_dot\_wo)

    def eval(self, wo: glm.vec3, wi: glm.vec3, normal: glm.vec3) \-\> glm.vec3:  
        n\_dot\_wi \= max(1e-6, glm.dot(normal, wi))  
        n\_dot\_wo \= max(1e-6, glm.dot(normal, wo))  
        h \= glm.normalize(wo \+ wi)

        \# 1\. Avaliação GGX NDF \- D(h) \[Celes 2026, 11.microfaceta.pdf, p. 15\]  
        cos\_theta\_h \= max(1e-6, glm.dot(normal, h))  
        d\_denom \= cos\_theta\_h\*\*2 \* (self.alpha\*\*2 \- 1.0) \+ 1.0  
        D \= self.alpha\*\*2 / (math.pi \* d\_denom\*\*2)

        \# 2\. Avaliação do Fator Geométrico Smith-Schlick \- G(wi, wo) \[Celes 2026, 11.microfaceta.pdf, p. 17\]  
        k \= self.alpha / 2.0  
        G1\_wi \= n\_dot\_wi / (n\_dot\_wi \* (1.0 \- k) \+ k)  
        G1\_wo \= n\_dot\_wo / (n\_dot\_wo \* (1.0 \- k) \+ k)  
        G \= G1\_wi \* G1\_wo

        \# 3\. Fresnel Schlick \- F(v, h) \[Celes 2026, 11.microfaceta.pdf, p. 13\]  
        F0 \= self.albedo  \# Assumindo comportamento metálico simplificado com F0 baseado no albedo  
        h\_dot\_wo \= max(0.0, glm.dot(h, wo))  
        F \= F0 \+ (glm.vec3(1.0) \- F0) \* ((1.0 \- h\_dot\_wo) \*\* 5)

        \# 4\. Denominador Cook-Torrance exato protegido de grazing angles  
        denom \= 4.0 \* n\_dot\_wi \* n\_dot\_wo \+ 1e-5  
        return (D \* G \* F) / denom

### **Resultados Esperados**

Simulação fiel de realismo em materiais metálicos polidos ou oxidados e superfícies rugosas dielétricas.1 A variação de rugosidade linear modulará de forma fisicamente coerente a transição de reflexão nítida para lóbulo de dispersão fosco, extinguindo a representação de modelos locais empíricos (como Phong clássico).1

## **Seção 7: Singularidades de Dirac e Refração com Atenuação de Beer-Lambert (Fase 6\)**

Dielétricos perfeitamente polidos (vidros lisos) e espelhos planos ideais concentram toda a distribuição de espalhamento ao longo de direções determinísticas únicas geradas pelas Leis de Snell e da Reflexão pura.1 Sob a modelagem de Monte Carlo, essas interações envolvem funções de impulso do Delta de Dirac, apresentando densidades probabilísticas analíticas infinitas.1  
Para integrá-los de forma consistente ao pipeline de transporte discreto, as singularidades são isoladas.1 O método de amostragem define uma PDF unitária estática (![][image57]), marcando a flag indicadora de impulso is\_specular \= True.1 Para neutralizar o cosseno e a PDF na LTE global, o valor de BRDF/BTDF retornado é previamente dividido pelo próprio cosseno local 1:  
![][image58]  
Isso faz com que o throughput ![][image14] receba exatamente o coeficiente de atenuação de Fresnel no laço iterativo principal.1  
Adicionalmente, ao intersectar superfícies puramente especulares (is\_specular \== True), a probabilidade estatística de que uma amostra de NEE aponte exatamente na direção do Delta de Dirac é nula.1 Consequentemente, o integrador deve anular a amostragem de luz direta (NEE) para impactos especulares, evitando divisões numéricas indefinidas.1 Se o raio rebater estocasticamente de uma face especular e colidir na fonte de luz no passo seguinte, o peso MIS complementar da BRDF é fixado estaticamente em ![][image59], garantindo a transferência total de energia.1  
O transporte de luz no interior do dielétrico translúcido segue a Lei de Beer-Lambert.1 Sempre que o pipeline registrar uma intersecção de saída do meio (hit.IsBackfacing()), o throughput é atenuado multiplicativamente por uma exponencial proporcional à distância ![][image12] percorrida internamente e ao coeficiente de absorção espectral do material 1:  
![][image60]

### **Prompt para a IA (Contexto: material.py / scene.py)**

"Readeque o ReflectiveMaterial e o TransparentMaterial do projeto antigo para a infraestrutura de Path Tracing, focando no tratamento numérico de Deltas de Dirac (PBRT 4e Cap 9.3).

1. No sample(), forçe a flag is\_specular \= True e retorne pdf \= 1.0. A BRDF retornada deve ser cancelada da divisão pelo cosseno.  
2. No TracePath, não aplique a estimativa de luz direta (NEE) caso is\_specular \== True.  
3. Se um raio emergindo de um hit puramente especular colidir na luz de área no passo iterativo seguinte, force o weight\_brdf \= 1.0 (Heurística de Veach adaptada para deltas impulsivos). Comente explicando que PDFs de espelhos perfeitos gerariam divisão por zero." 1

### **Trecho de Código Esperado**

Python  
\# Contexto: src/path\_tracing/material.py (Readequação de TransparentMaterial)  
class TransparentMaterial(Material):  
    def \_\_init\_\_(self, ior: float, attenuation: glm.vec3) \-\> None:  
        super().\_\_init\_\_()  
        self.ior \= ior  
        self.attenuation \= attenuation  \# Coeficiente de absorção Beer-Lambert (RGB)  
        self.is\_specular \= True  
        self.is\_emissive \= False

    def sample(self, wo: glm.vec3, normal: glm.vec3) \-\> Tuple\[glm.vec3, glm.vec3, float, bool\]:  
        """  
        \[Celes 2026, 5.tracado\_de\_raios2.pdf, pág. 32, 34\]  
        Amostragem dielétrica determinística com reescalonamento para anulação do cosseno na LTE.  
        """  
        n\_dot\_wo \= glm.dot(normal, wo)  
        is\_entering \= n\_dot\_wo \> 0.0  
        out\_normal \= normal if is\_entering else \-normal  
        eta\_ratio \= 1.0 / self.ior if is\_entering else self.ior  
        cos\_i \= abs(n\_dot\_wo)

        \# Fresnel aproximado de Schlick  
        r0 \= ((1.0 \- self.ior) / (1.0 \+ self.ior)) \*\* 2  
        R\_schlick \= r0 \+ (1.0 \- r0) \* ((1.0 \- cos\_i) \*\* 5)

        \# Avaliação de Reflexão Interna Total (TIR)  
        sin\_i2 \= max(0.0, 1.0 \- cos\_i \* cos\_i)  
        sin\_t2 \= (eta\_ratio \*\* 2) \* sin\_i2

        if sin\_t2 \>= 1.0:  
            \# Reflexão Interna Total (TIR) pura  
            wi \= glm.reflect(-wo, out\_normal)  
            \# BRDF escalada: dividida pelo cosseno geométrico para cancelamento analítico  
            brdf\_val \= glm.vec3(1.0) / abs(glm.dot(normal, wi))  
            return wi, brdf\_val, 1.0, True

        \# Decisão estocástica baseada em Fresnel  
        if random.random() \< R\_schlick:  
            \# Canal de Reflexão Especular  
            wi \= glm.reflect(-wo, out\_normal)  
            brdf\_val \= glm.vec3(R\_schlick) / abs(glm.dot(normal, wi))  
            return wi, brdf\_val, 1.0, True  
        else:  
            \# Canal de Refração Especular (Snell)  
            wi \= glm.refract(-wo, out\_normal, eta\_ratio)  
            brdf\_val \= glm.vec3(1.0 \- R\_schlick) / abs(glm.dot(normal, wi))  
            return wi, brdf\_val, 1.0, True

*(Nota: O integrador final unificado de scene.py contendo a fusão de todas as fases estocásticas anteriores é apresentado no quadro de códigos integrado abaixo)*.1

Python  
\# Contexto: src/path\_tracing/scene.py (Algoritmo TracePath Integrado Completo)  
    def TracePath(self, primary\_ray: Ray, max\_depth: int) \-\> glm.vec3:  
        """  
        \[Celes 2026, 8.tracado\_de\_caminhos.pdf\] e Integrador de Path Tracing Completo.  
        Combina Múltipla Amostragem por Importância (MIS), Iluminação Direta (NEE),   
        Roleta Russa e atenuação volumétrica espectral de Beer-Lambert.  
        """  
        L \= glm.vec3(0.0)  
        beta \= glm.vec3(1.0)  
        current\_ray \= primary\_ray  
        last\_specular \= True  
        last\_pdf\_brdf \= 1.0

        for depth in range(max\_depth):  
            hit: Optional \= self.triangle\_bvh.Intersect(current\_ray)  
            if not hit:  
                L \+= beta \* self.background  
                break

            hit.wo \= \-current\_ray.d

            \# 1\. Avaliação Volumétrica (Beer-Lambert)  
            \# \[Celes 2026, 5.tracado\_de\_raios2.pdf, pág. 33\]  
            \# Se o raio saiu do material refrativo, aplica atenuação proporcional à distância  
            if glm.dot(hit.normal, hit.wo) \< 0.0:  
                if hasattr(hit.material, "attenuation"):  
                    d \= hit.t  
                    attenuation \= glm.pow(hit.material.attenuation, glm.vec3(d))  
                    beta \*= attenuation  
                \# Inverte a normal de impacto para orientá-la corretamente para superfícies internas  
                hit.normal \= \-hit.normal

            \# 2\. Avaliação de Emissores (Luz Direta e MIS de BRDF)  
            if hit.material.is\_emissive:  
                Le \= hit.material.Le(hit.wo)  
                if depth \== 0 or last\_specular:  
                    L \+= beta \* Le  
                else:  
                    \# \[Veach 1995\] MIS de caminho estocástico atingindo a fonte naturalmente  
                    pdf\_light\_sa \= self.EvaluateLightPDF\_SolidAngle(hit, current\_ray)  
                    w\_brdf \= (last\_pdf\_brdf\*\*2) / (last\_pdf\_brdf\*\*2 \+ pdf\_light\_sa\*\*2 \+ 1e-10)  
                    L \+= beta \* w\_brdf \* Le  
                break

            \# 3\. Next Event Estimation (NEE \+ MIS)  
            \# \[Celes 2026, 9.tracado\_de\_caminhos2.pdf, pág. 16, 21\]  
            \# NEE deve ser completamente ignorado para materiais baseados em Deltas de Dirac  
            if not hit.material.is\_specular and len(self.lights) \> 0:  
                L\_direct \= self.SampleDirectLight(hit, beta)  
                L \+= L\_direct

            \# 4\. Amostragem Estocástica do Material  
            wi, brdf\_val, pdf\_brdf, is\_specular \= hit.material.sample(hit.wo, hit.normal)  
            if pdf\_brdf \<= 1e-6 or math.isnan(pdf\_brdf):  
                break

            \# Quantização iterativa da LTE: beta \*= (BRDF \* |dot(n, wi)|) / PDF  
            cos\_theta \= abs(glm.dot(hit.normal, wi))  
            beta \*= (brdf\_val \* cos\_theta) / pdf\_brdf

            last\_specular \= is\_specular  
            last\_pdf\_brdf \= pdf\_brdf

            \# 5\. Terminação Estocástica por Roleta Russa  
            \# \[Arvo & Kirk, 1990\] e \[Celes 2026, 9.tracado\_de\_caminhos2.pdf, pág. 13\]  
            \# Roleta Russa ativada somente para depth \>= 3 (4 vértices mínimos exigidos)  
            if depth \>= 3:  
                q \= max(0.05, min(0.95, max(beta.x, max(beta.y, beta.z))))  
                if random.random() \> q:  
                    break  
                beta /= q \# Roleta Russa \[Celes 2026, 9.tracado\_de\_caminhos2, p. 13\]

            offset\_dir \= hit.normal if glm.dot(wi, hit.normal) \> 0.0 else \-hit.normal  
            current\_ray \= Ray(hit.p \+ offset\_dir \* 1e-4, wi)

        return L

### **Resultados Esperados**

Anulação de picos de energia e comportamentos numéricos indefinidos (divisão por zero) em superfícies reflexivas ou refratárias perfeitas.1 Exibição correta de sombras de Fresnel (reflexões acentuadas em ângulos rasos e alta refração frontal), acompanhada da modelagem física de absorção volumétrica de Beer-Lambert ao atravessar meios dielétricos coloridos.1

## **Seção 8: Algoritmos de Integração Global de Alta Complexidade (Opcionais Avançados)**

Caso as restrições e objetivos do projeto demandem tratamento computacional rigoroso de cáusticos de reflexão/refração concentrados, ou transporte global sob forte oclusão geométrica, o integrador unidirecional estocástico clássico pode ser substituído por métodos avançados alternativos.1

### **Sub-seção 8.1: Traçado de Caminhos Bidirecional (BDPT)**

O algoritmo de BDPT estende o transporte de luz de Monte Carlo ao traçar sub-caminhos independentes gerados simultaneamente a partir da lente do observador e da face dos emissores ativos.1 Um sub-caminho do olho com ![][image61] vértices ![][image62] e um sub-caminho da luz com ![][image63] vértices ![][image64] são conectados de forma cruzada, testando-se a visibilidade mútua entre os vértices finais ![][image65] e ![][image66].1  
Este procedimento produz ![][image67] estratégias de amostragem independentes para um mesmo caminho de tamanho ![][image68].1 Para combinar de maneira ótima essas estratégias sem gerar viés físico, aplica-se o cálculo estendido de múltiplos pesos MIS baseados na heurística balanceada de Veach, mapeando retroativamente todas as probabilidades direcionais locais em PDF baseada em área de superfície 1:  
![][image69]

#### **Prompt de Direcionamento IA (BDPT)**

"Substitua o integrador iterativo por um BidirectionalPathTracer conforme 10.metodos\_bidirecionais.pdf (pp. 8-10). O algoritmo deve traçar sub-caminhos independentes (s vértices a partir da luz, t vértices a partir da câmera) e tentar conectar seus endpoints. Implemente laço de conexão explícita e a formulação estendida de MIS de Veach para pesar de forma não viesada as múltiplas estratégias de conexão (k+2 estratégias) de um caminho de tamanho k." 1

### **Sub-seção 8.2: Metropolis Light Transport (MLT)**

Diferente do Path Tracing convencional que avalia amostras independentes, o Metropolis Light Transport (MLT) explora o espaço tridimensional de caminhos utilizando Cadeias de Markov via algoritmo de Metropolis-Hastings.1 O mapeamento de um caminho é construído sobre o Espaço de Amostragem Primário (PSSMLT), associando-se coordenadas parametrizadas em um hipercubo unitário multidimensional ![][image70].1  
Mutações Grandes exploram globalmente o domínio, enquanto Mutações Pequenas realizam perturbações locais e infinitesimais sobre as coordenadas uniformes do caminho preexistente de alta contribuição, mantendo a coerência estrutural de conexões difíceis 1:  
![][image71]  
Onde ![][image72] e ![][image73] delimitam os intervalos estocásticos de perturbação de Kelemen et al. (2002).1 O integrador calcula o fator de aceitação da mutação com base no quociente de luminância ![][image74] do caminho 1:  
![][image75]  
Se a nova cadeia for rejeitada, preserva-se o registro anterior e acumula-se o peso cumulativo na posição de tela, mitigando a variância de oclusões severas.1

#### **Prompt de Direcionamento IA (MLT)**

"Implemente o Integrador Metropolis Light Transport operando no espaço de amostragem primário (Primary Sample Space MLT), conforme sugerido em 11.metropolis.pdf (pp. 18, 25-29) e no artigo de Kelemen et al. (2002). Em vez de amostragem estocástica independente, utilize Cadeias de Markov para mutar caminhos prévios de alta contribuição (através do hipercubo U \=^d), aplicando Mutações Grandes e Pequenas. O estimador deve registrar as amostras no filme baseando-se na probabilidade de aceitação Metropolis-Hastings." 1

## **Seção 9: Conclusões e Recomendações de Engenharia para Consolidação**

A transição arquitetural para o algoritmo de *Path Tracing* estocástico de Monte Carlo de múltiplos saltos, fundamentada pelas especificações físicas de Kajiya, Pharr e Celes, mimetiza com exatidão os fenômenos de iluminação global macroscópica em ambientes virtuais poligonais e analíticos.1  
Com base nas análises de engenharia dos componentes propostos, as seguintes recomendações devem nortear o desenvolvimento da base final:

1. **Proteção contra Grazing Angles na BRDF Microgeométrica:** O cálculo da BRDF especular de Cook-Torrance sob ângulos quase tangenciais expõe o sistema a imprecisões numéricas extremas devido a arredondamentos infinitesimais no ponto flutuante, podendo corromper o filme de imagem com picos de NaN.1 É recomendada a manutenção estrita do coeficiente de salvaguarda de ![][image76] no denominador analítico do estimador.1  
2. **Tratamento de Offsets Dinâmicos de Normal:** Deslocar a origem do raio estocástico subsequente utilizando uma constante escalar estática linear expõe o traçador ao artefato numérico de auto-interseção de raios (*shadow acne*) em malhas poligonais de proporções e escalas discrepantes.1 Recomenda-se a adoção de offsets de normal adaptativos, calculados em função do tamanho e da distância local da primitiva planar intersectada.1  
3. **Estratificação no NEE de AreaLight:** Sorteios puramente uniformes pseudoaleatórios na amostragem direta da superfície emissora podem induzir ruído granular acentuado nas penumbras de sombra suave.1 Para acelerar a convergência do NEE em MIS, recomenda-se que o motor herde e processe amostragem estratificada bidimensional (*jittered*) na superfície da fonte retangular, distribuindo homogeneamente as frações de oclusão do raio de sombra.1

#### **Referências citadas**

1. Arquitetura de Path Tracing com IA  
2. inf2608-proj1.v3.pdf  
3. INF202608 \- Fundamentos de Computação Gráfica  
4. the-rendering-equation-123av1m206.pdf, [https://drive.google.com/open?id=1TIBlo4FB4SW5NkoSoLS0-j-PBsJfS3L2](https://drive.google.com/open?id=1TIBlo4FB4SW5NkoSoLS0-j-PBsJfS3L2)  
5. 8.tracado\_de\_caminhos.pdf  
6. 7.montecarlo.pdf  
7. Image-based Lighting \- Graphics Programming \- Part 10 \- Chapter 2, acessado em junho 5, 2026, [https://www.mathematik.uni-marburg.de/\~thormae/lectures/graphics1/graphics\_10\_2\_eng\_web.html](https://www.mathematik.uni-marburg.de/~thormae/lectures/graphics1/graphics_10_2_eng_web.html)  
8. Visualize the output of a Trowbridge-Reitz Half Vector Sampling Function, acessado em junho 5, 2026, [https://computergraphics.stackexchange.com/questions/5053/visualize-the-output-of-a-trowbridge-reitz-half-vector-sampling-function](https://computergraphics.stackexchange.com/questions/5053/visualize-the-output-of-a-trowbridge-reitz-half-vector-sampling-function)  
9. 10.metodos\_bidirecionais.pdf  
10. 11.metropolis.pdf

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAXCAYAAACoNQllAAAEaElEQVR4Xu2YV4hlRRCGfxPmLGYZVMwiqBgRH4wPYo4PRsw+qIiiouCAiAEDomJAWROmBzGBmFd9MGdRMOeAiKKIOfzfrdNz+9ace+/sMLs7wnzw755T3afPudXVVd0jzTDDdGN5a/Fs/B+xRjYMYlFrR2sPa7XU1sbq1ovWspWNMVao7qc7x1jXZGNmA+sB6x1r1LrQ+sl6xFql260HHPG8dVRzv431s/Wv9VTpNI/YyfrI+tr6xrq9t7nDS9Yn1vuKvpc39gWatjOa+3GcrRj0cGvhyj6iePBja6nKXrhU0c4LCktbn2veO6hwl/Wj9Y+1bmpbSDH5z2j8strW+tPaMNl1hfW7tXVuaDhSERHnJfsyigjbPtkBp80vB71pna745hIhNRdZB2Zjw60KB4+xj2KgQeuPHEOfl5P9FOvtZCu8oPnjINLEPdZy1i/WD9YSPT2kZ62Vk61A7v273JBUv7R+VTihHywZwpWX1Txm3ZdsBfJSm4OIuoOt460tU1uBZbC5tbOiMvL+k61j6059YNyTmuvrFRN7XLe5M96r1X2mBEOH05qbG8aa22EJ0e/DZP9AkYPaaHPQ3opcxo/Y05pt3WktWfVZx3rXmmWdqUikrymcQxpYsdu1FcbbqLneVPHdLLkCTr+6us+QS4m8Do8rBqDEDYIfRL8HKxuz/Id1QmWryQ4iIv6ydqtshDkV59rKRkTikALRgGPYMkxk2/B6uucb+HaWDpxv7d9tbqXj0EUUL+ZhSvMgcAz9Tq1sI42NGWkjO+h+RULHsTWXKMZhPGCL8HC3WXsp2vetbP0o+admP8XzxU7+Wanb3Mq9/MP+hbyC2sp3YRNFny+sxSr7FooX838b2UE8jzLnqtcB5DXyYoFJofQO+1FANJf8U2BCPlOMsb7GF5o2bioX5BQ+blCCvkXR57BkX7uxH5DshewgPvL76r5wgWKcUnbJTV8pnr1MsQQPadqGcbdiQjPs8XjHc9aVqa2NJ8sFNZ8HD+q29cDumLxBBclQWXj2rNzQwNFjdnXPrpbyyXM1T1vfqpuor1IseSZtO40v0f0guXICqDesBaKPSs33sq0ZBpPZgXMWpRvP5upwtCIsB5VWlsyN2WgWVCQ6oohrYEdL/9qh61m/KfZThVHFMqNwHKGYvM2q9n4Q4W+p+77MLMUEDUv0pBFSyhhbKX4MJZtIudh6z3rU2qHq18bN6o0SYNZZFiRkxHKhggH7LvYmT1gPKZY4SbRmd8VMZxGRa1b9CrsojkhECOKIwZksQ65kwoaxseJ9PXD2YtN2qOIEP9Lb3Bfyz3fqTd4TYVVFwqSS1rAUcCqVsZwHWWIcgZjA2xrb3IRIfCMbJwvhzLo/JzdMEpY1jmiDpUlkz02o7ET1sH3hHEHVYe+ST8aTgQj6VLE34iwFJN1dFYm836Z0qmCiX9Gcr4ihsJeZqvAnT51oXaf429Qdiq1A218MphImmGPNWrlhqhjVxDZz0xWqNQVrhonwH1l888rSU83NAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAAAaCAYAAAAZtWr8AAAD/0lEQVR4Xu2YachNaxTHl/kaMlwuGTPeuHwgIhkTUggZ4vLJNV5TJEqGRHwxJFNIpszUdXGvcL+4yXBTREquWShD5inT/9/az3ues5yzz96vFyfOr/6951lr7332Wc9az7OeVyRHjm+VataQZVS3hmxgOjTFGrOMDdBAa4xKJ+gSdAW6GHz+HzrgXxSTPtAFqLh1ZBlVoXtQW+uIwx7oPdTLOmLCl3kC9bSOLGWqaNIUs46o3IEeQ0WtIyaz5dOy9UvDqmCljbKOKPwsmm37rSMmfAlOQD/ryHJmQmesMQrDRQM32Tpi0kb0OU2tA5SFOkNlgnFFqD/0Y94V0SgENbBGj0pQC2vMwK/QO+gn68jEZtEfHPcLLUNEn+OC4ygJ/Q0dgk5D46HV0EToLNQtcWlGJkBLrdHjX+gNVNo6Qmgp+t7c1GJxE3oIFbGOmDDlWaoWZnJ3SQR2judjEP7zxmEw23gtsyodfDa/o7axh8Gs5z1jrCMMpj1v2mcdAeUleluxTnTGLfNFn7EMeh58dqwULZMoJcvMnGRsXGZKeeMq0G3RIMfhATTLGsMYIRq4dM3qH1Bla0zDn4HSwbI8bGwM9EuJ1g7skuTTSDPRoPt9WAVotzeOCvvXudYYxlbRwLWyDtAE+ssaQ2Anfs4aA1he/JE8UTi49r2Ajnq2ME6Z8TDoFlTYsy2GfvfGUeAS9Vo0eyPDNYkNq+3fSkAHocHGXlO0V5sn2uz6LBQtxVRl0ld0gtp5NrYtb6HWnq0u9IM39uG7Ng4+85od0N6EWxpB1yW5dPkuA6BFwd9U8Dv5btz1I8FU5w22YW0O/QM9leTdaSS0XrQc2Ptxh/RhBvB5NYydcBOgr3cwLid6tOMPctQRzUoe11LBZeOa6MTxXm5ofOZxaAX0SJIXeLZAx6AuwXiLJL7fp6vocxjAUNpDl6FnojcwS66KvtR90Zfnls7F3sHFmzPOxZew5eC9DKKjdmDr6NkcLGEGmmsgn3tCPs5m/tDzohNWz/hID9GF3wWL2c9nccxS48bhZzt3WJauYwG0xBs7WNoMuq26AmGaaB/mYHtxwxs7GCDbSHNz4Y+bEYxrSXI5WZg9zOhUcEeub2xcMuwGxus4AWzKHWxlfvPGjrWSOqAFAmeFiz9h+R6BBiXcefDfNHdF2xgH1xYGroNnSwczxi4d+YHZw42D5U/Y3DLLbXP+C/RK0k/UJ8PFeCc0DloDDU1258Ed7qQkSoTHLwbCBS5Tv8bTxGhrzCec2FXQWGi7pD5ScQNcbo2fAy7qmWDpsC9qKBrkjdAmaJvo8SYMBi3VrpxfmHnplgVuFKycKD3kF4OtQawjzFeALVXY8S1Hjhw5vhs+AIg4vr5T1oJiAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAbCAYAAABFuB6DAAAA3UlEQVR4XmNgGAXUBMxA7ATEklA+CxD7AbE6XAUULATiWUD8GYiTgHgJEOcA8QkgroApMgXibiCWAeL/QLwbiNmhcsFA/BuI+UGcWCA2AOIQqEIbqCIQCIeKBSCJMUwG4q9AzIYk1swAUWiLJEa8wstAvAdZAAgOAPF3IOaDCYgA8T8groUJAIEEA8Qj5UhiYN+BrJiAJLYaiE8xQMIUDqYA8Tcgng5VcBCIW4CYA1kRCFwF4r1QtigQCyPJwYE4A8TaenQJdNDJAFFYBMTyaHIoYBEULwPiRDS54QkAnb4poic4NxUAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAABIUlEQVR4Xu2STytEYRSHDxGlST4DjT/NBiU7xcZCWdtR2EhJrNhZSeIDSMnGn2+gmc+ALGwsxE5ZWZANz+ncGeeeujM1VlP3qad7z++83fe+vUckJ6e1GIyBowunsD026jGGdzF07OEPzsZGPU5xOoaOGbGPLoY8kz68DJn+0VDIHrAUskzWccHVnfiGuy5TKtgWskxOcNTVA2JHHXbZPF65uiEXuObqTXwXu3FFn084XlthTOA+bmN36MkGfuARlvELP/EFD/EZr6uLE85wCztwFY/TbZF+sXHSI7+KTcEyfieZfqCnttom4dbVc3jv6hRFsZ2rFMQ2jNzgjqsP8NzVTaEXtpS864884shfuzl0VnWuV8Q2mEy3/0dvDHJajF9U4ivCiQpKHwAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAAAaCAYAAAAZtWr8AAAD70lEQVR4Xu2YR4gVQRCGy4yYI0ZUxJyzmCN4EROe9LCKATyIiJg9mVEMKGIWQTFiwoQ5gR4UFAUF01MERTDn7P9bM25v7bz3ZlzFQd8HPzpVM296uqu6qlckQ4Z/kcJQeWuMERxfBWv82xSADkHtrSNGFIXOQw2sIyw9oNvQXeim9/9b0GH3pogshjZaYwzpC92BKlpHFPZC36B+1hERDuYVVNk6YgozY7M1RuER9BIqaB0ROQ1NscYYUw96DzWyjjDUFY22A9YRkWaivxPnohDECWipNYZhpOgHT7COiEyDnlujR02oo2RHNFea20LUCC8JVbJGh4ZQDWtMw2romjWGgTnOiWttHRFZC120RtAc2grdh9ZBC6C50CzoElQ7+9a07IYGWaNHCegtdME60jBR9PvLWkc6HohGCtuIvMCQ5wRZdkFlRCf2I9TH8V0Vncgw1IJOWqPhLJSwxjQMFJ24SPtcHdGH9luHR2nRZjEMbGlmGlt+yZ4YpsMxx0euQ5eNLRnzoJbOdSFojHNNGI07jS0dTUXnoKt1pGKU6EMM1yD2SPg+h1V5vDV6sGB8haY7tiLQJ+i4Y0sGF+CcsY0TTU13YftDY53rMFQXnYNe1pGKLaIPtbMO0Bg6aI0puActt0YPRgLf08mxdfNssx1bMqqJ9poum6BtzjUnl3tspJQDXUTHwewLDfs3Nqy2ujEajkBDjJ2TORlaCBU3Pm70yU4cy6B3kjM6OMkPRbcDH1bFIOpDj6F83nUV6Ibk7ARGQPuca1JMNAs43lbG5zMc+iLhtyRpITrT9mP5AqbPa9EX+zDN/KMUJ3SY4yOMAB7XgmAR4MT5Jwq+4w004OcdIlmi41nl2HwYTU9Fz5eM0BeiBY3pz4LEfe0D1MR/ALQV/Q62Pnw+IcE95hzRip8WhibPaBw4B8p9IiGaak9EB/MZ2uDdTxhp7LBHQ5NEz6PupJIs0T3LRi//CsHfZDScgtZ7//LDXDqIRiDPzEHMEB0ro4MLyEm4IvoNzJze2bf+gBXWPUIyjd2F8tku0bakSDAlzog2n1y9IJg+bDdsPzhY9OM6i6Ya+7ZUrY+tvC7lJHcDzN+z2wYXgRHuv6eUaDDYnpHfwoUKmtDfQk/RfsyHlbaNc+2zEjpqbCtEP4L7ZjqqSs5I/1VYIBLONTOEY7Pw1MRMS7WQeYIrs0a01E8VTRt26hZWv2eiKcLB8M9WHBj7NUYie69U7BA98/4OWBA4Tp5QFknuTGFRYsFhRvxx+DK7h1k4WZwolnce57gfsXCw9eFZMxn0DbXGPMJ9OFk0LRE9+sUK9m3drTFGcM+bL7mjMEOGDBn+S74DlOW89P1JGUwAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEoAAAAaCAYAAAAQXsqGAAAD2ElEQVR4Xu2YV4gUQRCGyxwxY44YMII5YEQEBRUVI6gvJkRFMYIYwAC+GBATKiIq4mHCrBgfVDBjehHDmVBBBLNi/n9rZre3bnZ37rjj9mA/+Lntqp7UU11VcyJp0hQ0alpDilDLGvKThdA8a0wRJkAbrDEsvaHHUCb00Pv9CDrlTgrJEOgBVNw6UoRC0HVornVkh8PQX2iQdYSkBvQJGmgdKUZn6CfU1DrC8gb6CBW1jpAskZxFYX6wE8qwxjA0EY2m49YREm41LvQw60hRekC/ocrWkYyJogs1xzpC0lX0+NbWAcpBfaCy3pg3NxyqFJkRDuaXxtboUAVqb41xYFXm/Wb7xe4WPTDshSxjRI/3F8OnFHQSOgPdhqZDW6CZ0D2oX3RqUmZA66zR4SL0CypjHQFw0b9Aa60jGS+h91AR6wjJYtGtZ2GE9pfoQi5zfHxoVqAw+NWKURMPnpvXqG/s8bgL7bPGRDCceYFj1uFRQWLLPasFH95lu+gbtawQPXY99NX77bMJ+iPhtiAjb5axMV2UdsbVoNeii+rTF2rpjF0OQhesMRGTRBcqXpN4CKrqjCeL3qTLEU/x4DY7a2xc2O9QMWMPYr/EdvttRBe5m2OrCB1wxmQj1MnYfLZBl6wxEXtEFyrohHwbJ6wxgB3QfWv04HbhQ7Fj92Hu+gZddmyJuGnG7LBfQYUd2xpoijNOxnnR3Bwa5hY2irZ/KgGdhkY7NkbTUokNb7JKdGtZOxkq+iK6OzZWG5bnLo6NW7C6M3bhPbbwfpeE9kJHo25pBj2X6FbkX+assZEZWeH85dYYD4YwH8I2iu2gc9BniVYR5qW2op8otqvlG+Z5ahs7YdKmb7A3Li/6ibQ6MkPJFH1h7Oks3P7PRJtaHsvCw3NeEd1eH6Cpkdkis6GGElxgCBebUT7OOixsuJ6IlkhekNHwVPRm3omehKWWSdqHrUMrb44b8qS+6Hl6xZr/wy3J1oA5jOe7KrFR6sMUwIUabx1ggGii9henjui5OP4hmujdaOa9ToN2OTaX5qLHdrSO3GKlxA9XLgjbARcWAd7QIm9cV2IrlWWEaHEJghWzkbHx+9ItNC43RBvdILgl71hjbsEoYihza8w3PjIKeivaTvjwwblQPR1bIjZDDawxBzBiXohWQpvgmXv5HxKmizyBoX1LtENmrrJwIa+JVh/CzxnmPn+hkvVLHSSbVSgB9US3+ALJ+rVAG6so81SewcrINxIPbgW+LSb7raJf6cwTGZI8H4yUHHykJiDoU4b/4WRuZo7Ld1iq3QqUSrBRZuSmSZMmTYHnH6+uuFMaUdMNAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABjElEQVR4Xu2VvytFYRjHv0giocRiNVrIYDCIxcpCFotYGCxEmJRR+RGDJAb8C5RuBqVkIaIom5AIC/nxfXrec3rP0617HHdR91OfzjnP9z3nPe+Pey7wz8in7XSS1pssq0xAO2qhV7Q/kmaJIvpGO9y1dHpHC8IWaWiGNtyhe7QuGoeM0TnvuotWuvMheuNlEQrpKvThU+74TWf8Ro4maDZgA5JHj+iwDYRSukvXvVov9GGDXi1gmX7SahtARzptiwGjdI2WmJp0JFPpI/P+QFOmLnRD7xNk1DK6jGzQD1ps6m3QF5B18GmFrpls7Ubo/bG4hM61ZZF+0RqvVkafoS8QmPLytMjbjEAbH0OnQpSaeEsPw9YJka18Su+hHV3Tc3rm6heuPhvc8Fc26Suim0Pog3bUY+qJkMV/ods2IPPQjmptkIRO6MPkaNmnj4i5bTOxBR2R3dbCEz1w5xV0HPpj/zWyJrI2KzYgVdCRvkP/CmTnpfs8xaKBLtByGziW6An0mxh8qXPkyAH8AMvgUBEyQ0dSAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGYAAAAaCAYAAABFPynYAAAEyUlEQVR4Xu2ZV4hlRRCGyyxmXXPOWTErmDCAPphAUQTFvLIGFAOKASOoqJgVxbCuOYuKOaIPRnR11QfDjgomEAyY4/9NnbPTp/ake+eCC/d88DPT1efeM91d1VXdY9bR0TFrsGw0DCnLRcOg2FhaIhob2El6KBqHlMOla6JxPCwkvSZNkX6WVi12V8JzX0lrxo4hZTbpDenk2NEvF0rvS6dL/0rbFrsreVO6NBqHnK2kP6W1Y0c/TJcmSytK2xe7KtlB+kZaOHZ0jO48d0djr6xgHiXHx44GyCtXR2PHKNtJf0sTYkcb5pVWl440X5iDs/Z8yTNVzC79buWLOYe0o7RM1p5T2kNaa8YT7an7zDzm0c3fMgjID2tEY8Li0mbRWAFVKnO6T+xow87Sk9KI+Zc8lbW3Tp6pYnnzz+wWO8St0g3ST9Kh0u3SMdKr0qnJc01sIr0TjQnnmf8Nu8aOPjlOuioaE16W/pLmjx0lsMgUUVfEjl54UPo8GhsgVJmUmOA2ly62sYV7xtyzYW/zpNg2J91sHnlVUKbnkT5e8mqKqKgid4SVg72Kd6X7orEXPpUeicYGDjLfQ+cO9gOljcxDmEFsk/Ttl9n2SmxVLCrdE2xERnSE96T1g60f+O4Tgu0IK27rS5kfDVjEnF2s+v04/AvR2Ba8l8k6O9ibYBA/RmMCWwKhnC5c7nFtSvFjpf2T9lzSt9IZiQ2es+JE9cv9Vry94KD9jxUdC2d5IGnDtdKWwZZzk/RKNLaF5MlkkZx74RDzz1WFPp78bLC9KP1qfpht4kbzycmhKOF96yS2PaV7k/Z4eCu0OcF/acXC4jLpqKTdxPPSHdHYFqoqBkxOSGHi8fANpNPMQzZld/PPcZiKsFh425mJbWnz/HJKYlsss5fBGeDopE2Efmdj+YqfH0ubznjC2UK6yPzkTdWZUve+r6X1st/5HAv+6Fj3qEOQh/OtjZ/MD1t3FTx/fjS2hQqKQ2IKg8UbP5CuNM8XMQflHnxAsANJnr7LExtJ8HXz0jlnunnlVnadg8PQh5cSeb+ZRxuD5aZhxGZOrIzlJPN3TLTi+6HufQ9Ln0nnmC/49+ZjoJJku/rBio5yorSa+YKWweLinFSlfTHNZr6A3NB8P2UiFjE/j5RtWSNWnps4dP4iXWc+eS+Ze0704LvMJ+qwYAcGTanM5HxhXp2xvfyR2ViEtGylQns7aVPGT03aUPc+niex54vBofuWrM07idg0l3Ge4QhwW2JLWdf8s0RwzzAw6nK2rQgDpXysgwV4LBrN79xIysBN9YSkL7KvuXdXgXenUbag+aJFnja/58uhZC+btLr3UaiwE6TglEsGWw73hJwFy2CLi47RyCTpcfO7LryhLBrONR9cHSuZbzFp5UJJiaecldjquF5aJRr7gJyQOxiL+aG510YG9T6+m0hmZ4kFAfnvE/MI74mPzD19svkClPGE1R/uci4xr2ioXrgAJfGyMIQ+C1cHh9G+q5YAZwnOPZw9WKSyomSQ72Ns/JuEKF0g9GFjTuLW3QjnAyoOqqZ4QMxpc+0AbDNc47BvkxCnZLrTyrfIFA6cddtcP9TdKgz6fWVzxH8wObCTo/532PcviMYhhYglMjs6Ojo6OmYJ/gNomOYpH90xVgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABACAYAAACnZCtBAAAJ4klEQVR4Xu3dB6wsdRXH8SMgCBaKCHZeAMUeQ1ARRBIhSpFQVNSIJiiiotg7loAmIMUSFALSHhAENfYGFq4lASMkGolKBHygRuxij2L5/95/Tu7ZszNvZ/fu7ltyv5/k5M6cvbt3d+Z/93/2P/+ZNQMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAu6o3ldgtJwEAALAYXlziASX+V2LfdBsAAAA2sj2tFmoAAABYUKcaBRsAAMBCU7H2xZwEAADA4lDB9q6cBAAAwOJQwbYmJwEAwF3fA0tsnZNTtmWJa3JyI3tHiTfn5Aw8Lydm5IAS38rJCT2pxN1yMviy1RMcFp3a3CNzcgLzaCsfyYniypyYo6/YhtuA6PYtchIAMNotIX6abmujN9trc3JGDimxQ05OyY1WX+9Nzc/tB29upftsnpMz8LsST8nJGXhPiQ/n5AReUuJrJc7LNwRrc2JBqc3pfyF7WomflbjZapsZZR5t5XtWr58XfT2tz5PawKiC7c4Sz8hJAMBoj7DxzhL8c4m9cnKG/lni0Tk5JXrdT8zJDifmxAypo+9TPD+5xKtzsqfNSvy1xGPyDRPQdjzIuoveb+bEgtMFhNva3O1Wt9so82wrF6f1b6T1eVKxOKpg+05OAAD6OdbGK9huyIkZUwf0oZyckjtKbJqTLVRAqbOepz4nAuxf4u052dMeVvf7JvmGCfwxJ5Jx2teiaGtzfV7HvNvKU0vcN6xfHZbnrU/B9q+cAAD08wurhUtfp4flx5e4vMT5JU4r8d4Su4Tbs0/nRPH3nEg0D6hPRzmul5Z4Y052OMoGn4Pm1321xPdLnFvidVbng3V5TU4U3y5xz5wMNPJ3eE4mT7fJCzbtt5Vu14usdtI6RHjW4E0DrgvLsc2cbLNpM9k9Sjwo5fYrcUrKRW3bpi2X5bYiaiN/KXFpiVeVeOvgzQN2zwmrh6672pcKpFhcLoXlj5f4U4nPWG0nOtQ+Lm3/Z6Wctn/btAh9uGor2PT/8c4SnyzxnyY3yT4BgFVNnUvfwmUnq2+qTkWaaO6KUxHTxTuju4dc7gyyx9lwBzgNv7Th0bVt0rq70GqB5VRoaO5XLBz+G5YjdbSvb5ZVJG7VLO9o7Z1b9O6csPoVUjrpQ/F8qx2cryv60vOdxnZ9kbUXGZEKDjePNpN9NixrjppT8SSaFpDlbfOwEl9IOW8vuv/BzXJuKy8s8WwbfLz82G7bEleE9fi8/NB12/yvq8OyH37WvMIXWL+/qxNC9CGkTdf2V/Elx4S8nkdu0xpRO6NZ1t/4QLM8yT4BgFVNb+JxHpc++XbRm3funDVvSWfEiU5I6Jr0HA+9vdaWJ2QfFvJtHmLdHc1KtD3mETnR+FwT0Q9tsOjQXLs26ti8kFKR5CcTqHMeRaNP2WUlPtaEOsgfhHVFX3r9t+fkBN5voyfXe8HqZt1moseWOCesx32mDwPy8pBzuX1o6kA+61MjV6L7qxiXtrZyZom/hfX82O54q0W4qEDybSReCLWNZMZ5YXG+4EetjrC5rr+rfNso54a2v8+dPLv5KUs2XLDpsf1Dnk7cONQm3ycAsGrp8gU6FT+6LSwfabVDdve24cM56oz8jVyjTj7q8Kjmp9MnZr2Zq3j5ScjHzk0dezzkKvpicj+MkqlD64q3hd9rkzuvOFFcoxl6Hvdq1jVCkA/D6f77NMsaQdEJALJz89OpKNIEdhXCn29y2u6+nbVNtJ0VkR5Hc9Q2ZCWHRPX8dZhqpeL8tV2tbhNt/zhik9vYLNtMLh7V8X+iWdYHE83dEx2edCeFZZfbnPZjPOHgKqsjWKL7e6HS1lZUqPu2vn+JtzTL2zU/3eUlXtks63WpmFXc1OQ0OqsRuywW9rFg0z5+Q7Osv6u2snb55pF8+0vb9j/Q6uO6JRsu2K4Ny34JmeNssn0CAKuSDoP+22qHu87qGYPqWI5ubo+HsbrmyNzP6n2Uu8AGR+p+FZadOjJ1GBphySM88TBSnLuleThfCusr9eMSf7DaIa+z+hy0fHNzu0bKXmb10I3PMVtjwwWeDuOp4/quLXfc9ynxIxscrXim1W2hjutCq4+jztg7Nj9EpKIjbmd1aqPOSJy0YNPojZ5HLhjGlQ/1PcFqwaIRlEjtzMU2o5h2m9Eo1SUhr1Ei7Se1b213tXddDsMLaxULtzbLkbc5TerX6Jj+9roSv7f6/LUvxe/vo1FrbLit6DVoJErFVCyuNCKqQ5dO7Ubt6udWR6N0OFGv3duh/lZ8baIiN27DWLCpyPJ2pqJYhXMuaEfRc9f/R9v21wc4FeluyYYLNv1/fMrqfjnR6py4SfcJACDRm7reTF3sVH5ry4dNn2P1TVxv0m2HVLJ4Npt+30ew9irxj2ZZF+SNj6XLW4yafD9NGgWIowbuhrC8gy2PmPictOjhaT12kpqD5pTfu1lWhxW38/lhucukBZsOO/W5bMgop1gtYiKfyxWp8HCxzWwa8l0maTOXhWWn4kJUBOdCOB96VkExTpvL949tRfyQb3wt7ticsOXn5885yqOuecQtFmy5bT40rfeh5+z/D3H7iz6MREs2XLDJTmFZI4ZunH0CAOiguTSaABwnQYsmCOuMN3W2+hSsEas4Idn5IY++NMKkN+l4CFajAurg50nzfjQ/RwVZ7DDViftomEYq9rX2ESqdETcOzeXRdtbIk9Phtrar2E+LXkfbmat9aUTxTqtnGKt4dXuG5ejBVucuzaPNqHjzEak+VGDEbaE295uwPorff/eQi23lfVZHkWLR4jQiOQ49xglhXcvXh3WJBdusqY3G/88lay/YxpX3CQBghPwJ3WmOkjqPtVbnnehQYHZUTvSQR1w+mNbnxedUZTpsqnk9F1udbxQPRblX5MQIGlnI21mjfG0FzbRoxMfn3E1CRZH2u76OKsr7L1KRpjMtZ91mfD7UOOKoj9rcyWG9j3h/F9uKRvyOHrx5vefmxJhusXpSTjTPgi1bsukUbNK2TQEAWFXyHCsAAAAsGAo2AACABde3YNPZsjqxAQAAAHOka5r5JSlEJ5XozM5YxOnK96JrqV0T8gAAAJiDI23wq510tqvoWljumOZn38u1AAAAYIV0zbI7rJ55+ut0m+girTpzVGe4nhfyt1n9Qm8AAADMmF9Zfl2JgwZvWk+X+PDLMfg3PgAAAGAj6PrCeb/Iqy4UrK9dUvE2y+vAAQAAYAwq4o5olnUR39OsnpgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADW+z91PbmcHIDJKgAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAADc0lEQVR4Xu2YWahNYRTHl3meQqZ0EZmSMk958UJSyJAyDyFlehAR90FJERle5MFMlEQpw4MQMoWkzBEyhUjm4f+3vm1/e9lnn3Ode86Vzq/+3b3X+s43rm99374iBf55NkFPoTbWUVbUg6pZYynSGnoJlXPvbK966M6OKlB/aDDUxPjiaAqdh+pYRykyBdrvvXeATkM1PFuJaQsdhG5AxdAK6C10BGoUFovAyTkHTbIOUBu6CT0RDUfWWzVSQmQd9AC6Dd2Fzng+RsxiaDZ0AJrj+chq0f6WN/aMWCTaqfFQRc9eBF2A7kM1PXvAKlF/EGpxzIDeQD8kfmIGiLbdTcJ6WkGnRKOnBfQd6ux8AZzQZ9A0Y0/LGugT1MM6HBNFO7vM2NkgI6CPsVv2iE4k67hsfGQgtNHYuKLF7pmDfyXxKzkZeghVto5UDBXtiG3Qh7PMMheNnSF23djiuCq6cgxX1mMnaDk00ntnhH0UzSOEg+IExFEB+gwNs444mGQeQx9EB5WKWqIh9drYj0nqjgQwL+x1z2NEB7wrdP/iJNTQe+dKMiMHSZDJap7otovjFrTBGuOYL9oBnnFJcEVYjknF547oHk5iOjTTPVcSTWBckcbOxsR0yT37MFFxCy2E1kLbRVc6jsOiUZSW46IDmWodBnaa5Q55tiCUmJCS2A219945CNa11L0zYa0P3REYWUECtdndh5n+hTVaONtMVGy8p/FZOFCWm+vZipyNHU7iinnnynKiuJXYB+7f4ZESJYfR8E3ik9pveH5yX1Jxx01AR9EyjyQ6y11EB8y/qWgn4f712Sn629GiR0/9qLvEjBPtY9pMzT3JhpMS1lbRMqzUp6WzjzB2H+7dWdYIekuY9W3m/xu4PRgxadkm2vAo63DwkvBVNGQs3F/8LZNKKvZBnazRwYHy90xI2cJx8JqZFt6TedSclT/DinfXL5J8i2GYb7ZGBwfKulNdSSeIDpj3gGzh+c5BZ0R36JroEcOVXCl6rh2F+nnl4tgCnTC2utA90bOdeg8tiZRQmEN4h+ZXT7Y8hxZYYxJM/V2hsaJfSMzAmcD9y+Mg6cjINc1FT5vgXM8pPAb4BcQvmrKCGX+HNeaSIdA7qJl15IG+onki7/8F4R7l1S+fMLr4WTrIOvJFMdTAGnNIL0l9ty5QoMB/xk9zwK2QQZfohgAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABG0lEQVR4Xu2TvUoDQRRGr6YylYRgYylEJKl8gBSJDyAGS1sV6zTpAmmsBCFNqjSBGF9C0MKAIqJgI4jYmE4bsRB/zjiz7M5lNo2VsAcOO3O/Yf7YEcn4KzV8wGec4MCPf7nAR7wXO/bASwMc4St+4ZLKctjGU1z0ozA32MRvCa+8j5u6GGIZj3Ee3/AF894IkTNcULUgO7jn2j2xu9uOY5nDq0R/KkNcce2K2MnMsSPq2E30p3Kt+idiJ6y6fgcbcZxOdF9JNsROFtXNfRXjOJ1die8rwvwKT/iBJbz043RGWNZFaInd3TkeqizIDN65r8Yc613shOsqC7KFtzirA0cfP7GggyRrYt+hWdlonpF5o5pVHOtiRsa/5gcPXDQmGhr6FgAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAZCAYAAADnstS2AAAA1UlEQVR4XmNgGDKAHYiF0AXRgT0QfwDi/0B8HE0OKwCZCFLcjS6BDbgwQBT7oEtgA61A/BeIBdAlYMAIiC2g7KNAfA5JDg7kgPgwEG8G4hoo/QuI+5AVgYAkED8C4hlIYm0MEPf6I4mBwTwg/gnEwkhizQwQ9woiiTGIQQVBTkAGh4D4PJoYgwMDxDoPJDEnqFgAEJsDcQZMgg2IvwJxLJQvwgAxEaRYAYinALEeVA4M0oD4ARBPB+LZDBCTQR7eB8STEcoQgBOI1ZD4LEAshcQfBXQCABPEJSomqrbYAAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAABp0lEQVR4Xu2WzSsFURiHX6zIQsjGUpHYUD5WFr42NiJLCwsfKTsbEcrGhlI2VjYK1z9g43tBkUTZkGTDRkiykI/fue+cZubt3rl3Jt0jnaee7pzzO/M2b3NPc4gsFstfohnewHv4AFf8cZxjeAuviNfO+9LMkg37YKkMUrEGn+EXLBNZDpyG+xSh8C/RDzfgI/yGdf44NedwlPjmRG9oFvbIyQwyAjvgHEVosALGYAF8g08wz7eC6ACWiDkTjFGEBgfhsHO9RFxgwI0pF556xiaJ1OAqrHSuq4kLqL+spgUuesYmidTgmRjvEBdpcsYzsNuNA8mH23AvibvE9dUa5RasUTemSegG9f7z0kVcRM+r/VfsxkbRDdbLIBlD5O4/jfos3MEPWA5P/LFRdIMNMkjGOqySk+QWOoQLIgsii3jPtoWwKH5neoRqUD3MpfMrUX/Jd+JinSILQn1exuFECOXBIgjdYKMMEtELL4iPP4lYhp+wUAYGmSJusF0GXlqJz53qDSnVEU2dSSW18EhOGmITXhM/6wt8JT4bT3oXWSwWi8Vi+ef8AM8YYcZoiFLJAAAAAElFTkSuQmCC>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAZCAYAAADqrKTxAAAA+klEQVR4Xu3SsUpCYRiH8c/AlijBNpOwxEmwbOsW2hSvQgUdJHBxcHLQwQIbnTVQ9wRpk1Y3L8AxaKsU6vk8nnzPm2Fr0AM/OP79PHAOGvOnS+Bcjz8VxwAVVDHGieeEKoQHxMRWR018/lYLF2q7Nc6NNnaKez3SFCU9ujVwCT/C2EUOTzgQ5zyNsIcZPjDHK47lIVkQvdX1EZLYxwR37iFdCgU90jVe9OjWxJkeqYyFcZ7P0yGejfMCZPZZ3pFX+7I03nAltgAe0YVP7F/dGOcH9tV20MYQWXlIZ++4s7q2f6PI+qvN2efp63Fb9lUX9bitDKJ6/O8XfQJ+ASPc9BwSpgAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAZCAYAAAAIcL+IAAAAq0lEQVR4XmNgGLqAEYjDgVgNXQIdOALxfyCuQZdAB/xAHAfEPOgSZAFjILYGYiZ0CWQwD4jrgfg6EM9Ck4ODTCAOgLLnAPEbJDkU0IPEvgLE+5D4WIEwEP9jgDgBL5gExD+AmANdAh1cAuID6ILoQIQBYm0dugQ6CGGARJ0NugQI5ABxDJS9AojvAzErQhoBQCaAPJAIxD8ZILGCFfQD8V4gXgjESmhywxMAAOgYGW0J8M6vAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,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>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFkAAAAbCAYAAAAXmyPIAAAExUlEQVR4Xu2ZZ6xlUxTHl26il8EgefigBtFriC6EIHrG6D26KNGGKFGiji9CMogSQoQPgskQg9GDiM5kBJEQNbrg/7Puyz1n3X32Oee+9+SN3F/yz8ystc89Z6+999pr7zH7/7OotJu0yyhoQAWXSfdLZ4yCBiRYVnpXWiQ65nWWkSZEY58sEQ0tuVw6UVogOkbAKtEwUpgB20l7SpOCL8XK0svSUtHRJ49Li0djQwjGs9Ly0TFC7pQOjsZ+WEt6VHpHmipdJf0gPSGt2G1WggF5UToyOjosJp0VjRmGpIejsQVXSMeYb3xFlpTel76QvjTvY2xzszRX+lD6WHqh4GOyfS1tW7C15nzzl0+RFizY6fQr0hxLz67rzP3zFWykjvOkGdKv0k8FXx0XSPtHY0NWlx4x/+YqTpC+k/629MTYyTwOm1q5T3CueRwWCvZG3CD9Jm0eHR2OMP+oS4Kd2cFM3zrYV5BOkbY3X7ptgvyS9c6wppCLCRyrpwoqDiYS/Xk9+GB36dZo7LCw+SxnoFqxj/kLq34YyLm0eTXYT5PeDrYIqaZpkLeQbo/GhpDqpkvrBHvkTfMZSiqgT3GCMFAHBFuRi81/ozFsVJ9Lv5gHsgp2+7+kb4P9KfPlmaNNkKeZz/4U5P6VorHApdJRlq9MGIgHOn8/xDzI93bd/8LKmxhsRQ41j0WuTYkzzV90W3QEGG3asRkU+cg8J+doGmTy3GvWmwdhaekc6cLo6LCe+QBtFB2B481LO+B9bIK/W3fwKEH5hhykVGKxb3RUwcbEA+zGOfg42j1WsFGD8oF1+alpkPeWrgw2Ar6+dJF5qnre0iuOJXys+R6R4z4rpxP2GPrF88Cmd0vXnYSDDs+cHB0pGEk2Ox4gF+YguLQ7vWAb6tj4sBwE+edoTPCg9eZTgkzdu4d0rfSpdHSphdkG0jXSlsGe4o3wb2YwE4WUSTzIx/uVWqT5xnqLgCTkOHILSpVmw7AUafOZlXf9jc2DzJ85CDI5Pwfp4LloLMCq2ca8zn3IyqcvSk9mVS4Xw9rWzcdF7jHvx0HSLGm5sjsJaZMBaQSNeUFqCQ7DSYc2hwU7NSn2upq2SZCPM69UcnCCYzbPsW59u6F5Zzmd1kEuTi3xrcz7QTqK1VOK4TRJemrEXeYvODA6OtCZP6VTo8N85vAsh44cBJkDSY6Z5rV1Djq3g/lsptZd1XzjPtvydfEwpCPyewqCS19ujI4Ea5i33Tk6qphkXpbNtt5lQu77w/IjRgqpq2ufNh/5qpS0mpU31Bwc7almPpGuNz/671hsUAHBpZ9VVwOHmweOM0Mdu5q3JdiN2Ux6y7wcY8ZeLX0gPWn15/Tp0jPBBgwYJyOWNidCRCffM79IL0JZRj5swvzml+jMZn6fiZC7ziTXMyCkK0SVkyoD+Y255tcBdZwkfW/lq4dG8MAm0mTzm7ehsrsS8vFX1v8xGDhGt7kipSLgGoDnmszi0eYO6aZoHEuYWdxmcanTDwxsXbqJUNYxEbgb4f3/Jeual71rRsdYs5f0o/V3qU1ebVIZjBdIobk7njGFPHd3NNbALOQElzpGj0fYFLnX6Ouac7SYau3+N4ILFnb1eQWO/G36N2DAgAEDxhH/APH28yCUhi6pAAAAAElFTkSuQmCC>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAZCAYAAADnstS2AAAAtklEQVR4Xu3OMQtBURjG8bcoKYOFgax8AdnZbQZlZ7bJalAMdma+gEE+gLKZZRarYubvnOP23pNbNilP/ere533qXpF/vpkk6ij7Bz8d7NDHGlPEQwuXLo7IuPc87qgFC5csrmioLi12PFadyQg3JFRXFTseqC74XE91KZyxVZ1JS+x4orohTiiqzmSGC+ZYYIMlSnr0ygEr91xATt1CeR78/41MU+y44h/epY09Yv4hKh8Pfy0PowAeB5eSriQAAAAASUVORK5CYII=>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA5CAYAAACLSXdIAAADuklEQVR4Xu3dWehtUxwH8GXMLG6ZkjJkvnXdIopSJHkQkelBHigic/eFQklJiYgHpSSFKKEMKXW9yBPxQoZ44UGGlCjT72ev7ayz6PwN/z/7uJ9Pfdtr/fY56/9/XK299jqlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABbpK0ip9crAAATc0Lkzcj9kc3dPQAAJiAnaqOcuAEAMCFnRE6s7R0i3zf3AACYgPea9vORb5o+AMCa2qYMK0aLbOoLE/RI5IK+uIp+jrwaebIMLx0AAPwrNkY+jLzb32icHdm+L07QvpHP++IqyhW1PSKH9jcAANZSrhpdEjm8q49ui7zYFycsJ5aX98VVsE9ZjlVGAOB/KCdsG/pi47PIuX1x4t7qC6tgfeSwvggAsJauj7wU+aJed5+//Zuc0O3S9F8ow3EWV0eui7zd3OtdE7mvq70W+aGrraQfI+UYO/fFKv/nfIwLALD0DijDxG2RnGC18pHjt/WaHozsObs9px37snrdO/JpU19Ju7k/x9iptnOM8ZcGLq3XUU5Cb+lqAABL6czIyX2x82xfCK807ZzQbdf0W/vV6zGRn2o7N+0/Xdt/xlNNO8cYz0Ebx9gx8lxtjz6I3N7V/olcsVsUAIA180zTzmM9Lo6cVubfgszVtPY3M8+JnFTbubftx9rOVbbcmN86ql7zGIxxUvVJma2SpTvL/JEiBzXtlHvoUn5mHOOIMhvjrsjxtT3KSdSpXS3ld25ekINnHwUAmIaPm/ZVZVjByknYDU09Jz/7N/3cT3ZWbb8fubu2Pyq/P0g2x8+3TL8qwzgPRK5s7ue5adtG7qn9A8tsJW6Uk8ocI/9WjvF65Ot6b+vIhZHHa3+Un+snfgAASyf3hvWP83K1qvdO5MamP34n97/1zuv6uc/tkKa/V9N+OXJTbT/a1FN/zlk7Rp611voysltXu7frAwAsnZx05dudpzS1fOy5a9Mf5SrWG7Wdx3/kd//oJYNjI4/1xQWOjjxRhselrXzz9K/IMa5t+jkRBABYendELuqLC+SqVh6s+1AZVsOOm7/9q/Mj6/ri33BFX1hBe7RHPqrd3PQBANjC5JEk+Xi2DQAAE5H75PKFiP5Ij3xkDADAf+zIMhxnkvv88miQPEsOAIAJerhe8ye3AACYoO/q9dYy+2kuAAAmZDzgd2OZPxIFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYFp+AUsvgzbsxNdtAAAAAElFTkSuQmCC>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAACR0lEQVR4Xu2WX2iNYRzHv/4sMVokpSkt/xeKyYrZ3lAo5cKFJEUpNayh1KIk12tx4WZS2y72R1xwI/mXcqHtQik3drGIpFaKIhHfb897nF+/c1Zn79nF3uP91Kdzft/nOb3n97znfZ4DZFQe83yQMmbQuT70PECYmFa20cs+9DxCuptsold86PkvmnyMdDe5A1mTgScobFIf3GjqFXQfrTHZVLDGB4Y5tIXO9AOOZiRosoP20N/0OL1Br9ML9BvdlZ9aFpvpKx8artI/dK8fcJTU5FPkm9SZeTd+/5H+oNvjWozQQVOXwy2604cGLaaaPOZyj+72pJrcSg/SWoQL+PPnA+13mWcDHaaH/IBhIQoXS3dsrcte0/Wm3uNqUVKTz1D4TB5BaLLBZPVxdtJkxdC45vX6AcMZetjUVfQzvWQy4TdFPTqNphYREjbZTb/QWSbTXf1Fl5isGPrC++kiP2C4STeZeiXCwqwz2QE6ZOqJiJCwybf0vsve0Ifx+2t0sRmbLAP0lKnP0XGEHVXodRT5X5L2Cm1ER+PaEiFBk0sRVvWsyXR0KDuPcJzcMWNJaKdfaRfCPy5tcN/pO9pJx+jt3GTkr/vJZDkiJGhSD7eOilUmE/foC/ocYWMqB31hHR9auPcIu+wJ+jPOemj1v9nAFnqa9pksR4QETc7GxD/FZQjP3FSxGuF6ORYgLEAxdHzt9iESNjkd0c6uO66jp9WNRaiQJpfTl/Qine/GIlRIk8I+o5YIJTTZ5oOUUYdwLmdkZExz/gKwu2gHyXOvOwAAAABJRU5ErkJggg==>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA+CAYAAACWTEfwAAAE3ElEQVR4Xu3daahuUxgH8GUersxDKGTmi9yEkCLDB5QhmUrGFB+MUUiJ7hdCmafM85Dhi8xTKElC1weSlKHIlEyF57HX7l1295xzz71d5z3O71f/9rPXft9zTufTaq29n10KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAItv/eEAAADj4+rB+ZaRBYOxmfZNZK/hIADAXPFTU+8T+Syyb+ShZnymXRD5dDgIADAX7FT+vR36V2R+rV+PPN9cm2mXDAcAAMbFiaWbSD0RuSzya2SPyC2RnyPHjj5a3oqcHfmunh8eeaV037838m3k+zLa8rytHnv5uY1r/Ug9n0iuwn0ZOTPycOlWwKYzqcrvDb0WmTccrHaNHDYcBAAYFzlx2qzWOUn6vdaPRxbWevnIe7U+N7JtrVN+//jIo5HlmvEXmzrl5zaqdW6JTjZhy999f+S8en5l5OvR5Sm9PRwo3YR0i1qfEllrdKmsGzmjOQcAGCvtxOn9yBu1vnFwLSc0z0RejhzdjK8e+TCydjOWfhyc58/atNY5uZtswpba619FHmjOe6dF7h4Ohk3qcecyeqBgnXqcyOXDAQCAcdFOjHIVLe8vS9c311aJfF7rvSPH1DqtWrrtxiuasZQPGLTyZ+1Q62dLt+U6mfbvyvqI5ry3UulWxyaSK2m5Opj6J1a3j+xe694KkVMHYwDAHLVymX5fsn5VallpJ0YfRd6pdd6D1l87P3JUre+LnFS6idp2kTfr+AuRzWud8r62Vq7eXVPrXyL71fqEyM21bj3Z1E+X7n+Xv3Nx5GTx49LdU5f33t1QuhXCXGXbKnLy6KP/OKB0LUcAAMpdw4HFkDfqZ6+wmdZOllZr6onktuQug7EVI0cOxtJUT4xuEFljODiJnNz18v+3YXN+eukeatitGbu9qQGAOeyQMnpKcrqyV1hu/802zw0HJnDHcGAZypXCs5rzHSO/NecAwByVPcmmusl+Kv1TmrNJrmTl/W+TWXM48B97tczOyTAAsIRy8tFv3eXWX39D/EWlu5+qtc3gPA23EFt/lm5rcLbJNxyMs+neUwgAzHIHlW4lLXt+pWvrMXuSPVjrlP3KFjVRyO9uMRys8tqieoXlBDEb2LZ5uXS/Mx8EyNYWAAA02hvos91FbrdlT7JzmvHsQ9bLlbO+V9hj9Zg39eeTka1Pil5hAABLLVfNLq51TrqyfUXKNhPX1Tr1rTPSF2XUKyyfYJxIvoFgUb3CcrVu/0my3uijAADkFuihtc4+YFfVOnuS5Xkv3915aR3Lrc7sFfZDvZaTt2xM226hpvycXmEAAEvpg8hTpWtTcVwzfkLkj+b84DKaqOVns+63TLO5a26ZDpu75oQu+5gBALAUJmvdcdNwYBL5NoFsidHLXmHtC9cBAFgCt0buiew6vNBYWKbuS5bmNXVusWavMAAA/gP5AvPp9iVbUBbdAuT/YK3S3Ze3den60uURAIAxcWHkwHrcs3QPWuQRAIAxkC9nP7/Wd9ZjrrYBADBmjo+8VLp3ra49uAYAwBjIp2rnl+51XO2bIAAAGBPvlu5NDZn+/asAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwA/4GpzOzIhgACSQAAAAASUVORK5CYII=>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHYAAAAaCAYAAABikagwAAAEO0lEQVR4Xu2YXagVVRTHl2YqVopmWmn25Vfqi2Uq+KCIhSaKBRYXMT/CUtB8UfGLOvgklYWiom8VfoBCD6JpoKAphkRiipiKehNNLUGsMBXK/n/Wmeue5Zkze+ZMR8n9gx/cs/acs+fuNXvvtUckEAgE/k88B/vB7rahDrSHbWwwUAx74Uq4wDbUgT5wH3zINgRqZ48NlBkEF8HFsL9py8ozcJINllkGt8DmtiFQG5USOwcehW/ABngCzoxdkc4LcCn8Af4Dt8Wbm2gLL8FptiEg8iR8CQ4oyyXOF5vY3vCW6O9EvApvwJ5OLI2BcKroffG7SYklvO4sbGkb7keawffhAbhedJ/8FH4sunz6YhPL3/jdxDjgnHVZftclLbEPwJvwddvgQw/R6s/yiOggFcl/3VdruBUuh51MW1ZsYg/Bn02MMNm7bNCTtMQSLvd8ODMxH34GT8IZTvwpeA2OdmK1Uo++PoFzbTAnNrHn4XETI7/BYzboiU9iv4Y/2mA1usFN5b8vwC+dNg4895OuTqwW6tHXY/AIfNA25MQmlkmolEAWODQPPoldIfrwePO2aLlOObCTnTYm4YzzOYIFxHgb9CBrX0/AeXCCaHXowwi4ULRgSrJj09Xp2MRehz+ZGGFSf7FBT5hYzshqsF74W3Ice1h6swO+7Yjgzbqzqgv8QrREZ0GSF5++OHNXi77x4VnuNGzltCcxBX4HN1ZxVdPV6djEnhPdRiyX4WEb9IRjsd0GDRNFC7TMlTGfwm+czzxncVZVOj+VpLbE+vTFCpOFCmEx9Cecdbs5kaGilWtR2MSyyrZLLgs+n+Qk4fPdD0T390xwJnBg+eWI6eUYl90G+IrTVpLkxHaAj9ugg29ffEc70rmGM4KzMQ0uVawge9mGnNjElkRnDh+2CP6/vH8ulxFp4+DCxO6wQQNXM75ezEQL0YH7qPyZx46D8C/RM9RXEn9fWZLkxHKf/EOSD+tZ+yJjYaPEl+5qDIc74aO2IQc2sc+L/n/jnBhfIFyUeCLTxiGCRR7PqN+Kjk0S+yW+VXnDAqURfg6/Fy1sror+4OzoojIluMHEIriH8R96xzY4ZOmrs+iT+qyJpzFGdC/8UHS/5gzLXHjInYklo0Sr+iWi9cIp2Dd2Rfo4vCZ6fyy4eAamXOK52rRzrov4VbSQzAWfGL484MwhXDYrDWhJ9MaTeBO+a4MGn744c7kyPC26jw2ON6fC5fA9uFl0Bu8WTRQ/+1IpseRh0eQwyVx1KuEzDj7wjM/l2ndpz01Jqid2rdyZpKww8azA+R72RfiWaJLqTVJifShiHAgf7nU2WCTc43gE4Z7YKHrjtkh5WZL33yxwCWVB4jrMvaBO5E1sUeMwBF4RXd3uKpxZRRQt9wpMLPfnrOfHIsaBNQFrEC73gYLhmZhn7jW2oQ6wpmDFHQgEAoFA4B7hX5IX8GX4aYriAAAAAElFTkSuQmCC>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAADVElEQVR4Xu3cW6htUxgH8OEackkSSmyXI3IrlygpHhAPkkuUOHL3oFwipJwXDx4JD3Ir5Zo88aBw5E0KRSjlKERKuZQ8uHzfmWOac42zT+es1lr21v796t/4xhhr15zjaTTG2qsUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmMlBkSunCAAA/6EDIw9Hbp4ii7J3OwAAQCmXRG5rB1fI0+3AjN6P3Bj5JHJRMwcA8L+xoR1YQYe0AzPYMfLXqP935PpRHwBgakdETqn1CeOJBdtvVOf16ErYM3Jm5Lh2Ykavj+rcsF1b630ih0eOjKyrbe/0MrkO+VkAgM1y0/JK5PzSbS42TMx2noi8O8rGyDuRtyNvDR/bLvtH3hv17yyTm5qXRnOLcmjku1r33437PrJHrXvte2fyvTP53tf8+8nlnRN5stb3Rc6r7RmRN2ubLoscXbp1SLkGX9YaAFjjdq3tptreEdm31otyT+TiUX/30m1Ulmr/h2Gq7FS6k6d5+zjyVK2fr20+wzz/E3WvyOdlWOO7a/tsbT+qbXowcnsZNmy5Bs8M05v/1j9GAMAadlUZNgpbc3LpTou2luUcG/kz8nszvr7p5zXgvbW+pWz5LDc0/Xn4sbZ5JdlvjPJZl2rd29Z7j680Ww/V9vjI2bW+unSncyeWLd8z+/06ZL2u1vfX9rfIrbUGANaYLyKvtYNzcnDpNh/997HGJ2u9kyIX1PqX0l0Vjp+n3bB9FTmqGZvWT5FLI8+V7hk/K8NJ2Dz8Wrrr4o2Rn0u3aUu5Fvm+S7Uey36uwzGlW4P2enZTWfzpJwCwSuXJ0jyvAlsvRy6sdX4HbDmfRl6M3BX5owzf7Ur58xhjL0Sua8amldesb0S+jrwauXxyeib9FW+fXN/d6tyHkR1qciM39kjp1iGfK9cgN3y9AyKHjfoAAHO1S+Tb0v0e2RXN3Pa4qR0o89u85HXwardz5NzSbSqXWwsAgJnlaVJedX7TTmzDaZHHIx9EHhuNnzqqZ5XXoavdA2U4rTtrcgoAYH7yh2MfbQcBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWIX+AaXghYN995ehAAAAAElFTkSuQmCC>

[image25]: <data:image/png;base64,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>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGoAAAAaCAYAAABfA8lWAAAEhklEQVR4Xu2ZaYhVZRjH/+6aa6mkmTouWWmgpqnk5Ixb6gc3CqywsGhBU5DUEjWH1C8SUeK+27griIqIWNpofcglbTFEqIj6IkqgRBq5Pv+ec+597zPnXM6dOzP3Xjg/+DP3PM+595zznmd533eAmJiY/OERa8iSDtZQoDQQNbbGXLFA9L41ZsmbopXWWIAsFD1vjblgouiSqKF1ZEkd0RnRHOsoML6FZlVOaS/6WzTWOqqJQaJboieso0AYLFphjbngI9ERa6xmykW7rLFAWAsNtpzCUndZ9KJ1VDNDRHdEra0jz2kELd01Rj3RMGhZI/VF40SPJ85QmNb3RH2M3cee78KHKBHVtY4AOJvkdWo6IKLwnKiXc8wx4PgEwfsts0aPlqKuom6i7qLHPPEz7ZH4XLQO2nveEG0TTYc2xbnOeZOhA9jMsfk8LfreGh0WQ7872joC4KTiH9Ey66hFGFCHoPd8WzQf2pd3uycZDkBfhIXPfgP6W0Fi9eBLS8szoo9Fj0K/9AU0+skL0MbOaCCcdrL0BbEJmpVhDIf+/hRjD+NH0V5rDIABdiJEFaKvPB0XHUP0678iWgUtwy+Ldoouih50T3JoA72eZZ5oj2iU93k9NCuPQn+Xn59KnJ2GV6GljGnLgSx2fJM82wTveLPo66Q7AW/eRhozx87cfkLqTfHmw25yH3SA84F20GxhMIfBCjTV2NjTudZkhSBbRCO9z6w+fgJkxHJouXHXRn65Yp0mBz1ZZkCjw4driCvQRbELI9q/acKIHegcu2wUfWONOYD9Yz+S/TuMk6KHrNGBOxUckybQMb6W6o4Oo/1LY6sQ3RS18I7Zyy4kvEk2iPo6x2yQfMFPOrbx0BIQFZaq7dYYQD9olEYV7y0qnESw/IaVO58e0AqQjteQrBC9oePTKumOBuvrXdGHjo3pzv70gWP7BNoU3awgXPO86xy/J/oLyV7Hv79AB5U8AM1Wlt0w/hAtscYA3oFmblSl66MuHEw+FzPAZwy0xFkWQXdr0nEe2qNIKfRFDU14I8JJA7/4mWNjJJ1G6lSUe3E8z9bqmdAZ46fQrPwXmokcbL7c35E6MZgFnR2FTUxYJhg4nIHmgk7QMsVSzZnn29Dn+BWVyxuD9izSb6eVQMeNM2NS5B0zoDOCWx7MlNXQAeWMidFsd4CLoBcoTTX/P+hsjvT9CY1avtT/PBtLZtPE2UB/aGRudWwuPaHfG2AdtQAH/jB0NsYFN18W7+Wc6FnnPJ9i6Lilg35mlF+J+Pc6tKpkxM/QGyJtkX5HgD1qtjV6sFa7GdgcwesKwigcYY0eLIk/WGMtwfWTWzF4zMCx5d5nDYJfoAtLvQ16Tk7CfjOQh6ERU2YdIbwkuooqNEIHPjgzj016mvGxn7HEMCPzHZa7U9ZYUyxFsl52Nr4gGGHsXexHVYXX4QNytW93OWj7DpUjMB/hNhs3AWqFck87RK8bXxhMW0a9XdBmgtuzfPgf3t9EHa0jT+FuRRdrzDe4RnKn5NXBW9AtrUKh0P/BGRMTExMTkzX3AdGV00ny3FkfAAAAAElFTkSuQmCC>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABGCAYAAABxPchcAAAFfklEQVR4Xu3da8ilVRUA4O39RjmmecEmMcNRwUgsBZmSvKAhYomFjhgOIiZ47UY4ikwRQf4Yf4RaI1IEJYpilDkmavkrZBARJEMMFCQRhSKLoh+6F+85zT5r3nPmfN9857vM9zywOO+79sAemR8u9t7vXqUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFM7KCd6HJgTAAAsjhtrfCMnezxV47ScBABgto6pcVxOli5/Z421Kf+d9A4AwIzdlxMDz9U4ssb2lD+0dMUcAACL4Fs13s3J0p1VO3zw/Nt2YOB/OQEAwGz8t8bmnKy+V+OOGlvywMBfcyK5PL1/tsbBKdf6XPO8b/MMALDqvV9jY05Wf6yxpoz/cvSZnEh+3TyfUbrt1XFiBS/+HptqXJzGAABWvSiUzkm5I8r4lbWhB3Kix29qfL905+CmEUXex3ISAGC1i4LtrJ5cjuzenOhxXo1/5eQYnyg+ZAAA6BXF2BU5OYXHcyJZX+Ojg+eHa1zVjGUPlh1br19sBwAAKOWNGltzcgrv5URyWHqPDwk+nHLhd6X7GvXpGi+UnVf7AABWvSjWXsrJKfRtk87H8Mza3jX2agcAABZKbOfdXLqOALN0W5nNPPvVeC3lzi3dZbo/q3FPja+NjHZ+kBMrwCU1bqnx09IViADAKhBfQA5Xhf7dDiywmGfYDirmyduNu2tDGV3dOmXw++katzf5obhTLbodrCQX1Phl835h8wwA7MHaJuh/b577nJQTc5Dn6btY9vicqD6UExM8X+OE5n1Y0MQZs1Z0Rrgr5VaCWFkbOrbGZ5r3ob7rR2zTAsAK9qXSbVHGWa7oFjDJfL7CHJrLPLGNOSww4qLauLB2vqI1VRh3ce5K8pHSFWjRTus/Nf48OjziD6W7MDjEtul1O4Z6xXhsVz9Z+gtpAGAJ3V3jgNKtbF02+O0TK2vbcnIOhvN8qkyeJ0QrqZ+U7uLbM9PYniDOnkUHhjaeHUR8ZXr1///kqCh6w7oaa8vkPqjnl67YjWLtF2msz5uD31i1yxcQAwBLKK6heLR5j/+5xzmzLIq1d2r8aoroM+08raNrPJaTq1wUdK1YDZskVspeKbs+K/ij0hXT4Qtl1/82AMAi+nKNbzbvcUj/q817Ky6NvSEnpzSXeUIUa38q3TmzPfHs1emlWwEbF5/c8UdHtH1No+h9q3nPolh7qMbZpVvBm+QvzfPm4tJfAFhWtpeuMApRQL3djPWJtkvz0c4TJs0TB+bj682hKPSmaR81V7HdGtuPuxLF5nIpGv/RPMdFwTc17619alybcuOa3F9ZdtxF98Maf2vGAIBl4NbB78kj2cmGW2dz0c5zSDuwhOIcWRYfRUQXg1zsvFq6Am8pxbZyiNW3YaushRD/bU+U7kwcALAMxf1ki2Gx5pnWcaX/epK4zDcO6uctwTjTtSXlFtulObFAYnXtuzkJACwPsW22GBZrnmnF2a5xd819JScacb/bUvp2TiyQOL+23P6NAIBVbn0Z3z90Y41Ty+gHEkM/zok9hGINAFh2oq3T6zlZurNrk3y+dFupAADM2IulO6c2Vx+v8fWcBABg4cWZrd+nXGyR5siOKv0N5AEAWGBx+Wx7Uey04m64aKkFAMCMbS1dm625urB059gAAJixaG7et+W5K4/kBAAAs3NNjf2b97ib7f7SnW3bVrrrPVoXldG2UAAAzFjcPbaheT+0dCtvPy/9Laser7EpJwEAmK3ry85N5dfVeDnl1pT5N70HAGA3tfeqnTj4/WeNvZv8Bc0zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAQvoAfrG0LDrGWI4AAAAASUVORK5CYII=>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHsAAAAaCAYAAACXbyOAAAAEoElEQVR4Xu2Ya6hUVRTH/6aVgWYPKwtLi7JCLYOkAvXaC/pQkmlWlPgIoQ9ZWfQuVCztCb1E7IEYKVZoFD3ppV9SIzXQuEHkvVogFqUVWRE9/n/WnO6e5ZmZfa4zc5w4P/h/mLVm9j6z19lrrb2BgoKCgn3hOG+oEwdRR3lji3KoN7QiF1KveWOdOIRaS53uHS3GGGq+N1ZhAnWuN+bNSdQOaoh31JHLqK3U0d6RI20lxfICNcIbKzCY2kPNdvbc+Yx63BsbwDvUMm9sMhdTi6kO6h/q9nJ3RZSdPvHGKqyEjb/QO/LkfGon1c87GsCp1O/UUO9oIkqtk6hrkS3Y11B3eWMFVBK/hI3/qvPliur0M97YQD6invTGHDgP2YL9FnWCN6bQi1pPnQMbf025O46e1AXUsaXPGnQcbLd0lwOoP6hbvAONmU88S23xxhzIEuwB1AfeWIGbqXuoA2Hjt5e741gKW6hfqOnUS9SN1DrEpxfPQNgDXeodaMx84g7YnEd4R5PJEuxZsDWohY6X6n8OLn3eRf3Y5Y5jJPUouoLzProGVA36E9VrbqUuW0cJjXeas+/rfNW4AjZmrbqtYCgFVtJq6mNYWZDU/CXPGEOWYKsxizlfP4fyjfM1bA7t8mgmw1r+ibAfjwp8V5Vslwe2kBOpX2Fp2DOF+gt26RGSdb6nYIv/HqzTHRz4PGfAft/mHU0mCbYyTTWGUS97YwpnU28426ewObp1WfU0LHBhcObBBhwd2EJWwPyqO55bqZ+9MSB2PtX+3bCOtRbHw35/kXc0mSTYd3qH42Gkl7mQHrDd/z3VCbtP6ICdPDTHWf99MwObsXejsJr6DelpRmdKBVQTakd5psF8/b2jROx8Z8LGibkwSUrHKd7hOBz2/LHScUdNZSwxwdZLvBHpWTFkKvWIN5LnYXNc4h21UED+pu4PbNqtqp9pD6wHVIOlBVCqTttJutXSw6Rd6WWZ7ybEd9hqdNJKh0d9xH0ZdDe6V7OrNZs6jdQ6Jh5GfU719Q6yADbHFO+ohRoj/fCJwKYDu+pC2punACRXez/ALhE8J8PGvM47kG2+VYg/q+tuebs35kAb7P896B0BS2C1uBLaEO8ifVcLvYSaQ0exTGgxdde6CLbo6kgfoHqHXyqhdPohdTWsodINmY4PaXRSc5xNxM6neqWX6UpnH+s+J7xCve2NTWQu9RWsvv4E61m2UW+GX4Jdj+pypBL6H1oflTRlu3sDn7KSxlS/I7++p848ulH7AhZAofPckYHP8xisjo0taRP1UOAPUVD9HxWx8yl76O09JrDpZZsTfE5QDdRCj/eO/RBtlMw7sh5oIbWgs70jBdXmmc6mS3mlpDQGwbrGUYEty3xqANuDz6rFuoIdHtgSZsDe+CyNVF7oGBVzPVp31P5r8bWwCk4aSqevw64/ww5aaesb6luUN1shygQbYDtPfzBmPtXthbAy0AFrBnXLpmAqk3jUyHyHvdP9/oiymO4McuHFkpbDjkv1RoFTo3E9dRsaM58aPXWnrcANsOPU/xYdHRoVDF2tKlsoc7QCCnYfbywoKCgoKCgoSPgXy7QQf+BaA40AAAAASUVORK5CYII=>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABCCAYAAADqrIpKAAAGY0lEQVR4Xu3deai36RgH8Ns6mAyyM4wlKbKGCBlEZC+SNGHCyPaHPwZjpJA9S3aDwtgl/GEpzBFRtqHsipd/lJRt7Ov99fwe5/rd53fe83udwznvz+dTV+d+rvvtec9bU3N1L9fTGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACb4dwep41JAACOhvMXPy/p8bQ6AQDA0XKsx9XGJAAAR8O1e9x4TAIA8L930x6X6nGXHrde5C7b4749HtnjnEUOAIBDkCLtwh7v6nFej4sX+ef1+McizlzkAAA4BC9e/Px4m7ZAn1HmAAA4Is7qcZsxCQDA0XFBj0uPSQBgM917TKzhFj1OHZOH6DI9PjEm1/T4Hq8fk0fcFXv8bUwCAJvrZ2NiTR9rR2eF51U93jEm15Sbll8ZkyeB64wJAGAz3bPHVcbkms7u8dMxeUiePSb+A+8bEwAAB+1ePa7bpl5cDx7mVsnq2J+G3BnDc9xtTBQ/GBP7dKM2/f7xkJI/nueMie6ui583b9vv20taYaySLwZ8fsg9scebhxwAwJ7e0uO3berP9dQez1qe3uH0trNI+fHwHOOfqdJW4qDctk2rXG/r8fIeL2xTc9i9vHV4znuy8pd3pP3F19p67/ndmChu0Lab08Y729HZDgYAThJp8fDwtlxc1fFWj0+1aQVr9pi28+B6DrPHTUrutWX8gDKOp7eDK1xSYMWnS+4bZTx7/vBci8z8LnnPt0ruu237Pe/v8cUeT9me/rcPj4nBDXt8ucd7xokV5ua1/w8BAJyAFFZ1laj+z/RXPR5VniPNVn9Tnm9Vxh8p41eX8RPKOFIoXn7I7cc1epy/GJ/S4zNlLm7X401Drv4bZn8v47+07ffk3/z9MldlZW8vL+hxxzEJALCuFCnPXYxzg/CZZa6uOM0e1JaLuictft6px19Lfu6in/ncqKyyNbjK/dpUeO0Wu0nROReAr+tx1TIX9+nxhSGXLc/RH8o4t2Dn9/yiTSuRq+x1gSJbzWkfcr22vD0KALC23/d4Y4/Pten81yxF1iPKc3WsjLOdmKIvBVo66KeYm9td3KFNK3Dj9ufPh+f9uGab/v6tHm9vU+FY5TxaPmr+6yH/2LZ8sSDvScuRvGOr5OPbZZzCq9ptey+ffkrbkCoF8SuH3GFKIXnnMXkAskX+pTHZfXJMAADrmbf9rr6UnQ7hp+iIa9WJNq1iVTmnNRtvWL6ijCMH8cdbpvuRojJFUwrM8ZLAzdr095/Zpj9zhTKXwisF5SzvuXub3pFCpnpDGb+ojOObw/PJZCwoD1JWYsf/buo5QwBgTS9t08rYGUM+HfyPtekGabb0Ll6anazaUhyliPp6j9uX3C/bVEgdhBRWP2nTBYHLDXMpGLKqdv82FZ9/bjtXePK7pA1IWpvkPbWAm+VSwYfadFYtheZDy1xag9Qi8GSSFdWD6EN3PH/sccvyPJ4tBADWkLNkub34uHFiDWPxs5u62pat0RRQByWFZr5UkKLytGFuHSnUUuy9u03vee/y9HFdv8ePxuRJJCuOuazx3/TZHq8pzwo2AGDjZHXvA226NHFem266piHvQfjqmFhDVhNTqFYp/F4y5GbntuUzfingAAA2SraOH93jHuX5nO3pfzX/zeH+uoo1Sg+4VdJqpDq1Tef6VsV8W/aji5/pt5ct58gN3TRcjvFzZbkVWwu2i8oYAGBjXNC2b9k+uU2XOmY5G7jbLdXZbvNz25VZCsNsCa+KnNXLbd/5s1rptzdfIEi/vbldyXhDNxdM6t+/VcYAABsh249zwZOWIPnCRM4E5rxdZMt0vLG7rnXPIM7ST++Di3H67c0XNObCL2cTX7YYz85uy1/F2CpjAICNkB5y31uMsy2Zm6y5IDE3CU4xN7fOGJsT7yVfclj3A/eRVb70qbukTf32csN27rcXV25Ts+Eq5+/qd2O3yhgAYCOkCLpSeR4bEH+njOczZetKm5NVbUz2kt8pUuzVgu+BbefXJH7Y42HleauMAQA2Xi4c5IP0OeOWb76eaBPc09u0SnZQ0rsvK4KzrAiOX8rYGp4BANhD+tCdMib3ITdNZ7mMMNoaEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAn7J2chILlbFYXOAAAAAElFTkSuQmCC>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAkUlEQVR4XmNgGAXUBCxA7ATEglC+ABB7AzE3XAUULAfieUD8CYhLgXgFELcC8U0gZoQpsgPiJiDWBuL/QLwPiDmA+DQQfwNiTpjCFCDWBOIEqEIzqHg4ELtC2SgAZPU7IGZCl0AHd4F4PbogOpBmgFibjy6BDiIZIAr10SXQQTsQ32BACgpcgBeIudAFRwH1AQBXXxRK+83PqwAAAABJRU5ErkJggg==>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAaCAYAAABctMd+AAABMklEQVR4Xu2SvytGYRTHj5/DG0VJ8koZMAqbRQbDW953epc3g8EgFmIzWI1SimIxWCQkg80i/gCRMshuMNnE53Tu5Xhcw72r+6nP8HzP8+N2zxHJyfk/NOAU9rj1CE5gU7wpK8d4iK84iae4ijv4gu3fW9Mxhms4gB/4hB1RrSXK5qN1amaxH6fFLhp3Nc01m3OZ0od7eIMnuPmz/Jtdsd9S77IFscsHXRajPdFad1hI4hHPg+wSb4MsZhHvwjCJothXrLisC9/FGtuI+66m6BBsBVkiNbHLh11WibJRnMFlV6sTm6Kqy/5kHR/EDsW04TNe4AE2u9qQ2MOdLtOzfhi+aMVCGIo1tzcMYQnvg6yMpSDLxBluu7X27EqsN5nRkdT5fsNrsfE9EhvhDbcvJycln8GFMo6Z/kZBAAAAAElFTkSuQmCC>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAABQUlEQVR4Xu3TzStEURjH8cdLzIqF95piZyU2dpT8AVJIs7BgLQsbNqLYyEZeEjuSzRRrMTV2srFAlvgDlBIWCt/nnsM8HVdNdnR/9ak5v+fMuc2de0WSJPk7KUMvmvy6HH1o/drxi2xjC48Ywy7GcYpps6/odGIJabzjCJV+NoBXVPt10RlBBwbFHdplZsO+6zfdCvI4xCZazOxbVvGECtPNizu023SleEDGdD/mAsdBl8cLqkzXLu5C9aaLTS3eMGO6RnH3c8p0mglcBl1s9A/Rqy+bLoszcY+XzT7Wgi42uukZG+IOO8ECUnYTKcE9hoK+J1hHuULOf65DjZnZ6FOiv6jBdHpv58w6im7QjbPhICaTuDZrfVIO0Ga6KIviDtUvNAezz+h9XcctbsS9ffrW3eG8sK2QHW8Po8EsyX/OB5O3OPxlPnQYAAAAAElFTkSuQmCC>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAaCAYAAAD1wA/qAAAB4ElEQVR4Xu2WTShmYRTHDzUiDYWNj5l8LqR8rpQVzcbOZKnMQinUWEgpWZCiWKAoGxsbFNYzzGAhWVKTZjGlRFnQLOSz+B/nxbmne1/ehXt76/7qV+/9P+ft3ue59zz3EoWEBEI5rLRhPFEGV+EAHIQ7sMBR4R/FsBeOwlaY7Bz2Jgf+hCUqG4Mj6tgvmuEv+I1kMufwEBapGk+mYbXJpkgm5ydp8ASWqqwJ3sNdlblSCJdsCP7CHhu+M3UkF32gshR4Ecn5kfNkHNbCDzAPJsFOkhXgFfITPh8/VkMm/0MyEV50T37DVHhMUnwLr+BnXRQgPLk7uGcHNBlwOfI7F1bBj3AfzjwVRWEWbnq4QbJILK/yOkkDx8owyQK32AENN9J3G5LsFv9tGAD8TrskuZ6oTMAKG4I+ktvJ/RIU2fAfbLMDbmzBRBuCRZIGe40a+CUGo+46Cu4LfiF/VRn//qSOn8mEZyS7lYab/AZ2mdyNdtgfg/Xyt6jw9fAXRoPJf8Askz3CM7yGjSpLJ2lUviMJKvcLPuc8PCLZIFi+Hn4VnKo6B5Mkk+CiBTgH12CHLvIZfvx4h3JzW9U54Jk+9Qd/a+W/DMUP3B8rNoxH+P3RbcN4hD+V3/RZHBISEhI4D+pMX0meGQmdAAAAAElFTkSuQmCC>

[image34]: <data:image/png;base64,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>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABF0lEQVR4Xu2SP0tCURiH3yIRsoY+gUNRFi5W4BiUUJtzQ9DQ1B8IG3VrFremCKKl9CvkBwgcgtYGyUWCJofCJZ/jucnr63XIIRruAw+X3+893HvPPVckIuJvWbGFIo5bOG0HYazjsy0Vl/iNe3YQxg1u21KxI/5mh6YfYQEfTOfeIGW6F0yrvGtynzPcVzmG71hSnaOOUypfYVblPteYUXlJ/JZWVZfHqspjuccTlQv4If4EHe76ihtBnhV/IAdBHuIcO1jBR/zCT3zDMjax9rMYLnAR26ob4Abut3Bba4k/1SPsBt0tJgarRTbxFO9UN8Iyzqg8L/5BYTQwZ8tJWBO/A/dLHZvZr0niExZxzswmQn/DiP9CDzJeKIV+z/4sAAAAAElFTkSuQmCC>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAA2ElEQVR4Xu3PvWpCQRCG4SGgaCOiYuMFhHT2Nv6ACArBKlXaXIWdIFhpp42FIhZiZy9ErTW5A6tcgGCRIjHvsrswq3Ua8YOHw/l2OLNH5J7/Sh4VxPGAp/BYJIctlmjhHSt09VACnxiqroMzGqqTEb6RVl0bP0j6IoYjNr5wWWOni7rYFeYLPuZHzIae6qQodrCmurLrnlUnUZzw6t4z2OMXKT/k84YDBpjjCx96QMfc69E9zf364fF1qmLv17w88ImggIXYwRdkgwkXs3aKCcaYoRRM3Er+ABRfJS7y55KOAAAAAElFTkSuQmCC>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE8AAAAaCAYAAAD2dwHCAAADbUlEQVR4Xu2YWchNYRSGl3meM2S4MBMpJRSRElHGUoZSlDvcmKP8uTBEQi7kxi8ZUpQyltmF3ElkJvMckbEM79v6j/Z5nbP3tzdOyXnqvfjX+v599vfu/a1vfdusTJkyZp2g3lAXTZSA2lBLDWahrQZKxDloM7REEyWgHnQe6qmJtBzXQIk4o4EqBkBLoWVQX8mlpQE0T4NVjIHuQK00EUo36AG0D6o0X0qlopB586Er0ERoCnQDmp03Iplm0GLzl+IT9D4/nccRaKcGk6hu/kTeQMuhXVCFpX8KtaA+UL+ImuaNKI6a1wP6bn6NHCOgz+YPORTOYQ40FDpr8eZ1Nze4lybiWGt+o5M1EUhnaD90EtoKbYTWQWuggZFxcah566G3EmNh/2a+hLNwzOLNI5wD7z8Ivi10+xVUQ3IhjDMvtmM1kRI17yJ0T2KEhp7QYCAh5vHhX9ZgMeqb3xAdT0t76CrUWBMZUPMeQdclRl6Y/2YWQsxbaL4Km2uiGGwRXpsX41Xmhbpa3ojCbIKmaTAjah5rWyGTnlUpCyHmcXOiecF1jzWEy+QwdAHaZr6JJHEAamfeGxZTnZ+j41HzWEquSYzQuMcaDITmfdCgwA2P5nGDSWSB+RMO3RWjsI3YnaBhP0fHo+Y9hG5KjLyELmkwEJr3UYNCB3PzhmtC4bpmX9dRE4GwL0rbzhRDzeMK0OXJUsLlzN/NQoh5Q8zN66oJhc3jQQ2mYCa0XYMZUfMqzNuSupFYG/OJzY3E2L4kTrQKmsdyEAfn9NX8urGwv+OTYPOZBbY2vKFJmsiAmsfe8R00PhLjxJ6am5ij0tzkkI3rFPQFaqiJCCuh+xosBL9g8AbpNDcL9mw180Yk0wTaYz551jf+zd4xLWoeGQU9gVZAq6Hb9usuyNMDe9QdEs/Rwrx23jVvySh2FtyMRkbG5dhr7kUQNJD/wFrCJcH+anreiDAGmZ8Kjpr3jDSDGh0dFEMh8wjfEl6DRjaSXA7WXR4pfxd2GDR6giaS4Pcsnm9vmfdCrfPTf51i5oUwFZqhwQzMMj/VpD5pcZfhaWOweV1JLJh/mKzmsUycNv/c9DuwVXtuGev3IuiQ+SeZoAbxD0PzuLOmfWj86tJfgxnYYH66+idhveTOvUUTJYBvL78AhZyqypQpU+a/4weJULI+L4XVUwAAAABJRU5ErkJggg==>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAaCAYAAAAnkAWyAAACKUlEQVR4Xu2VS0hUYRSAT5b2lMpe5KpSatGibQuxhRBBRC1c1CKJNm1qIRWJRkURhQ8kcNnDoloECYK1qAhRsAdBLQQ3QYuI3IhRhA8y+05nnLn/79jc5g6jA/eDD5xzfi/3/uf85xeJickZ5X6gkHjhBwqF7fgZH2MnbnOyC5QiPI3f8CI+xEu4MbAmHev9wHzQgtN42E9k4Dp2Y42fyBfFOI4juNjLhWEztmEv1opVMRdswX24IfF7ZyqVYgV+x5d+4j9ZJ9ZqA3gcS5xseHQzb+N7PIuv8Q6+CS4K0oGjeBKv4Rlc5KwIzyqx8/MW63Glm86IvuggLkn83ivW0q3JFR7n8QM+FftCfUDU8i/FE2LPa8LVbjotR8Ve9EAgpufJjyXR0gzhGj+RA3QDdAh8FXuxTDzDCbFWnuEyTuHaQOwvZWJzfaufiIj27TF8hVck3EjVyvzCfi/eJ9b/s2jAHj8YgeV4SuyQaUVL3fQ/WYZjYuN3Bn2eVqI9EEui813/QQ9FFHTXGsV2Wvtc+z0bnuOtxN86tu+K9fuh5IoAlfhDrKf0sB6U1CkPg7bDVbHSHpHs7okgu/ET3sQufIe/xdo7LfoBj8TKo1/5BeucFXOjldvvByOiG7BD7J7Q/tcpmBG9yXQ+f8SfuMlN5x29Lybxhp9IR7XYiKrCYcn+hswFu/CCWCc0Y4Wbns05fIIPcI+Xyyd6N3TiPbEDe1/s5o+JiSlU/gCdXlv/A3SaZQAAAABJRU5ErkJggg==>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAaCAYAAAAnkAWyAAACMElEQVR4Xu2WTUgVYRSGj2nR/x9ZJAhmZUSLdtFCdGFEi6RwFUS1Clq0iX4XViJBUUEKLoLKLCpCyk2lUBFSFJVFLYI2QYsI2oSRRCpZPYcz3jvzOXXnjiNyYR544M73ztz5+c75ZkRSUhKjzB0oJB66A4VCFX7C29iBlYE0HrV4B3e7QVJMwf34DY/jDWzCxb598qEI6/ERnpdkHsI/OYN/cJsb5EkxbseneBqXBuPkmYqD+FXs5HGYjnvwJR7FBcE4FhW4CUu97TXZKMtM/C42xfkyBw9hH+7DWcE4Fvow2/ENHsTneBlf+Hfy04b9uBdP4gGxus2FrkyvcZEbjAO90HdY4m1vFCvps5k9HBrxLXaL3aH+gTZxLvQEu/AZnpDsFMdlh9iFarOPUhcylkGn5j3Od4M80FlqwF5swfJAGp37OCRWyqM044iE9NFCsXV9mRuMgw3YI1a3q5zsf8zDX/jEGX8sVv9jOIJ33cGEWIe38CaudbIwdMX6iad8YzPEZuKcbyyDru96gDbFRLFarId2ukEID/CS91uX7Sti9b41s4ePFTggVlParFsk2+WTwXr8iBexC1/hb7HyDkVvoFNsevQuP0u0pzRR6BPXXpkmVv+6CuZElzn9vvmAP3BJMA5FX/8rIzrXOyYqs3EYW90gjBqxJaoav4jdeS70/XAhopu9Y6KgDX5MrBL0G2l5MB7LYbyH18U+YycLfTl24FWxhr0m9uZPSUkpVP4CaWVkottr9HQAAAAASUVORK5CYII=>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABACAYAAACnZCtBAAACMUlEQVR4Xu3dv6uNcRwH8K+fJUXIouiuUkJSRoNFUq7JH2BhkMVmskipm8GgJJnIjz/Adq/BZjOxGk0GF8Xn63nKx7d7r6vOcb7D61XvzufH+QOeznme71MKAAAAAAAAAAAAAAAAAAAAAAAAAAAAANClU5FN7RAAgNnbEXkQuR5ZanYAAHTgWqovRDanHgCAGat/gW5L/f1UAwDQgYXIy8iPyHLk4p9rAABm7XmqT5Thwg0AgI5cTfXJ4oINAKA7x1P9LvIs9QAAzNieyO2x3lCGC7a9v9cAAPzN4ciRdjhBd8fPg8WBuQAA/2Rf5FXqb6V6Uuqvay/aIQAA63Mvciz1+eJtUg5FzrZDAADWpz6tuSWyNXKlDK+OWs18OwAAYPq2Rz5GvkW+NLus3nf2th0CADBd55u+vpB9JXNl+Ou03u+2VnaO32/V89bWCgAAq1hs+qdNny0Vx3AAAPx3n1J9IPI19a16HMfrdggAwHSdiTyJPIxcbnYr2d8OAACYro1luPdsrpkDANCB9oEDAAD4pb714PRY1/vmAADozPvIjTIcE/K52QEAMGP5KdTlyJ3UAwDQgXxIbq3PpR4AgA68SbXXXAEAdOjD+HkpspAXAAD0Y1fkZmR3uwAAoA/zke+Ro+0CAIA+PI48KsOxHgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANCpnzPzOaZToRhjAAAAAElFTkSuQmCC>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAaCAYAAAAnkAWyAAABgUlEQVR4Xu2UzytEURTHjwgLkhVZiZKyEiXJQqIoNVmQrbXYKPlRZGXDlqU/QvlR48dG2U1Tk19Rys9YsSHC93Te031n3syjePPK/dSn5n3PfXXvnfMOkcViiQItcBrOwEZVizTjMAX74RA8gSOeFRGlHn7AZiPrhi+wzsgiyRJ8VFkhfCdpoUAqYAy2wQJV+2sS8EKHJAeK69CkHK7CfTjm/N406mFwBY91CO7hoQ5d8uAGXIP5TsYfDZ/Yfda0wr0s7sIduO24Dov4xSxwb/tt8s7Rlwn4BquMjG+/x3gOg2d4pEOSjV/rkCmDryQ3lWsu4akOwQNM6pDpIBlPU7oQAH8jXT+wkzK3oMsBpbcHtzS3E7ddGu0kmx/QBfK2kYZnMo+v7zpJwT0/RzIWi42skmR/o0b2BS+8hbMqH4RbFHxbv0ktfCIZ1S7DJPvjQ/jSBM/hClyEy7CP5C8LGx4SN3AeLsAz2OBZkYFqWKPDHFACe0kOUqpqFovFYvknfALsglATcWc4UQAAAABJRU5ErkJggg==>

[image42]: <data:image/png;base64,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>

[image43]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGIAAAAdCAYAAABR0bkaAAADPUlEQVR4Xu2ay6tNURzHf97yKtdbpAyUjF3CRN6RTAgz79zIxPt5r1dSSB4xwB0wkMwkBlxCDDGRksc/YEIkhe+3tVZ+92fvc+++dztnnX3Op76dtX9r733W2b+1f+u3fh2ROnUiYpo11KkMh60hBgZDA60xUnpAa60RbINmWWMJjliDZzS02Nh6QuegkcaeGyehH9BvaLvpi5WF0DprBNehFmsswVFr8ByHJhlbH+g9NNvYc2WjOEdMtx2Rcgnq59sHoHG+PR9a5ttJLIf2KbWZ41Xi7sv7k17QRd8mdFyDb/PtYH+uXIa+QL1tR4QwLJ1Wxx+gAb59Chqm+iyc1f2VTphj9nMyrvDnT4Ee+jZD01XfJhxH7ryF7lljpHAWPodGQJuhj9BkaAl0wZ/DtW4TtB7a4G1JJIWmGeIeOB16BboLjRUX8vjG0AFroIPhgrwYIy4s7RK3EC2CJrQ7Iz5aoV/QNeisuPE/k78L6TGo0bcZftJIckRfcRPzm7g184m4+zNq0AnjoQXi1pFcWSnui25Ct8TNsnfifkzM6BDENkNH4KX/5CS7o+yWtFnNew1Vx3z7NOehmdAgY+8WXJjoCC5WATrhs7T/cUk0QY9T9MiLM5Jx9gF0hheVAS7gS8U9sFGmT9PVOH8D2iJdvz6RN9BTY2OMpCOqmZBV/Q+Y1OTqBM4W+zaQT9BtYysnHFNR1CmYpvFkZgoB1l9oW61saUyE5mXQVHdZHQtj6Fdx+XOAWch3cQsRN0ClNkjc4e7PIKZ9WWAImOvb3KzFDLNNwpAVxtxpXkP3je2FuIWVN2yTytafuFHb4duHdEeENPtPTuq9yt4hzJd/yr8bnq3QK3HOmGP6yg0nwU7fbtEdOZFnGTyMj8/VrrkdwipjEsOhIdZYAegIbjRJWqW0O+RZBg/3YraW2RGxk+YIhs3YyuDhXoV0BBOGJEfEWAavSUfEWAYP42MVtyYcwbAUYxm80G9E0hrBWRhjGbxmHKEznFaJrwyuHZFpH1EN6H1Es7KT2MrgOn3do+yFQDsi7aElUYkyuN7Q7Vb2QsAfFf5ZknWWlbsMHsIR+6rl3zCZCOli+IwVPb7Yx1rH8gdipuWh/5iqXwAAAABJRU5ErkJggg==>

[image44]: <data:image/png;base64,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>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAZCAYAAAA8CX6UAAAA70lEQVR4Xu2Tuw5BQRCGx61To1BQaRUkaq9BrVLwFKLTq3RKtNSeQOd+iUsiaCg0/JM5ZM9wgk5xvuRr9p/M7pndQ+TyK2k4hBu4hWs4hWM4gwNYgWGr/iNNeIMZYy0Iy3BJ0jhqZI5M4BF6dQCyJJs0dKDhnbiwrQMLH9zBK/SrzEaOpFFJBwZ9kpqYWrdRJylK6sBgT1IT0YEJ39qB3s+H4RvjJmfoUdmTx3xaOjAo0BfDztPn+fTo9Wm8wI/P6bPicAW7MKAyGwmSnTpqPQSL8ASrJNf/Fj7iiGR43OgCFyS/xNyyBlNWvYvL/3MHAG42Bbor924AAAAASUVORK5CYII=>

[image46]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAAA3ElEQVR4Xu2SIWtCYRRAr6IWdUl0S/4MxWqyWRSxb2CwDQxmi00waLGL2GcQi8GqRYSV/QHLBmMY3HHfU65XXx6CB045997HF57ITRDHqI3XaOMP7vHVzHx5EXeQtQM/+viJITvwY4NvNvrxJO45DUxiAdNnG4aKuIMhjrCG79jSS5qeuIOmaoflLQZVO7HGuWkDcQcXpOTy6wc+cGzaH2VxBznVMl6rqnaii18YVq2D3xjDEhbVTFY40QEWOMUAzkT9XxHc4fMxeNRxKe4ob2byaINHAh9svPP//AJkGSa6qGwTIQAAAABJRU5ErkJggg==>

[image47]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIkAAAAaCAYAAACD1n8kAAAF00lEQVR4Xu2aBahnRRTGP2MN7A7UVdfFwO7G7g4QaxcDA7sLG7HWWDuwsLuwdddELGzFegYqJgYKtufnmfPuvPn/XyD37dvHux987J0zc+9/5sw3Z87MW6nBUMBSxhOMGxiHFXUNGmhb4/7GxYwPG2/sWt2ggfSY8bz0vLrxH+OSVXWD/sK0iYMBaxoXT89LyEWyYFXdoG4cbvxN7uhjirrBgHOM95TGBvVjBQ1OkRBRHjBOVVY0qB8za/CJZFHjVXKBzJvYoB8xowaXSOY23mpc3ric8Uzjwl1a/A/MYtxSA5/cTCcf2IbybHwG4/rylZyDcz/2A4zrpnJgVuOKxo1UZfTTGJeVt1072XLMZtzYOCKVCdPHG0emMv0IkUwqv4PgO+X9A0niWsbNUhlx0c/u/Dq5cT3jfvK+8e0cRIHtjbvLI8PmXau1iPxd+s6WuFCyj5P3N/iHWvvaZzAp1xqfkjv8YuOLctEAnNTdAPsDOOpt+cDulidcrxpfljsU4BjanCJ3zqXGV1RN6B7G7+XfOD3ZEM1ryfZssgWY+A+NhxlvM3YYLzPebhyb2uAn3j032flt/PajvD+A/j0jT3K/NY4y3idPfD8xXpHaBeaR9/tK4yZyv483Tp3qESHzslXiE8Y3Ux3ANyfJBX2s8Vfjdll9LWB1vS7/sVxlOPGS9IzTwvntsIrxyR44Xq5qBggfNE7Jiz1gMvkk/2Kcw3iE/F3s9PlT42mdrX31PSoXwRTJRrjNRRJADLlIlpa3I4oCJvoL41nyb8WRN0Tyu3G+ZON3v1Tr5DPpf8vFG9jX+KdxeGZDUC9kZaIlbRgvuMt4UFX932J9Iz0Tyb6T+ySAaGsXSQwmQlTgDONfxmXkSh4IfG58ujQaDpZPFqE1BysR+66pHDlEKRKElIvkUHm7lTIbq5t2OUIkNxf2t9TaTy6xaBsRBrBlYCNSgrjgQuwIP0jEfCi1eVwuhKPkophE1d3HGvL375ULg+1wTlU7QC3AiYRFbuZKhOMekTt/IIBI2l0lXy/vWynscPr5qTx9KiP4HKVI4r09U5ko95Wq28pAiOTsws7KJiLk4F6CtvnFG9fk2Mg/wN6p/JzxuoJsIYBFStSkHeR5nVQHLszqyDmuVrVV1QLCKx8/uayQJ0LUsff2hpnkiVlfyUrKQ2R3QCQIogROpG8kiDn4NvaLUplVSZltIwfbay4SwLbYIc83WL3j5OPKEYlrb6IDY+Rt8wnbOtnoJyDiUT6us0UrECzfIInnd782/iBf4PgQslj2kd+F8L0TebEuhFN3KCtUqXzlsqINCKkMtK88Wr3nJACRIIgSJKX0rYxwrD7sJKiAUwFlJixADkGUYPUGZjfeL89FGO8CWV0ORNNOJO1Eh9hKkWyTbCES7izIuW7pbFFhi/Qv3yYiBkbK0wMS2l3kyXMOFhWCrw3sb+y9+UpDmaPk+yID4giJUvOOTggMM36j9g5kMskBmNiISEzgS/JEL8D4OoyXZzaiJ05+X9VRk22EJPkQ427GnYybqvVvNJEIR6QKvCv3V3wP8Ju05VgdYDFiiwQZkF8hlBA2YPL3Ss8fG4+sqjS/PEWYyzja+Jm65iBcnLEF1QqSNU4bN8nFwrHvQPkqxM6Jgj8zT0iRsOJY7T/Jj5cfqXJagAkh639e3ndOGCR3ZYQi2nxgvCCRIz75A5PFt5kcBElyji0nv8+RGPAvCSS2n+XHWXIDRIgNciJaLdXRBhvv0M875aKPtrGNMg7G9o7c33eoa+RDgJxYOGmOlV+OsYjBaPlYrpHnQLSDuTBrBcdM9vASw9V6uTMxgTyB7Y5o0BMYR6y4EfIjbEQKbiK5y+BbRB8iFVvQqfJkMD+h9Bc4avP/PhBsDuYF0CdOLjnIS2JR0N/y3QY1gpC9c2mUO52IsGNZ0WDogYsrto1VMxshm7ziPbXmJg2GKLiYYnu5QX77jEC4IW0E0qBBgwYNGjRo0KDBxI5/AQ42WZHYuhMFAAAAAElFTkSuQmCC>

[image48]: <data:image/png;base64,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>

[image49]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAaCAYAAAAT6cSuAAAC1UlEQVR4Xu2XWaiNURTH/+ZZXcqYMXm4pkK8eKF4QEKRBx5EXURKknks04NZptLJEIWIUkoUyfBASiRJijKVMUOE/7+1P2ff5R6O68p36vvXr7v3Xvt099pr7bX3B2TKVHKqT3qREaRtNN6ctIn6JaVWZCt5R66R3eQk2UxakytkwI/ZJaTZ5DXZS1o62zzyNlDX2VKvmeQbme4NQUrFr+SMN6Rd42EL3+MNTjfIfD+YZjUhz2FR6+FsXoraQD+YZs2FOXbHG6pQV1LLD6ZZl2HOrfSGIlUPeYfVTpVewpzr7Q1UJ1i0Ood2F1IW2ReRHFlA1pKjka1YqVCtRuGNaUfOk+ve8DuppH8mH70h6BA5B7NrA+6RqcE2hJwIbUl33+2oX6x6kqukaeg3gzkbqy954MaKkhakhevyLqRH5D1pEI3p3tsf9aWDrl8dTSLb3ZiyqlrO6eUh58Z6Q1B3mP2sG+8fxneSkbCdT3Z/CjlAhpE5ZBMZBFukCpjSuVGYu5wchqXnUPKY3CQbw3xJ0ZVzg8kK2HVUJ9h+KaXBQ/KClDub3pEXYE4sdDZpMnkFsz+D/XOpMex3l2AO94Od7VnBnkP+sdAB9tTT2dYxWUV2kYakdpijK+oTmRj6p2B3c1HqSE6TD7AIaXeUYhfJGLINFqmqpAXp7jsGS99E6itKUnvYIyFJaxWfDaEtaWPknLQMP6elnNOzMHFWjw1F/4/UjYwmE2BfBIUqmKRIqpIl0leE3p2qqtIRMiO09VXxJbQlFQylXaInqOzcjtBWOiZ/tQGJFNnFUb/GtZ4sjfoqSHeRv/MUuULOrUFl554i75zOkyKjKMlRSWfPO7ck6te41sEWoRSqIPvIuGCbBjvH+mQaRY7Dqm0Olhl6DQnNV0FTyunaUfTl5C1YdPvAskNn7A3ZAjt392FFZzj+kZIPWEVKBaNFZPtbqRKqoGTKlCnT/9d3c62K9YBUOD0AAAAASUVORK5CYII=>

[image50]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAAAaCAYAAAD7aXGFAAACzklEQVR4Xu2X28tMURjGH+dzSIgcphRRylnOhNzhgiShJDlzI4UbN4S4QgmJXIiSQkQYxxySFJL8AYoLcio+h+eZd3/Nmvfbe2aTbzTsX/3q28/ae75Za6/1rjVARkZGOjr44E+gD23nwxrmAm3vw99lO/1Mf9ANrq1W6UtPu6wjXUF30bW0R2lzZZbCBmmMb6hRNtM5wXV/ep+uocvoE/qBzg7uqchB+pG28A01yj3aOrjO08XBdVdaB+uz/k7FS3rZhzXKaHoouG5Kv9DvtGeQX4WtHq2iivSG3bwlyLrTscH136AJHUln0JaurRx76SSX7afnaXOXqd9LgiyRhbCbx8NGfQc9Th/TucF91UQD85zuocvpI1g9CdvjULl4CBvgSjyALblUy01T8xNs+9dbGEVXwgZuUXCfR9urpuz1BPP0WnSPvEKH6sEKqHZot50QZNOjLEcHw15iHDPpNh/GoM9T/8JlWRbVo6ewBwZF2QC6CqXFrxpoF9ILO+byNrBOafs+AutkHKfoQB86dB7ULNURIdUy7gX7529h2+J6pJuqjcVOFJe+R1t2nt6AlQVPJ3rLhw7VJB0yD9Nmri2RBbAvNQ5WqN/APiANGsypsLea1i6FJ5NR7fmK+Des76a2Ib4hQuefdT50qG+qufVo6U4JrmM5gNLz0Rn6Ivp7PpILpGgLO7RpV0xrv8KTydyGLYU4XtGLPgxQ3evmw4CtdKPLNqH00BnLM3opuD4Jm9LiHKr/W24W7EzTOcg0sEfpa3o3yoYVmwvk6FmXhWiWvUdxI8nTO/QdbDYl0op+o6uDbBrsy2iwyu1sjYnq0k26G3YE2EdH0MmwTp1AwwOgZuk8l9Wjol8HKyte9b/i5tQHDQu1Hkp1dmhEVJhzPoQdO+KWlH6GaDAyEhiOXzjv/K9oSU70YUYRLUvtiL5kZASodupnTEZGRsY/z08CN5Bf3mZwVQAAAABJRU5ErkJggg==>

[image51]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA9CAYAAAAQ2DVeAAAKfElEQVR4Xu3dB6xsRRnA8bH3rthQQCW2GI29hoclaGxRUaNiHmKLYtcYjYVHMCrGgsYOKoK9d7GDmtiNJmrE9sTYSzRWwHr+njNvv/32nN29Z/fe9x7v/0smd87sspz9zsKZnflmthRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkiRJkvZEd+j+Xrspd4sPLOmQUL9NqEuSJGkN3tf9PTu0vTPUFzm+KdubcnB3/N+mHDZ5WJIkSau6X1Ou3pRjQtvbQ726UVO+ltrO35QXNuWDoe0XpX09SZIkrdGJTblAV6fjtl94rLpQU+6RGzuMqlXPDXVJ0ha6Wm7YInvyt/TdFZPswrlhSVfKDfuoK+aG5HK54TzoqmXS4bpMVyeX7b27nrHYv7u/Y/LfJElLukqZJB1nz27K03PjFnlzbtgkl27KXZtyse74oPDYkDExeVVuSLgOhzblfN3xdcNjfRgR+XhuXNKXmnL93LgH4BpcNjcuaUz8bp0bkxs05RK58TyGfLO/huMPNeXzZWNfmD7QlFc05ZX5AUnSaq7ZlC805V6h7cwy+aYMvnnfMxzvDjtzwxq9oSl/acoFu2Nu4ByftusZs4gJzxmDzsE/c2Npr8VZ4fgKpb0WzwhtfTgPzmessZ29zUTH4dTcuACf4xw/PsfLxG8Zv8kNkiRtle93JXpNmc5FOTbUd5cf5oY1IVn67025WWrn/T8ztUXEZF6HbpFT0jFTclyHPPXGtVi0PcK881wGI1A3zI27GQnrG+mwDcWP67iu+B1Vxk89S5I0GtN5786Npb3BxVGX2HlDnWqKFuUAZUw/MnUVMe10QGqrHlzWn291q9K+Nzpt2e/LZMStD//cTcLxRmNC7tvh4ZjXG7oW8zwrHW80rtV3csMaEJ8nlOlO1LbSJqwz3Xmt0F4xknvTpvy8THfY9i/tZ+AaoS3Kn9Fq0ehhjh9TsYd0daZAc/yd6pMkbTlucpfMjT1+Hep0TPKSfhzXlANz4xyfyw2lndL6aW7sXL4pR+fG0p7/Z5tyRiinl/b1af/MrmfO+k8ZvtEvEmOCMTGpHTRyhxjlW+ZaZLzHaKNxrcbGYQiJ6rUT+5wyyY06qbRxx2Ob8q+ujj+G+jll0mHj3O7e1V9aZnPJavzGyPFjWnp7afcSe0SZjcvv0nHFe8mfQcqiz6AkSQvlmxE3woNK28ngb8UNvyIp/yld/ZFNuXhXv3LpH2UawigK2CKgYh+o93R1bpbZMblhRbz/34Zjzp/3zWgUoz8X7dqv15T71yd1YkxQY4K+mPB+WHkX1c7Vk8pk01JwHegwcB4Hhva+5Pid6TjGlU4EYlyH5M/CquLrEY96fEKoE9NaJwePXMKKvLLaYTu7tKOVxIX3kmMwL37xc7wofnWkte4lRgyZmo3IiesbkV0FMbBsfpGkvVbf/8ToWOT9k+J02TdC/ZdlcvN6WWhfhOmt6i2h/vUynEvFzZYOYkaH6E5NucucMoT3/93Udp2uPdrRlLemtqEpROK3bEzqaz6g9K8c5TzytcgxOCvUc1zrLvXz4lrl97yq+Hp0fOtI2kvCY/dJ9Rd0deQO27zp6Xnxy+bFD0eUyT+3rczGP3fgKjr4+XO3zGdQkqSF/lZmR8Xe1pTbp7Y43cRUIDd/bsIf7trYFuJnXZ3X4wZKqcihihixqv/euOCBbQTAHk45D4sb4p1TGxi9IQ+JbUeGypBvl+nVsHhUmb3R7yizHTZiEmNXY/Ku0FZjwvvNIzt4XveXbRO+VWavBeeRr0XucMQOdI7r07p6jSsYfXpxOK5iHOLo4ljx9Q4tk5jSia31+4Y6eW5xV306bDXmPCduPcK0ZVTjl+XriHnxw4vKZAXvm0q7D1n0xXRcMfKcP3fLfAYlSVoKeUM/Ke3Pypxe2lGFLN74SBj/VVO+XNobGo8xHVg7CnVUiU7By7s6z8+rPOnwcFNnqovXiDlhlyrtSFfE9N68UZax6BD9obT5ZB9pym2b8smpZ7QdNjqyEee8LRzXmJAUz2PnljYmdES46T988tT/oxN7y3DMyBzX4vWlvQ6vLW18MzqU0ZFlOi4xrnRIY1yZxr13V2dEK/pYqH+vTO/HNRZ7vNHpYqqT6WFWWNIR+3NppzHJB6NeR1n57LyxtNObfJkgjnTcD27KO7rnxfOMiB+f41Xjx0hu3UuMesZCnc3UN227TnzuhjqdLIT5am5cM/7bzobOZxVj9/CTpD0Wie50UphW3C89VuXpv7i1Qdz/i/bbdXWS8GMn5dOhDvbIqqNodGhiwn3fz97E/KZ1u3FpVyD2rVrEjjL7m4rEpI5gIcckxpL3yurN6KHpGMRgexm+Dnh0OuYme/NwHOOKGNd/lLZDQC5dHDliCjd34F6djse4SFm8aW3GSBorNelY5A1b90/HGZ/jVeNX5e1BQGc8j/yu26Jp9HVgWrovD48vHA9LbU9Nx6tgyrtv1HPofMb6U1M+mhslaV/A/0yXvZG8rimPK9NbcDB6RadoWeQj5ST/vhylrcCN+5ulXWUZOx/EZNnRiAeWdkSpYgo3T8UtwhYkdKLIR8uxYGSujpzNw6gnKzZZaVkxEhEXXuDJTXlMatvbxfjlqWfit4xlnzfWGWX5PeFWxXR9/JLBFwo6vNXjS7u9CSOd6zT0evl8VvGQMvniKEn7HEY+js6NW+T5uWEPMiYmt8gNa8DqyTGOL+sd3dhbkWc3z2ZOU1aMDEXkJNZpWfI6GeHbCPaQqyOCXOM49fuDMr2n3KdCPRrqYI3B+dd8PqbIo3w+q/hxqHNdGemVJElaC0b/oveXdjT1iaXN4dw5/fBCx5bJ6twjyvQoL7mA5DhWPwr1aJ0dNtIAyBnlSwL5iHEUPZ/PKuq0KyNt5KXmEWlJkqTRjgv1OioUN/bNK5WrT+SG0q5AZmo75ozRgan4BYq6kveA0p9bBhaxDCH/r68M5RDSKTypq5NeEFcix/OJyMHMrx9LHzqph3d18kyHnidJkrRhcfNlsOiiJv0zpRlX/EZDnS1G7L4SjuMiDka76i9OsNny0GuwUGUIC3H6yslldkU3C0b4d7BYJ+cQIp5PdGSZff1Y+rDCmTxNFtdIkiSt1Wnp+MQyyWFjwQRboMRRskXoILH6G0fFBxqnlMl2Gmy1MdRhY9PidWAxUp1eJV8Nh3V/Ec9nFQ8q7eIJpn95T2wJ4z54kiRpbdiwN45MxSlC9n87s0x+mH4Z/EoDo2zki+VpQVYGxz3lTg51sG8iOXN0ElkdGztXY/BeWD0O9t+LG0wjn89YtdPHKnX25WM/PUmSpLU5t0zvCZf3fItb5SwrT01W55Tp1yfna9Vft5iHX6eoU6H8e/J7yeczVnyNvqlXSZKklZDntdl7vYE9ypgqzPgVirxZ8VYYOh9JkqQ90h3L5u4bxuIFfoWkD7lep+bGLTB0PpIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZK0l/kfR0Il4wOFy+MAAAAASUVORK5CYII=>

[image52]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAA30lEQVR4Xu2SzQoBURiGP7/52SllZ2ODhQXZiztwCXZSNnIxNjZWspLCHbgGio0SKUks8U7fSZ+jM6NZn6eeZr6feU/NDJFFpwHXf5pRz3wRgAm4hC9Yh1EYgTGYhQP4VLWRI7zCkD4AKXjQm5IC8ekzrR9X1zBcyYFOmzigJ3olOFT3TlBXzH4YEwdUVO28kylsfTY8OBEHbJU3Vefkkoki8fIcBom/QBPu5ZIbHeKAvujl4UjUrkyIA6qil4RpURtxfqIzmb+/J2Xi0xf6wIsa3MALfMA73JGPIIvFN2++SC9CnIFfXgAAAABJRU5ErkJggg==>

[image53]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAbCAYAAACTHcTmAAABW0lEQVR4Xu2TSytEYRjH/+7XUmoiC0o2KAoZ2Uh8AfkIVqRssLHyCextbKxkQ8TsLSwsrSg2yiUluexc/k/PM2eeczTmzMks1Pzq1znP5Txz3jPvC5QpNdP0Iqbt9kxBKmgjzdAvOkVraQ2tp110k35aXBT39JlWRQukld5Gk4Xog77lQSTfYNdqeuoLcViADl12uUG6ZfcyfMnVYrEDHTpisXzjfToXdCTgATr0ynyxuMc3FUM/dMARrYT+87P0xjcZkl+DfppfWYQOXXW5XrrtYmGFrtM6ukHnw+UwJRm6Cx066nJNNOVi2VJ3tNPiAXqWK4eR0/SI/Js+Szf0h7P7toO+Qp//wTC0+ThaiJCG9snRFWQVEssRDpikl/SJvtM3eo38w4egQ+R7Cm0WywoSI8uVIS0Wyxt+0OagIyHnyO3PCXriaokZp4d0hu5Bt92fIMsds2uZ/8g3CrxGshNuc2wAAAAASUVORK5CYII=>

[image54]: <data:image/png;base64,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>

[image55]: <data:image/png;base64,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>

[image56]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABBCAYAAABsOPjkAAAFkklEQVR4Xu3daYh+UxgA8IPsZJctskXZsiS7QSQla5aILB9skeWDPUtCtuyyFUkoW74o2wglUkSWLCFFyE7Idp7uuc2Z887MO//8529Gv189zXOe+8688/HpnnuemxIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAg5ZsC40128IC9l9/PwDAfHdijo9zfJHjsxwf5ng5xynVZ8Lipd5bI8ffOX6oamGhHK82td7nbeFf2D91399aPcdObREAYK5bO8fjTe2SHMdU62jMdqjWIRqms5ta74FmvVuO5ZravzVRwxbez3FCWwQAmMuOzHF6U9s0x7PV+q0q70XDtF1bLP5s1o826/nhx7ZQXJjjjbYIADCXxR2phZtaNGzvVuurq7z3XuruzN2YY5Xm2s9VvlYavBv2UI7vcjyW47YcX4+/PFRsfT6duq3bp5pr26bB7wMAmLPi7tpEzc39aWxLdJ0ce1TXwqE59ix5bKmeWl0Lj1T50Wn8HbfjchyRxr53wypvvZJjk7aY3ZrGtliPyrF5dS1806wBAOasO9NgsxQnQWO7camy3qpE7ZYci5Y8GrvNqmvhrio/Iw0eTrgjdXfYwklp8H/oRf3Ytpi9XeX3pO6wQy0OTwAA/C9EQ9QeOPgjx0XVetk0/nBBbH/WDVZ8PrZU76tqn1b5vmmwIYv1mSWPu2/npq7xmo6D09jfO6DkcRfw8lJbr7oOADBPFmsL0zDTc8WisYk7YL1rcxxWrXtxJ653YBrfEEUeTVTd1P1V5RukwQYq1ltW+dZp/P8xlRty/FTyK3L8kuOmNHYAYq80+H0AAENdl6Z/B6k2W+aKfZVjiZIvU6IX25HtlmR7SjMaqlq/3Rri7lw8Bzddq6bxhyTaYb6xHXt9UwMAGOqctjAPZsNcsdjWnGyMRuu8NNbc1V5rCzPk5rYAADDMFjlWbovzYLbMFTu/LUwgtnA/aovFk21hBsQbEPrDEAAA48S2XMwDez3H7akbRLt3uVY//xVOS93sstoLqXt4fyLmigEAzAdnpcGZZv07Nes3BoSot3fcLk2TN2Urpsmvxd9+vonnSv2Z6nMAAGRvpm76fu/X8rOdQRYvTg9xSrI/TblCjodLHnfrli95z1wxAID5IO6C7VzyGHOxfcnbh+37yf3xeqYnSh5zy+Lk5MY5riq13lRzxeIB/3i2bLIAAKASTVU89B6vTPqgqtcDZcMnOS5O3aT/+J14a8DJ5VoMkD285L3ZOFesHeOxINUjQQAApi1mg11Q8rahiC3Qbap1DNCNYbK9+N3eSjm+rdZhtswVu7LK29lw8baCBdVUxrbzf9kwAgBzVIys2DV1BwQmEk3Yfm1xAvFS9Qeb2myYKxZ3DOuGrN/67b2XFszYjhCHKTRsAMA8uzfHA6kbwTGR3XO80xYnsXSVz5a5YrFVO1XDFtfqV1PNJA0bAEAlXkEVM+LaWXC7VHmIGXJ3p268SXsqdpiDmnW8bP7lplaLkSUaNgCAIgb87pMGG7bY/q39nmOk5C9V9WHWbQvFx22hEnPmNGwAAKl7H2j/TF7bsI1U+SE5dix5NGCTHT6YqP5ilf+SugMZ4dSq3hpNGjYAgAGxbTlZw/ZWlcc7T2ML9ZqqNpUvy884SRvbqeH48jPE83xn5Ni6qo0mDRsAwIDD0uQNW/+2hj6P8SaPV7WpfJPjshzfp+534+DGb9X1OGCwURq/RTqaNGwAAEONVPkqVR7WatbDrFbl61f5DjkWKXkcauiNJg0bAMBQI21hBvSv8Aq3Vflo0rABAAw10hZmSDzD1t9l640mDRsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPwf/QMUIuM0pMeFggAAAABJRU5ErkJggg==>

[image57]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGMAAAAaCAYAAACjFuKcAAAEKUlEQVR4Xu2ZZ6gVVxSFlyUaNDaM3aBgbFFEE2uiJljQPzYUCzxBRVEsxNjBhpj8EBGjJrH3KDbyIyAotqcJxkQTrKhYSRAsiKBY0ETdK3vm3XP3nbnvju/6LuJ8sHicdeZOOefM3vvMA2JiYrJPbWsUkTrWiMmMWaJp1iwiI0XfWzMmPf1EF0VlbEcRKSE6LppqO3JIedFkaxZCSVEv0Teir0S1kruzB0/8AHqx10F70TNRE9tRjFQRzRDtFz0RPUzuTgsX6C7RblFnaPS4IergHpQt5on2WDPLbBJts2YxUl00QfS56AiiTcYY0S1ROcfjG3JJVNrxigxn/aZogO3IMlxR/4mq2o4csBfRJuMv0c/G6yZ6Iepo/EBKibogEds4g71FjQuOUD6DnrSl8X3s8S5loSuN8bQwWKXxOq970jMhymRUht73RuN/7PmzjR8If7wKmgtGiH4UjRcdg8ZOnzzoSd9zPB9e8KQ1HeZDf9vTdgTARM4BWGI7ckCUyWgIfcaVxm/m+cuNn0Ib0UJRXegP9kFXMekPTaaVvPYcaJgKYh307QqjK/T8w4wfxmnRTmsGwEV0OET5okOeDooOIPPr+0SZDCbpoEFv6vnbjZ/CUGjYYUiwcW2Q5/X12utFvyS6C2D1YS/EN8BWRGdEzZ12D9N2+Qk6iLmGk/HImiGwEuR4rTC+PxlbjR/KMugKcPcOfmjp5LWZmGxyIqw8hjjtd0S3oRtDF65MhiCfH0TtnLbLWtGv1swBnIzH1gzhQ+h4rTY+Fxz9pcYPhauWdbVLPvRGKnpt5pazBb0J1ohaOW3/prgifPqIdjjtwmBY2WLNAD4RdY8g3lsUokwGc+m/SI0Sn0LHY7rxA3lf9BzJ2b4mNF+4J1gEfWXd1U24JxjntCeJ7iKRe/j3MnTgCGtwvnUMkWH8LframgGMhr6BmSpdXguCk8GNXxCMIv4z+eSLfjPeYOhktDB+IEzUPPhbx2Py/APJGxV+O+JxdR2PTIRWYouR2LVyNXFAOYHXkZyM+XmhAcKLgXehi4OVXa5h3nqK4ApyA3Q88hyPeZbh3v2Iyk1svtNOy3fQFc8qgIPGSoSrkoPiUh968S+S7f8HlmUt+/6Brj5OHB+CHsMbv/H4tIaWzpsdz+Uj6O/a2o5igptN7pivie57uie6AC06fPgMfF57n3zrz4u+hG4TjiIR6gvlHDS5kmpIv/NlzphiTY9GSH6TKkAnKogT0J1pEAxfp6z5hsEwPxBa7rKgyYga0FU413aEwPh3B7rbfFW48rmiWBKPNX3ML1egb9ZbxwLoZDDp1jN9QfBzBnMJ88Orwuv8LpqJ1FhM70+khsi3AiYXihuS4aYvDH7D4uq1m7oouDnEh//puyr6wHbEpId7CLeczQajoJ9nYmJiYmJiYtLwEk2w2l8RkoStAAAAAElFTkSuQmCC>

[image58]: <data:image/png;base64,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>

[image59]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABSElEQVR4Xu2UvytGURiA3/wsKVI2g8HArMjgD2CSBUkilJhMmAwKg5FsNvkD/BpMYmQShbIpRmVA4Xk753LO67ufblnkPvX0dZ9zOu/X7d4rkvMXacRhG3+gFodwBUexMl7+ogWX8RTfcDdeLkoDXuAqduAGXmJduCmhTdw/acVnyTZoG3dMO8FN076RZVC9uP0zpi/ikxS5hUqWQT34jiOm62DtnaZHZBk0Lu7AAdOnfO8zPSLLoDkpfOCk7/qbig7aszGFWXEH9pueDJowPUIH7duYwpi4AwdNn/a91/SILIO6pPAtmve93fQIHXRgo0cf56bgukrcY7wUNEVf2gcsNf2TcnzBIywza8otvor7TCWs4xmW+OsKvMGFZENIN17jHT567/EKa4J9W3iO1UHTgw+9eguPcS1Y/3Waxb1P+t3MyflPfAAtEEfrbJQlOAAAAABJRU5ErkJggg==>

[image60]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAACmUlEQVR4Xu3czYvNURgH8EOUl/ISNt53FhTFGuU1JbKxIUUpKS+xIIXyB3hZINkpihIbRCks+QtY2MpCWVvwnH6/a86c7pg705g7xudT3+45z1NzZvn0O/d3UwIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg/+5EvtRFAAAmjiORx3URAKDfpkSW1sW/YLzO6WZh5FzkamRX1ctmRi5EnkROVj0AgL66H5nTrneWjTG2Iw2c86FsjKGjqRm6ymTTI5va9af2s3a5/fwWmVrUAQD66mCxXhLZUOxr+enYmbrYo3zOqXadz/lZ9Eqz60JYXhdGYX2x3tZ+ro6cjexJzYA2t62fjpxv1wAAffc6Mis1Q9TDqlfbF7lSF3uUz5mRBs65Pbj926tqnwepA1WttjWyuS52kQfGm+06D59vUzOYbWlrl1JzZXovcritAQD01d7UDDGrUvO06cfg9iB5cDpRF0eg83Stc87+olfLg9S81AxOx6peKQ+BX4t9/tu9mha5FnkWOVT1AAAmjOuRtcU+Dy/drIy8iyweJp0rxW7qc54W+9r21Axtx+tGJV+r7k7N/3dxcKsn+Slbju+rAQATVj00/em3x/J16KK62KMF1T6f07ma7CZfmeYna29S86RtKHmoAwCY1L5H5rfrNWn4K8+7aeAL+yNxI/V+zoNqvzEN/eTuc7HOL0usKPYAAJNC/pmLj5FHkedVr5tlaXQ/KJufhOVz8osGw53T7ftkQ12Nvoy8j7yI3Kp6AAD/vHzFOR7yOZ0XDgAAGIH8wsF4yOesq4sAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADw//gFH8dHRw1XpQYAAAAASUVORK5CYII=>

[image61]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAcCAYAAACtQ6WLAAAAkklEQVR4XmNgGOTABYgXoQvCwFEgPo4uCAM4JXmA+DcQdyAL8gGxChDHAPF/IE4HYlUgZgVJZgHxTiB+xgDRCWKDsDRIEgZA9h1DFoABbiD+BcTt6BIg4MYAsc8dXQIE2hgg9oFcjAFAdp1E4s8DYhYY5wUQz4Gy04C4BCYBAhVA/B6IZwJxK7IEDIgy4LBzRAMAaC8Zom6t39QAAAAASUVORK5CYII=>

[image62]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAaCAYAAACehIP6AAAERklEQVR4Xu2YachVRRjHn9wyTQ0zt8qtXJAkP5i5JJIlLkEKLUIuqaARqJkoCqYFRguCRlqS5lJWJCmIiAppXVHByg9BZWqCkkqfRNRMwdT+f5+Ze+Y+nnN5j1e6vi/zgz/3zjPDPffMzLPMiEQikUgkEolEIpFIJBKpa9SHhkDtXLsB9CzUvTji1tAcehq627XvhV6AWhZH1C0eg3oG7UFOtxWfQSuh89Bk6AtoGrQfmheMq4S7oO3Qt9DP0AzRZ74O/QINT4bWCTh/H0L/QnOgNe5zI7QBapwMrR7cnYuhB6Brootzp+t7DroMtXDtSpgNPQONE33OoqBvGfRT0K7tNIG2ue9HoRNQJ9duJfr+nIuqMx7qDT0v+qeeCPrGONto1+4LvSHqpfX8oBryLtQIWg794757VkBXJQn/TaEJohNVG+kFTYTuE50/zpmnjbN9ENjyzqWH6fpJqJ/tyAu974KULgq9k3+UeWogtFk0XzMiMHTdDAzxO41tD3QJagi9KpqG+Nyu4aBaCOfJOtRTzrbAtbmAx0U3fB646OuhU9AU05ebtEUpQBdFC7VNolHCcxpqFrRrAj2ZHh56AmsBPmNfYCN1YfHTHOot0Xcb6tqPQ4eKvfkpSIWL7xfF70bSVjTfz3XtP6ERSbccEU0DIV2kfCHjPSGseJlurkD9Axspt/hhBZ0Gw+3D1mhgrUOvy4I10IPWGMAFzfp/HjrUrhQbC1/yjmiN9Qf0XnFEPgpS4eL7RQnz0DfQj6LHPkLv9LuV/Aa9HLQ7i26gw4HNQk8IawgWkiyIlhRHJGQt/kTRvk+MPeSY6MbtZOye6aK/sdR2OBiNzkJ/S3Z0Wyf6vmON3eMdinPIdEZ4AjgDdXRtOgqjLYtgX2TnpSAVLr4vwlh4cdF3Q29LqRefg4YF7d9Fj4UepoaDohP2UGAP+VX0mLcFWgv9INmTx8XpZo1gAPSXqLdk8ZXos/x9goV3DSdFi8o07oC+g/ZKdjHGDcTUx7ybhi+gPxX1bqbNr6H2wRg6FueVUdbTA5pfRo8kQ69TgKYaWy7oxT48MWTy8sXCMD8qaNO7RgZtz8eSvmitpbTQ6SB6JMqCY8tdMtn6pBrwnbjR0vhIklMNi7m0FMJ8byMlNxudLkt2MxagV4ytxvijx5u2w8Do8Jr7zhdiWLSeRY/ZYWyeF0WfM9h2ZFBu8e8XjRzV5iVokjU6GAW/t0YD7z540cWQv9D01ZSCVLD474tO9CxJclEajAj0Ni7iavdp4W0dj2oW3iNwU/jFL3edy/zH36fXbIVmlnZfh6npUWv8n2G9UpAbj2j3SHI/wptSG6ZDeIXODcL3zUqVWTBqMMryqHdANNLQ+XLxuRPDV9Yu9jBH9ZHSHBXChU/7A6tEn8H8yLxnTwl5YG3BDVJtOA9p78ETEd+TdxVfit6eloPvkzZnkUgkEolEIpFIZfwHh2LPKw7Fab4AAAAASUVORK5CYII=>

[image63]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAZCAYAAAAIcL+IAAAAj0lEQVR4XmNgGAW0AopA7AvEOkDMiCYHB41AfAiI84B4JRD3oEpDgCwQfwJiQSh/MhBfQUgjQCYQ/wPiIiCWBmIXIDZAUQEFYkD8FYj/Q/EUVGkImATEt5H4kkD8E4gjkMTA4D0Qz0Pi2wDxLSAWQBIDg0QgPswA8QBIw04gVkBWgAyYgVgJiDnQJUYB9QAA/GcU8835cpEAAAAASUVORK5CYII=>

[image64]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH0AAAAaCAYAAACacVPHAAAEEUlEQVR4Xu2Ye4iVRRjGn7YUNS9pN1FkvVAqKvqHaVjgMfGuaHRRDBH7QxCKEBGDNE8qS6WoRWih5Xq/oBIIIiphJmKQpaCGUrQEJv5RUBSimPU8vN+3++645+y5LOyF+cHDOfPOnPPNzPvOOzMfEIlEIpFIJBKJRCKRSKQlM4IaT3WkKqjB9avLpgP1PDWaeoB6mKqs16Lt0JeaTD2elIfUVbUMelNnqCPUcupr6ivqA9+oTMZSV6lPqE3UfupXaopv1AZoR31B/UAtpc5R26hvfaPmpit1kfrU2aqo/6jpzlYOw6g/qTnOdpb6l+rmbG0BOfgS9VBSngiby3W1LVoAn1O3qUedbTXMIY8k5VGwDKB0pbRfDErjP1HfBfZvqPOu/CS10JVbI/NgDp7hbNouQ1u5DKJeCY2Foj32L5gDPKep75Pvz1FfUp2pl2BpuRjGwAatQErRmUGBtj4pf0wdo67XtmidHIeNq5OzrYItoO7OVirahrfDFsvuoK5gpiG3QzYk5UOwCE75neriyo2xFvYMRXzKC4ltprNl0Lqdrm3qLhpeQNrfm5IsynB6Bjb5StspoUPCw9Y1WLr39IdljYbIUvfQePRnkNvp7amnQmOA6h8LjQ4Fs24n+dAJO19A5+uHxn+Let/ZwgUk9B8vU++i/rwXQxZlOF0d+Ad1K1mTpqiUk3okNg1kQvJdXKbmu3I/WHudzBtC24OCqE9Sfob6g7pQ28LIILfTq2HPeC2wpwyArTKdHXKhjBVmF0/aT63MXFQjfz9OwM5I4kFYKtZ/zqptAayEZdheKP1En0UZThc6PNVQm6kD1G+o7xDt+ZNc+UfqdVfW6f8K9Tds8kM0eE2EDnJbqV2widjoG8Gcrmc3xJuwbWVnWJGgPigYd4QVjrdhWWtoWJFQSf1MfRhWOBrrx7PUL7BxHoaN2S8goTORrseLYI4XyoLv5JGCxJOl9gS2olEaGph8Kh15hyid+9WhQU115RTdvZ8OjQ7dDrTa09Osj36RoW4ENs8TaIKBNgGN9UNBrrlUFtX+HmY0zdEWWLZ7y9m1PeRSev1LyVJ7A1vJpHfKF51NL1PSzmkgum/rJO/RtUyn70KogkW/vyKKDPI7fS61IDQ2A4X2Q3N0h/rI2ZQhliXflyQqhSyawOl6i6Q97SDM6bNhES30GvEk9SosTeszZDEsXeVDhzatcu39N2FXOWUW8R51FBZQ1bj/pZBOxqdgr22bk0L7MRx2UNNcartIt70VMIetgb210yIqBs2hMqqu0zXUZ7CsUhL6ofZa7Yk6fCh9jXP1Si8jqZ7O5pHDtdrzoXSuSNf/6zn7YC9kCkHPDm8MzUEh/aiABW46l5rXN1y9AiYN9kgkEolEIpFIpDD+B7i8ymAEi96zAAAAAElFTkSuQmCC>

[image65]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAaCAYAAAA9rOU8AAABcUlEQVR4Xu2UzStEURTAj28lLBAiVlgpG9mwsbGTopRQZEFZyIaSLNhISVE+SiLZ2Noh7GQr8X/4Wij8jnvNXNfMeG8xU+r96lfvfPQ6786ZKxIRERGRGXKwE6ttnIvd2BTryCD7uIOPOIqHOInXOOv0pZ1WXMFa/MBTLLC1XnzDUhunnSFswT4xw7Q7tX6b63Fy2c5zGIpwGMv9QiLW8RnzndyimGE6bNyMV/FyYCbErIK+q8GrJeQWz7zcJb5iiY1ncCtWDU+gYfTo3nHeyVWJ2RcdoAZX8R4vcMzpC0OgYXRRtXHNyR3jjZi/eZaY03nCesxz+sIQaJgNfMFNMUPoXixhodPThg9OrHThXAqL461f6DCNXu4Xd3hunyuwzKl9oz/XtpfTU9OBk+mjw6S8SCvFNC34BY8THMA6HPdqQflzmGUxTdNi9iEZejHuibmpE311KgZxV8wq6EdN/SzHObAe4YhX88nYTRwR8e/4BIWIQjS0QsqRAAAAAElFTkSuQmCC>

[image66]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAaCAYAAAA9rOU8AAABbklEQVR4Xu3UuytGYRzA8R8iUhIysLuUwUZZXEqKklImIzIZDAbXImVicSlRLimy2XVcFiWX/8DCaFAGg8v31/Oces6J9zgvnel865PX73nqfTqXVyQtLS0t+RrRgSLkoj64nEzVuMQJpnCGUyy5m5KoBPfYcGaL+ESPM0ukLbyh3JnN4x2lzuwv5aENzeEFt0K84CI0P8dNaJZteog9PGIotBaoW8zt0Cvhpw+vXqllZ/YfeRJxmFYxh+lyZu121uvMCtCPGQnujZMnEYfRL3nFoP2/Arf4QJm/iWbFXMUqXDnzOHkScRhtGA9YxxGecOduoEMxr/6omANpdZjMoMHu8/PEfFdk+pzU2r/6vKwEl6UGm3jGmJ3pj6K+AD/RdTcPI6FZxjrFPC99zkzfhAn7edzKJk9+eZh8tOBYzGEGUGnXpjGHBWyLec7i1IQ1Ma/2NVaRE9gRSm/RPnaxgwMxvw9+xWJuYVpa2nd9AUaDQNCS12vOAAAAAElFTkSuQmCC>

[image67]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAaCAYAAAAnkAWyAAAB5UlEQVR4Xu2WSyhFURSGFxKSoUQYUsqAojyGHmWovBJKMvDKRApJKY9MTYSJRDGRjDyikIEJeSSZGjGQwsjjX9apu86+57rnHroZnK++Ovdf+7pr7/beB5GPz5+QApPN8L8zCd/gJxwwatEkFjbAaTgIC+zl0HSQNF9iFqJEItyD47AFbsIPOKEHhWIevsB4sxAhPPk+M3TBGEkPcSo7I1nQGpU5cgd3zNADFXDIDF2wS9Joo8pGrWxZZUFkkQwaUVkaLFWf3VJJ3ppvhycwR2X1JH0tqSwI3mM8qJzk0PCB4dmewzo1zg1V5K15J2ZI+qo1C5oF+EpyTc7CYthF8sVWNc4Nf9V8KnyCFzDJqNng/X5FMok8K8uF3SS3QCjSYYZhE5xyyFl9GMOxAm9gplnQcJFXmGd5CfthjG2EM/xC4x9YNdwn2W5mzuZ/fzM8w/CUZPV/pJmk+TKSA/oIF20jIuO326aN5ObhxWF4y3QGynbmyH6/b8Bb65m3QLX17JbfNM+/tQ4TVMYLyufQkWu4rT6vwQPreYsi/1/Ha/OF8BkekbxpD+AhvIe9gWEBeIbvsEdl/JJ5IJlEpDcN47X5Y5Lt6yT/TUeyKfiA8g0T9rCEwGvz/wK+EovM0MfHx8cn6nwBs5JfdwJVj6QAAAAASUVORK5CYII=>

[image68]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHQAAAAaCAYAAABmZHgNAAAC50lEQVR4Xu2YWahOURTHl6lrniVCt5CQhCiXUsbLo3iQUOIF4UWZHo3xoHgx5UXIE2W8MpbhhSgkvClleJBCrvH/v+voO2fde3z77Nt3ji/7V7/6ztr7fMNe31l7nSMSCAQCgQLpBrvYYKD62Am/wF9wgxkLFEctXGaDrqwQTehkO/AfUwvPwr4mXklGwl3wPvwJzyeH3TkMP8EOdqCK4Z9zrQ1mYDv8JvluQ5PgcjgBfpVWJPQlvGKDVc5MuNkGM3AX3rPBHPFO6GDRcrs1FusP62LHRdARToGzYU8z5sIsyZ5QVqhhcDRshEfhcNgjPiknvBO6RDShU2FbuBseh4/gwti8POGiPoB74Sb4EA5JzCgP/whZE8o1uAwfi67Jneh4bnxSTngn9Aj8LLpXHBCt46tEf9DS2DxLV3gN3kzxBrwezaFX4Tie6MAh0e6bsIJwf19QGnbCJ6F/KGL/tHgnlPvnE9HEjopiI+Bq0bJXBG/gbTgd9hFt32sSM5IMgAONi0Q7Rhun7fS0VHhlcg91obc0f/80O0XnuMCEXrDBcgwSvRI/iJaZ9bBNYkYx7BH9XvStaDufBh+InIAnjawO3DZsnI5pOrNleFU2SqlClGObNH//NOdH57jAhF60wXIsFl00Nh918L1oI+ACEz9DtPlwlVebC53hStFF+CFaRbLiW3J5Htek3g7kjFdCD0ry/vMMfB69ZsmaE71uCS76FtHu2NWhTWemw+7ylSSfkOyHz2LHrvgmdAf8Lnrlk42i3ytvmNBLNliOp7AhdnxatJkh5yT/pmAdfAfHR8fc6/ijuJ9nxTehp6RUEcaKrkne8AJj2b8F25uxVGpEy9maWIw341xQ/oi/dbiVgg0Gyww/f5/oozfetvjgm9Bpol3/MdHbt+7J4YoyD76Ar+HHSDaIrJpO98K8t7NNEDvbfiaWN71EG7bW4JtQwu2ED1cC/xC8TZhog4FAIBAIBAKBQCAQKITfY0Oe6dwlGwQAAAAASUVORK5CYII=>

[image69]: <data:image/png;base64,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>

[image70]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFIAAAAaCAYAAAAkJwuaAAAC80lEQVR4Xu2XWahNURjHP1PIlBczma4hU4ZnyhDCkycprim8GOLBFB6UsSgledBFhjyYQlFcQzxQJC+ESAqRUsYU/v++de5Ze7XHc/Y97Yf1q1+ds7692+t8Z631fVvE46khR+AHWOcGPNkYDD/DFm7Ak40l8Jw7WGTaik76LHwKRwXDTXBl7IC73ECOtIeb4Sp4Aa4OhotLS3gNHoS34T84M3BFmRmi8XluICcGwruwF+wP/8Ix9gW1pDMcBydYtgpcEc1h+Ad2cgOGM/A77OAGcoIrcLv5zKR+Ef2ja8pUeAdehIfgfrgX7obdrOui4ITfwstuwNBHNMmn3EBOtIa/4ETzfbFoYlPD0j7SHRRdFWmrFc+tS3C0G8gAt3Pctj4mGp/jBnKCfyQrdBfznUVmLdzYdEUMG0RXzgu40hrvC3/AWdZYFLPhFXewAq7ClxK+laaIJvGnaDFoLlhgtonm5QA8IboyY+knWiXJe3jcijGpnDi3UxIP4CB3MCO8nwf7OjcgmjgmmPO57sSiYCPNwhXmLdhovAlvwHreZOBO5DYn7azxSBbAsUZOst6KMcGvre9R8EHnRatcnEnsEz2furoBsFN0fnS9EysU7Ml+S/BHfJTgCo1iAHwFTyfYo3RDCPz3P0n4wT5e9Ii5J5rIas7gZueZaB9XYrjopJdZY1Fw27HvSluUwpgu+rw1znhv+E70jOL2Y0LDzs8w+AdMyyBfBauCbxT8EVutsRVmbJho48sHxcGVu8gdzMAm0efxzaZEd/gEboFtRJP4yIonsVz03rRO1tsqh9uKJX+P+c6DlhNmdWQTzRYgqfntCR+LruRKYHvBRLJqs5mfBJ/DhSY+xMRPwo5mrJDMh29gA3woWnS+wvuS/j2TSeS9DXCEaPLTvs3w3PsmmiwWHPaj3Jol2CAzxjlxi3MXFRauzDop/3hOloUkC9yCc+FR0TalUcotR1LlHgqXSvgz2RmwWrMRr+Ys9ng8Ho/H4/F4CsN/wy+X5jm6ABgAAAAASUVORK5CYII=>

[image71]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAyCAYAAADhjoeLAAAFe0lEQVR4Xu3caah1VRkH8GWTNmlRkTRRZpIaVhRBIVHQAEVUYDgQJlFa4UBYkBSRNKhlNOiHaKSJyiQIsj6IZhaFIKZ9yGiA6IuNBEmJZdT6s/fyrHd5h3O953rve/394OE++9nn9Zx7zoXz+Ky1dykAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3L89fixs01vHQnXIWACA/egJYwGW9JWx0PnoWNjE+8bCGh5Q46ruOH+7v6vxma4GAPvOOTXuGouwpI0ati+MhQ1kSvaJsbiO07v8r10OAPvW7TXeMRb3gBfXeNxYXMcLaryzxv9qPGM4t1v+U6bXsxVpfs4r07/7+nBur2oN2z/L1HCd3517Q5dfU6am7KSu1rukxqHd8WNqXN4d9x7b5X+scW6NB3Y1ANh3tjIFuS99uMaLxuI6XlfjQWNxl6Vx3GrDdnON14zFXXbYGtH76vzzLzWOq3Fqd+6lXZ7/KfhJjYeV6TF90xUndnmWPa+s8fz5+HM1nr04ffdnnaZur33uALAjMp3aiz5Slm/Y0kR8aCzusqPL1hu27OH681jc4742//xbuWfD1i4QOL5ME7AWD63xvPagWbtwIOd/P+ftMWPDlvc2zu5qAHDQe0+ZlqvePh8/ucarF6dXLs/3m+74X12+rGUbtmNqfKfGf8vql8V+WeODZdrQftNcyxQsjdgna3y+TEuBzVNr/KxMy4LfK4uGLUt9mUS9tsaXahw713tpWG6s8eMapwzntuvCGtfX+NZ4YpBl6F+UaRq2itdwdZf3E7Uzy/ReNe3vstd/lmnYntMd5/dpvj0HABz0rph/tv1G+YJ80pxv5kdrxA9rXFvjB+XAfUfxlDI9321dbdlJU/vyTfyqTM/Tjr/RPa6XPUyZ6ny3xjOHc9vx8DI1jZElujQfD5mPf1sWk6T23kaauTRGcVpZ/N5Z3v33nMf3u7zJFZVZ4ntujW8O5+IRZXrP+8/hurL4LPLv1vOPGo+ucdl4YpB9dxfN+SqaoPX2Rv6hTI1h8/EuX0ua2HbFaf6+2ucSaQTzt5LfDwAOeheXxZfan/oTO+TOLh+vJHxUmRqijSwzYcu+p1fMeaZXq1zezVJfW3qLPNen5rxN2yJNUNtHlQbt5XOe5bzWsOVnbj2R9yHx5bne+2mXr9XQbUemgHkNbRN/pnknlOlqyyxjxsllmihm79gH5toqpNHczNj0b+SJYwEA9ot8IfZTruSZELXmIlozMsq+qvXigrL2l21q75/zt5Vp8tWe61U1Lp3zjSzTsL27y8erKlsjcm+9pUyvtckyXGsIf97VP13jwXOe9/WsOe8btlvKgU1y/9+NLP/l9iqRixWy52uUzfrvLff8DFo8ffHQA+T1Na2JThOVpi1a85jPqV+qdW8+ALiPZQLU7lf1yBp3lGnf12ZTrnsrz5clrDxXplFpSNpzvb6sf2uH3jINWxqbZ815lv2aM8ryy7Drye+QfWh57ZlMZn9Z5PjWMi2TRva3HTHnmZK16dtny+I15GrHu+Y8vtjlTSZbMTae2/X3Lv91l0eashfO+VE13jTnaUBzmw0AYBdkepOGo5+KvblM05l3dbVVSMPTNo4/rT9Rpo35q5LGqV+6XLU0Y2k8tyLvcyZimSy26VvkAonW3K3lyLGwImnGxttxfKzGy8qBTXH26K1yHyAAsCLtXlfjMt1OyXJcJnw7zV6njWUJNBcqbHYhAgCwR7xyLOyQTN2y1NauRNwph9d441gEADiY3TAWdkguErCZHQBgC15SphvotnuHAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADcL/wf0LfCCEUnBZwAAAAASUVORK5CYII=>

[image72]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGsAAAAaCAYAAACwwaJoAAAD7ElEQVR4Xu2YaWgVVxTHj9aoiEgVUWMR1NYNF4rF3TZPqf1QFxBFBf1gBLWFalFoq6AGFf1QlLqBS0FciiIu4G5wSVS0FaUItrhUWhW3Iu4ICm7/f85MvHPy5mXeizHPx/zgRzLn3sx7uWfmzJkrEhMTE1NV8mB9G4zJTubAr2ww5t1Q4BmVP0TvLkttWAg/sgMeHB8KF8BpMD84XM7ncK7n12YsGR3gXhvMJQbB1fA/+Ar+EBwOpR9cYWIT4VZ4V/RcPYLDZdSF20QX9Qv4I7wB+7iTwCK4EY6FS+ALeEjCyy4vgJPwfzuQS4yAo0QXJZ1kMcG9TWwKHAwXS3iyvhFd0AZOjHfYP7COd5yAZ2EjfwJYKnrOn52Yy3T4VHI8WT68sqMmqx48bYMOMyU8WX/CXSb2pej8/t7xLO94VfkMvQsZu+7EfNrB/Z5VSlYb0frcBdYyY9lEOskaCYts0CEsWR968fUm3t2Lz/aO+Xen4PDyGSLNROdcc2KEa1oMP4H7pArJ4oPxGJwKt4jW4WwlnWTthB/boENYsngHMM4S6tLZi680cReWV85ZZuLfiZZAknGyWsFHsLF3vBz+9WY4I9bAoyGWwhLPI/AwHM8/ikjUZDUV/axUhCXL/wyblE5enBd0GCdE15NzfVrDg6LNBck4Wd/Cl6JZZwvLuvxpYIZIczjJxGoKfyHZnaWCVzL/t1T4yepp4mxIGHefRcRP1iYT9+EaPYYDTXy3BJOXcbJYY5+Ifglq21zezgdE29ZswE/WT3bAwLLexAYNfrJ6mTifK4z/auJ8nicrcWQAvCkV79IJop/jknGyCD+AbelF0S8zLjhc1qKmk6zPRN+LosrFiUqUZLWHO2wwCWHJagifS8Vy11eSf3ZXeA52dGLfez83wKvwCvzX85no+fk7W/1I8Arhe4NPvuiJxjgxkpD0kjVZtK2Nqi0bqfCTNcMOOMyTYIcWhp8s+x5GSuHvJsZ14fxuTozPfD57+dMnT7RLDIOJTfvOug/XOsd8f7gk2rq6JCS9ZFUnBaILxkqQDLbIZ0R3ICqjSPRcyfYNR4s+Hlo6Md4lpc4x1+lv0YaMjVKJaPk9D7c78ywX4D0brIxCeFy0A2TSikU7F0tCtB7XJHy9YBW4Ax+KdlwsL3vcSaIXnO3iLHwGX4YPRM/FpoDn5oavy3zRhWdJ+010m8jdreAFw2Qnc6Ezz4fbUfzO/O70NvwlMKMSPoBtJXwviyTgLRvMUtjB8dnytmghus3F8svylvUk5P1IFktfqmdFzsPyw1aT5WIdHBIYzS6GScVSFpOlbBbd44x5D6hsCyomJiYmJiamGnkNxzzvsoCCPvcAAAAASUVORK5CYII=>

[image73]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFYAAAAaCAYAAAAtzKvgAAADKklEQVR4Xu2YaahNURTHl4xlCJmHjAnJkCFTPQklUYZkSqYyJElmwlM+GEqZhyKfJCFCKbMPiI98ME8lIVNJvuD/b+3j7rO8e+851/PeuTq/+tU9a+997j3r7L3OPlckJSUluVSHtWww5e9ZB0fYYMqflDijckt01lrqwclwNexq2iw14VnYxjYUO8PhfvgM/oTLws1ZGQR32SAYI3qumaLnfgL7hHqE2Sz6vV1sQ7EzHk6EUyVeYnkz+ptYD/gBdnDHnP085/bfPcL0g1/lP01swACJnlgu3zsmVg2+hMe8WF24BfbyYgE8xzW4TQpMbDs4GnaDVUxbkoiT2AlwvYlxtnL8YtHrZM2sGuoRZhOcApdLAYkthdfhItE7ybuTVOIk9rRklnvAbNHxG+F5eBi+hQv8Tg7O4BPuc+zEtoZfYAN3vBPeyzQXxAHR5VOWV+EV52V4Cc7goIhETWwj0e+y7BEd/1B0mZNgFrOGB7Bk8De2cMexEzsf/oBLYEs4DPb02muLPjm5dHgTKpsgsbzQXCwUvTbLcdHxa038jYTr8RrR6w6IndgmknniUX9rwhp0EHaH0+E3yb/f+9cEiV1hGwwsbQ1tEOwWHc+66fPYxRuLJu9MuDl+Yklf0SL9QHTwNBcfDL/Dpu74omRqTi56i+4No9pRh0UiSmI7wZM26FgqOn6ciT9y8Wai9fYFfA6fOj+79leiLxw52SF6woDmoomc5I7riCY52CUwqUfc51zMFV1qUR2qwyIRJHalbfDgg2msDTo6i46fY+Kv4X3JviPisyfyjP0ID3nHnKEs6vW9WACL+HvRC6tMSkQvkCusLJiYu7CGbfDgyjvnHXOG85wjvZhln2gfPujywuJ8Q/RuMMEXYFu/g4P7vFNwlG2oQEpFV9c70WXJnQyXK9/ffTg59pqYhcudOx9eE7eWnK2rQj0ysBbzdfeT6Hfyje1mqEcWmLT2kvtvta2iuwUy0G9IIJxZUX4jZzbr+yzYyrRVCKxl80Q3y3zn5uxOKlz+t20wiQwRrSu+G7z2pMF/rPjfa0o5c1T0P4+Ucibfa25KSkpKShHzC8/+sz/Ga1U+AAAAAElFTkSuQmCC>

[image74]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAaCAYAAADbhS54AAACS0lEQVR4Xu2WS6hNYRiGX9dQEjFwKSXJpQwUSSiRJIqBkhSScplIISUMxAADRZkoBnIt0ekkyuBMTomBDMU5GLgkuZTOUS7v61sr/3nPWvusvY/OaD/1tNf+3n+vVv//7W9voMnAMskLFZnshf/JcnrbixW5TDd6sRZa3EnfZK8v6XO66d+Sv0yjb+kMq1dlIv1IF3vQF3fpb7rKg4zH9IwX6+Qg7aDDPChjEP1Av6H4Q8voezrGgzoZjjiNnR6UMQexW60eZKivznmxQY7Qp14sYw/iwfZ7QAbTbrrXg4yxdAliXYp2Z4TVhHr3F53gQRE3EQ823wMyBZGt8QBxxLdoC71u2TN6ympiAeJ+6z1w8v76SodYJpYibjTT6lr7gI6i1+jrJJuF+MzmpJYzDpHplGrSV39toT8RR5Myl26lQxFj4FKS7Ubcc2pSS/lEj3rRyfvrgAcZ+xC7WYbGiz6/OqndQM8ddF7Q41508v7S2RexDZGP9yDjAnqPmXf0SvI+RS3wg+7wwNF80o11JEWsRTzYQg8y2unD5L16Ues1q6bTQ0km9AuifIXVezAPsUhNXIZuXtbI4g59lF1rZGgHtX4RPYwYJSkrEbkesBcbEBP4M/2O2LFXiGYuopMes1qOvoEd9Cp9QnchBqiuVXP0xfiC8hOqC019zapaaAdGZtcaQdppH7riIj3rxUbR174LDfwzMGYjfkUa/YdSyGnE8RTtQlXu0/Ne7C/qiXt0uwcVWUfbUPzvpd+Mpie9WJETKJ+FTZoMCH8ALvZvJYefRbYAAAAASUVORK5CYII=>

[image75]: <data:image/png;base64,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>

[image76]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEwAAAAaCAYAAAAdQLrBAAACUElEQVR4Xu2YS4hOYRjH/4jcpakJKQuTFBvRyGxGhFhIlJINNkpYuWXUoFxK2VNWdpYuWbnFgo2YyG0mKdfYoMTC5f/vOUfveWbO+c5ZfMd8en/1q/M9z3um8z3fe3nOAJFIBUbSg3RV4v4kFslhMv1Ff9KHdGkmGxnEJHqKjvGJVqQ7MY/FtIceogtcriwTYQVbSNe5XEuwgp6hL+lvujeb/sse+piup5voc7ozM6Ic4+h92kk30it0dGbEMGcD7ME3I79gc2G5RUFsJf1B5ySfNUazL8/5yTgRLscBujz43DIsQX7BTtMvLqYvrc1by1PopBtbYHoSrqW9ybV4AitoZWbQDh+skaKCPaCvfBBWxGs+2IBd9EhyPYp+h7UXpdB6PkEf0dv0Ep2SGVEfRQV7Q5/5IPkImyFVaKPn6FZ6FzZ7S9EOu+EGne5yeZylt3K8Cftb8jrsl9+im0pSVDDtVUMV5kNiVUbATtlZPlHEBfqNzoat73/d7aYF2+cTsGXz1AdhxXrrg81gKmzD/Ez7A7vCQTWTFkyvKp7X9IUPkk+0zwebgaajHu64TzRAzZ76prJWOUSKCnYPg5eelpWW6lUXbwoTYNP8gE80YDvsGC/rMrutFGnBhnqmw7AVofYgZRps/O4g1lQuwjbncO+aGVzXTTesAMd8ArbPfkX2VWYbfQ8rXC2Mp+fpHXoSdrrtyIyoB/VE2p/UImhPVW+lnutyOIispu/oUdjzqkOflxlRE+q7tNdoTxju6MV5Dax4+q9DJBKJRCKRSOQ/5g+EyH7MYVorPwAAAABJRU5ErkJggg==>