"""
Gera os conjuntos de dados "experimentais" usados nas seções
"Da simulação ao dado real" do livro.

Os dados são SINTÉTICOS: produzidos por modelos físicos com valores
verdadeiros conhecidos, aos quais se somam as imperfeições típicas de uma
medida real (ruído, resolução finita do instrumento, deriva, desvios
sistemáticos, pontos perdidos). Assim o leitor pode verificar se o método
de análise recupera o valor verdadeiro — e entender por que, às vezes, não
recupera. Os valores verdadeiros estão listados no Apêndice do livro.

Uso:  python gerar_dados_sinteticos.py      (grava os arquivos em ../dados)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.io import wavfile

PASTA = Path(__file__).resolve().parent.parent / "dados"
PASTA.mkdir(exist_ok=True)
rng = np.random.default_rng(2026)        # semente fixa: dados reprodutíveis
g = 9.81


def gravar_csv(df, nome, cabecalho):
    """Grava CSV com linhas de comentário (#) descrevendo o experimento."""
    caminho = PASTA / nome
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        for linha in cabecalho.strip().splitlines():
            f.write(f"# {linha.strip()}\n")
        df.to_csv(f, index=False, float_format="%.6g")
    print(f"{nome}: {len(df)} linhas")


# %% [1] Capítulo 1 — videoanálise de um chute (Tracker)
def dados_chute():
    m, R, rho, Cd = 0.43, 0.11, 1.18, 0.24         # valores verdadeiros
    k = 0.5 * rho * Cd * np.pi * R**2
    v0, th = 18.0, np.radians(35.0)

    def f(t, s):
        x, y, vx, vy = s
        v = np.hypot(vx, vy)
        return [vx, vy, -k / m * v * vx, -g - k / m * v * vy]

    def chao(t, s):
        return s[1] - R
    chao.terminal, chao.direction = True, -1
    sol = solve_ivp(f, (0, 5), [0, R, v0 * np.cos(th), v0 * np.sin(th)],
                    events=chao, dense_output=True, rtol=1e-10, atol=1e-10)
    t = np.arange(0, sol.t_events[0][0], 1 / 30)           # 30 quadros/s
    x, y = sol.sol(t)[:2]
    sigma = 0.015                                          # erro de marcação (m)
    df = pd.DataFrame({"t_s": np.round(t, 4),
                       "x_m": np.round(x + rng.normal(0, sigma, t.size), 3),
                       "y_m": np.round(y + rng.normal(0, sigma, t.size), 3)})
    gravar_csv(df, "cap01_chute_tracker.csv", """
        Videoanálise (Tracker) de um chute de bola de futebol — dados simulados
        Câmera a 30 quadros/s, perpendicular ao plano do movimento, a 25 m
        Calibração: trena de 10,00 m no quadro; incerteza de marcação ~1,5 cm
        Bola: massa 430 g, raio 11,0 cm; ar a 25 °C (densidade 1,18 kg/m³)""")


# %% [2] Capítulo 2 — operação de uma pequena central hidrelétrica (PCH)
def dados_pch():
    horas = pd.date_range("2026-07-06 00:00", periods=24 * 7, freq="h")
    h = horas.hour.to_numpy() + horas.minute.to_numpy() / 60
    fim_de_semana = horas.dayofweek.to_numpy() >= 5
    # despacho: carga baixa de madrugada, pico no fim da tarde
    Q = 6.0 + 2.5 * np.sin(2 * np.pi * (h - 11) / 24) \
        + 1.5 * np.exp(-((h - 19) / 1.5)**2)
    Q = Q - 1.2 * fim_de_semana + rng.normal(0, 0.35, h.size)
    Q = np.clip(Q, 2.5, 10.0)
    dias = np.arange(h.size) / 24
    montante = 612.0 + 0.35 * np.sin(2 * np.pi * dias / 7) \
        - 0.03 * (Q - 6) + rng.normal(0, 0.01, h.size)
    jusante = 560.0 + 0.04 * Q + rng.normal(0, 0.01, h.size)
    H_bruta = montante - jusante
    H_liq = H_bruta - 0.020 * Q**2                    # perda de carga no conduto
    eta = 0.905 - 0.35 * (Q / 10 - 0.85)**2           # curva da turbina Francis
    P = 1000 * g * Q * H_liq * eta / 1e6              # MW
    df = pd.DataFrame({
        "data_hora": horas.strftime("%Y-%m-%d %H:%M"),
        "nivel_montante_m": np.round(montante + rng.normal(0, 0.02, h.size), 2),
        "nivel_jusante_m": np.round(jusante + rng.normal(0, 0.02, h.size), 2),
        "vazao_m3s": np.round(Q * (1 + rng.normal(0, 0.01, h.size)), 2),
        "potencia_MW": np.round(P * (1 + rng.normal(0, 0.003, h.size)), 3)})
    falhas = rng.choice(h.size, 5, replace=False)     # falhas de telemetria
    df.loc[falhas, "vazao_m3s"] = np.nan
    gravar_csv(df, "cap02_pch_operacao.csv", """
        Registro horário de operação de uma PCH (uma unidade Francis) — dados simulados
        Níveis em metros acima do nível do mar; vazão turbinada pelo medidor ultrassônico
        Potência ativa nos terminais do gerador; células vazias = falha de telemetria""")


# %% [3] Capítulo 3 — ensaio de flexão de uma régua de alumínio
def dados_flexao():
    E, L, b, hh = 69.0e9, 0.400, 25.40e-3, 2.980e-3     # valores verdadeiros
    I = b * hh**3 / 12
    massas = np.r_[np.arange(0, 601, 50), np.arange(550, -1, -50)]
    sentido = ["carga"] * 13 + ["descarga"] * 12
    P = massas * 1e-3 * g * (1 + rng.normal(0, 2e-4, massas.size))
    y = P * L**3 / (48 * E * I) * 1e3                    # mm
    y = y + rng.normal(0, 0.006, y.size)
    df = pd.DataFrame({"massa_g": massas, "sentido": sentido,
                       "flecha_mm": np.round(y, 2)})     # relógio de 0,01 mm
    gravar_csv(df, "cap03_flexao_regua.csv", """
        Ensaio de flexão em três pontos de uma régua de alumínio — dados simulados
        Distância entre os cutelos: L = 400,0 mm (trena, incerteza 0,5 mm)
        Massas aferidas (tolerância 0,1 g) penduradas no meio do vão
        Flecha lida em relógio comparador de resolução 0,01 mm""")
    dim = pd.DataFrame({
        "medida": np.arange(1, 6),
        "largura_b_mm": np.round(b * 1e3 + rng.normal(0, 0.02, 5), 2),
        "espessura_h_mm": np.round(hh * 1e3 + rng.normal(0, 0.008, 5), 3)})
    gravar_csv(dim, "cap03_dimensoes_regua.csv", """
        Dimensões da seção da régua em cinco pontos — dados simulados
        Largura com paquímetro (resolução 0,02 mm); espessura com micrômetro (0,001 mm)""")


# %% [4] Capítulo 4 — esvaziamento de uma garrafa PET
def dados_garrafa():
    D, d, Cd, h0 = 0.0900, 0.0040, 0.62, 0.200
    A, a = np.pi * D**2 / 4, np.pi * d**2 / 4

    def dhdt(t, s):
        h = max(s[0], 0)
        cd = Cd if h > 0.02 else Cd * (0.45 + 0.55 * h / 0.02)  # gotejamento
        return [-cd * a / A * np.sqrt(2 * g * h)]

    def vazio(t, s):
        return s[0] - 0.004
    vazio.terminal = True
    sol = solve_ivp(dhdt, (0, 600), [h0], events=vazio, dense_output=True,
                    max_step=0.5)
    t = np.arange(0, sol.t_events[0][0], 5.0)
    h = sol.sol(t)[0] * 1e3 + rng.normal(0, 0.8, t.size)
    df = pd.DataFrame({"t_s": t, "h_mm": np.round(h).astype(int)})
    gravar_csv(df, "cap04_garrafa_pet.csv", """
        Esvaziamento de uma garrafa PET por um furo lateral — dados simulados
        Diâmetro interno da garrafa (parte cilíndrica): 90,0 mm (paquímetro)
        Furo feito com broca de 4,0 mm; diâmetro medido 4,0 ± 0,1 mm
        Altura da água acima do centro do furo, lida no vídeo (régua milimetrada)""")


# %% [5] Capítulo 5 — barra de alumínio aquecida numa ponta (aleta)
def dados_aleta():
    k, rho, c = 167.0, 2700.0, 896.0                 # alumínio 6061
    D, L, h_conv, T_amb = 6.35e-3, 0.300, 12.0, 24.0
    alfa = k / (rho * c)
    m2 = 4 * h_conv / (k * D)
    N, dt = 60, 0.05
    dx = L / N
    Fo = alfa * dt / dx**2
    Bi = h_conv * dx / k
    T = np.full(N + 1, T_amb)
    x_sens = np.arange(0, 0.29, 0.04)
    idx = np.round(x_sens / dx).astype(int)
    desvio = rng.normal(0, 0.15, idx.size)           # erro sistemático de cada sensor
    linhas, t = [], 0.0
    passos_por_leitura = int(10 / dt)
    for leitura in range(271):                       # 45 min, leitura a cada 10 s
        T_base = T_amb + 56 * (1 - np.exp(-t / 90))
        if leitura > 0:
            for _ in range(passos_por_leitura):
                Tn = T.copy()
                Tn[1:-1] = (T[1:-1] + Fo * (T[2:] - 2 * T[1:-1] + T[:-2])
                            - alfa * dt * m2 * (T[1:-1] - T_amb))
                Tn[-1] = (T[-1] + 2 * Fo * (T[-2] - T[-1] - Bi * (T[-1] - T_amb))
                          - alfa * dt * m2 * (T[-1] - T_amb))
                t += dt
                Tn[0] = T_amb + 56 * (1 - np.exp(-t / 90))
                T = Tn
        else:
            T[0] = T_base
        leit = T[idx] + desvio + rng.normal(0, 0.04, idx.size)
        leit = np.round(leit / 0.0625) * 0.0625      # resolução do DS18B20
        amb = np.round((T_amb + rng.normal(0, 0.08)) / 0.0625) * 0.0625
        linhas.append([round(t)] + list(leit) + [amb])
    nomes = ["t_s"] + [f"T_{int(round(x * 100)):02d}cm" for x in x_sens] + ["T_ar"]
    df = pd.DataFrame(linhas, columns=nomes)
    gravar_csv(df, "cap05_barra_aquecida.csv", """
        Barra cilíndrica de alumínio 6061 (diâmetro 6,35 mm, comprimento 300 mm)
        aquecida numa ponta por um resistor de potência — dados simulados
        Sensores DS18B20 colados a cada 4 cm (resolução 0,0625 °C); leitura a cada 10 s
        T_ar: sensor no ar, longe da barra. Ponta livre exposta ao ar""")


# %% [6] Capítulo 6 — gravação do som da corda mi grave de um violão
def dados_violao():
    taxa, dur = 44100, 2.5
    t = np.arange(int(taxa * dur)) / taxa
    f1, B, beta = 81.60, 1.5e-4, 0.20               # f1 verdadeira, inarmonicidade
    sinal = np.zeros_like(t)
    for n in range(1, 25):
        # cada harmônico desvia um pouco do ideal (acoplamento com o tampo)
        fn = n * f1 * np.sqrt(1 + B * n**2) * (1 + rng.normal(0, 3e-4))
        amp = abs(np.sin(n * np.pi * beta)) / n**1.1   # dedilhado a L/5 do rastilho
        tau = 2.2 / n**0.6
        # a afinação cai um pouco enquanto a amplitude decai (tração dinâmica)
        fase = 2 * np.pi * fn * (t - 0.0015 * 0.4 * np.expm1(-t / 0.4))
        sinal += amp * np.exp(-t / tau) * np.sin(fase + rng.uniform(0, 2 * np.pi))
    sinal *= 1 - np.exp(-t / 0.004)                 # ataque da palheta
    sinal += 0.004 * np.sin(2 * np.pi * 60 * t)     # zumbido da rede elétrica
    sinal += rng.normal(0, 0.003, t.size)           # ruído da sala
    sinal = sinal / np.max(np.abs(sinal)) * 0.8
    wavfile.write(PASTA / "cap06_violao_mi_grave.wav", taxa,
                  (sinal * 32767).astype(np.int16))
    print("cap06_violao_mi_grave.wav: 2,5 s, 44,1 kHz")


# %% [7] Capítulo 7 — perfil das franjas de Young medido com fotodiodo
def dados_young():
    lam, D, d, a = 632.8e-9, 1.000, 0.247e-3, 0.0493e-3
    I0, fundo, yc = 2.10, 0.015, 0.31e-3
    y = np.arange(-15.0, 15.0001, 0.1) * 1e-3
    s = (y - yc) / np.hypot(y - yc, D)
    beta = np.pi * a * s / lam
    I = I0 * np.cos(np.pi * d * s / lam)**2 * np.sinc(beta / np.pi)**2
    deriva = 1 - 0.02 * (y - y[0]) / (y[-1] - y[0])   # laser perde 2% no ensaio
    V = fundo + I * deriva
    V = V * (1 + rng.normal(0, 0.015, y.size)) + rng.normal(0, 0.002, y.size)
    df = pd.DataFrame({"y_mm": np.round(y * 1e3, 2), "V_V": np.round(V, 4)})
    gravar_csv(df, "cap07_young_fotodiodo.csv", """
        Perfil de intensidade da fenda dupla — dados simulados
        Laser He-Ne (632,8 nm); fendas comerciais: d = 0,25 mm e a = 0,05 mm (nominais)
        Distância fendas–detector: D = 1,000 m (trena, 2 mm)
        Fotodiodo com fenda de 0,1 mm num transladador; tensão no amplificador (V)""")


# %% [8] Capítulo 8 — tensão de um gerador de bancada no osciloscópio
def dados_gerador():
    NBA = 0.0125                                    # Wb (verdadeiro)
    linhas = []
    for rpm in (600, 1200, 1800, 2400, 3000, 3600):
        rpm_real = rpm * (1 + rng.normal(0, 0.02))
        f = rpm_real / 60
        w = 2 * np.pi * f
        t = np.linspace(0, 4 / (rpm / 60), 1000)     # 4 períodos nominais
        fase = rng.uniform(0, 2 * np.pi)
        V = NBA * w * (np.sin(w * t + fase) + 0.06 * np.sin(3 * (w * t + fase))
                       + 0.02 * np.sin(5 * (w * t + fase)))
        escala = min(e for e in (0.1, 0.2, 0.5, 1, 2, 5) if 4 * e > 1.3 * NBA * w)
        V = V + rng.normal(0, 0.004 * 8 * escala, t.size)
        passo = 8 * escala / 256                      # osciloscópio de 8 bits
        V = np.round(V / passo) * passo
        linhas += [(rpm, ti, vi) for ti, vi in zip(t, V)]
    df = pd.DataFrame(linhas, columns=["rpm_nominal", "t_s", "V_V"])
    gravar_csv(df, "cap08_gerador_osciloscopio.csv", """
        Tensão em circuito aberto de um gerador de bancada (bobina girando entre ímãs)
        Rotação ajustada pelo controlador do motor (valor nominal) — dados simulados
        Osciloscópio digital de 8 bits; 1000 pontos por aquisição""")


# %% [9] Capítulo 9 — elongações das luas galileanas de Júpiter
def dados_jupiter():
    luas = {"Io": (5.898, 1.769138), "Europa": (9.386, 3.551181),
            "Ganimedes": (14.97, 7.154553), "Calisto": (26.33, 16.689018)}
    fases = rng.uniform(0, 1, 4)
    linhas = []
    inicio = pd.Timestamp("2027-01-10 02:00")       # 23 h, horário de Brasília
    for noite in range(70):
        if rng.random() < 0.40:                     # noite nublada
            continue
        for extra in ([0.0, 2.0] if rng.random() < 0.3 else [0.0]):
            instante = inicio + pd.Timedelta(days=noite,
                                             hours=extra + rng.uniform(-0.5, 0.5))
            tdias = (instante - inicio).total_seconds() / 86400
            linha = [instante.strftime("%Y-%m-%d %H:%M"), round(tdias, 4)]
            for (a, T), ph in zip(luas.values(), fases):
                x = a * np.sin(2 * np.pi * (tdias / T + ph))
                linha.append("" if abs(x) < 1.1 else round(x + rng.normal(0, 0.12), 2))
            linhas.append(linha)
    df = pd.DataFrame(linhas, columns=["data_hora_UT", "t_dias"] + list(luas))
    gravar_csv(df, "cap09_luas_jupiter.csv", """
        Elongações das luas galileanas, em raios de Júpiter (R_J = 71 492 km), positivas a leste
        Telescópio de 150 mm com webcam; posição medida nas imagens — dados simulados
        Campo vazio: lua escondida atrás ou na frente do disco do planeta""")


# %% [10] Capítulo 10 — curvas I–V de LEDs para medir a constante de Planck
def dados_leds():
    h, c, e = 6.62607015e-34, 2.99792458e8, 1.602176634e-19
    leds = {  # nome: (lambda_pico nm, largura nm, desvio da tensão de joelho V)
        "infravermelho": (940, 45, -0.05), "vermelho": (630, 18, -0.06),
        "ambar": (591, 16, -0.05), "amarelo-verde": (568, 20, 0.00),
        "verde-InGaN": (523, 32, 0.30), "azul": (468, 25, 0.12),
        "violeta": (405, 14, 0.08)}
    espectros, iv = [], []
    for nome, (lam, larg, desvio) in leds.items():
        V0 = h * c / (e * lam * 1e-9) + desvio
        Rs, nVt = rng.uniform(12, 20), rng.uniform(0.05, 0.08)
        lam_med = lam + rng.normal(0, 1.5)
        espectros.append([nome, round(lam_med, 1), larg])
        for V in np.arange(0, 4.0, 0.01):
            I = nVt / Rs * np.logaddexp(0, (V - V0) / nVt) * 1e3   # mA
            I = I + rng.normal(0, 0.01)
            if I > 30:
                break
            iv.append([nome, round(V, 3), round(max(I, 0), 3)])
    gravar_csv(pd.DataFrame(espectros, columns=["led", "lambda_pico_nm",
                                                "largura_nm"]),
               "cap10_leds_espectros.csv", """
        Comprimento de onda de pico e largura a meia altura de cada LED
        Medidos com espectrômetro de fibra óptica (resolução 1,5 nm) — dados simulados""")
    gravar_csv(pd.DataFrame(iv, columns=["led", "V_V", "I_mA"]),
               "cap10_leds_iv.csv", """
        Curvas corrente–tensão de sete LEDs (fonte de tensão + multímetro) — dados simulados
        Tensão em passos de 10 mV; medida interrompida ao atingir 30 mA""")


# %% [11] Gera tudo
if __name__ == "__main__":
    dados_chute()
    dados_pch()
    dados_flexao()
    dados_garrafa()
    dados_aleta()
    dados_violao()
    dados_young()
    dados_gerador()
    dados_jupiter()
    dados_leds()
