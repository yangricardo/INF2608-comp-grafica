# INF2608 - FUNDAMENTOS DA COMPUTAÇÃO GRÁFICA - 2026.1 - 3WA - DI PUC-Rio

> Aluno: Yang Miranda

Este repositório implementa um renderizador de traçado de raios baseado nas aulas do Prof. Waldemar Celes.

## 🛠️ Requisitos e Ambiente

- **Python**: 3.13.9
- **Gerenciador de Versão**: asdf (com plugin python/pyenv)
- **Biblioteca Matemática**: PyGLM (OpenGL Mathematics para Python)

## 🚀 Passo a Passo para Setup

### 1. Instalação do asdf e Python

Caso ainda não possua o `asdf` instalado, siga as instruções oficiais. Em seguida, adicione o plugin do python (que utiliza o `pyenv` internamente):

```bash
# Adicionar o plugin do python
asdf plugin add python

# Instalar a versão específica
asdf install python 3.13.9

# Definir como versão local para o projeto
asdf set python 3.13.9

# Criar venv
python -m venv .venv
source .venv/bin/activate

# Instalar bibliotecas recomendadas
pip install --upgrade pip
pip install PyGLM pillow numpy
```
