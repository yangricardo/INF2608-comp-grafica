## Plan: Relatorio Tecnico-Cientifico v5

O novo v5 deve ser um relatorio teoria-dominante, com validacao experimental breve, derivado primariamente dos tres PDFs, complementado pelos resumos em materiais/_.md e apoiado externamente apenas por PBRT 4e. Os arquivos em docs/_.md passam a ter status secundario: servem para reaproveitar estrutura, localizar lacunas e checar consistencia, mas nao para definir a formulacao teorica principal. A execucao deve primeiro estabilizar o mapa de paginas e o mapa de linhas de codigo, depois revisar comentarios/docstrings que afetam interpretacao fisica ou rastreabilidade, e so entao fechar as referencias lineares no texto; isso evita que a propria revisao de comentarios invalide as citacoes de codigo.

Referências confiaveis externas: https://www.pbr-book.org/4ed/contents

**Steps**

1. Phase 1 - Matriz de fontes e escopo. Consolidar uma tabela mestre em docs/relatorio-proj1.todo.md com quatro colunas por topico: PDF/intervalo de paginas, complemento em materiais/_.md, apoio PBRT 4e permitido, implementacao correspondente no repositorio. A regra de precedencia deve ser registrada no topo do todo: PDF > materiais/_.md > codigo/documentacao inline > docs/\*.md. Isso inclui: Slide 4 com algoritmo por pixel, raio parametrico, hits e normais, intersecoes com plano/esfera/caixa, camera pinhole, filme e AA, Phong, sombras e visibilidade; Slide 5 com AA/Monte Carlo, instanciacao, normal por inversa transposta, luz de area, reflexao Fresnel-Schlick, refracao/Snell, TIR, Beer-Lambert, transmitancia e recursao; Slide 6 com triangulos, baricentricas, Moller-Trumbore, AABB/slabs, BVH, complexidade e os conteudos dos slides que nao foram implementados. Apoios PBRT recomendados: 1.2, 2.1-2.2, 3.5-3.10, 4.1-4.4, 5.1-5.4, 6.1-6.2, 6.5, 6.8, 7.1-7.3, 8.1-8.5, 9.1-9.5, 11.2, 12.1-12.6.
2. Phase 2 - Congelar o mapa de codigo antes das citacoes finais. Auditar os modulos centrais e registrar no todo os simbolos e linhas que serao citados depois do pass de comentarios: camera.py com Camera.**init** e Camera.generate_ray; film.py com SamplingMode, get_sample/get_samples_for_pixel e render; hit.py com Hit e set_face_normal; scene.py com compute_intersection, offset_point, can_spawn_ray, transmittance e trace_ray; light.py com PointLight.radiance, AreaLight.sample_radiance/radiance e AmbientLight; material.py com Material.shadow_transmittance, PhongMaterial.direct_lighting/eval, ReflectiveMaterial.eval e TransparentMaterial.shadow_transmittance/eval; shape.py com Sphere.intersect, Plane.intersect, Box.intersect, Triangle.intersect, TriangleMesh, Instance/Translate/Rotate; triangle_bvh.py com AABB.intersects, TriangleBVHNode.intersect, TriangleBVH.\_build/\_collect_stats; e as scenes main_area_light.py, main_box.py, main_triangles.py, cornell_box.py e render.py como ancoras concretas.
3. Phase 3 - Revisar comentarios e documentacao que afetam a leitura tecnica. Executar antes do texto final e antes de fixar as linhas citadas. Priorizar, no Python: esclarecer a diferenca entre focal_distance pinhole versus lente fina em camera.py; posicionar PhongMaterial.eval como nucleo local reutilizado por materiais recursivos em material.py; documentar a aproximacao energetica de ReflectiveMaterial; condensar a documentacao do laco de transmitancia em scene.py sem perder a fisica; uniformizar referencias de paginas em film.py; deixar explicito em triangle_bvh.py que a BVH e estatica, local a malha e usa median split, nao SAH. Priorizar, no Markdown: corrigir documentacao desatualizada ou inconsistente em README.md, AA_IMPLEMENTATION.md e UNDOCUMENTED_FEATURES.md, especialmente onde a narrativa fisica divergir do comportamento atual do codigo.
4. Phase 4 - Redigir docs/relatorio-proj1.v5.md com estrutura teoria-dominante e rastreabilidade explicita. Recomendo esta organizacao: Introducao e metodologia, com objetivo, corpus primario dos tres PDFs, apoio externo restrito ao PBRT 4e e metodo de rastrear teoria -> implementacao -> evidencia; Fundamentos geometricos e opticos do Slide 4, cobrindo raio parametrico, interacoes, orientacao de face, plano/esfera/caixa, camera pinhole, filme e amostragem, iluminacao direta de Phong, sombras e epsilon numerico; Extensoes do Slide 5, cobrindo Monte Carlo/AA, instanciacao e transformacoes afins, normais com inversa transposta, luzes de area, transicao do tracador local para recursivo, Fresnel-Schlick, Snell, TIR, Beer-Lambert e transmitancia acumulada; Estruturas de aceleracao do Slide 6, cobrindo triangulos, coordenadas baricentricas, Moller-Trumbore, AABB via slabs, BVH, custo assintotico, estatisticas da arvore e separacao explicita entre conteudo dos slides e o que o repositorio de fato implementa; Mapeamento para o codigo, com paginas dos PDFs e linhas/simbolos do codigo ja estabilizados; Validacao experimental breve com 2-3 estudos de caso curtos; Limitacoes e escopo; Conclusao.
5. Phase 5 - Politica de citacao e rigor. Padronizar ao longo do v5: sempre que possivel, citar intervalo de paginas dos PDFs e associar a um simbolo ou bloco de codigo; usar capitulos do PBRT apenas como apoio conceitual complementar, nunca para substituir ou contradizer a formulacao dos slides; distinguir cuidadosamente o modelo fisico adotado pelo projeto de formulacoes mais gerais do PBRT quando houver simplificacoes do codigo, como PointLight sem queda explicita por 1/r^2 e o uso aproximado de Phong + Fresnel-Schlick.
6. Phase 6 - Fechar e validar. Depois do pass de comentarios e do texto: atualizar no todo o estado de cada secao, pagina confirmada e linha confirmada; fazer uma revisao cruzada para garantir que nenhuma citacao de linha ficou deslocada apos editar comentarios; verificar que todos os arquivos/imagens citados no relatorio existem e que os links Markdown abrem corretamente; rodar uma checagem barata de sintaxe nos arquivos Python comentados e uma revisao visual do Markdown renderizado.

**Relevant files**

- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/4.tracado_de_raios.pdf - fonte primaria do nucleo geometrico/fotometrico
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/5.tracado_de_raios2.pdf - fonte primaria das extensoes opticas e de amostragem
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/6.estrutura_aceleracao.pdf - fonte primaria de triangulos, AABB e aceleracao
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/4.tracado_de_raiosv1.md - resumo complementar prioritario para o Slide 4
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/4.tracado_de_raiosv2.md - resumo complementar prioritario para o Slide 4
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/5.tracado_de_raios2_1.md - resumo complementar prioritario para o Slide 5
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/5.tracado_de_raios2_2.md - resumo complementar prioritario para o Slide 5
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/5.tracado_de_raios2_3.md - resumo complementar prioritario para o Slide 5
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/6.estrutura_aceleracaov1.md - resumo complementar prioritario para o Slide 6
- /Users/yang/projects/INF2608-comp-grafica/materiais/traçado_de_raios/6.estrutura_aceleracaov2.md - resumo complementar prioritario para o Slide 6
- /Users/yang/projects/INF2608-comp-grafica/docs/relatorio-proj1.v4.md - base estrutural imediata a ser condensada para um v5 mais teorico, mas com confianca inferior as fontes em materiais/
- /Users/yang/projects/INF2608-comp-grafica/docs/relatorio-proj1.md - versao madura para reaproveitar estrutura, BVH, limitacoes e experimentos, mas nao para definir a teoria principal
- /Users/yang/projects/INF2608-comp-grafica/docs/relatorio-proj1.todo.md - checklist operacional do trabalho, com controle de paginas, PBRT e linhas de codigo
- /Users/yang/projects/INF2608-comp-grafica/docs/AA_IMPLEMENTATION.md - apoio secundario para o bloco de amostragem/anti-aliasing e possivel atualizacao de consistencia
- /Users/yang/projects/INF2608-comp-grafica/docs/UNDOCUMENTED_FEATURES.md - inventario secundario para separar funcionalidade implementada de funcionalidade ja documentada
- /Users/yang/projects/INF2608-comp-grafica/README.md - documentacao de alto nivel parcialmente desatualizada em relacao ao modulo ray_tracing_2
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/camera.py - camera pinhole e geracao de raios primarios
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/film.py - amostragem por pixel, loop de render e correcao gama
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/hit.py - estrutura de hit e orientacao front_face/backfacing
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/scene.py - closest hit, offset numerico, transmitancia e trace_ray
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/light.py - luz ambiente, pontual e de area
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/material.py - Phong, reflexao, refracao, Beer e Fresnel-Schlick
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/shape.py - primitivas, intersecoes, malha triangular e instanciacao
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/triangle_bvh.py - AABB, BVH estatica e estatisticas da hierarquia
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/main_area_light.py - caso curto para penumbra
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/main_box.py - caso curto para instanciacao/Cornell-like
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/main_triangles.py - caso curto para TriangleMesh/BVH
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/cornell_box.py - caso curto para materiais reflexivos/transmissivos
- /Users/yang/projects/INF2608-comp-grafica/src/ray_tracing_2/render.py - metadados e propriedades das saidas, util para a secao breve de validacao

**Verification**

1. Confirmar no todo cada topico do relatorio com: PDF/pagina, capitulo PBRT de apoio e simbolo/linhas do codigo correspondentes.
2. Congelar as linhas do codigo apenas depois das revisoes de comentario, para evitar citacoes quebradas.
3. Verificar links e imagens citadas no Markdown final e manter somente assets que ja existam em outputs/.
4. Rodar uma checagem simples como py_compile ou compileall nos arquivos Python com comentarios/docstrings alterados.
5. Fazer leitura final do v5 em preview Markdown para revisar formulas, listas, titulos e consistencia terminologica.

**Decisions**

- O v5 sera teoria-dominante com experimento breve, nao uma galeria longa de renders.
- O pass de ajuste cobre Python e Markdown, mas limitado a clareza, coerencia fisica, algebra linear e rastreabilidade do relatorio; nao amplia escopo funcional do renderer.
- O relatorio deve separar explicitamente conteudo dos slides de funcionalidades realmente implementadas no repositorio, sobretudo na parte de aceleracao.
- As citacoes externas ficarao restritas ao PBRT 4e, usando capitulos pertinentes como apoio conceitual complementar.
- A hierarquia de confianca das fontes passa a ser: PDFs originais > resumos em materiais/_.md > codigo e comentarios inline > docs/_.md.
- Os arquivos em docs/_.md podem sugerir estrutura e checkpoints, mas nao devem dirigir a formulacao teorica quando entrarem em conflito com os PDFs ou com materiais/_.md.
