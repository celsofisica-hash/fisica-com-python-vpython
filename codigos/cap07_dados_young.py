"""
Capítulo 7 — Da simulação ao dado real: medindo as fendas pela luz.

Um fotodiodo percorre o padrão de interferência da fenda dupla. Ajustando
a expressão completa I(y) = fundo + I0 cos²(πd sen θ/λ) sinc²(πa sen θ/λ)
aos dados, determinamos a separação d e a largura a das fendas — medidas
de décimos e centésimos de milímetro feitas com uma régua de luz.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura e constantes
dados = pd.read_csv(PASTA_DADOS / "cap07_young_fotodiodo.csv", comment="#")
y = dados["y_mm"].to_numpy() * 1e-3
V = dados["V_V"].to_numpy()
lam = 632.8e-9                      # comprimento de onda do He-Ne (m)
D, u_D = 1.000, 0.002               # distância fendas–detector (m)


# %% [2] Modelo com cinco parâmetros livres
def young(y, I0, fundo, yc, d, a):
    s = (y - yc) / np.hypot(y - yc, D)            # sen θ
    return fundo + I0 * np.cos(np.pi * d * s / lam)**2 \
        * np.sinc(a * s / lam)**2                  # np.sinc(u) = sen(πu)/(πu)


# %% [3] Estimativa inicial a partir do próprio gráfico e ajuste
chute = [V.max(), V.min(), y[np.argmax(V)], 0.25e-3, 0.05e-3]
u_V = 0.015 * V + 0.002                            # ruído: 1,5 % + 2 mV
p, cov = curve_fit(young, y, V, p0=chute, sigma=u_V, absolute_sigma=True)
u = np.sqrt(np.diag(cov))
residuo = (V - young(y, *p)) / u_V
chi2_red = np.sum(residuo**2) / (y.size - 5)
I0, fundo, yc, d, a = p
# A incerteza de D se propaga integralmente para d e a (d ∝ D):
u_d = d * np.hypot(u[3] / d, u_D / D)
u_a = a * np.hypot(u[4] / a, u_D / D)
print(f"d = {fmt(d * 1e3, u_d * 1e3, 'mm')}   (nominal 0,25 mm)")
print(f"a = {fmt(a * 1e3, u_a * 1e3, 'mm')}   (nominal 0,05 mm)")
print(f"centro = {yc * 1e3:.3f} mm, fundo = {fundo * 1e3:.1f} mV, χ²_red = {chi2_red:.2f}")

# %% [4] Diagnóstico: os resíduos têm tendência?
metade = y.size // 2
print(f"Resíduo médio: lado esquerdo {residuo[:metade].mean():+.2f}, "
      f"lado direito {residuo[metade:].mean():+.2f}")

# %% [5] Figura: dados, ajuste e resíduos normalizados
aplicar_estilo()
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.3, 3.9), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.1]})
ys = np.linspace(y.min(), y.max(), 2000)
a1.plot(y * 1e3, V, ".", ms=3, color="k", label="fotodiodo")
a1.plot(ys * 1e3, young(ys, *p), "-", color="C1", lw=1,
        label=f"ajuste:\n$d$ = {d * 1e3:.3f} mm\n$a$ = {a * 1e3:.4f} mm".replace(".", ","))
a1.set_ylabel("tensão (V)")
a1.legend(loc="upper left")
a2.axhline(0, color="gray", lw=0.6)
a2.plot(y * 1e3, residuo, ".", ms=3)
a2.set_ylabel(r"resíduo/$\sigma$")
a2.set_xlabel("$y$ (mm)")
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap07_dados_young")
