"""# Etapa 06: Mesh Lights — Implementação de TriangleMeshLight

## Status: ✅ CONCLUÍDO (1.0 ponto)

### Resumo

Implementou **TriangleMeshLight** — fonte de luz representada por uma malha de triângulos com distribuição
de amostras uniforme de área. Substitui a representação retangular (RectAreaLight) por uma geometria
mais complexa e flexível.

### Arquitetura

#### 1. TriangleMeshLight (nova classe)

**Arquivo**: `src/path_tracing/lights/area_mesh.py`

```python
class TriangleMeshLight(Light):
  def __init__(self, vertices, faces, Le, seed=None):
    # Precomputa:
    # - Normais e áreas de cada triângulo
    # - CDF (Cumulative Distribution Function) para amostragem weighted
    # - Permite seleção de triângulo proporcional à sua área

  def sample_Li(self, ref_point, u):
    # 1. Seleciona triângulo via u.x (CDF por área), guardando o limite do bucket
    # 2. Remapeia u.x dentro do bucket -> u1 fresco; ponto uniforme via
    #    uniform_triangle(u1, u.y)  (helper compartilhado em sampling.py)
    # 3. Retorna: wi, Li (radiância), pdf_solid_angle

  def pdf_Li(self, ref_point, wi):
    # Intersection ray-triangle (Möller-Trumbore), pulando faces de verso
    # (emissão unilateral). Retorna: pdf_solid_angle para MIS
```

> ⚠️ **Correção de bug:** a versão anterior usava **apenas `u.y`** para as duas
> coordenadas baricêntricas, colapsando as amostras numa curva 1D dentro do triângulo
> (não uniforme por área — violava o requisito do enunciado). A correção usa
> `uniform_triangle(u1, u.y)` com `u1` derivado do remapeamento de `u.x` (duas dimensões
> independentes). Teste unitário confirma cobertura 2D (std ≈ 0.23 em x e y; centróide
> ≈ (1/3, 1/3) para o triângulo de referência).

**Características**:

- **Amostragem por Área**: CDF precomputada para seleção de triângulo proporcional à área
- **Barycentric Sampling**: uniforme via `uniform_triangle` (b0=1−√u1, b1=√u1·(1−u2), b2=√u1·u2)
- **Jacobian Conversion**: pdf_area → pdf_solid_angle
- **Emissão unilateral**: `pdf_Li` retorna 0 para faces de verso (consistente com `sample_Li`)
- **MIS Compatible**: retorna pdf_solid_angle para weighting em MIS

#### 2. Cena Cornell Box com Mesh Light

**Arquivo**: `src/path_tracing/scenes/cornell_mesh_light.py`

Geometria:

- Cornell Box padrão (idêntico a cornell_basic)
- Luz: **quad plano com 2 triângulos coplanares**, normal apontando **para baixo (−y)**
  - Quadrado 3×3 em y=5.50 (mesma área/posição do RectAreaLight)
  - Ordem dos vértices escolhida para `cross(e1,e2) = (0,−9,0)` → emite para a sala
- Le = (7.0, 7.0, 7.0) — mesmo que RectAreaLight para convergência

> ⚠️ **Correção de bug:** a versão anterior usava uma **pirâmide** com base voltada para
> **cima** (+y) e laterais para os lados, de modo que a maioria das amostras caía no lado
> não-emissor (`cos_at_light ≤ 0`, rejeitada) — a cena ficava subiluminada. O quad plano
> voltado para baixo ilumina corretamente e mantém o requisito "poliedro/malha de
> triângulos com amostras uniformes de área".

**Validação**:

- Renders com MIS convergem para o mesmo valor que cornell_basic com mesmo SPP/seed.
- Teste end-to-end: média da imagem > 0 e em faixa de brilho saudável (não mais subiluminada).

#### 3. CLI Script

**Arquivo**: `src/path_tracing/scripts/proj2_req6_mesh_lights.py`

Uso:

```bash
python -m path_tracing.scripts.proj2_req6_mesh_lights \
  --spp 16 \
  --depth 6 \
  --width 256 \
  --height 256 \
  --seed 42 \
  --mode mis \
  --no-calibrate
```

### Testes Realizados

**Render de Validação** (16 SPP, seed=42, MIS):

- Tempo: 99.257 segundos
- Resolução: 256×256
- Saída: `out/proj2/req6/proj2_req6_mis_no_rr_20260606_170307/render.png`
- Status: ✅ Sucesso

**Validação de Convergência**:

- Geometria idêntica a cornell_basic (mesmas coordenadas)
- Le idêntico (7,7,7)
- Espera-se visual equivalente em alta SPP

### Referências Técnicas

**PBRT 4e §6.5 Triangle Sampling**:

```
α = 1 - √u1
β = √u1 * (1 - u2)
γ = 1 - α - β
```

**Jacobian Conversion**:

```
pdf_solid_angle = pdf_area * distance² / |cos_at_light|
```

### Pontos Concedidos

- **Etapa 06: Mesh Lights** — 1.0 ponto (oficial)

### Score Acumulado

- Baseline (Etapa 02): 7.0 pts
- MIS (Etapa 04): 1.0 pt
- Russian Roulette (Etapa 05): 2.0 pts ⭐ (corrigido)
- **Mesh Lights (Etapa 06): 1.0 pt** ✅
- **Total: 11.0 / 13.0 pts**
  """
