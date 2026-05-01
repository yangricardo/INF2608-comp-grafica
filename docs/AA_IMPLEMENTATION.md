# Anti-Aliasing (AA) — Implementação

## Resumo

O anti-aliasing do projeto está concentrado em `src/ray_tracing_2/film.py`. A classe `Film` preserva o caso básico de uma amostra central por pixel em `get_sample()`, mas o fluxo normal de renderização usa `get_samples_for_pixel()` para gerar múltiplas amostras subpixel e estimar a cor média do pixel por Monte Carlo.

Os dois modos suportados são:

- `jittered`: amostras independentes e uniformes dentro do pixel
- `stratified`: subdivisão do pixel em uma grade `G x G`, com jitter interno em cada subcélula

## Estrutura da Implementação

### Estado mantido por `Film`

- `image`: buffer NumPy `(H, W, 3)` em RGB linear
- `samples_per_pixel`: número de amostras por pixel, truncado para no mínimo 1
- `sampling_mode`: enum `SamplingMode.JITTERED` ou `SamplingMode.STRATIFIED`
- `rng`: `random.Random`, opcionalmente inicializado com `seed`

### Amostra central versus AA real

Há duas rotas importantes no arquivo:

- `get_sample(i, j)`: devolve o centro do pixel, isto é, a formulação determinística do núcleo do Slide 4
- `get_samples_for_pixel(i, j)`: gera uma lista de amostras subpixel e implementa a extensão do Slide 5

Essa separação é útil porque evita confundir a câmera pinhole básica com a política de amostragem. A geometria da câmera é a mesma; o que muda é a qualidade estatística da estimativa da cor do pixel.

## Modos de Amostragem

### `jittered`

Para cada uma das `SPP` amostras, a implementação gera `rx, ry in [0,1)` e monta:

$$
x_n = \frac{i + r_x}{W}, \qquad y_n = \frac{j + r_y}{H}.
$$

Isso produz amostras independentes dentro do pixel. É simples e compatível com a formulação apresentada nos slides, mas permite agrupamentos aleatórios locais e, portanto, variância maior para o mesmo número de amostras.

### `stratified`

O pixel é subdividido em `G = ceil(sqrt(SPP))` subcélulas por eixo. Em cada subcélula, a implementação escolhe um ponto com jitter interno e o converte para coordenadas normalizadas. O resultado é uma cobertura espacial mínima do pixel, o que costuma reduzir ruído em bordas e regiões de penumbra.

Esse modo não altera a física do renderer. Ele apenas melhora a distribuição das amostras usadas no estimador Monte Carlo.

## Loop de Renderização

`Film.render(scene, camera, filename, gamma_fix)` segue a sequência abaixo:

1. itera sobre todos os pixels;
2. pede a lista de amostras para o pixel atual;
3. para cada `(xn, yn)`, chama `camera.generate_ray(xn, yn)`;
4. avalia `scene.trace_ray(ray)` e acumula a cor retornada;
5. divide pela quantidade de amostras para obter a média Monte Carlo;
6. grava o resultado com `set_pixel()`;
7. aplica `gamma_fix` opcional apenas no fim, antes da conversão para `uint8`.

Portanto, o pipeline correto é `Render.render()` -> `Film.render()` -> `Scene.trace_ray()`. O `README` antigo descrevia `film.py` como pouco integrado; isso não corresponde mais ao estado atual do projeto.

## Reprodutibilidade

Se `seed` é fornecido, `Film` inicializa `self.rng` de forma determinística. Isso é importante para comparar:

- `spp` diferentes sobre a mesma cena
- `jittered` versus `stratified`
- versões distintas do renderer sem introduzir ruído amostral diferente entre execuções

## Observações Técnicas

- A acumulação é feita em RGB linear; `gamma_fix` é apenas pós-processamento de exibição.
- `stratified` tende a convergir visualmente melhor que `jittered` para o mesmo `SPP`, sobretudo em contornos e sombras suaves.
- O arquivo `properties.md` gerado por `Render` registra `samples_per_pixel`, `sampling_mode`, `seed` e `gamma_fix`, o que facilita rastreabilidade experimental.

## Arquivos Relacionados

- `src/ray_tracing_2/film.py`
- `src/ray_tracing_2/render.py`
- `src/ray_tracing_2/camera.py`
- `src/ray_tracing_2/main.py`
- `src/ray_tracing_2/main_area_light.py`
- `src/ray_tracing_2/main_box.py`

## Exemplos de Execução

Com o pacote instalado em modo editável:

```bash
python -m ray_tracing_2.main --spp 1
python -m ray_tracing_2.main_area_light --spp 16 --sampling_mode stratified --seed 7
```

Sem instalação, a partir da raiz do repositório:

```bash
PYTHONPATH=src python -m ray_tracing_2.main --spp 16 --sampling_mode jittered
```
