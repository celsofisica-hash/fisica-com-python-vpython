"""
Capítulo 6 — Ondulatória: da oscilação de uma massa à onda numa corda.

A corda de um violão é modelada como uma fileira de N contas ligadas
por trechos tensionados. Cada conta obedece à 2ª lei de Newton; o
conjunto exibe propagação de pulsos, reflexão com inversão de fase e,
quando excitado na frequência certa, ondas estacionárias (harmônicos).
"""
from vpython import *

# %% [1] Parâmetros da corda
L = 0.65                # comprimento vibrante (m) — corda de violão
mu = 0.005              # densidade linear (kg/m)
T = 60.0                # tração (N)
N = 80                  # número de trechos (N+1 contas, extremos incluídos)
dx = L / N
m = mu * dx             # massa de cada conta (kg)
v_onda = sqrt(T / mu)   # velocidade da onda (m/s)
f1 = v_onda / (2 * L)   # frequência fundamental (Hz)
gamma = 30.0            # amortecimento (1/s): perdas para o ar e o tampo
A_exc = 0.0005          # amplitude da excitação na extremidade (m)

dt = 0.2 * dx / v_onda  # passo bem abaixo do limite de estabilidade dx/v
passos_por_quadro = 15
print(f"v = {v_onda:.1f} m/s, f1 = {f1:.1f} Hz, dt = {dt:.2e} s")

# %% [2] Estado inicial e a cena (deslocamento y exagerado 20×)
y = [0.0] * (N + 1)
vy = [0.0] * (N + 1)
exagero = 20

scene.title = "Ondas numa corda: pulsos, reflexão e ondas estacionárias\n"
scene.width, scene.height = 900, 350
scene.background = color.white
scene.center = vector(L / 2, 0, 0)
scene.range = 0.2

corda = curve(pos=[vector(i * dx, 0, 0) for i in range(N + 1)],
              radius=0.003, color=color.blue)
box(pos=vector(L + 0.005, 0, 0), size=vector(0.01, 0.1, 0.05),
    color=color.gray(0.3))                      # rastilho (extremo fixo)
excitador = box(pos=vector(-0.005, 0, 0), size=vector(0.01, 0.02, 0.05),
                color=color.red)
info = label(pos=vector(L / 2, 0.15, 0), box=False, height=13)

g_meio = graph(title="Deslocamento do ponto x = L/4", xtitle="t (s)",
               ytitle="y (mm)", width=900, height=220, scroll=True,
               xmin=0, xmax=0.1)
c_meio = gcurve(graph=g_meio, color=color.blue)

# %% [3] Controles: pulso único ou excitação senoidal com frequência ajustável
modo = {"tipo": "pulso", "t0": 0.0, "f": f1}


def enviar_pulso(b):
    modo["tipo"], modo["t0"] = "pulso", t


def ligar_senoide(b):
    modo["tipo"] = "senoide"


def mudar_f(s):
    modo["f"] = s.value
    texto_f.text = f"  f = {s.value:6.1f} Hz  (f/f1 = {s.value / f1:4.2f})"


button(text="Enviar pulso", bind=enviar_pulso)
button(text="Excitação senoidal", bind=ligar_senoide)
scene.append_to_caption("\n\nFrequência da excitação: ")
slider(min=0.3 * f1, max=4.2 * f1, value=f1, step=0.5, length=500, bind=mudar_f)
texto_f = wtext(text=f"  f = {f1:6.1f} Hz  (f/f1 = 1.00)")
scene.append_to_caption("\n")


def y_extremo(t):
    """Movimento imposto à extremidade x = 0."""
    if modo["tipo"] == "pulso":
        largura = 0.1 * L / v_onda               # duração do pulso (s)
        return 4 * A_exc * exp(-((t - modo["t0"] - 3 * largura) / largura)**2)
    return A_exc * sin(2 * pi * modo["f"] * t)


# %% [4] A 2ª lei para cada conta e o laço temporal
t = 0.0
while True:
    rate(60)
    for _ in range(passos_por_quadro):
        y[0] = y_extremo(t)
        y[N] = 0.0                                # extremo fixo
        for i in range(1, N):
            F = (T / dx) * (y[i + 1] - 2 * y[i] + y[i - 1])   # força restauradora
            a = F / m - gamma * vy[i]
            vy[i] += a * dt                       # Euler-Cromer
        for i in range(1, N):
            y[i] += vy[i] * dt
        t += dt
    for i in range(N + 1):
        corda.modify(i, pos=vector(i * dx, exagero * y[i], 0))
    excitador.pos = vector(-0.005, exagero * y[0], 0)
    info.text = f"t = {1000 * t:7.1f} ms   v = {v_onda:.0f} m/s   f1 = {f1:.1f} Hz"
    c_meio.plot(t, 1000 * y[N // 4])
