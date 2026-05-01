# Funcionalidades e Nuances Pouco Explícitas no README

Este arquivo não serve mais para listar recursos “ausentes” do `README` em bloco, porque o `README` foi atualizado para refletir o escopo principal de `ray_tracing_2`. O objetivo agora é registrar nuances físicas, limitações arquiteturais e observações de uso que são importantes para manutenção, mas não precisam aparecer em destaque na documentação principal.

## 1. Convenção física da `PointLight`

`src/ray_tracing_2/light.py`

A `PointLight` desta base **não divide a energia por $r^2$** em `radiance()`. O campo `power` é tratado como radiância constante da fonte, e a redução de energia no caminho até o ponto sombreado vem apenas de `scene.transmittance()`.

Essa escolha deve ser lida como convenção de projeto, não como modelo radiométrico geral. Ela difere do caso de `AreaLight`, que já usa decaimento geométrico explícito por distância em cada amostra do emissor.

## 2. `AreaLight` não é só “uma PointLight maior”

`src/ray_tracing_2/light.py`

`AreaLight.sample_radiance()` aproxima a integral sobre um retângulo emissor por amostragem em grade com jitter. Isso produz penumbra real por visibilidade parcial da fonte, e não apenas um borramento artificial de sombra.

Em resumo:

- `PointLight`: convenção simplificada, sem $1/r^2$ explícito
- `AreaLight`: emissor estendido amostrado, com $1/r^2$ explícito

## 3. Anti-aliasing preserva a câmera do Slide 4

`src/ray_tracing_2/film.py`

O anti-aliasing não altera a geometria da câmera. `get_sample()` continua representando o caso básico de uma amostra central por pixel, enquanto `get_samples_for_pixel()` apenas substitui essa amostra única por um conjunto de amostras subpixel cuja média estima a cor do pixel.

Essa distinção é importante porque evita descrever o AA como se ele mudasse o modelo óptico da câmera. O que muda é o estimador numérico da integral sobre a área do pixel.

## 4. `Scene.transmittance()` generaliza o shadow ray binário

`src/ray_tracing_2/scene.py`

No caso opaco, `transmittance()` se comporta como o teste binário de sombra do traçador local. No caso transparente, o mesmo método acumula atenuações sucessivas ao longo do segmento até a luz. Isso é um ponto arquitetural importante: o projeto não mantém dois sistemas separados para sombra opaca e sombra transparente.

## 5. Beer-Lambert e orientação de face

`src/ray_tracing_2/hit.py` e `src/ray_tracing_2/material.py`

`TransparentMaterial` depende de `front_face` e `backfacing` para distinguir entrada e saída do meio. Sem isso, Snell, reflexão interna total e atenuação Beer-Lambert seriam aplicados com semântica física incorreta.

Na prática, `Hit.set_face_normal()` é parte da infraestrutura óptica do projeto, e não apenas um detalhe de orientação geométrica.

## 6. A BVH é local à malha, não global à cena

`src/ray_tracing_2/triangle_bvh.py`, `src/ray_tracing_2/shape.py`, `src/ray_tracing_2/scene.py`

O projeto implementa uma BVH estática construída por mediana no eixo dominante e usada apenas por `TriangleMesh`. Isso significa que:

- há poda por AABB dentro da malha triangular
- não há SAH
- não há compactação linear da BVH
- não há acelerador global para todas as primitivas da cena

Logo, a presença de BVH não muda o fato de que `Scene.compute_intersection()` ainda percorre `scene.objects` linearmente no nível superior.

## 7. `Render` é a interface real de saída

`src/ray_tracing_2/render.py`

O fluxo de uso mais fiel ao projeto atual passa por `Render.render()`, que:

- instancia `Film`
- salva `render.png`
- cria uma pasta timestamped em `outputs/`
- gera `properties.md` com metadados da cena

Esse `properties.md` é parte importante da rastreabilidade experimental do projeto e deve ser tratado como artefato de saída, não como mero extra.

## 8. Nem todo script auxiliar tem a mesma maturidade

O diretório `src/ray_tracing_2/` mistura:

- cenas de referência do relatório, como `main.py`, `main_area_light.py`, `main_box.py`, `main_triangles.py` e `cornell_box_pyramid.py`
- scripts laboratoriais ou variantes antigas, como `main_boxes.py`, `cornell_box.py` e alguns geradores auxiliares

Para documentação principal e validação do relatório, prefira sempre as cenas âncora usadas em `docs/relatorio-proj1.v5.md`.
