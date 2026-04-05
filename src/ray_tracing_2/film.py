from __future__ import annotations

from PIL import Image
from pyglm import glm
import numpy as np
import random
import math
from typing import Optional
from enum import Enum

from ray_tracing_2.camera import Camera
from ray_tracing_2.scene import Scene


# Enum público para escolher modo de amostragem (jittered ou stratified)
class SamplingMode(Enum):
  JITTERED = 'jittered'
  STRATIFIED = 'stratified'

class Film:
  def __init__(self, width: int, height: int, samples_per_pixel: int = 16, sampling_mode: Optional[str] = None, seed: Optional[int] = None):
    self.width = width
    self.height = height
    self.resolution = (width, height)
    # Slide 4, p. 24-28: buffer 2D de pixels que armazena a imagem final da renderização.
    self.image = np.zeros((height, width, 3))
    # Parâmetros de amostragem para Anti-aliasing
    # `samples_per_pixel`: número de amostras por pixel (Monte Carlo)
    self.samples_per_pixel: int = max(1, int(samples_per_pixel))
    # `sampling_mode`: usa o enum `SamplingMode` definido no módulo
    if sampling_mode is None:
      self.sampling_mode: SamplingMode = SamplingMode.JITTERED
    elif isinstance(sampling_mode, SamplingMode):
      self.sampling_mode = sampling_mode
    else:
      # aceita string 'jittered' / 'stratified'
      mode_str = str(sampling_mode).lower()
      if mode_str == SamplingMode.STRATIFIED.value:
        self.sampling_mode = SamplingMode.STRATIFIED
      else:
        self.sampling_mode = SamplingMode.JITTERED

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
    # Slide 4, p. 25-29: amostragem no centro do pixel para disparar um raio primário.
    return (i + 0.5) / self.width, (j + 0.5) / self.height

  def get_samples_for_pixel(self, i: int, j: int) -> list[tuple[float, float]]:
    """
    Gera uma lista de amostras normalizadas (xn, yn) para o pixel (i, j).
    Suporta dois modos: 'jittered' (Monte Carlo jittered) e 'stratified'.

    Comentário (PT): Implementação de amostragem por pixel baseada nos slides
    de amostragem/anti-aliasing (Slide 4, p. 25-29). Em 'stratified' usamos uma
    subdivisão GxG do pixel para reduzir variância por amostra.
    """
    spp = max(1, int(self.samples_per_pixel))
    samples: list[tuple[float, float]] = []

    if self.sampling_mode == SamplingMode.JITTERED:
      # Slide 4, p. 25-29: jittered Monte Carlo dentro do pixel
      for _ in range(spp):
        rx = self.rng.random()
        ry = self.rng.random()
        xn = (i + rx) / self.width
        yn = (j + ry) / self.height
        samples.append((xn, yn))
      return samples

    # stratified
    # Slide (amostragem estratificada): subdivide o pixel em GxG subcelulas
    G = math.ceil(math.sqrt(spp))
    count = 0
    for a in range(G):
      for b in range(G):
        if count >= spp:
          break
        # ponto aleatório dentro da subcélula (a,b)
        ux = self.rng.random()
        uy = self.rng.random()
        sub_x = (a + ux) / G
        sub_y = (b + uy) / G
        xn = (i + sub_x) / self.width
        yn = (j + sub_y) / self.height
        samples.append((xn, yn))
        count += 1
      if count >= spp:
        break

    return samples
  
  def render(self, scene: Scene, camera: Camera, filename: str, gamma_fix: bool = False) -> None:
    # Slide 4, p. 24-29: percorre todos os pixels e pede um raio para cada amostra.
    # Comentário (PT): início do render com múltiplas amostras por pixel conforme
    # Slide 4, p. 25-29. Aqui usamos `self.samples_per_pixel` e `self.sampling_mode`.
    print("Renderizando a cena com AA (spp=", self.samples_per_pixel, ", mode=", self.sampling_mode.name, ")...")
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
    img.save(filename)
    print(f"Imagem salva em {filename}")