"""
Estilo comum dos gráficos de análise de dados do livro (Matplotlib).

Uso:
    from estilo import aplicar_estilo, virgula_decimal, salvar
    aplicar_estilo()
    fig, ax = plt.subplots()
    ...
    virgula_decimal(fig)          # 1,5 em vez de 1.5 nos eixos
    salvar(fig, "cap01_dados")    # grava figuras/cap01_dados.pdf e .png
"""
import logging
from pathlib import Path

import matplotlib as mpl
from matplotlib import ticker

PASTA_FIGURAS = Path(__file__).resolve().parent.parent / "figuras"
PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"

# Paleta acessível (daltônicos) — Okabe & Ito
CORES = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
         "#E69F00", "#56B4E9", "#F0E442", "#000000"]


def aplicar_estilo():
    """Fontes serifadas, eixos finos, ticks para dentro, tamanho de coluna."""
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "CMU Serif", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "legend.fontsize": 8.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.minor.visible": True,
        "ytick.minor.visible": True,
        "lines.linewidth": 1.4,
        "lines.markersize": 4,
        "legend.frameon": False,
        "axes.prop_cycle": mpl.cycler(color=CORES),
        "figure.figsize": (6.3, 3.6),
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def virgula_decimal(fig):
    """Troca o ponto decimal por vírgula nos eixos lineares da figura."""
    formatador = ticker.FuncFormatter(
        lambda x, pos: f"{x:g}".replace(".", ",").replace("-", "−"))
    for ax in fig.axes:
        if ax.get_xscale() == "linear":
            ax.xaxis.set_major_formatter(formatador)
        if ax.get_yscale() == "linear":
            ax.yaxis.set_major_formatter(formatador)


def salvar(fig, nome):
    """Grava a figura em PDF (vetorial, para o livro) e PNG."""
    PASTA_FIGURAS.mkdir(exist_ok=True)
    fig.savefig(PASTA_FIGURAS / f"{nome}.pdf")
    fig.savefig(PASTA_FIGURAS / f"{nome}.png")
    print(f"Figura gravada em {PASTA_FIGURAS / nome}.pdf")


def fmt(valor, incerteza, unidade=""):
    """Escreve valor ± incerteza com 2 algarismos significativos na incerteza."""
    from math import floor, log10
    if incerteza <= 0:
        return f"{valor:g} {unidade}".strip()
    casas = max(0, 1 - int(floor(log10(abs(incerteza)))))
    texto = f"({valor:.{casas}f} ± {incerteza:.{casas}f})"
    return f"{texto} {unidade}".strip()
