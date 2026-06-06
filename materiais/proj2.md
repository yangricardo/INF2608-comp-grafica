INF2608 – Fundamentos da Computa ̧c ̃ao Gr ́afica
Projeto 2: Algoritmo de Tra ̧cado de Caminhos

## Prof. Waldemar Celes

Departamento de Inform ́atica, PUC-Rio
2 de junho de 2026
O objetivo deste projeto ́e renderizar uma cena 3D usando o algoritmo de tra ̧cado de cami-
nhos.
A aplica ̧c ̃ao b ́asica a ser desenvolvida deve atender aos seguintes requisitos:
•A cena deve ser criada com instancia ̧c ̃ao de esferas, caixas e/ou planos.
•A cena deve ser iluminada por uma ou mais fontes de luz retangulares.
•A cena deve conter objetos com materias difusos (BRDF constante).
•A cena deve poder ser renderizada com m ́ultiplos caminhos por pixel.
•Os caminhos devem ter profundidade m ́ınima de 4 (isto ́e, o quarto v ́ertice deve estar na
fonte de luz).
Para a avalia ̧c ̃ao, os pontos associados a essa aplica ̧c ̃ao b ́asica s ̃ao 7.0 pontos.
Al ́em disso, a aplica ̧c ̃ao deve ser estendida com os itens abaixo, a escolher:
•Aplica ̧c ̃ao de MIS para o ́ultimo trecho do caminho (amostras na fonte de luz e amostras
por BRDF) – 1.0 ponto.
•Uso da estat ́egia Roleta Russa para tratar caminhos profundos – 2.0 pontos.
•Fonte de luz representada por poliedro (malha de triˆangulos), com uma distribui ̧c ̃ao de
amostras uniforme de ́area – 1.0 ponto.
•Instancia ̧c ̃ao de fonte de luz infinita (luz oriunda de todas as dire ̧c ̃oes, do ambiente) – 1.0
ponto
•Instancia ̧c ̃ao de objetos n ̃ao difusos (microfacetas) – 1.0 ponto.
•Instancia ̧c ̃ao de objetos refrat ́arios – 2.0 pontos.
Espera-se que sejam implementados 3.0 pontos. Alternativamente, o aluno pode optar por
alcan ̧car os 3.0 pontos implementando uma das estrat ́egias a seguir:
•Tra ̧cado de caminho bidirecional
•Renderiza ̧c ̃ao Metr ́opolis

## 1

O aluno deve elaborar um relat ́orio explicando o trabalho desenvolvido, com screenshots para
ilustrar os resultados obtidos, seguido de uma an ́alise dos resultados alcan ̧cados. A qualidade
do relat ́orio tamb ́em faz parte do crit ́erio de avalia ̧c ̃ao. De forma geral, o relat ́orio deve conter:
•Nome do autor
•Descri ̧c ̃ao das t ́ecnicas adotadas.
•Imagens ilustrando o resultado obtido da renderiza ̧c ̃ao da cena escolhida.
•Imagens comparando o uso de diferentes parˆametros (como n ́umeros de amostras por pixel,
profunidade m ́ınima de caminhos etc).
•Imagens demonstrando os efeitos escolhidos para a extens ̃ao da aplica ̧c ̃ao b ́asica.
•An ́alise dos resultados alcan ̧cados.
Entrega:Enviar um relat ́orio (formato pdf) e o c ́odigo fonte (apenas o c ́odigo fonte codifi-
cado pelo aluno). O envio deve ser feito via p ́agina da disciplina no EAD at ́eter ̧ca-feira, dia
30 de junho. N ̃ao haver ́a prorroga ̧c ̃ao do prazo. Eventual atraso adicional pode acarretar grau

## IN.

## 2
