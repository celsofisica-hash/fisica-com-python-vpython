"""
Capítulo 5 — Da simulação ao dado real: o coeficiente de convecção de uma barra.

Oito sensores de temperatura registram o aquecimento de uma barra de
alumínio presa a um resistor. No regime estacionário, o perfil T(x) é
ajustado pela solução da equação da aleta; o parâmetro m fornece o
coeficiente de transferência de calor por convecção h.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura: uma coluna por sensor
dados = pd.read_csv(PASTA_DADOS / "cap05_barra_aquecida.csv", comment="#")
sensores = [c for c in dados.columns if c.startswith("T_") and c.endswith("cm")]
x = np.array([int(c[2:4]) for c in sensores]) * 1e-2           # posições (m)
k, D, L = 167.0, 6.35e-3, 0.300                                # Al 6061

# %% [2] Regime estacionário: média dos últimos 5 minutos
final = dados[dados["t_s"] >= dados["t_s"].max() - 300]
T_med = final[sensores].mean().to_numpy()
u_T = 0.20      # incerteza de cada sensor após calibração em banho (°C)
T_ar = final["T_ar"].mean()
deriva = (dados[sensores].iloc[-1] - dados[sensores].iloc[-31]).abs().max()
print(f"T_ar = {T_ar:.2f} °C; maior variação nos últimos 5 min: {deriva:.2f} °C")
print(pd.DataFrame({"x_cm": x * 100, "T_media": T_med.round(2)}).to_string(index=False))

# %% [3] Ajuste do perfil da aleta (ponta com convecção → comprimento corrigido)
Lc = L + D / 4


def perfil(x, theta_b, m):
    return T_ar + theta_b * np.cosh(m * (Lc - x)) / np.cosh(m * Lc)


p, cov = curve_fit(perfil, x, T_med, p0=[55, 7], sigma=np.full(x.size, u_T),
                   absolute_sigma=True)
theta_b, m = p
u_theta, u_m = np.sqrt(np.diag(cov))
chi2_red = np.sum(((T_med - perfil(x, *p)) / u_T)**2) / (x.size - 2)
print(f"θ_b = {fmt(theta_b, u_theta, '°C')}, m = {fmt(m, u_m, '1/m')}, "
      f"χ²_red = {chi2_red:.2f}")

# %% [4] Coeficiente de convecção e calor dissipado
h = m**2 * k * D / 4
u_h = h * 2 * u_m / m
A = np.pi * D**2 / 4
q = k * A * m * theta_b * np.tanh(m * Lc)
print(f"h = {fmt(h, u_h, 'W/(m²·K)')}  (convecção natural no ar: 5 a 25)")
print(f"Calor conduzido pela base: {q:.2f} W")

# %% [5] Figura: aquecimento de cada sensor e perfil estacionário
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
for i, c in enumerate(sensores):
    a1.plot(dados["t_s"] / 60, dados[c], lw=1, color=plt.cm.plasma(i / 8),
            label=f"{int(x[i] * 100)} cm")
a1.axvspan((dados["t_s"].max() - 300) / 60, dados["t_s"].max() / 60,
           color="0.9", zorder=0)
a1.set_xlabel("$t$ (min)")
a1.set_ylabel("$T$ (°C)")
a1.legend(ncol=2, fontsize=7, loc="right")
xs = np.linspace(0, L, 200)
a2.errorbar(x * 100, T_med, yerr=u_T, fmt="o", mfc="none", label="média dos 5 min finais")
a2.plot(xs * 100, perfil(xs, *p), "k-", lw=1,
        label=f"aleta: $h$ = {h:.1f} W/(m²K)".replace(".", ","))
a2.set_xlabel("$x$ (cm)")
a2.set_ylabel("$T$ (°C)")
a2.legend()
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap05_dados_aleta")
