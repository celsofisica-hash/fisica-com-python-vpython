"""
Capítulo 4 — Da simulação ao dado real: o coeficiente de descarga de um furo.

A altura da água numa garrafa PET que esvazia por um furo é lida num vídeo.
Pela lei de Torricelli com coeficiente de descarga, √h decresce linearmente
com o tempo; a inclinação fornece C_d. Os pontos finais, quando o jato vira
gotejamento, são analisados à parte.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura e geometria
dados = pd.read_csv(PASTA_DADOS / "cap04_garrafa_pet.csv", comment="#")
t = dados["t_s"].to_numpy()
h = dados["h_mm"].to_numpy() * 1e-3
u_h = 0.8e-3                         # leitura no vídeo: paralaxe e menisco (m)
g = 9.81
D, u_D = 0.0900, 0.0001              # diâmetro da garrafa (m)
d, u_d = 0.0040, 0.0001              # diâmetro do furo (m)
razao = (d / D)**2                   # a/A

# %% [2] Linearização: √h em função do tempo, só enquanto há jato (h > 2 cm)
jato = h > 0.020
raiz = np.sqrt(h[jato])
u_raiz = u_h / (2 * raiz)            # propagação: d√h = dh / (2√h)
coef, cov = np.polyfit(t[jato], raiz, 1, w=1 / u_raiz, cov="unscaled")
incl, u_incl = -coef[0], np.sqrt(cov[0, 0])
chi2_red = np.sum(((raiz - np.polyval(coef, t[jato])) / u_raiz)**2) / (jato.sum() - 2)
print(f"Inclinação de √h: {fmt(incl * 1e3, u_incl * 1e3, 'mm^½/s')}, "
      f"χ²_red = {chi2_red:.2f}")

# %% [3] Coeficiente de descarga e sua incerteza
Cd = incl / (razao * np.sqrt(g / 2))
u_rel = np.sqrt((u_incl / incl)**2 + (2 * u_d / d)**2 + (2 * u_D / D)**2)
print(f"C_d = {fmt(Cd, Cd * u_rel)}")
print(f"  contribuição do diâmetro do furo: {100 * 2 * u_d / d:.1f} %")
print(f"  contribuição da inclinação:       {100 * u_incl / incl:.1f} %")


# %% [4] Ajuste não linear direto de h(t), para comparação
def h_modelo(t, h0, Cd):
    return (np.sqrt(h0) - Cd * razao * np.sqrt(g / 2) * t).clip(0)**2


p, cov2 = curve_fit(h_modelo, t[jato], h[jato], p0=[0.2, 0.6],
                    sigma=np.full(jato.sum(), u_h), absolute_sigma=True)
print(f"Ajuste direto: h0 = {p[0] * 1e3:.1f} mm, C_d = {fmt(p[1], np.sqrt(cov2[1, 1]))}"
      " (só a parte estatística)")
t_teo = np.sqrt(p[0]) / (p[1] * razao * np.sqrt(g / 2))
print(f"Tempo previsto até esvaziar: {t_teo:.0f} s; último ponto medido: {t[-1]:.0f} s")

# %% [5] Figura
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
ts = np.linspace(0, t_teo, 200)
a1.plot(t[jato], h[jato] * 1e3, "o", mfc="none", label="jato")
a1.plot(t[~jato], h[~jato] * 1e3, "s", color="C1", label="gotejamento")
a1.plot(ts, h_modelo(ts, *p) * 1e3, "k-", lw=1, label="Torricelli com $C_d$")
a1.set_xlabel("$t$ (s)")
a1.set_ylabel("$h$ (mm)")
a1.legend()
a2.errorbar(t[jato], raiz, yerr=u_raiz, fmt="o", mfc="none", elinewidth=0.6)
a2.plot(t[~jato], np.sqrt(h[~jato]), "s", color="C1")
a2.plot(ts, np.polyval(coef, ts), "k-", lw=1)
a2.set_xlabel("$t$ (s)")
a2.set_ylabel(r"$\sqrt{h}$ (m$^{1/2}$)")
a2.text(0.45, 0.85, f"$C_d$ = {Cd:.3f}".replace(".", ","), transform=a2.transAxes)
for ax, letra in ((a1, "(a)"), (a2, "(b)")):
    ax.text(0.04, 0.06, letra, transform=ax.transAxes)
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap04_dados_garrafa")
