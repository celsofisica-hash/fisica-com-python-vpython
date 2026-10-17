"""
Capítulo 9 — Da simulação ao dado real: pesando Júpiter com suas luas.

Durante dois meses de observação, a posição de cada lua galileana foi medida
em relação ao centro de Júpiter. Como vemos as órbitas quase de perfil, a
elongação oscila como x(t) = a sen(2π t/T + φ). Para cada lua, um
periodograma sugere o período e um ajuste não linear fornece a e T. A 3ª lei
de Kepler, T² = 4π² a³/(G M), dá então a massa de Júpiter.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import lombscargle
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura das observações
dados = pd.read_csv(PASTA_DADOS / "cap09_luas_jupiter.csv", comment="#")
luas = ["Io", "Europa", "Ganimedes", "Calisto"]
print(f"{len(dados)} observações em {dados['t_dias'].max():.0f} dias")
print(dados[luas].count().rename("medidas válidas"))
G, R_J = 6.674e-11, 71492e3
u_x = 0.12                                   # incerteza de cada posição (R_J)


def orbita(t, a, T, fase):
    return a * np.sin(2 * np.pi * t / T + fase)


# %% [2] Periodograma de Lomb–Scargle: amostragem irregular não é problema
periodos_teste = np.linspace(1.2, 25, 20000)            # dias


def periodo_inicial(t, x):
    """Período (dias) do pico do periodograma de Lomb–Scargle."""
    potencia = lombscargle(t, x - x.mean(), 2 * np.pi / periodos_teste)
    return periodos_teste[np.argmax(potencia)]


# %% [3] Ajuste não linear de cada lua, partindo do período do periodograma
def ajustar(t, x, T_chute):
    """Testa várias fases iniciais e fica com o ajuste de menor χ²."""
    melhor = None
    for fase0 in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        try:
            p, cov = curve_fit(orbita, t, x, p0=[np.abs(x).max(), T_chute, fase0],
                               sigma=np.full(t.size, u_x), absolute_sigma=True)
        except RuntimeError:
            continue
        chi2 = np.sum(((x - orbita(t, *p)) / u_x)**2)
        if melhor is None or chi2 < melhor[2]:
            melhor = (p, cov, chi2)
    return melhor


resultados = {}
for lua in luas:
    ok = dados[lua].notna()
    t, x = dados.loc[ok, "t_dias"].to_numpy(), dados.loc[ok, lua].to_numpy()
    p, cov, chi2 = ajustar(t, x, periodo_inicial(t, x))
    a, T = abs(p[0]), p[1]
    u_a, u_T = np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])
    resultados[lua] = (a, u_a, T, u_T, chi2 / (t.size - 3), t, x, p)
    print(f"{lua:10s} T = {fmt(T, u_T, 'dias')}, a = {fmt(a, u_a, 'R_J')}, "
          f"χ²_red = {chi2 / (t.size - 3):.2f}")

# %% [4] A massa de Júpiter pela 3ª lei de Kepler
massas = []
for lua, (a, u_a, T, u_T, *_) in resultados.items():
    a_m, T_s = a * R_J, T * 86400
    M = 4 * np.pi**2 * a_m**3 / (G * T_s**2)
    u_M = M * np.hypot(3 * u_a / a, 2 * u_T / T)
    massas.append((M, u_M))
    print(f"{lua:10s} M_J = {fmt(M / 1e27, u_M / 1e27, '× 10²⁷ kg')}")
M_arr, u_arr = np.array(massas).T
pesos = 1 / u_arr**2
M_med = np.sum(pesos * M_arr) / pesos.sum()
u_med = 1 / np.sqrt(pesos.sum())
print(f"Média ponderada: M_J = {fmt(M_med / 1e27, u_med / 1e27, '× 10²⁷ kg')}")
a_arr = np.array([r[0] for r in resultados.values()])
T_arr = np.array([r[2] for r in resultados.values()])
incl = np.polyfit(np.log(a_arr), np.log(T_arr), 1)[0]
print(f"Inclinação de log T × log a: {incl:.3f} (Kepler: 1,5)")

# %% [5] Figura: elongações ajustadas e a 3ª lei
aplicar_estilo()
fig = plt.figure(figsize=(6.6, 3.6))
grade = fig.add_gridspec(4, 2, width_ratios=[1.7, 1], hspace=0.15, wspace=0.35)
ts = np.linspace(0, dados["t_dias"].max(), 3000)
for i, lua in enumerate(luas):
    ax = fig.add_subplot(grade[i, 0])
    a, u_a, T, u_T, chi, t, x, p = resultados[lua]
    ax.plot(ts, orbita(ts, *p), "-", lw=0.7, color=f"C{i}")
    ax.plot(t, x, "o", ms=2.5, color="k")
    ax.set_ylabel(lua, fontsize=8)
    ax.tick_params(labelsize=7)
    if i < 3:
        ax.tick_params(labelbottom=False)
ax.set_xlabel("$t$ (dias)")
axk = fig.add_subplot(grade[:, 1])
axk.loglog(a_arr, T_arr, "o", mfc="none")
aa = np.geomspace(4, 35, 50)
axk.loglog(aa, np.sqrt(4 * np.pi**2 * (aa * R_J)**3 / (G * M_med)) / 86400, "k-",
           lw=1, label="$T \\propto a^{3/2}$")
from matplotlib import ticker
axk.set_xticks([5, 10, 20, 30])
axk.set_yticks([1, 2, 5, 10, 20])
for eixo in (axk.xaxis, axk.yaxis):
    eixo.set_major_formatter(ticker.ScalarFormatter())
    eixo.set_minor_formatter(ticker.NullFormatter())
axk.set_xlabel("$a$ ($R_J$)")
axk.set_ylabel("$T$ (dias)")
axk.legend()
virgula_decimal(fig)
salvar(fig, "cap09_dados_jupiter")
