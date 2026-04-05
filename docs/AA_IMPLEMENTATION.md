# Anti-Aliasing (AA) — Implementação

Resumo

- Este documento descreve como o anti-aliasing foi implementado em `src/ray_tracing_2/film.py`.
- Suporta dois modos: _jittered_ (Monte Carlo jittered) e _stratified_ (amostragem estratificada).

Arquitetura geral

- A classe responsável é `Film` (arquivo: [src/ray_tracing_2/film.py](src/ray_tracing_2/film.py)).
- Parâmetros configuráveis: `samples_per_pixel` (SPP), `sampling_mode` (`jittered` | `stratified`) e `seed` para RNG.
- Integração com runner/CLI: `--spp`, `--sampling_mode`, `--seed`, `--gamma_fix` (em [src/ray_tracing_2/main.py](src/ray_tracing_2/main.py) e scripts auxiliares).

Detalhes da implementação

1. Representação e estado

- `Film.image`: buffer NumPy float32 shape `(H, W, 3)` usado para acumular valores linear RGB.
- `self.samples_per_pixel`: inteiro >= 1.
- `self.sampling_mode`: enum `SamplingMode` com valores `JITTERED` e `STRATIFIED`.
- `self.rng`: instância de `random.Random()`, inicializada com `seed` quando presente para reprodutibilidade.

2. Geração de amostras por pixel

- Método-chave: `Film.get_samples_for_pixel(i, j)`.
- Jittered:
  - Para cada amostra (0..SPP-1) gera `rx, ry = rng.random(), rng.random()` e computa ponto subpixel:
    - xn = (i + rx) / width
    - yn = (j + ry) / height
  - Resultado: SPP pontos independentes dentro do pixel (Monte Carlo jittered).
- Stratified:
  - Calcula G = ceil(sqrt(SPP)) e subdivide o pixel em GxG subcélulas.
  - Para cada subcélula (até SPP amostras) escolhe ponto aleatório dentro da subcélula (ux, uy) e constrói xn, yn normalizados.
  - Garante cobertura espacial mais uniforme e reduz variação por amostra.

3. Loop de renderização

- `Film.render(scene, camera, filename, gamma_fix)`:
  - Itera sobre pixels (j, i).
  - Para cada pixel obtém `samples = get_samples_for_pixel(i, j)`.
  - Para cada `(xn, yn)` chama `camera.generate_ray(xn, yn)` e `scene.trace_ray(ray)` para obter `color` (glm.vec3 linear).
  - Acumula e divide por `len(samples)` (média Monte Carlo) para obter `final_color`.
  - Armazena com `set_pixel(i, j, final_color)` (faz `clamp` interno).
  - Ao final aplica `gamma_fix` opcional: `img_data = np.power(image, 1/2.2)` antes de converter para uint8.

4. Reprodutibilidade e debugging

- Se `seed` é fornecido, `self.rng.seed(seed)` garante que as amostras são determinísticas entre execuções.
- O `Render` centraliza a criação de pastas e grava `properties.md` com detalhes da cena (objetos, materiais, luzes), o que facilita reproduzir uma cena e comparar SPP/seed.

Boas práticas / notas

- A média das amostras por pixel usa soma simples e divisão por N (estimador Monte Carlo com variância ~1/SPP).
- `stratified` tende a convergir com menos ruído para o mesmo SPP que `jittered` por reduzir agrupamentos aleatórios.
- `gamma_fix` é apenas pós-processamento visual (não altera a estimativa linear durante acumulação).

Referências diretas no código

- `Film.get_samples_for_pixel`: [src/ray_tracing_2/film.py](src/ray_tracing_2/film.py)
- `Film.render` (loop principal): [src/ray_tracing_2/film.py](src/ray_tracing_2/film.py)
- `SamplingMode` enum: [src/ray_tracing_2/film.py](src/ray_tracing_2/film.py)
- Flags CLI e uso do `Render`: [src/ray_tracing_2/main.py](src/ray_tracing_2/main.py) e [src/ray_tracing_2/render.py](src/ray_tracing_2/render.py)

Exemplos rápidos

- Render com 1 sample (rápido, sem AA):
  - `python src/ray_tracing_2/main.py --spp 1`
- Render com 16 samples, stratified:
  - `python src/ray_tracing_2/main.py --spp 16 --sampling_mode stratified`

Se quiser, posso adicionar uma seção com visualizações (diferença entre `spp=1` e `spp=16`), ou pequenas ilustrações SVG mostrando as amostras no pixel.
