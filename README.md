# INF2608 - FUNDAMENTOS DA COMPUTAÇÃO GRÁFICA - 2026.1 - 3WA - DI PUC-Rio

> Aluno: Yang Miranda

Este repositório implementa um renderizador de traçado de raios baseado nas aulas do Prof. Waldemar Celes.

## 🛠️ Requisitos e Ambiente

- **Python**: 3.13.9
- **Gerenciador de Versão**: asdf (com plugin python/pyenv)
- **Biblioteca Matemática**: PyGLM (OpenGL Mathematics para Python)

## 🚀 Passo a Passo para Setup

### 1. Instalação do asdf e Python

Caso ainda não possua o `asdf` instalado, siga as instruções oficiais. Em seguida, adicione o plugin do python (que utiliza o `pyenv` internamente):

```bash
# Adicionar o plugin do python
asdf plugin add python

# Instalar a versão específica
asdf install python 3.13.9

# Definir como versão local para o projeto
asdf set python 3.13.9

# Criar venv
python -m venv .venv
source .venv/bin/activate

# Instalar bibliotecas recomendadas
pip install --upgrade pip
pip install PyGLM pillow numpy
pip install -r requirements.txt
```

### 2. Execução

```
python src/main.py
```

Este relatório analisa a implementação do seu motor de traçado de raios (_Ray Tracer_), correlacionando a estrutura do código com os conceitos teóricos apresentados nos materiais didáticos da PUC-Rio (Prof. Waldemar Celes).

### 1. Visão Geral do Algoritmo

[cite_start]O traçado de raios é um algoritmo de renderização que opera **por pixel**, determinando quais objetos afetam a cor de cada ponto da imagem ao simular o caminho físico da luz[cite: 1, 3]. [cite_start]Sua implementação segue o procedimento padrão: geração de raios, cálculo de interseção com a cena e cálculo de iluminação (_shading_)[cite: 4, 2, 3].

---

## 2. Análise Teórica e Técnica dos Módulos

### A. Modelo de Câmera e Geração de Raios (`camera.py`)

[cite_start]A classe `Camera` implementa o modelo **Pinhole**[cite: 4, 14].

- [cite_start]**Conceito:** A câmera é definida por parâmetros extrínsecos (posição do olho `eye`, alvo `center` e vetor `up`) e intrínsecos (campo de visão `fov` e proporção da tela `aspect`)[cite: 4, 15, 21].
- [cite_start]**Implementação:** O código utiliza a matriz de visualização inversa (`inv_view`) para transformar o raio gerado no espaço da câmera para o espaço global[cite: 4, 29, 38].
- [cite_start]**Mapeamento:** O método `generate_ray` calcula as dimensões do plano de imagem ($\Delta u, \Delta v$) com base no FOV e atira o raio pelo centro do pixel ($x_n, y_n$)[cite: 4, 25, 29].

#### B. Geometria e Interseções (`shape.py`, `hit.py`)

[cite_start]A visibilidade na cena é resolvida encontrando o ponto de impacto mais próximo para cada raio[cite: 4, 5, 6].

- [cite_start]**Esfera:** A classe `Sphere` resolve a equação implícita da esfera através de uma equação de segundo grau[cite: 4, 15, 16]. [cite_start]Sua implementação trata corretamente as duas raízes ($t_1, t_2$), selecionando o menor valor positivo que respeita a tolerância $\epsilon$ (0.001) para evitar auto-interseção[cite: 4, 17, 18, 58].
- [cite_start]**Plano:** A classe `Plane` utiliza o produto escalar entre a normal e o vetor do raio para determinar o ponto de interseção[cite: 4, 11, 12].

### C. Instanciação e Transformações Afins (`shape.py`)

[cite_start]A classe `Instance` permite que um objeto geométrico seja movido, rotacionado ou escalonado sem alterar sua definição original[cite: 4, 44].

- [cite_start]**Conceito:** Em vez de transformar o objeto, o algoritmo transforma o raio para o **espaço local** do objeto usando a matriz inversa ($M^{-1}$)[cite: 4, 33, 44, 46].
- [cite_start]**Implementação:** O código aplica $M^{-1}$ à origem e direção do raio, realiza a interseção e, em seguida, transforma o ponto e a normal resultantes de volta para o espaço do mundo usando a matriz original $M$ e sua transposta inversa para a normal[cite: 4, 46].

### D. Modelo de Iluminação de Phong (`material.py`)

[cite_start]O `PhongMaterial` implementa a interação luz-matéria para determinar a cor do ponto de interseção[cite: 4, 42].

- [cite_start]**Luz Ambiente:** Representa a luz indireta global: $c = m_{amb} \cdot l_{amb}$[cite: 4, 54, 55].
- [cite_start]**Componente Difusa (Lambert):** Baseada no cosseno do ângulo entre a normal e a luz: $m_{dif} \cdot L_i \cdot \max(0, \hat{n} \cdot \hat{l})$[cite: 4, 32, 42, 49].
- [cite_start]**Componente Especular (Glossy):** Simula o brilho refletido: $m_{spe} \cdot L_i \cdot \max(0, \hat{r} \cdot \hat{v})^{shi}$[cite: 4, 32, 43, 49].
- **Visibilidade e Sombras:** Antes de aplicar a iluminação direta, o código dispara um **raio de sombra** em direção à luz. [cite_start]Se houver obstrução, apenas a componente ambiente é considerada[cite: 4, 38, 39, 51, 52].

### E. Gerenciamento da Cena e Renderização (`scene.py`, `main.py`)

- **`Scene`**: Centraliza a lista de objetos e luzes. [cite_start]O método `trace_ray` coordena a busca pela interseção mais próxima e a avaliação da radiância resultante[cite: 4, 35, 47, 48].
- [cite_start]**`Film` (`film.py`)**: Gerencia o buffer de pixels onde os resultados são armazenados como valores reais (_float_), permitindo precisão antes da conversão final para imagem[cite: 4, 24, 26, 28].

---

## 3. Conclusão da Análise

O código implementado demonstra maturidade arquitetural:

1.  [cite_start]**Modularidade:** A separação entre geometria (`Shape`) e óptica (`Material`) permite estender o motor facilmente para novos modelos (ex: refração ou reflexão recursiva)[cite: 4, 34, 46, 48].
2.  [cite_start]**Conformidade Física:** O uso de coordenadas homogêneas via `PyGLM` e a aplicação da lei do inverso do quadrado da distância para a radiância das luzes ($P/r^2$) garantem resultados condizentes com os slides[cite: 4, 30, 40, 49, 52].
3.  [cite_start]**Correção Técnica:** As questões críticas apontadas anteriormente, como o tratamento de raízes negativas na esfera e o deslocamento de raios para evitar auto-interseção, foram devidamente aplicadas no código revisado[cite: 4, 17, 18].

[cite_start]Seu projeto está pronto para evoluir para funcionalidades adicionais, como **Antialiasing** (múltiplas amostras por pixel) ou **Reflexão Recursiva**, conforme sugerido na Parte II do material[cite: 5, 4, 5, 51].
