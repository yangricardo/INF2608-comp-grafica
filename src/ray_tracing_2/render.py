from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Optional

import glm

from ray_tracing_2.film import Film


class Render:
  def __init__(self, out_root: str = 'outputs'):
    self.out_root = out_root

  def explain_properties_md(self, props: dict) -> str:
    """Gera o texto Markdown com as propriedades da simulação.

    Comentário (PT): reutiliza o formato usado em `generate_scene.py` e
    `random_scene.py` para manter consistência de saída.
    """
    lines = []
    lines.append('# Propriedades da Simulação')
    lines.append('')
    lines.append('![Imagem da Simulação](render.png)')
    lines.append('')
    lines.append('## Valores usados (numéricos)')
    lines.append('')
    lines.append('```json')
    lines.append(json.dumps(props, indent=2, ensure_ascii=False))
    lines.append('```')
    lines.append('')
    lines.append('## O que significa cada valor (explicação para leigos)')
    lines.append('')
    lines.append('- **Spheres**: lista de esferas; cada uma tem `center` (posição [x,y,z]) e `radius` (tamanho).')
    lines.append('- **Plane - `y`**: altura do piso; valores menores colocam o piso mais abaixo.')
    lines.append('- **Material - `ambient`**: iluminação ambiente (suave).')
    lines.append('- **Material - `diffuse`**: cor principal sob luz direta.')
    lines.append('- **Material - `specular`**: cor/intensidade do brilho (pequenos reflexos).')
    lines.append('- **Material - `shininess`**: controla quão pequeno/afiado é o brilho especular.')
    lines.append('- **Lights - `pos`**: posição da fonte; **power**: intensidade por canal (R,G,B).')
    lines.append('')
    lines.append('> Nota: abra este `properties.md` dentro da pasta de saída para visualizar a imagem incorporada.')
    return '\n'.join(lines)

  def render(self,
             scene,
             cam,
             width: int,
             height: int,
             name: str = 'scene',
             props: Optional[dict] = None,
             samples_per_pixel: int = 16,
             sampling_mode: str = 'jittered',
             seed: Optional[int] = None,
             gamma_fix: bool = False) -> str:
    """Renderiza a cena, salva `render.png` e `properties.md` em uma pasta timestamp.

    Retorna o caminho da pasta criada.
    """
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    sim_dir = os.path.join(os.getcwd(), self.out_root, f'{name}_{ts}')
    os.makedirs(sim_dir, exist_ok=True)

    img_path = os.path.join(sim_dir, 'render.png')

    # Cria o Film com parâmetros de AA e renderiza para o arquivo de saída
    film = Film(width=width, height=height, samples_per_pixel=samples_per_pixel, sampling_mode=sampling_mode, seed=seed)
    film.render(scene=scene, camera=cam, filename=img_path, gamma_fix=gamma_fix)

    # Gera o markdown de propriedades e grava
    props = props or {}
    md_text = self.explain_properties_md(props)
    md_path = os.path.join(sim_dir, 'properties.md')
    with open(md_path, 'w', encoding='utf-8') as f:
      f.write(md_text)

    return sim_dir
