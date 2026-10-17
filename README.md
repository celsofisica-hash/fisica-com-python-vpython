# Física com Python e VPython

**Ensinando física com simulações em 3D: do lançamento de projéteis ao átomo de Bohr**

Programas e dados do livro de **Celso Henrique Correa Carvalho** e
**Adhimar Flávio de Oliveira**, do Instituto de Física e Química da
Universidade Federal de Itajubá (UNIFEI).

> Livro em preparação (1ª edição, 2026). O ISBN e o endereço de publicação
> serão informados aqui assim que estiverem disponíveis.

## Sobre o livro

A melhor maneira de entender uma lei física é colocá-la para funcionar. Neste
livro, o leitor escreve, bloco a bloco, programas em Python que aplicam as leis
da física e as mostram em animações 3D com o [VPython](https://vpython.org):
a trajetória de uma bola de futebol com resistência do ar, a potência de uma
usina hidrelétrica, a flexão de uma viga, o esvaziamento de uma caixa d'água, o
ciclo de um motor a combustão, as ondas numa corda de violão, a imagem formada
por uma lente, a geração e a transmissão de energia elétrica, as órbitas de
planetas e satélites e os primeiros passos da física quântica, de Planck a
de Broglie.

Cada simulação é testada contra a teoria, e cada capítulo termina levando o
tema ao laboratório: a videoanálise de um chute, o som de um violão, as luas de
Júpiter, a medida da constante de Planck com LEDs. Os dados são analisados com
NumPy, SciPy e Matplotlib, com ajustes, incertezas, resíduos e erros
sistemáticos.

Não é preciso saber programar. O livro é indicado para estudantes de
licenciatura e bacharelado em física, engenharias e química e para professores
do ensino médio e superior, que encontram roteiros de aula de 50 minutos
alinhados à BNCC, uma rubrica de avaliação e sugestões de uso em sala.

## O que há neste repositório

```
codigos/   17 simulações em VPython e 10 programas de análise de dados
dados/     arquivos de dados das seções "Da simulação ao dado real"
requirements.txt
```

Cada programa é dividido em células marcadas com `# %% [n]`, o mesmo formato
usado pelo Spyder, pelo VS Code e pelo Jupyter. No livro, cada célula aparece
como um bloco numerado, e os números de linha correspondem aos deste
repositório.

## Programas por capítulo

| Cap. | Tema | Simulações (VPython) | Análise de dados |
|---|---|---|---|
| 1 | Força e movimento: projéteis | `cap01_projeteis.py`: bola de futebol no vácuo e no ar | `cap01_dados_chute.py`: o arrasto numa videoanálise |
| 2 | Energia mecânica: usinas hidrelétricas | `cap02_hidreletrica.py`: uma parcela de água descendo o conduto forçado | `cap02_dados_pch.py`: uma semana de operação de uma PCH |
| 3 | Equilíbrio e mecânica dos sólidos | `cap03_viga.py`: um caminhão atravessando uma ponte biapoiada | `cap03_dados_flexao.py`: o módulo de Young de uma régua |
| 4 | Mecânica dos fluidos | `cap04_fluidos.py`: hidrostática, Bernoulli e o esvaziamento de uma caixa d'água | `cap04_dados_garrafa.py`: o coeficiente de descarga de um furo |
| 5 | Termodinâmica e calor | `cap05_motor_otto.py`: o ciclo Otto; `cap05_aleta.py`: a aleta de arrefecimento | `cap05_dados_aleta.py`: o coeficiente de convecção de uma barra |
| 6 | Ondas e acústica | `cap06_corda.py`: a corda de violão; `cap06_doppler.py`: o efeito Doppler da sirene | `cap06_dados_violao.py`: o espectro de uma corda de violão |
| 7 | Óptica | `cap07_lente.py`: imagens de uma lente delgada; `cap07_fenda_dupla.py`: o experimento de Young | `cap07_dados_young.py`: medindo as fendas pela luz |
| 8 | Eletromagnetismo e indução | `cap08_gerador.py`: o gerador de corrente alternada; `cap08_transmissao.py`: por que alta tensão? | `cap08_dados_gerador.py`: a lei de Faraday no osciloscópio |
| 9 | Gravitação | `cap09_kepler.py`: as leis de Kepler; `cap09_satelites.py`: a Estação Espacial e o geoestacionário | `cap09_dados_jupiter.py`: pesando Júpiter com suas luas |
| 10 | Física quântica | `cap10_planck.py`: o corpo negro; `cap10_bohr.py`: o átomo de Bohr; `cap10_dualidade.py`: elétrons, um de cada vez, na fenda dupla | `cap10_dados_leds.py`: a constante de Planck com LEDs |

Também estão em `codigos/`:

- `estilo.py`, que define o padrão dos gráficos de análise;
- `gerar_dados_sinteticos.py`, que recria a pasta `dados/`.

## Como rodar

1. Instale o Python (testado com a versão 3.13) e as bibliotecas:

   ```
   pip install -r requirements.txt
   ```

2. Rode uma simulação:

   ```
   cd codigos
   python cap01_projeteis.py
   ```

   O VPython abre a cena numa aba do navegador. Quando a animação termina, a
   cena continua ativa: gire com o botão direito do mouse e aproxime com a
   roda. Para sair, feche a aba ou tecle `Ctrl+C` no terminal.

3. Rode uma análise de dados:

   ```
   python cap01_dados_chute.py
   ```

   Os resultados aparecem no terminal, e os gráficos são gravados na pasta
   `figuras/`, criada automaticamente.

Se aparecer um erro sobre `pkg_resources`, rode `pip install "setuptools<81"`.

## Sobre os dados

Os dados das seções "Da simulação ao dado real" são **sintéticos**. Eles foram
gerados por modelos físicos com valores verdadeiros conhecidos, aos quais se
somaram as imperfeições típicas de uma medida real: ruído, resolução do
instrumento e erros sistemáticos.

Isso permite conferir se a análise recupera os valores verdadeiros, que estão
no apêndice do livro. O programa `gerar_dados_sinteticos.py` recria todos os
arquivos, sempre com a mesma semente aleatória (2026).

## Como citar

CARVALHO, C. H. C.; OLIVEIRA, A. F. de. **Física com Python e VPython**:
ensinando física com simulações em 3D: do lançamento de projéteis ao átomo de
Bohr. 1. ed. Itajubá, 2026. ISBN a ser informado.

## Licença

A licença ainda está em definição. Até lá, os direitos são reservados aos
autores.
