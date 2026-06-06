from __future__ import annotations

import os
from PIL import Image
from pyglm import glm
import numpy as np
import random
import math
from typing import Optional
from enum import Enum

from .camera import Camera
from .sampling import stratified_grid_samples_2d, uniform_samples_2d
from .scene import Scene


# Enum público para escolher modo de amostragem no filme.
class SamplingMode(Enum):
  CENTER = 'center'
  JITTERED = 'jittered'
  STRATIFIED = 'stratified'


def normalize_sampling_mode(sampling_mode: str | SamplingMode | None) -> SamplingMode:
  if isinstance(sampling_mode, SamplingMode):
    return sampling_mode
  if sampling_mode is None:
    return SamplingMode.JITTERED

  mode_str = str(sampling_mode).lower()
  if mode_str == SamplingMode.CENTER.value:
    return SamplingMode.CENTER
  if mode_str == SamplingMode.STRATIFIED.value:
    return SamplingMode.STRATIFIED
  return SamplingMode.JITTERED


def effective_samples_per_pixel_for_mode(
  samples_per_pixel: int,
  sampling_mode: str | SamplingMode | None,
) -> int:
  spp = max(1, int(samples_per_pixel))
  return 1 if normalize_sampling_mode(sampling_mode) == SamplingMode.CENTER else spp


def sampling_mode_help_text() -> str:
  return (
    'Film sampling mode: center = single central sample per pixel (no AA); '
    'jittered = random subpixel sampling; '
    'stratified = stratified subpixel sampling.'
  )


def describe_sampling_configuration(
  samples_per_pixel: int,
  sampling_mode: str | SamplingMode | None,
) -> str:
  requested_spp = max(1, int(samples_per_pixel))
  mode = normalize_sampling_mode(sampling_mode)
  effective_spp = effective_samples_per_pixel_for_mode(requested_spp, mode)

  if mode == SamplingMode.CENTER:
    return (
      'modo=center (amostra central, sem AA) | '
      f'spp efetivo=1 | spp solicitado={requested_spp}'
    )
  if mode == SamplingMode.JITTERED:
    detail = 'AA jittered' if effective_spp > 1 else '1 amostra subpixel aleatória'
    return f'modo=jittered ({detail}) | spp={effective_spp}'

  detail = 'AA estratificado' if effective_spp > 1 else '1 estrato subpixel'
  return f'modo=stratified ({detail}) | spp={effective_spp}'

class Film:
  def __init__(self, width: int, height: int, samples_per_pixel: int = 16, sampling_mode: Optional[str] = None, seed: Optional[int] = None):
    self.width = width
    self.height = height
    self.resolution = (width, height)
    # Slide 4, p. 24-29: buffer 2D do filme onde a radiância estimada por pixel
    # é acumulada antes da conversão final para imagem exibível.
    self.image = np.zeros((height, width, 3))
    # Parâmetros de amostragem para Anti-aliasing
    # `samples_per_pixel`: número de amostras por pixel (Monte Carlo)
    self.samples_per_pixel: int = max(1, int(samples_per_pixel))
    # `sampling_mode`: usa o enum `SamplingMode` definido no módulo
    self.sampling_mode: SamplingMode = normalize_sampling_mode(sampling_mode)

    # Semente para reprodutibilidade; pode ser None para variabilidade
    self.seed: Optional[int] = seed
    self.rng: random.Random = random.Random()
    if self.seed is not None:
      self.rng.seed(self.seed)

  def set_pixel(self, i: int, j: int, color: glm.vec3):
    # Slide 4, p. 24-28: grava a cor calculada no pixel (i, j), já limitada ao intervalo válido.
    self.image[j, i] = glm.clamp(color, 0, 1)

  def get_sample(self, i, j):
    """Retorna as coordenadas normalizadas (0 a 1) para o pixel (i, j)"""
    # Slide 4, p. 25-29: amostragem determinística no centro do pixel, isto é,
    # a versão sem supersampling da câmera pinhole apresentada no núcleo básico.
    return (i + 0.5) / self.width, (j + 0.5) / self.height

  def get_samples_for_pixel(self, i: int, j: int) -> list[tuple[float, float]]:
    """
    Gera uma lista de amostras normalizadas (xn, yn) para o pixel (i, j).
    Suporta três modos: 'center', 'jittered' e 'stratified'.

    Comentário (PT): `get_sample()` preserva a fórmula central do Slide 4,
    enquanto este método implementa a extensão de anti-aliasing do Slide 5
    (pp. 4-9). Em ambos os casos, a meta é aproximar a integral da radiância
    sobre a área do pixel pelo estimador Monte Carlo

      L_hat = (1/N) * sum_k L(x_k),

    de modo que o padrão de amostragem afeta principalmente a variância do
    estimador, não a geometria da câmera nem da cena.
    """
    spp = max(1, int(self.samples_per_pixel))
    samples: list[tuple[float, float]] = []

    if self.sampling_mode == SamplingMode.CENTER:
      # Slide 4, p. 25-29: preserva explicitamente o pipeline original do
      # projeto, no qual cada pixel usa apenas a amostra central da câmera
      # pinhole, sem jitter nem estratificação subpixel.
      return [self.get_sample(i, j)]

    if self.sampling_mode == SamplingMode.JITTERED:
      # Slide 5, p. 4-8: jittered Monte Carlo dentro do pixel. As amostras são
      # independentes e simples de gerar, mas podem concentrar mais ruído local.
      # O nome público continua `JITTERED`, mas a implementação concreta agora
      # delega para `sampling.uniform_samples_2d()`, que materializa os pares
      # aleatórios xi in [0,1) do domínio bidimensional normalizado do pixel.
      for rx, ry in uniform_samples_2d(spp, self.rng):
        xn = (i + rx) / self.width
        yn = (j + ry) / self.height
        samples.append((xn, yn))
      return samples

    # stratified
    # A amostragem estratificada impõe cobertura espacial mínima ao subdividir o
    # pixel em GxG subcélulas, reduzindo variância em comparação ao jitter puro.
    # A implementação do padrão 2D fica em `sampling.stratified_grid_samples_2d()`;
    # este método apenas transforma as coordenadas locais [0,1]^2 em coordenadas
    # normalizadas do pixel corrente.
    # TODO(sampling): experimentar sequências de baixa discrepância para reduzir
    # ruído sem aumentar `samples_per_pixel` de forma puramente bruta.
    G = math.ceil(math.sqrt(spp))
    for sub_x, sub_y in stratified_grid_samples_2d(G, G, self.rng)[:spp]:
        xn = (i + sub_x) / self.width
        yn = (j + sub_y) / self.height
        samples.append((xn, yn))

    return samples
  
  def render(self, scene: Scene, camera: Camera, filename: str, gamma_fix: bool = False) -> None:
    # Slides 4-5: percorre todos os pixels, gera um raio por amostra subpixel e
    # estima a cor média do pixel por média aritmética. Quando há uma única
    # amostra central, o comportamento recai no pipeline básico; com múltiplas
    # amostras, entra a aproximação Monte Carlo do anti-aliasing com
    # c(i,j) = (1/N) * sum_k trace_ray(ray_k).
    for j in range(self.height):
      for i in range(self.width):
        # Para cada pixel, gera uma lista de amostras subpixel.
        samples = self.get_samples_for_pixel(i, j)
        accum = glm.vec3(0.0, 0.0, 0.0)
        for xn, yn in samples:
          # Gera o raio primário para a amostra atual (Slide 4, p. 29)
          ray = camera.generate_ray(xn, yn)
          color = scene.trace_ray(ray)
          accum += color
        # Calcula a média Monte Carlo das amostras para o pixel
        final_color = accum / float(len(samples))
        # Armazena a cor no buffer (com clamp interno em set_pixel)
        self.set_pixel(i, j, final_color)
    # Correção gama opcional para aproximar a resposta visual exibida na tela.
    if gamma_fix:
      img_data = np.power(self.image, 1/2.2)
    else:
      img_data = self.image
    # Converte para uint8 e salva a imagem usando PIL.
    img_data = np.clip(img_data * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_data)
    output_dir = os.path.dirname(filename)
    if output_dir:
      os.makedirs(output_dir, exist_ok=True)
    img.save(filename)
    print(f"Imagem salva em {filename}")