# Funcionalidades Implementadas não Documentadas no README.md

O `README.md` atual documenta apenas as funcionalidades do módulo `ray_tracing_1`
(câmera pinhole, esfera, plano, Phong básico, sombras, instanciação). Todas as
funcionalidades listadas abaixo estão **implementadas e funcionais** no módulo
`ray_tracing_2`, mas não aparecem na documentação principal.

---

## 1. Anti-aliasing (Supersampling)

**Arquivo**: `src/ray_tracing_2/film.py` — linhas 60–99

Implementa dois modos de amostragem por pixel conforme slides p. 4–6
(5.tracado_de_raios2.pdf):

- **Jittered** (Monte Carlo): cada amostra é um ponto aleatório dentro do pixel
  ($x_n = (i + \xi) / w$, $y_n = (j + \xi) / h$)
- **Stratified**: subdivide o pixel em $G \times G$ subcélulas ($G = \lceil\sqrt{spp}\rceil$)
  e gera uma amostra aleatória dentro de cada subcélula

Configurável via parâmetros `--spp` e `--sampling_mode` nos scripts de entrada.

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 4–8

---

## 2. Objeto Box (Caixa Alinhada)

**Arquivo**: `src/ray_tracing_2/shape.py` — linhas 70–140

Interseção raio-caixa pelo **método de slabs** (intervalos por eixo). A caixa é
representada por `p_min` e `p_max`. Calcula as normais de entrada e saída
corretamente para cada face.

Usado extensivamente na Cornell Box (paredes, teto, chão, blocos).

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 24

---

## 3. Material Reflexivo (ReflectiveMaterial)

**Arquivo**: `src/ray_tracing_2/material.py` — linhas 80–115

Implementa `PhongMetal.Eval` dos slides p. 26–27:

- Reflexão de Fresnel-Schlick: $R(\theta, \lambda) = R_0(\lambda) + (1 - R_0(\lambda))(1 - \cos\theta)^5$
- Iluminação direta atenuada por $(1 - R)$
- Raio refletido recursivo: $c += R \cdot \text{scene.TraceRay}(\text{reflect}(-\hat{v}, \hat{n}))$
- Controlado por `max_depth` para evitar recursão infinita

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 26–28

---

## 4. Material Transparente (TransparentMaterial)

**Arquivo**: `src/ray_tracing_2/material.py` — linhas 118–230

Implementa `PhongDieletrics.Eval` dos slides p. 29–34:

- **Lei de Snell**: $\eta_i \sin\theta = \eta_t \sin\phi$ via `glm.refract()`
- **Fresnel-Schlick**: $R_0 = ((η-1)/(η+1))^2$
- **Lei de Beer**: $I(s) = I_0 \cdot a(\lambda)^s$ para atenuação em materiais
  coloridos (ex: vidro verde)
- **Reflexão interna total**: detectada quando `glm.refract()` retorna zero
- Suporte a `backfacing` para distinguir entrada/saída do material

Parâmetros configuráveis: `ior` (índice de refração), `attenuation` (cor de Beer).

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 29–36

---

## 5. Luz de Área (AreaLight)

**Arquivo**: `src/ray_tracing_2/light.py` — linhas 69–118

Fonte de luz retangular definida por origem `p` e dois vetores de aresta `e_u`,
`e_v`, conforme slides p. 15–23:

- Amostragem estratificada com jitter dentro de subcélulas
- Cada amostra gera um raio de sombra independente via `scene.transmittance()`
- Produz sombras suaves (penumbra) por média de múltiplas amostras
- Parâmetros: `samples_u`, `samples_v`, `power`, `seed`

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 15–23

---

## 6. Transmitância em Raios de Sombra

**Arquivo**: `src/ray_tracing_2/scene.py` — linhas 42–98

Implementa o loop de transmitância dos slides p. 35 para suportar sombras
através de materiais transparentes:

```
while hits.material.IsTransparent() do
  if hits.IsBackfacing() then I = I * hits.material.a^||p-hits.p||
  ray = Ray(hits.p, l̂)
  hits = scene.ComputeIntersection(ray)
```

Delega o cálculo por material via `shadow_transmittance()`:

- `Material` (opaco): retorna `vec3(0)` — bloqueia
- `TransparentMaterial`: retorna Beer attenuation ao sair, `vec3(1)` ao entrar

**Referências nos slides**: 5.tracado_de_raios2.pdf — p. 35

---

## 7. Recursão Limitada por Profundidade

**Arquivo**: `src/ray_tracing_2/scene.py` — linhas 38–40

Método `can_spawn_ray(depth, max_depth)` controla a profundidade máxima de
recursão para reflexão e refração. Usado por `ReflectiveMaterial.eval()` e
`TransparentMaterial.eval()`. Valor default: `max_depth = 4`.

Configurável via `--max_depth` nos scripts de entrada.

---

## 8. Correção Gama

**Arquivo**: `src/ray_tracing_2/film.py` — linhas 123–125

Aplica $c^{1/2.2}$ ao buffer final antes da conversão para uint8. Ativado via flag
`--gamma_fix`.

---

## 9. Classe Render com Saída Automatizada

**Arquivo**: `src/ray_tracing_2/render.py` — linhas 170–286

Classe `Render` que organiza a saída de cada renderização:

- Cria pasta timestamped: `outputs/{name}_{YYYYMMDD_HHMMSS}/`
- Salva `render.png` via `Film.render()`
- Gera `properties.md` com metadados da cena (câmera, objetos, luzes, materiais)
- Serializa propriedades dos materiais (ambient, diffuse, specular, shininess,
  reflectivity, ior, attenuation)

---

## 10. Cena Cornell Box

**Arquivo**: `src/ray_tracing_2/main_box.py` — linhas 64–155

Implementação completa da cena descrita em `proj1-exemplo.pdf`:

- 5 paredes (Box) com materiais branco, verde e vermelho
- 2 blocos instanciados (Box + Translate + Rotate)
- Esfera luminária transparente
- PointLight no teto
- AmbientLight global
- Suporte a troca de material dos blocos: `--small_block_material {opaque|reflective|transparent}`

---

## 11. Translate e Rotate (wrappers de Instance)

**Arquivo**: `src/ray_tracing_2/shape.py` — linhas 186–196

Classes de conveniência que criam `Instance` com matrizes de
`glm.translate()` / `glm.rotate()`:

```python
class Translate(Instance):
  def __init__(self, x, y, z, shape): ...

class Rotate(Instance):
  def __init__(self, angle_deg, x, y, z, shape): ...
```

---

## 12. Carregador de Cenas JSON

**Arquivo**: `src/ray_tracing_2/generate_scene.py` — linhas 52–80

Constrói cena a partir de especificação JSON com:

- `"spheres"`: lista de esferas com centro, raio e material
- `"plane"`: plano com altura y e material
- `"lights"`: lista de luzes pontuais
- `"camera"`: parâmetros opcionais de câmera

Uso: `python -m ray_tracing_2.generate_scene --input inputs/example_scene.json`

---

## 13. Tracking de Face no Hit

**Arquivo**: `src/ray_tracing_2/hit.py` — linhas 17–29

Campos adicionados ao `Hit` para suportar refração:

- `geo_normal`: normal geométrica original (sem flip)
- `front_face`: `True` se o raio atinge a face externa
- `backfacing`: `True` se o raio atinge a face interna (saindo do material)

Método `set_face_normal(ray, outward_normal)` orienta a normal automaticamente.

---

## 14. Classe AmbientLight

**Arquivo**: `src/ray_tracing_2/light.py` — linhas 31–40

Classe dedicada para luz ambiente (separada de `Light`/`PointLight`), aceita
`vec3` ou componentes `(r, g, b)`. Usada na construção da `Scene`.

---

## 15. Múltiplos Scripts de Cena

Além do `main.py` original, o projeto possui:

| Script                                       | Descrição                                      |
| -------------------------------------------- | ---------------------------------------------- |
| `src/ray_tracing_2/main_box.py`              | Cornell Box completa (proj1-exemplo.pdf)       |
| `src/ray_tracing_2/main_area_light.py`       | Demonstração de AreaLight com sombras suaves   |
| `src/ray_tracing_2/main_ellipse.py`          | Elipsoide via Instance com escala não-uniforme |
| `src/ray_tracing_2/cornell_box.py`           | Variante da Cornell Box com materiais mistos   |
| `src/ray_tracing_2/main_boxes.py`            | Cena simples com duas caixas                   |
| `src/ray_tracing_2/main_scene_variations.py` | Grade de variações paramétricas                |
| `src/ray_tracing_2/random_scene.py`          | Gerador de cenas aleatórias com documentação   |
| `src/ray_tracing_2/generate_scene.py`        | Carregador de cenas via JSON                   |

Todos suportam flags CLI: `--spp`, `--sampling_mode`, `--seed`, `--gamma_fix`.
