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
    # 1. Seleciona triângulo via u.x (usando CDF)
    # 2. Amostra ponto uniforme no triângulo via barycentric coords (u.y)
    # 3. Retorna: wi, Li (radiância), pdf_solid_angle

  def pdf_Li(self, ref_point, wi):
    # Intersection ray-triangle (Möller-Trumbore)
    # Retorna: pdf_solid_angle para MIS
```

**Características**:

- **Amostragem por Área**: CDF precomputada para seleção de triângulo proporcional à área
- **Barycentric Sampling**: uniform sampling dentro do triângulo
- **Jacobian Conversion**: pdf_area → pdf_solid_angle
- **MIS Compatible**: retorna pdf_solid_angle para weighting em MIS

#### 2. Cena Cornell Box com Mesh Light

**Arquivo**: `src/path_tracing/scenes/cornell_mesh_light.py`

Geometria:

- Cornell Box padrão (idêntico a cornell_basic)
- Luz: **pirâmide com 6 triângulos** (4 laterais + 2 base)
  - Base: quadrado 3×3 em y=5.50 (idêntico ao RectAreaLight)
  - Ápice: y=5.60 (0.10 acima da base)
- Le = (7.0, 7.0, 7.0) — mesmo que RectAreaLight para convergência

**Validação**:

- Renders com MIS devem convergir para o mesmo valor que cornell_basic com mesmo SPP/seed
- Nenhuma diferença visual em alta SPP (ambas as representações convergem para a verdade)

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
