"""
Capítulo 10 — Da simulação ao dado real: a constante de Planck com LEDs.

Num LED, um elétron que atravessa a junção perde a energia eV e emite um
fóton de energia h c/λ. Medindo a tensão de "joelho" V0 de LEDs de cores
diferentes (extrapolando a parte linear da curva I–V) e fazendo o gráfico
de V0 contra 1/λ, a inclinação é h c / e. O experimento é simples, mas
cheio de armadilhas sistemáticas — que os dados revelam.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura das curvas I–V e dos espectros
iv = pd.read_csv(PASTA_DADOS / "cap10_leds_iv.csv", comment="#")
esp = pd.read_csv(PASTA_DADOS / "cap10_leds_espectros.csv", comment="#")
esp = esp.set_index("led")
e, c = 1.602176634e-19, 2.99792458e8

# %% [2] Tensão de joelho: extrapolação da parte linear (I entre 10 e 30 mA)
V0 = {}
for led, curva in iv.groupby("led", sort=False):
    lin = curva[(curva["I_mA"] > 10) & (curva["I_mA"] < 30)]
    coef, cov = np.polyfit(lin["V_V"], lin["I_mA"], 1, cov=True)
    v0 = -coef[1] / coef[0]                       # onde a reta cruza I = 0
    jac = np.array([coef[1] / coef[0]**2, -1 / coef[0]])
    u_v0 = np.sqrt(jac @ cov @ jac)
    V0[led] = (v0, u_v0, 1e3 / coef[0])           # V0, incerteza, R_série (Ω)
esp["V0_V"] = [V0[led][0] for led in esp.index]
esp["R_serie_ohm"] = [V0[led][2] for led in esp.index]
esp["inv_lambda"] = 1 / (esp["lambda_pico_nm"] * 1e-9)
print(esp.round(3))


# %% [3] Gráfico de V0 contra 1/λ: inclinação = h c / e
def ajusta(tabela):
    coef, cov = np.polyfit(tabela["inv_lambda"], tabela["V0_V"], 1, cov=True)
    h = coef[0] * e / c
    return h, np.sqrt(cov[0, 0]) * e / c, coef


h_todos, u_todos, coef_todos = ajusta(esp)
sem_verde = esp.drop(index="verde-InGaN")
h_sv, u_sv, coef_sv = ajusta(sem_verde)
h_ref = 6.62607015e-34
for rotulo, h, u in (("todos os LEDs", h_todos, u_todos),
                     ("sem o verde de InGaN", h_sv, u_sv)):
    print(f"{rotulo:22s}: h = {fmt(h * 1e34, u * 1e34, '× 10⁻³⁴ J·s')}  "
          f"(desvio de {100 * (h / h_ref - 1):+.1f} % do valor exato)")

# %% [4] Figura: curvas I–V e reta de Planck
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.9))
cores = {"infravermelho": "0.4", "vermelho": "#d62728", "ambar": "#ff8c00",
         "amarelo-verde": "#9acd32", "verde-InGaN": "#2ca02c",
         "azul": "#1f77b4", "violeta": "#7b3fbf"}
for led, curva in iv.groupby("led", sort=False):
    a1.plot(curva["V_V"], curva["I_mA"], "-", color=cores[led], lw=1.2, label=led)
    v0 = V0[led][0]
    a1.plot([v0, v0 + 30 * V0[led][2] / 1e3], [0, 30], ":", color=cores[led], lw=0.8)
a1.set_xlabel("$V$ (V)")
a1.set_ylabel("$I$ (mA)")
a1.set_ylim(0, 32)
a1.legend(fontsize=6.5, loc="upper left")
x = np.linspace(0, 2.6e6, 10)
for led in esp.index:
    a2.plot(esp.loc[led, "inv_lambda"] / 1e6, esp.loc[led, "V0_V"], "o",
            color=cores[led], mfc="none" if led == "verde-InGaN" else cores[led])
a2.plot(x / 1e6, np.polyval(coef_sv, x), "k-", lw=1,
        label=f"$h$ = {h_sv * 1e34:.2f}".replace(".", ",") + r"$\times10^{-34}$ J s")
a2.plot(x / 1e6, np.polyval(coef_todos, x), "k--", lw=0.8, label="com o verde InGaN")
a2.set_xlabel(r"$1/\lambda$ ($\mu$m$^{-1}$)")
a2.set_ylabel("$V_0$ (V)")
a2.set_xlim(0.9, 2.6)
a2.set_ylim(1.0, 3.4)
a2.legend(fontsize=7, loc="upper left")
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap10_dados_leds")
