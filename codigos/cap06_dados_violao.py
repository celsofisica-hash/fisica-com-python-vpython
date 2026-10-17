"""
Capítulo 6 — Da simulação ao dado real: o espectro de uma corda de violão.

Uma gravação da corda mi grave é analisada pela transformada de Fourier.
Localizamos os picos dos harmônicos, ajustamos a relação f_n = n f1 √(1 + B n²)
(a corda real é ligeiramente inarmônica por causa da rigidez do aço) e,
com a densidade linear medida, calculamos a tração. Também verificamos se
a corda está afinada.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.optimize import curve_fit
from estilo import aplicar_estilo, virgula_decimal, salvar, fmt, PASTA_DADOS

# %% [1] Leitura do arquivo de áudio
taxa, som = wavfile.read(PASTA_DADOS / "cap06_violao_mi_grave.wav")
som = som.astype(float) / 32768
print(f"{som.size} amostras a {taxa} Hz = {som.size / taxa:.2f} s")
L_corda, mu = 0.650, 6.2e-3          # comprimento vibrante (m), densidade (kg/m)

# %% [2] Espectro: janela de Hann sobre 1,5 s a partir de 0,1 s
inicio, duracao = int(0.1 * taxa), int(1.5 * taxa)
trecho = som[inicio:inicio + duracao] * np.hanning(duracao)
espectro = np.abs(np.fft.rfft(trecho, n=8 * duracao))     # zero-padding
freq = np.fft.rfftfreq(8 * duracao, 1 / taxa)
dB = 20 * np.log10(espectro / espectro.max())


# %% [3] Localização fina dos picos (interpolação parabólica em dB)
def pico_perto(f_alvo, janela=6.0):
    sel = np.where(np.abs(freq - f_alvo) < janela)[0]
    i = sel[np.argmax(espectro[sel])]
    y0, y1, y2 = dB[i - 1], dB[i], dB[i + 1]
    desloc = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return freq[i] + desloc * (freq[1] - freq[0]), y1


f1_aprox, _ = pico_perto(82.4, janela=10)
harmonicos = []
for n in range(1, 21):
    fn, nivel = pico_perto(n * f1_aprox * (1 + 1.5e-4 * n**2) ** 0.5, janela=15)
    if nivel > -55:                     # ignora harmônicos apagados no ruído
        harmonicos.append((n, fn, nivel))
n_arr, fn_arr, nivel_arr = map(np.array, zip(*harmonicos))
print("Harmônicos ausentes:", sorted(set(range(1, 21)) - set(n_arr)))


# %% [4] Ajuste da inarmonicidade e cálculo da tração
def modelo(n, f1, B):
    return n * f1 * np.sqrt(1 + B * n**2)


p, cov = curve_fit(modelo, n_arr, fn_arr, p0=[f1_aprox, 1e-4])
f1, B = p
u_f1, u_B = np.sqrt(np.diag(cov))
T = 4 * L_corda**2 * f1**2 * mu
cents = 1200 * np.log2(f1 / 82.41)
print(f"f1 = {fmt(f1, u_f1, 'Hz')}, B = {fmt(B * 1e4, u_B * 1e4)} × 10⁻⁴")
print(f"Tração: {T:.1f} N; desafinação: {cents:+.1f} cents em relação a 82,41 Hz")
print(f"Para afinar: aumentar a tração em {100 * ((82.41 / f1)**2 - 1):.1f} %")

# %% [5] Figura: espectro e inarmonicidade
aplicar_estilo()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8),
                             gridspec_kw={"width_ratios": [1.6, 1]})
a1.plot(freq, dB, lw=0.6, color="C0")
a1.plot(fn_arr, nivel_arr, "v", color="C1", ms=4)
for n in (1, 5, 10):
    a1.annotate(f"$n$={n}", (n * f1, -8 if n == 1 else -62), ha="center", fontsize=7)
a1.set_xlim(0, 1700)
a1.set_ylim(-80, 5)
a1.set_xlabel("frequência (Hz)")
a1.set_ylabel("nível (dB)")
a2.plot(n_arr, fn_arr / n_arr, "o", mfc="none", label="picos medidos")
ns = np.linspace(1, 20, 100)
a2.plot(ns, modelo(ns, *p) / ns, "k-", lw=1, label=r"$f_1\sqrt{1+Bn^2}$")
a2.set_xlabel("harmônico $n$")
a2.set_ylabel("$f_n/n$ (Hz)")
a2.legend()
virgula_decimal(fig)
fig.tight_layout()
salvar(fig, "cap06_dados_violao")
