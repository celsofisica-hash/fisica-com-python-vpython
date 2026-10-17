"""
Capítulo 1 — Da simulação ao dado real: o arrasto numa videoanálise.

Lê as posições de uma bola marcadas quadro a quadro no Tracker e ajusta
dois modelos: (1) a parábola do vácuo e (2) a 2ª lei de Newton com arrasto
quadrático, integrada numericamente. Do segundo ajuste obtém-se o
coeficiente de arrasto C_d com sua incerteza.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura dos dados e constantes conhecidas
dados = pd.read_csv(PASTA_DADOS / "cap01_chute_tracker.csv", comment="#")
print(dados.head())
t, x, y = dados["t_s"].to_numpy(), dados["x_m"].to_numpy(), dados["y_m"].to_numpy()

g = 9.81            # m/s²
m, R = 0.430, 0.110  # massa (kg) e raio (m) da bola
rho_ar = 1.18       # densidade do ar a 25 °C (kg/m³)
sigma = 0.015       # incerteza de cada posição marcada (m)

# %% [2] Modelo 1: o movimento no vácuo (polinômios em t)
cx, cov_x = np.polyfit(t, x, 1, cov=True)          # x = x0 + vx t
cy, cov_y = np.polyfit(t, y, 2, cov=True)          # y = y0 + vy t − g t²/2
g_aparente = -2 * cy[0]
print(f"Vácuo: vx = {cx[0]:.2f} m/s, g aparente = "
      f"{fmt(g_aparente, 2 * np.sqrt(cov_y[0, 0]), 'm/s²')}")
res_x_vacuo = x - np.polyval(cx, t)
res_y_vacuo = y - np.polyval(cy, t)


# %% [3] Modelo 2: Newton com arrasto, integrado a cada tentativa do ajuste
def trajetoria(p, t):
    """p = (x0, y0, vx0, vy0, b), com b = k/m (1/m). Devolve x(t), y(t)."""
    x0, y0, vx0, vy0, b = p

    def derivadas(_, s):
        v = np.hypot(s[2], s[3])
        return [s[2], s[3], -b * v * s[2], -g - b * v * s[3]]
    sol = solve_ivp(derivadas, (0, t[-1]), [x0, y0, vx0, vy0], t_eval=t,
                    rtol=1e-9, atol=1e-9)
    return sol.y[0], sol.y[1]


def residuos(p):
    """Resíduos normalizados pela incerteza: (modelo − dado)/σ."""
    xm, ym = trajetoria(p, t)
    return np.concatenate([(xm - x) / sigma, (ym - y) / sigma])


chute_inicial = [x[0], y[0], cx[0], cy[1], 0.005]
ajuste = least_squares(residuos, chute_inicial)
J = ajuste.jac
cov = np.linalg.inv(J.T @ J)                # matriz de covariância
graus = 2 * t.size - len(ajuste.x)
chi2_red = np.sum(ajuste.fun**2) / graus
incertezas = np.sqrt(np.diag(cov))

# %% [4] Do parâmetro b ao coeficiente de arrasto C_d
x0, y0, vx0, vy0, b = ajuste.x
u_b = incertezas[4]
A = np.pi * R**2
Cd = 2 * m * b / (rho_ar * A)
u_Cd = Cd * u_b / b
v0 = np.hypot(vx0, vy0)
theta = np.degrees(np.arctan2(vy0, vx0))
print(f"Arrasto: v0 = {v0:.2f} m/s, θ = {theta:.1f}°, "
      f"χ²_red = {chi2_red:.2f} ({graus} graus de liberdade)")
print(f"b = k/m = {fmt(b, u_b, '1/m')}  →  C_d = {fmt(Cd, u_Cd)}")
xm, ym = trajetoria(ajuste.x, t)

# %% [5] Figura: trajetória e resíduos dos dois modelos
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.9),
                             gridspec_kw={"width_ratios": [1.4, 1]})
a1.errorbar(x, y, xerr=sigma, yerr=sigma, fmt="o", ms=2.5, color="k",
            elinewidth=0.6, label="Tracker (30 quadros/s)")
a1.plot(np.polyval(cx, t), np.polyval(cy, t), "--", label="vácuo (parábola)")
a1.plot(xm, ym, "-", label=f"arrasto, $C_d$ = {Cd:.2f}".replace(".", ","))
a1.set_xlabel("$x$ (m)")
a1.set_ylabel("$y$ (m)")
a1.legend(loc="lower center")
a2.axhline(0, color="gray", lw=0.6)
a2.plot(t, 100 * res_y_vacuo, "s", ms=3, mfc="none", label="vácuo")
a2.plot(t, 100 * (y - ym), "o", ms=3, label="arrasto")
a2.set_xlabel("$t$ (s)")
a2.set_ylabel("resíduo em $y$ (cm)")
a2.legend()
for ax, letra in ((a1, "(a)"), (a2, "(b)")):
    ax.text(0.03, 0.92, letra, transform=ax.transAxes)
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap01_dados_chute")
