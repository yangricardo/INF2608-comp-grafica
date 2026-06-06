# Etapa 02 — Path Tracer Unidirecional (core)

## Objetivo

Implementar um path tracer unidirecional com amostragem de BSDF para materiais Lambertians e reconhecimento de superfícies emissivas. Ao final desta etapa, o renderizador produz imagens da Cornell Box com ruído visível a SPP baixo que converge para a solução correta em SPP alto.

**Pontos:** 7.0 pts (entregável principal).

---

## Equação de Rendering

A equação de rendering (Kajiya 1986) na forma de integral hemisférica:

$$L_o(p, \omega_o) = L_e(p, \omega_o) + \int_{\mathcal{H}^2} f(p, \omega_o, \omega_i)\, L_i(p, \omega_i)\, |\cos\theta_i|\, d\omega_i$$

O estimador Monte Carlo, com uma amostra por vértice:

$$L_o \approx L_e + \frac{f(\omega_o, \omega_i) \cdot L_i(\omega_i) \cdot |\cos\theta_i|}{p(\omega_i)}$$

Para BSDF Lambertiana com amostragem cosseno-ponderada (Método de Malley):

$$f = \frac{\rho}{\pi}, \quad p(\omega_i) = \frac{|\cos\theta_i|}{\pi}$$

A fração cancela:

$$\frac{f \cdot |\cos\theta_i|}{p(\omega_i)} = \frac{\rho/\pi \cdot |\cos\theta_i|}{|\cos\theta_i|/\pi} = \rho$$

Logo $\beta$ se atualiza por simples multiplicação pela reflectância:
$\beta \mathrel{*}= \rho$

---

## Pseudocódigo (PBRT 4e §13.3)

```
function Li(ray, scene):
  β ← (1, 1, 1),   L ← (0, 0, 0)
  para profundidade = 1, 2, …, max_depth:
    hit ← scene.intersect(ray)
    se !hit:
      L += β × background
      parar
    se hit.emissivo:
      L += β × Le
      parar
    construir ONB com normal como z
    wo ← −ray.d em frame local
    (wi, pdf, f) ← bsdf.sample(wo, u)
    se pdf == 0 ou f == 0: parar
    β *= f × |cos θ_i| / pdf        ← β *= ρ para Lambertiana+Malley
    ray ← Ray(offset_point(hit.pos, hit.normal, wi_global), wi_global)
  retornar L
```

**Exigência do enunciado:** `min_depth = 4` — terminação antecipada (Russian Roulette, Etapa 05) só é permitida a partir desta profundidade.

---

## BSDF Lambertiana (`bsdf/lambertian.py`)

| Método          | Fórmula                                                                     |
| --------------- | --------------------------------------------------------------------------- |
| `eval(wo, wi)`  | $f = \rho / \pi$                                                            |
| `sample(wo, u)` | Método de Malley: $r = \sqrt{u_1}$, $\phi = 2\pi u_2$, $z = \sqrt{1 - r^2}$ |
| `pdf(wo, wi)`   | $p(\omega_i) = \max(0, \cos\theta_i) / \pi$                                 |

Convenção: **frame local** onde $z = $ normal, $\cos\theta_i = w_i.z$.

---

## BSDF Emissivo (`bsdf/emissive.py`)

Terminal: `eval = 0`, `pdf = 0`, `is_emissive = True`. O path tracer ao detectar `isinstance(bsdf, EmissiveBSDF)` acumula `Le` em `L` e encerra o caminho.

---

## Amostragem cosseno-ponderada (`sampling.py`)

```python
def cosine_hemisphere(u1: float, u2: float) -> tuple[float, float, float]:
    """Malley's Method — Ref: Slide 7; PBRT 4e §A.5"""
    r   = math.sqrt(u1)
    phi = 2 * math.pi * u2
    x   = r * math.cos(phi)
    y   = r * math.sin(phi)
    z   = math.sqrt(max(0.0, 1.0 - u1))
    return (x, y, z)

def cosine_hemisphere_pdf(cos_theta: float) -> float:
    return max(0.0, cos_theta) / math.pi
```

---

## Cena Cornell Box (Y-up)

| Elemento        | Coordenadas (min / max)                     | Material                        |
| --------------- | ------------------------------------------- | ------------------------------- |
| Parede frontal  | $[-0.10,-0.10,-0.10]$ / $[5.65,5.65,0.00]$  | branca                          |
| Parede esquerda | $[-0.10,-0.10,0.00]$ / $[0.00,5.55,5.55]$   | verde                           |
| Parede direita  | $[5.55,-0.10,0.00]$ / $[5.65,5.55,5.55]$    | vermelha                        |
| Teto            | $[0.00,5.55,0.00]$ / $[5.55,5.65,5.55]$     | branco                          |
| Chão            | $[-0.10,-0.10,0.00]$ / $[5.65,0.00,5.55]$   | branco                          |
| Painel de luz   | $[1.275,5.45,1.275]$ / $[4.275,5.55,4.275]$ | emissivo $\mathbf{L}_e=(7,7,7)$ |
| Caixa baixa     | $[0.85,0.00,0.85]$ / $[2.50,1.10,2.50]$     | branca                          |
| Caixa alta      | $[3.00,0.00,2.80]$ / $[4.10,2.30,3.90]$     | branca                          |
| Esfera          | centro $[2.10,0.62,4.25]$, $r=0.62$         | branca                          |

Câmera: $eye=(2.775, 3.200, 12.775)$, $center=(2.775, 2.775, 2.775)$, $up=(0,1,0)$, $fov=50°$. A face aberta ($z > 5.55$) fica voltada para a câmera.

---

## Galeria SPP (bsdf_only)

Para reproduzir:

```bash
# SPP 4
python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 4 --depth 6 \
    --width 512 --height 512 --seed 42 --no-calibrate

# SPP 16
python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 16 --depth 6 \
    --width 512 --height 512 --seed 42 --no-calibrate

# SPP 64
python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 64 --depth 6 \
    --width 512 --height 512 --seed 42 --no-calibrate

# SPP 256
python -m path_tracing.scripts.proj2_req1_lambert_basic --spp 256 --depth 6 \
    --width 512 --height 512 --seed 42 --no-calibrate
```

Saída em `out/proj2/req1/<timestamped>/render.png`.

A convergência ilustra a Lei dos Grandes Números: variância $\sigma^2 \propto 1/N$ — quadruplicar SPP reduz o desvio padrão do ruído à metade.

---

## Referências

- **Slide 7** "Integração de Monte Carlo" — estimador MC, amostragem por importância, Método de Malley
- **Slide 8** "Traçado de Caminhos" — LTE, integral de caminho, throughput β
- **PBRT 4e §2.1** _Rendering Interface_
- **PBRT 4e §9.2** _Material Implementations_ (Lambertiana)
- **PBRT 4e §13.1–13.3** _Light Transport I: Surface Reflection_
- **PBRT 4e §A.5** _Sampling a Cosine-Weighted Hemisphere_
- **Kajiya, J.T.**, "The Rendering Equation", _SIGGRAPH 1986_, pp. 143–150. **DOI: 10.1145/15922.15902**
