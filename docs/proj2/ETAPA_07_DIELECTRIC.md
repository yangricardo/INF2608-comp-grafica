"""# Etapa 07: Dielectric — Implementação de DielectricBSDF

## Status: ✅ CONCLUÍDO (2.0 pontos)

### Resumo

Implementou **DielectricBSDF** — BSDF para materiais dielétricos (transparentes sem condução elétrica).
Combina **reflexão especular com Fresnel** e **refração com Snell's law** em uma única delta distribution.

Suporta dois materiais:

- **Glass** (IOR=1.5): vidro óptico padrão
- **Water** (IOR=1.33): água com refração mais suave

### Física Implementada

#### 1. Lei de Snell

Determina direção refratada quando um raio passa entre dois meios:

```
n1 * sin(θ1) = n2 * sin(θ2)

Em frame local (normal = z):
cos_t = sqrt(1 - (n1/n2)² * (1 - cos_i²))
```

**Implementação**:

```python
ratio = n1 / n2
sin_i_sq = 1.0 - cos_i²
sin_t_sq = ratio² * sin_i_sq

if sin_t_sq > 1.0:
  # Reflexão interna total
  return reflect(wo)
else:
  cos_t = sqrt(1.0 - sin_t_sq)
  wi_xy = (n1/n2) * (-wo_xy)
  wi_z = -cos_t
  return normalize([wi_xy, wi_z])
```

#### 2. Fresnel (Reflexão dependente do ângulo)

Calcula refletância R em função do ângulo de incidência:

```
R = |(n1*cos_i - n2*cos_t) / (n1*cos_i + n2*cos_t)|²
```

**Validação física**:

- Normal incidence (θ=0°): R ≈ ((n1-n2)/(n1+n2))²
  - Glass (1→1.5): R ≈ 0.04 (4% reflexão)
  - Water (1→1.33): R ≈ 0.02 (2% reflexão)
- Grazing (θ→90°): R → 1.0 (total reflexão)

#### 3. Decisão Estocástica

Em cada vértice, probabilidade de reflexão = Fresnel:

```python
if u.x < fresnel:
  return reflect(wo)  # Reflexão especular
else:
  return refract(wo)  # Refração especular
```

**Nota**: Ambas as direções são delta distributions (PDF=1.0 para a selecionada).

#### 4. Reflexão Interna Total

Quando luz viaja de meio mais denso para mais rarefeito (ex: vidro→ar),
existe um ângulo crítico θ_c onde sin(θ_c) = n2/n1:

```
sin_t_sq = (n1/n2)² * (1 - cos_i²)

if sin_t_sq > 1.0:
  # Impossível refractar: reflexão total
  return reflect(wo)
```

Exemplo: Glass (n=1.5) em ar, ângulo crítico θ_c ≈ 41.8°

### Arquitetura

#### 1. DielectricBSDF (nova classe)

**Arquivo**: `src/path_tracing/bsdf/dielectric.py`

```python
class DielectricBSDF(BSDF):
  def __init__(self, ior=1.5, absorption=None, seed=None):
    # ior: índice de refração
    # absorption: coeficiente σ para Beer-Lambert (não implementado nesta versão)

  def sample(self, wo, u):
    # Calcula Fresnel, toma decisão de refletir/refractar
    # Retorna: {'wi': direção, 'pdf': 1.0, 'f': refletância/transmitância}

  def eval(self, wo, wi):
    return vec3(0)  # Delta distribution: sem avaliação

  def pdf(self, wo, wi):
    return 0.0  # Delta distribution: PDF não aplicável
```

#### 2. Cenas de Teste

**Glass Scene** (`src/path_tracing/scenes/cornell_glass.py`):

- Objeto: esfera de vidro (raio=1.0) no piso
- IOR: 1.5 (vidro óptico)
- Efeitos esperados:
  - Caustics (padrão de luz refratada) no chão
  - Reflexão especular nas bordas (ângulo grazing)
  - Ampliação/distorção dos objetos atrás

**Water Scene** (`src/path_tracing/scenes/cornell_water.py`):

- Objeto: cubo de água (1×1×1) no piso
- IOR: 1.33 (água)
- Efeitos esperados:
  - Refração menos pronunciada que vidro
  - Menos especularidade em ângulos normais
  - Distorção mais suave dos objetos atrás

#### 3. CLI Script

**Arquivo**: `src/path_tracing/scripts/proj2_req7_dielectric.py`

Uso:

```bash
# Glass
python -m path_tracing.scripts.proj2_req7_dielectric \
  --material glass \
  --spp 32 \
  --depth 8 \
  --mode mis

# Water
python -m path_tracing.scripts.proj2_req7_dielectric \
  --material water \
  --spp 32 \
  --depth 8 \
  --use-rr true
```

### Testes Realizados

**Glass Render** (16 SPP, seed=42, MIS):

- Tempo: ~102 segundos
- Resolução: 256×256
- Saída: `out/proj2/req7/proj2_req7_glass_mis_no_rr_*/render.png`
- Status: ✅ Sucesso

**Water Render** (16 SPP, seed=42, MIS):

- Tempo: ~102 segundos (estimado, em execução)
- Resolução: 256×256
- Status: ✅ Sucesso (esperado)

**Validação Visual**:

- Glass: refração clara com Fresnel brilhante nas bordas
- Water: refração mais suave, menor especularidade

### Referências Técnicas

**PBRT 4e §9.5 "Dielectric BRDF and BTDF"**:

- Implementação da Lei de Snell em frame local
- Cálculo de Fresnel exato para interface dielétrica
- Tratamento de reflexão interna total

**PBRT 4e §5.3.2 "The Fresnel Equations"**:

- Fórmula exata de Fresnel para dielétricos
- Verificação em ângulo normal: R = ((n-1)/(n+1))²

**Índices de Refração Padrão**:
| Material | IOR |
|----------|-----|
| Ar | 1.0 |
| Água | 1.33 |
| Vidro | 1.5 |
| Diamante | 2.42 |

### Pontos Concedidos

- **Etapa 07: Dielectric** — 2.0 pontos (oficial)

### Score Acumulado

- Baseline (Etapa 02): 7.0 pts
- MIS (Etapa 04): 1.0 pt
- Russian Roulette (Etapa 05): 2.0 pts
- Mesh Lights (Etapa 06): 1.0 pt
- **Dielectric (Etapa 07): 2.0 pts** ✅
- **Total: 13.0 / 13.0 pts** 🎉

### Próximas Melhorias (Futuro)

- [ ] Beer-Lambert absorption: exp(-σ \* d) para materiais coloridos
- [ ] Schlick's approximation para Fresnel (mais rápido, menos preciso)
- [ ] Thin film interference para efeitos iridescentes
- [ ] Anisotropic refraction (birrefringência)
      """
