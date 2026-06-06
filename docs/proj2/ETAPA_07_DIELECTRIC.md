"""# Etapa 07: Dielectric — Implementação de DielectricBSDF

## Status: ✅ CONCLUÍDO (2.0 pontos)

### Resumo

Implementou **DielectricBSDF** — BSDF para materiais dielétricos (transparentes sem condução elétrica).
Combina **reflexão especular com Fresnel** e **refração com Snell's law** em uma única delta distribution.

Suporta dois materiais:

- **Glass** (IOR=1.5): vidro óptico padrão
- **Water** (IOR=1.33): água com refração mais suave

### Convenção de frame (crítica)

`DielectricBSDF.sample` é avaliado no **frame da normal geométrica** (z = normal
outward, **não** a normal virada para o raio). Isso é essencial: o integrador, ao
detectar `bsdf.is_specular()`, monta a ONB com `hit.geo_normal` (sem flip). Assim o
**sinal de `wo.z`** codifica de que lado o raio incide:

| `wo.z` | Situação | n_i (incidente) | n_t (transmitido) | eta = n_i/n_t |
| ------ | -------- | --------------- | ----------------- | ------------- |
| `> 0`  | ENTRANDO (vindo do ar) | 1.0 | ior | **1/ior** |
| `< 0`  | SAINDO (vindo de dentro) | ior | 1.0 | **ior** |

> ⚠️ Correção de bug: a versão anterior usava `eta = ior` ao entrar (invertido),
> gerando reflexão interna total espúria na entrada do vidro. Como `Hit.set_face_normal`
> sempre vira a normal para o raio, `wo.z` era sempre `> 0` e o BSDF nunca distinguia
> entrada de saída. A correção passou a usar a **normal geométrica** no frame especular.

### Física Implementada

#### 1. Lei de Snell

Determina direção refratada quando um raio passa entre dois meios:

```
n_i * sin(θ_i) = n_t * sin(θ_t)

cos_i = |wo.z|
eta   = n_i / n_t          # 1/ior ao entrar; ior ao sair
sin_t² = eta² * (1 - cos_i²)
```

**Implementação** (forma vetorial geral, válida para entrada e saída):

```python
cos_i = abs(wo.z)
entering = wo.z > 0.0
n_i, n_t = (1.0, ior) if entering else (ior, 1.0)
eta = n_i / n_t

sin_t_sq = eta * eta * (1.0 - cos_i * cos_i)
if sin_t_sq >= 1.0:
    return reflect(wo)              # Reflexão interna total

cos_t = sqrt(1.0 - sin_t_sq)
sign_z = 1.0 if wo.z > 0 else -1.0
wi = vec3(-eta*wo.x, -eta*wo.y, -cos_t*sign_z)   # z vai para o lado oposto a wo
```

#### 2. Fresnel (Reflexão dependente do ângulo)

Refletância exata **não polarizada** = média das componentes paralela (∥) e
perpendicular (⊥) (a versão anterior usava só uma componente):

```
r_∥ = (n_t·cos_i − n_i·cos_t) / (n_t·cos_i + n_i·cos_t)
r_⊥ = (n_i·cos_i − n_t·cos_t) / (n_i·cos_i + n_t·cos_t)
F   = ½ (r_∥² + r_⊥²)
```

**Validação física**:

- Normal incidence (θ=0°): F ≈ ((n_i−n_t)/(n_i+n_t))²
  - Glass (1→1.5): F ≈ 0.04 (4% reflexão) — confirmado em teste unitário (fração refletida ≈ 0.040 em 20k amostras)
  - Water (1→1.33): F ≈ 0.02 (2% reflexão)
- Grazing (θ→90°): F → 1.0 (total reflexão)

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

#### 5. Integração no Path Tracer (tratamento especular)

Como o dielétrico é uma **delta distribution** (`eval=0`, `pdf=0`), o integrador o trata
de forma dedicada quando `bsdf.is_specular()` é verdadeiro
([path_tracer.py](../../src/path_tracing/integrators/path_tracer.py)):

1. **ONB pela normal geométrica** (`hit.geo_normal`), para o sinal de `wo.z` codificar
   entrada/saída (ver tabela acima).
2. **NEE é pulado**: a probabilidade de um raio de sombra coincidir com a direção delta é
   zero — NEE no vidro só gastaria shadow rays retornando 0.
3. **Throughput sem cosseno**: `β *= f / pdf` (com `pdf=1`). A delta-BSDF já embute o
   cosseno geométrico; multiplicar por `cosθ` (como no caso difuso) escureceria
   indevidamente as reflexões rasantes. `f` carrega refletância (`F`) ou transmitância
   (`1−F`) pura.
4. **Permite `wi.z < 0`**: o raio transmitido nasce no hemisfério oposto. O caso difuso
   aborta com `cosθ ≤ 0`, mas o especular **não** — caso contrário a refração nunca
   ocorreria (era o bug principal: o vidro renderizava como esfera escura sem transmissão).
5. **Peso MIS = 1.0**: a emissão vista após um bounce especular entra com peso pleno
   (a estratégia de amostragem de luz não alcança a direção delta).

> **Nota sobre o fator de radiância 1/eta²**: ao transportar radiância através de uma
> interface refrativa há um fator `(n_i/n_t)² = 1/eta²` (compressão do ângulo sólido). Ele
> é **omitido** aqui porque **cancela em objeto fechado** (o raio entra com `1/eta²` e sai
> com `eta²`). Como as cenas usam esfera de vidro e cubo de água fechados, o resultado é
> exato. Para uma única interface (ex.: superfície de água aberta) seria necessário aplicá-lo.

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

> ⚠️ **Atenção (correção):** as imagens commitadas em `out/proj2/req7/` foram geradas
> **antes** da correção (refração morta + IOR invertido) e estão obsoletas — mostram a
> esfera escura sem transmissão. Re-renderize para obter o resultado correto:
>
> ```bash
> python -m path_tracing.scripts.proj2_req7_dielectric --material glass --spp 32 --depth 8 --mode mis
> python -m path_tracing.scripts.proj2_req7_dielectric --material water --spp 32 --depth 8 --mode mis
> ```

**Validação por testes unitários** (sem render de imagem):

- `is_specular()` → `True`; refração ao entrar produz `wi.z < 0`; ao sair produz `wi.z > 0`.
- Lei de Snell numérica: `1·sin θ_i = 1.5·sin θ_t` (entrada no vidro).
- Reflexão interna total em ângulo > θ_c (ao sair): reflete com `f = 1`.
- Fresnel em incidência normal: fração refletida ≈ 0.040 (esperado 4% para vidro).
- Integrador end-to-end nas cenas glass/water: radiância média > 0 (transmissão ocorre).

**Validação Visual** (após re-render):

- Glass: refração com ampliação/distorção do fundo + Fresnel brilhante nas bordas rasantes.
- Water (IOR 1.33): refração mais suave, menor especularidade em ângulos normais.

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
