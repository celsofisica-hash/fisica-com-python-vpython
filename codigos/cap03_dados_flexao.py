"""
Capítulo 3 — Da simulação ao dado real: o módulo de Young de uma régua.

Ensaio de flexão em três pontos: massas penduradas no meio do vão e flecha
lida num relógio comparador. Um ajuste linear y = a P + y0 fornece a
inclinação a = L³/(48 E I); com as dimensões medidas da seção obtemos E e
montamos o balanço de incertezas (qual medida limita o resultado?).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura dos dados do ensaio e das dimensões
ensaio = pd.read_csv(PASTA_DADOS / "cap03_flexao_regua.csv", comment="#")
dim = pd.read_csv(PASTA_DADOS / "cap03_dimensoes_regua.csv", comment="#")
g = 9.81
ensaio["P_N"] = ensaio["massa_g"] * 1e-3 * g
L, u_L = 0.4000, 0.0005                     # m (trena)

# %% [2] Incertezas das dimensões: tipo A (repetição) e tipo B (instrumento)


def media_e_incerteza(valores, resolucao):
    """Média e incerteza padrão combinando dispersão e resolução."""
    uA = valores.std(ddof=1) / np.sqrt(len(valores))
    uB = resolucao / (2 * np.sqrt(3))       # distribuição retangular
    return valores.mean(), np.hypot(uA, uB)


b, u_b = media_e_incerteza(dim["largura_b_mm"] * 1e-3, 0.02e-3)
h, u_h = media_e_incerteza(dim["espessura_h_mm"] * 1e-3, 0.001e-3)
I = b * h**3 / 12
print(f"b = {fmt(b * 1e3, u_b * 1e3, 'mm')},  h = {fmt(h * 1e3, u_h * 1e3, 'mm')}")

# %% [3] Ajuste linear da flecha em função da carga
reg = stats.linregress(ensaio["P_N"], ensaio["flecha_mm"] * 1e-3)
a, u_a = reg.slope, reg.stderr
print(f"a = {fmt(a * 1e3, u_a * 1e3, 'mm/N')}, y0 = {reg.intercept * 1e6:.1f} μm, "
      f"r = {reg.rvalue:.5f}")

# %% [4] Módulo de Young e balanço de incertezas
E = L**3 / (48 * a * I)
contribuicoes = {               # incerteza relativa de E devida a cada grandeza
    "L (cubo)": 3 * u_L / L,
    "inclinação a": u_a / a,
    "largura b": u_b / b,
    "espessura h (cubo)": 3 * u_h / h,
}
u_E = E * np.sqrt(sum(c**2 for c in contribuicoes.values()))
print(f"E = {fmt(E / 1e9, u_E / 1e9, 'GPa')}")
for nome, c in sorted(contribuicoes.items(), key=lambda kv: -kv[1]):
    fracao = 100 * c**2 / (u_E / E)**2
    print(f"  {nome:20s} {100 * c:5.2f} %   ({fracao:4.1f} % da variância)")

# %% [5] Figura: dados de carga e descarga, reta ajustada e resíduos
aplicar_estilo()
fig, (a1, a2) = plt.subplots(2, 1, figsize=(4.6, 4.0), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.2]})
for sentido, marca in (("carga", "o"), ("descarga", "^")):
    s = ensaio[ensaio["sentido"] == sentido]
    a1.plot(s["P_N"], s["flecha_mm"], marca, mfc="none", label=sentido)
    a2.plot(s["P_N"], 1e3 * (s["flecha_mm"] - 1e3 * (reg.intercept + a * s["P_N"])),
            marca, mfc="none")
Ps = np.linspace(0, ensaio["P_N"].max(), 50)
a1.plot(Ps, 1e3 * (reg.intercept + a * Ps), "k-", lw=1,
        label=f"ajuste: $E$ = {E / 1e9:.1f} GPa".replace(".", ","))
a1.set_ylabel("flecha (mm)")
a1.legend()
a2.axhline(0, color="gray", lw=0.6)
a2.set_ylabel(r"resíduo ($\mu$m)")
a2.set_xlabel("carga $P$ (N)")
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap03_dados_flexao")
