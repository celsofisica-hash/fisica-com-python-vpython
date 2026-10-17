"""
Capítulo 2 — Da simulação ao dado real: uma semana de operação de uma PCH.

Com o registro horário de níveis, vazão e potência de uma pequena central
hidrelétrica, calculamos a potência hidráulica disponível, o rendimento
global da unidade em cada hora e ajustamos a curva de rendimento em função
da vazão. Também calculamos a energia gerada em cada dia.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura, datas e limpeza dos dados
dados = pd.read_csv(PASTA_DADOS / "cap02_pch_operacao.csv", comment="#",
                    parse_dates=["data_hora"], index_col="data_hora")
print(dados.describe().round(2))
print(f"Linhas com falha de telemetria: {dados.isna().any(axis=1).sum()}")
dados = dados.dropna()

# %% [2] Potência hidráulica disponível e rendimento global
rho, g = 1000.0, 9.81
dados["queda_m"] = dados["nivel_montante_m"] - dados["nivel_jusante_m"]
dados["P_hidr_MW"] = rho * g * dados["vazao_m3s"] * dados["queda_m"] / 1e6
dados["rendimento"] = dados["potencia_MW"] / dados["P_hidr_MW"]
print(dados[["vazao_m3s", "queda_m", "potencia_MW", "rendimento"]].head())


# %% [3] Curva de rendimento: ajuste de uma parábola em torno do máximo
def curva(Q, eta_max, Q_otimo, c):
    return eta_max - c * (Q - Q_otimo)**2


Q, eta = dados["vazao_m3s"].to_numpy(), dados["rendimento"].to_numpy()
p, cov = curve_fit(curva, Q, eta, p0=[0.9, 8, 0.003])
u = np.sqrt(np.diag(cov))
residuo = eta - curva(Q, *p)
print(f"η_max = {fmt(p[0], u[0])} na vazão {fmt(p[1], u[1], 'm³/s')}")
print(f"Desvio-padrão dos resíduos: {residuo.std(ddof=3):.4f}")

# %% [4] Energia gerada por dia (integração da potência no tempo)
energia_dia = dados["potencia_MW"].resample("D").mean() * 24   # MWh
print("Energia gerada por dia (MWh):")
print(energia_dia.round(1).to_string())
print(f"Total na semana: {energia_dia.sum():.0f} MWh; "
      f"fator de capacidade = {dados['potencia_MW'].mean() / 4.4:.0%} "
      "(potência nominal 4,4 MW)")

# %% [5] Figura: série temporal e curva de rendimento
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8),
                             gridspec_kw={"width_ratios": [1.5, 1]})
a1.plot(dados.index, dados["potencia_MW"], lw=1, label="potência (MW)")
a1b = a1.twinx()
a1b.plot(dados.index, dados["vazao_m3s"], lw=0.8, color="C1", alpha=0.7)
a1.set_ylabel("potência (MW)", color="C0")
a1b.set_ylabel("vazão (m³/s)", color="C1")
a1.set_xlabel("dia (julho de 2026)")
Qs = np.linspace(Q.min(), Q.max(), 200)
a2.plot(Q, 100 * eta, "o", ms=2.5, alpha=0.6, color="k", label="horas de operação")
a2.plot(Qs, 100 * curva(Qs, *p), "-", color="C1", label="ajuste parabólico")
a2.set_xlabel("vazão (m³/s)")
a2.set_ylabel("rendimento global (%)")
a2.legend(loc="lower right")
a1.text(0.02, 0.9, "(a)", transform=a1.transAxes)
a2.text(0.04, 0.9, "(b)", transform=a2.transAxes)
virgula_decimal(fig)
a1.xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())
a1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%d"))
a1.xaxis.set_minor_locator(plt.matplotlib.dates.HourLocator(byhour=[6, 12, 18]))
fig.tight_layout()
salvar(fig, "cap02_dados_pch")
