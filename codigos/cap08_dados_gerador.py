"""
Capítulo 8 — Da simulação ao dado real: a lei de Faraday no osciloscópio.

Para seis rotações de um gerador de bancada, o osciloscópio registra a
tensão em circuito aberto. Ajustamos uma senoide a cada aquisição (obtendo
frequência e amplitude reais) e verificamos que a amplitude cresce
linearmente com ω, como prevê ε_max = N B A ω. A inclinação é o fluxo N B A.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura: todas as aquisições num único arquivo "longo"
dados = pd.read_csv(PASTA_DADOS / "cap08_gerador_osciloscopio.csv", comment="#")
print(dados.groupby("rpm_nominal")["V_V"].agg(["count", "min", "max"]))


# %% [2] Ajuste de uma senoide a cada aquisição
def senoide(t, A, f, fase, c):
    return A * np.sin(2 * np.pi * f * t + fase) + c


resultados, parametros = [], {}
for rpm, grupo in dados.groupby("rpm_nominal"):
    t, V = grupo["t_s"].to_numpy(), grupo["V_V"].to_numpy()
    # chute inicial: com f fixa na nominal, o modelo S sen ωt + C cos ωt + c
    # é linear nos parâmetros e se resolve por mínimos quadrados lineares
    f0 = rpm / 60
    M = np.column_stack([np.sin(2 * np.pi * f0 * t), np.cos(2 * np.pi * f0 * t),
                         np.ones_like(t)])
    S, C, c0 = np.linalg.lstsq(M, V, rcond=None)[0]
    p, cov = curve_fit(senoide, t, V, p0=[np.hypot(S, C), f0, np.arctan2(C, S), c0])
    A, f = abs(p[0]), p[1]
    u_A, u_f = np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])
    rms_res = np.std(V - senoide(t, *p))
    resultados.append((rpm, f, u_f, A, u_A, rms_res))
    parametros[rpm] = p
tab = pd.DataFrame(resultados, columns=["rpm_nominal", "f_Hz", "u_f", "A_V", "u_A",
                                        "res_rms_V"])
tab["omega"] = 2 * np.pi * tab["f_Hz"]
tab["rpm_real"] = 60 * tab["f_Hz"]
print(tab[["rpm_nominal", "rpm_real", "A_V", "u_A", "res_rms_V"]].round(4))

# %% [3] Amplitude × ω: a reta de Faraday
coef, cov = np.polyfit(tab["omega"], tab["A_V"], 1, cov=True)
NBA, u_NBA = coef[0], np.sqrt(cov[0, 0])
print(f"N B A = {fmt(NBA * 1e3, u_NBA * 1e3, 'mWb')}; "
      f"intercepto = {coef[1] * 1e3:.0f} ± {np.sqrt(cov[1, 1]) * 1e3:.0f} mV")
print("Resíduos do ajuste senoidal relativos à amplitude: "
      f"{100 * (tab['res_rms_V'] / tab['A_V']).mean():.1f} % (harmônicos!)")

# %% [4] Figura: uma aquisição e a reta A(ω)
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
g = dados[dados["rpm_nominal"] == 1800]
p_ex = parametros[1800]
a1.plot(g["t_s"] * 1e3, g["V_V"], ".", ms=1.5, color="k", label="osciloscópio")
a1.plot(g["t_s"] * 1e3, senoide(g["t_s"], *p_ex), "-", color="C1", lw=1,
        label="senoide ajustada")
a1.set_xlabel("$t$ (ms)")
a1.set_ylabel("$\\varepsilon$ (V)")
a1.set_title("1800 rpm (nominal): pontos e senoide ajustada", fontsize=8)
ws = np.linspace(0, tab["omega"].max() * 1.05, 50)
a2.errorbar(tab["omega"], tab["A_V"], yerr=tab["u_A"], fmt="o", mfc="none")
a2.plot(ws, np.polyval(coef, ws), "k-", lw=1,
        label=f"$NBA$ = {NBA * 1e3:.2f} mWb".replace(".", ","))
a2.set_xlabel("$\\omega$ (rad/s)")
a2.set_ylabel("$\\varepsilon_{\\max}$ (V)")
a2.legend()
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap08_dados_gerador")
