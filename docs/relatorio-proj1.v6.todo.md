# Relatorio Projeto 1 v6 - TODO

## Escopo v6

Nova versao do relatorio organizada por requisito do enunciado, com a camera
mantida fixa entre as cenas didaticas e variacao apenas de objetos, materiais
ou luzes.

Arquivos principais desta rodada:

- `src/ray_tracing_2/proj1_req1_geometry.py`
- `src/ray_tracing_2/proj1_req2_point_lights.py`
- `src/ray_tracing_2/proj1_req3_phong_shadows.py`
- `src/ray_tracing_2/proj1_req4_sampling.py`
- `src/ray_tracing_2/proj1_scene_common.py`

## Restricoes operacionais

- Validacao do agente: `--width 800 --height 600`.
- Validacao do agente: `--spp` no intervalo `1..4`.
- Baseline de smoke test: `--spp 1`.
- Execucoes acima de `--spp 4` ficam para o usuario.

## Matriz requisito -> cena -> evidencia

| Status | Requisito                                                | Cena principal                | Evidencia esperada                                                   |
| ------ | -------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------- |
| [x]    | R1: cena com instanciacao de esferas e caixas            | `proj1_req1_geometry.py`      | Cornell base + 2 caixas instanciadas + 1 esfera                      |
| [x]    | R2: uma ou mais luzes pontuais                           | `proj1_req2_point_lights.py`  | Tres `PointLight` com contribuicoes distintas                        |
| [x]    | R3: iluminacao direta com Phong e sombras                | `proj1_req3_phong_shadows.py` | Materiais Phong com sombra dura visivel                              |
| [x]    | R4: multiplas amostras por pixel (distribuicao uniforme) | `proj1_req4_sampling.py`      | Comparacao `center` vs `jittered/stratified` com mesmo enquadramento |

## Checklist de redacao

- [x] Consolidar comandos reproduziveis para cada requisito (`--spp 1` e `--spp 4`).
- [x] Selecionar uma figura principal por requisito.
- [x] Inserir notas de limitacao (sem acelerador global; simplificacoes radiometricas).
- [x] Relacionar explicitamente o requisito 4 ao comportamento de `uniform_samples_2d()` no modo publico `jittered`.
- [x] Incluir secao de requisitos adicionais separada dos requisitos principais.

## Checklist de LaTeX v2

- [x] Inserir secao `Requisitos e Aderencia` no inicio.
- [x] Apontar cada requisito para um modulo `proj1_*`.
- [x] Incluir comandos CLI em bloco de reproducao experimental.
- [x] Atualizar conclusao com aderencia parcial/total por requisito.
