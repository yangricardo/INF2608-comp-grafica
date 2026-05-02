# Projeto Final: Cena Inspirada nas Variacoes Anteriores

## Objetivo

Esta cena final combina os elementos explorados ao longo do projeto para mostrar, no mesmo enquadramento, efeitos de reflexao, refracao, variacao de material Phong e iluminacao mista por luzes pontuais e luz de area.

Arquivo da cena:

- src/ray_tracing_2/proj1_final.py

## Composicao da Cena

- Teto e parede de fundo espelhados (ReflectiveMaterial).
- Paredes laterais com comportamento contrastante:
  - esquerda com dominancia difusa e baixo brilho especular;
  - direita com especular alto e shininess elevado.
- Tres fontes pontuais posicionadas em triangulo no teto, cada uma com esfera emissiva coincidente para tornar a luminaria visivel.
- Blocos classicos da Cornell Box:
  - bloco maior espelhado;
  - bloco menor transparente.
- Losango tipo piramide dupla (octaedro visual):
  - metade superior reflexiva;
  - metade inferior transparente.
- Elipse transparente (esfera instanciada com escala nao uniforme).
- Luz de area posicionada atras da camera para preenchimento de iluminacao.

## Efeito das Propriedades dos Materiais

## 1) ReflectiveMaterial (teto, fundo e bloco maior)

- `reflectivity` alto aumenta contribuicao de raios refletidos recursivos.
- `specular` e `shininess` controlam a nitidez dos highlights locais de Phong.
- Resultado esperado: repeticao visual da cena em reflexos, aumento de contraste e percepcao de profundidade.

## 2) TransparentMaterial (bloco menor, metade inferior do losango e elipse)

- `ior` controla desvio angular da luz (Snell), alterando distorcao do fundo.
- `attenuation` colore e absorve energia ao atravessar o volume (efeito tipo Beer-Lambert simplificado).
- Resultado esperado: distorcao do fundo, bordas com comportamento optico diferente e transmissao parcial de luz.

## 3) PhongMaterial (paredes laterais)

- Parede esquerda com `diffuse` alto e `specular` baixo gera resposta mais fosca.
- Parede direita com `specular` alto e `shininess` alto gera brilho concentrado.
- Resultado esperado: comparacao direta entre material matte e material brilhante no mesmo setup de luz.

## Estrategia de Iluminacao

## Luzes pontuais trianguladas no teto

- Trazem direcionalidade principal e sombras multiplas sutis.
- Como cada fonte tem potencia levemente diferente, a cena evita iluminacao uniforme demais.
- Esferas emissivas associadas tornam a posicao das luminarias legivel para o observador.

## Luz de area atras da camera

- Funciona como luz de preenchimento para reduzir regioes totalmente escuras.
- Ajuda a revelar refracao e reflexao em objetos frontais sem eliminar contraste global.

## Geometria e Leitura Visual

- O losango de duas piramides cria transicoes entre reflexao (metade superior) e transparencia (metade inferior).
- A elipse transparente adiciona variacao de curvatura e reforca o comportamento de refracao em geometria nao esferica perfeita.
- A combinacao de blocos classicos com novos elementos preserva referencia Cornell e amplia complexidade visual.

## Observacoes de Render e Estimativa

- A cena usa o pipeline unificado com `run_render_with_estimation`.
- A medicao inicial (calibrate) ajusta throughput para melhorar previsao de tempo na execucao corrente.
- Logs de tempo seguem formato padronizado: segundos (minutos).

## Execucao Recomendada

Exemplo basico:

```bash
python -m ray_tracing_2.proj1_final --width 800 --height 600 --spp 1 --sampling_mode jittered --light_sampling_mode stratified
```

Exemplo com mais amostras:

```bash
python -m ray_tracing_2.proj1_final --width 800 --height 600 --spp 4 --sampling_mode stratified --light_sampling_mode stratified --seed 42
```

Somente medicao inicial:

```bash
python -m ray_tracing_2.proj1_final --calibrate-only
```
