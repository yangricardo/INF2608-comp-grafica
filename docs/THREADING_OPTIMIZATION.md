# Otimização com Paralelismo — Traçado de Raios

Este documento identifica os pontos de otimização via paralelismo no renderizador
`ray_tracing_2`, com referências exatas aos arquivos e linhas que precisam ser
alterados.

## Consideração sobre o GIL do Python

O loop de renderização é **CPU-bound puro** (álgebra vetorial e interseções
geométricas). O Global Interpreter Lock (GIL) do CPython impede que `threading`
ofereça ganho real de performance para esse tipo de carga. As alternativas viáveis
são:

| Abordagem               | Módulo                            | Observação                                                  |
| ----------------------- | --------------------------------- | ----------------------------------------------------------- |
| **Multiprocessing**     | `multiprocessing.Pool`            | Cada worker é um processo separado; evita o GIL             |
| **ProcessPoolExecutor** | `concurrent.futures`              | API de alto nível sobre `multiprocessing`                   |
| **Tile/Row workers**    | `multiprocessing` + shared memory | Buffer de imagem em memória compartilhada para evitar cópia |

---

## 1. Alvo principal: loop de pixels em `Film.render()`

### Arquivo: `src/ray_tracing_2/film.py`

**Linhas 107–121** — O loop aninhado `for j / for i` é o gargalo dominante. Cada
pixel é **completamente independente**: não lê nem escreve dados de pixels
vizinhos. Isso o torna ideal para divisão em workers paralelos.

```python
# film.py L107-121 (trecho atual — sequencial)
for j in range(self.height):
  for i in range(self.width):
    samples = self.get_samples_for_pixel(i, j)
    accum = glm.vec3(0.0, 0.0, 0.0)
    for xn, yn in samples:
      ray = camera.generate_ray(xn, yn)
      color = scene.trace_ray(ray)
      accum += color
    final_color = accum / float(len(samples))
    self.set_pixel(i, j, final_color)
```

### Estratégia de paralelização

#### Opção A — Paralelismo por linhas (row-based)

Cada worker processa um bloco contíguo de linhas (rows). Simples de
implementar e com boa localidade de cache.

**Mudanças necessárias:**

| Arquivo                     | Linhas   | Alteração                                                                                                                                                                            |
| --------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/ray_tracing_2/film.py` | L22      | Adicionar `import multiprocessing`, `from multiprocessing import shared_memory`                                                                                                      |
| `src/ray_tracing_2/film.py` | L27      | Trocar `self.image = np.zeros(...)` por um buffer em `multiprocessing.shared_memory` ou `multiprocessing.Array` para escrita sem cópia entre processos                               |
| `src/ray_tracing_2/film.py` | L102–121 | Substituir o duplo `for` por uma função `_render_row_range(j_start, j_end, scene, camera, ...)` que cada worker executa, escrevendo no buffer compartilhado                          |
| `src/ray_tracing_2/film.py` | L102     | Adicionar parâmetro `num_workers: int = None` à assinatura de `render()` (default = `os.cpu_count()`)                                                                                |
| `src/ray_tracing_2/film.py` | L46      | `self.rng` é um único `random.Random` — compartilhar entre processos causa race condition. Cada worker precisa criar um RNG local com seed derivada: `Random(self.seed + worker_id)` |

#### Opção B — Paralelismo por tiles

Divide a imagem em blocos NxN (ex: 32×32). Cada tile é uma unidade de
trabalho. Melhor balanceamento de carga em cenas não uniformes (ex: Cornell
Box, onde pixels que atingem materiais reflexivos/refrativos demoram muito mais
que pixels de parede opaca difusa).

**Mudanças adicionais além da Opção A:**

| Arquivo                     | Linhas   | Alteração                                                                                                        |
| --------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| `src/ray_tracing_2/film.py` | L102–121 | Criar gerador de tiles `_generate_tiles(width, height, tile_size)` que produz `(i_start, j_start, i_end, j_end)` |
| `src/ray_tracing_2/film.py` | novo     | Função `_render_tile(tile, scene, camera, ...)` como unidade de trabalho atômica                                 |

---

## 2. Serialização de objetos (pickle)

Para `multiprocessing`, todos os objetos passados aos workers devem ser
serializáveis via `pickle`. As classes que precisam de verificação:

| Arquivo                                 | Classe                                      | Problema potencial                                                          | Solução                                                                                                       |
| --------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `src/ray_tracing_2/scene.py` L9         | `Scene`                                     | Contém listas de `Shape` e `Light` — OK se suas sub-classes forem picklable | Verificar que `glm.vec3`, `glm.mat4` são picklable; caso contrário, implementar `__getstate__`/`__setstate__` |
| `src/ray_tracing_2/light.py` L84        | `AreaLight`                                 | `self.rng = random.Random(seed)` — objeto `Random` é picklable              | OK, mas cada worker deve re-seed com ID único para evitar amostras idênticas entre tiles                      |
| `src/ray_tracing_2/camera.py` L8        | `Camera`                                    | `self.inv_view = glm.inverse(...)` — depende de `glm.mat4` ser picklable    | Testar; fallback: armazenar como lista de floats e reconstruir                                                |
| `src/ray_tracing_2/material.py` L80–230 | `ReflectiveMaterial`, `TransparentMaterial` | Só contêm `glm.vec3` e floats                                               | Provavelmente OK; testar                                                                                      |

### Como testar

```python
import pickle
from ray_tracing_2.scene import Scene
from ray_tracing_2.camera import Camera
# ... montar cena ...
data = pickle.dumps((scene, camera))
scene2, camera2 = pickle.loads(data)
```

Se falhar em `glm.vec3`, converter para tuplas na serialização.

---

## 3. Estado do RNG por worker

### Arquivo: `src/ray_tracing_2/film.py` L44–47

```python
self.seed: Optional[int] = seed
self.rng: random.Random = random.Random()
if self.seed is not None:
  self.rng.seed(self.seed)
```

**Problema**: um único `self.rng` compartilhado entre workers causa:

1. Race condition se usado via threading
2. Amostras idênticas se cada processo recebe cópia do mesmo RNG

**Solução**: cada worker cria seu próprio RNG na função `_render_row_range()`:

```python
worker_rng = random.Random(base_seed + worker_id)
```

O mesmo problema existe na `AreaLight`:

### Arquivo: `src/ray_tracing_2/light.py` L84

```python
self.rng = random.Random(seed)
```

**Solução**: ao invés do RNG no objeto `AreaLight`, passar um RNG por
parâmetro do worker ao método `sample_radiance()`, ou aceitar que cada
processo terá uma cópia independente (OK para `multiprocessing`; cada fork
recebe cópia com estado diferente se re-seeded).

---

## 4. Buffer de imagem compartilhado

### Arquivo: `src/ray_tracing_2/film.py` L27

```python
self.image = np.zeros((height, width, 3))
```

**Problema**: em `multiprocessing`, cada worker recebe uma cópia deste array.
Os pixels calculados pelo worker não são visíveis no processo principal.

**Soluções em ordem de preferência:**

1. **`multiprocessing.shared_memory`** (Python 3.8+): criar um buffer compartilhado
   e montar um `np.ndarray` sobre ele em cada worker. Zero cópia.

2. **Workers retornam resultados**: cada worker retorna `(j, row_data)` e o
   processo principal grava tudo no buffer. Simples mas com overhead de IPC para
   imagens grandes.

3. **`multiprocessing.Array`**: C array compartilhado; mais complicado de usar
   com numpy.

---

## 5. Ponto de integração: `Render.render()`

### Arquivo: `src/ray_tracing_2/render.py` L191–192

```python
film = Film(width=width, height=height, ...)
film.render(scene=scene, camera=cam, filename=img_path, gamma_fix=gamma_fix)
```

**Alteração**: propagar parâmetro `num_workers` do `Render.render()` para
`Film.render()`. Adicionar à assinatura de ambos os métodos:

| Arquivo                            | Linha                           | Alteração                           |
| ---------------------------------- | ------------------------------- | ----------------------------------- |
| `src/ray_tracing_2/render.py` L170 | Assinatura de `Render.render()` | Adicionar `num_workers: int = None` |
| `src/ray_tracing_2/render.py` L192 | Chamada `film.render(...)`      | Passar `num_workers=num_workers`    |
| `src/ray_tracing_2/film.py` L102   | Assinatura de `Film.render()`   | Adicionar `num_workers: int = None` |

---

## 6. Alvos que NÃO devem ser paralelizados

| Local                                | Arquivo / Linhas     | Motivo                                                                                                       |
| ------------------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------ |
| Loop de amostras por pixel           | `film.py` L111–116   | Poucas iterações (1–64); overhead de criação de task > ganho                                                 |
| Loop de luzes em `direct_lighting()` | `material.py` L52–66 | Tipicamente 1–3 luzes; overhead excessivo                                                                    |
| `sample_radiance()` da AreaLight     | `light.py` L92–110   | 16–25 amostras; overhead de thread/process > ganho                                                           |
| `compute_intersection()`             | `scene.py` L24–31    | Iteração linear sobre poucos objetos; melhor resolver com **BVH** (estrutura de aceleração), não com threads |

---

## 7. Alternativa complementar: vetorização com NumPy

Independente de threading, a geração de raios em `Camera.generate_ray()`
(arquivo `src/ray_tracing_2/camera.py` L19–25) pode ser vetorizada:

- Gerar **todos** os raios de uma linha (ou da imagem inteira) como arrays numpy
- Aplicar a multiplicação `self.inv_view * p_cam` uma vez sobre todo o batch

Isso não substitui a paralelização do trace, mas acelera a parte de setup dos
raios. A limitação é que `scene.trace_ray()` é inerentemente recursivo e difícil
de vetorizar.

---

## Resumo de alterações

| #   | Arquivo                       | Linhas   | Descrição                                                                                              |
| --- | ----------------------------- | -------- | ------------------------------------------------------------------------------------------------------ |
| 1   | `src/ray_tracing_2/film.py`   | L1–8     | Adicionar imports: `multiprocessing`, `os`, `shared_memory`                                            |
| 2   | `src/ray_tracing_2/film.py`   | L27      | Buffer compartilhado ao invés de `np.zeros` local                                                      |
| 3   | `src/ray_tracing_2/film.py`   | L44–47   | Suporte a seed por worker (não usar RNG global)                                                        |
| 4   | `src/ray_tracing_2/film.py`   | L102     | Adicionar `num_workers` à assinatura de `render()`                                                     |
| 5   | `src/ray_tracing_2/film.py`   | L107–121 | Substituir loop sequencial por despacho paralelo                                                       |
| 6   | `src/ray_tracing_2/film.py`   | novo     | Criar função `_render_row_range()` ou `_render_tile()` top-level (precisa ser top-level para `pickle`) |
| 7   | `src/ray_tracing_2/light.py`  | L84      | Garantir RNG re-seeded por worker em `AreaLight`                                                       |
| 8   | `src/ray_tracing_2/render.py` | L170     | Adicionar `num_workers` à assinatura de `Render.render()`                                              |
| 9   | `src/ray_tracing_2/render.py` | L192     | Propagar `num_workers` para `film.render()`                                                            |
| 10  | `src/ray_tracing_2/scene.py`  | L9       | Verificar/garantir que `Scene` é picklable                                                             |
| 11  | `src/ray_tracing_2/camera.py` | L8       | Verificar/garantir que `Camera` é picklable                                                            |
| 12  | Todos `main_*.py`             | argparse | Adicionar flag `--workers` nos scripts de entrada                                                      |
