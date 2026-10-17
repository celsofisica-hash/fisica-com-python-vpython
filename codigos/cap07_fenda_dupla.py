"""
Capítulo 7 — Óptica física: o experimento de Young (fenda dupla).

Um laser ilumina duas fendas estreitas. No anteparo, a intensidade é o
produto do padrão de interferência de duas fontes (cos²) pelo padrão de
difração de cada fenda (sinc²). Controles permitem variar o comprimento
de onda, a separação e a largura das fendas.
"""
from vpython import *

# %% [1] Parâmetros do experimento (SI)
lam = 632.8e-9          # comprimento de onda do laser de He-Ne (m)
d = 0.25e-3             # distância entre os centros das fendas (m)
a = 0.05e-3             # largura de cada fenda (m)
D = 1.0                 # distância fendas–anteparo (m)
Y = 0.02                # metade da altura do anteparo mostrada (m)
N = 300                 # número de faixas no anteparo


# %% [2] Cor de um comprimento de onda visível (aproximação RGB)
def cor_do_comprimento(lam_nm):
    """Converte λ (nm) em uma cor RGB aproximada."""
    if 380 <= lam_nm < 440:
        r, g, b = (440 - lam_nm) / 60, 0, 1
    elif 440 <= lam_nm < 490:
        r, g, b = 0, (lam_nm - 440) / 50, 1
    elif 490 <= lam_nm < 510:
        r, g, b = 0, 1, (510 - lam_nm) / 20
    elif 510 <= lam_nm < 580:
        r, g, b = (lam_nm - 510) / 70, 1, 0
    elif 580 <= lam_nm < 645:
        r, g, b = 1, (645 - lam_nm) / 65, 0
    elif 645 <= lam_nm <= 780:
        r, g, b = 1, 0, 0
    else:
        r, g, b = 0, 0, 0
    return vector(r, g, b)


# %% [3] Intensidade no anteparo: interferência × difração
def intensidade(y):
    sen_theta = y / sqrt(y**2 + D**2)
    delta = pi * d * sen_theta / lam        # meia diferença de fase entre fendas
    beta = pi * a * sen_theta / lam         # parâmetro de difração de uma fenda
    envelope = 1.0 if abs(beta) < 1e-9 else (sin(beta) / beta)**2
    return cos(delta)**2 * envelope


# %% [4] Cena: laser, placa com as fendas e anteparo (geometria fora de escala)
scene.title = "Experimento de Young: interferência e difração\n"
scene.width, scene.height = 950, 420
scene.background = color.black
scene.center = vector(0, 0, 0)
scene.range = 9
scene.forward = vector(1, -0.2, -0.7)

laser = cylinder(pos=vector(-14, 0, 0), axis=vector(3, 0, 0), radius=0.4,
                 color=color.gray(0.5))
feixe = cylinder(pos=vector(-11, 0, 0), axis=vector(7, 0, 0), radius=0.3)
for y_placa, altura in ((2.85, 5), (-2.85, 5), (0, 0.4)):   # duas fendas
    box(pos=vector(-4, y_placa, 0), size=vector(0.1, altura, 3),
        color=color.gray(0.4))

altura_vis = 14                          # altura do anteparo na cena
faixas = []
for i in range(N):
    y_real = -Y + 2 * Y * (i + 0.5) / N
    faixa = box(pos=vector(8, altura_vis * y_real / (2 * Y), 0),
                size=vector(0.1, altura_vis / N, 6), emissive=True)
    faixa.y_real = y_real
    faixas.append(faixa)

g_I = graph(title="Intensidade relativa no anteparo", xtitle="y (mm)",
            ytitle="I / I0", width=950, height=250, ymin=0, ymax=1.05)
c_I = gcurve(graph=g_I, color=color.red)
c_env = gcurve(graph=g_I, color=color.gray(0.6))
painel = wtext(text="")


def atualizar():
    rgb = cor_do_comprimento(lam * 1e9)
    feixe.color = rgb
    for faixa in faixas:
        faixa.color = rgb * intensidade(faixa.y_real)
    c_I.delete()
    c_env.delete()
    c_I.color = rgb
    pts, env = [], []
    for i in range(1001):
        y = -Y + 2 * Y * i / 1000
        pts.append([1000 * y, intensidade(y)])
        beta = pi * a * y / (lam * sqrt(y**2 + D**2))
        env.append([1000 * y, 1.0 if abs(beta) < 1e-9 else (sin(beta) / beta)**2])
    c_I.plot(pts)
    c_env.plot(env)
    painel.text = (f"\nλ = {lam * 1e9:.0f} nm   d = {d * 1e3:.2f} mm   "
                   f"a = {a * 1e3:.3f} mm   →   interfranja λD/d = "
                   f"{1000 * lam * D / d:.2f} mm\n")


# %% [5] Controles deslizantes
def mudar_lam(s):
    global lam
    lam = s.value * 1e-9
    atualizar()


def mudar_d(s):
    global d
    d = s.value * 1e-3
    atualizar()


def mudar_a(s):
    global a
    a = s.value * 1e-3
    atualizar()


scene.append_to_caption("\nλ (nm):  ")
slider(min=400, max=700, value=lam * 1e9, step=1, length=350, bind=mudar_lam)
scene.append_to_caption("\nd (mm):  ")
slider(min=0.05, max=0.6, value=d * 1e3, step=0.01, length=350, bind=mudar_d)
scene.append_to_caption("\na (mm):  ")
slider(min=0.01, max=0.15, value=a * 1e3, step=0.005, length=350, bind=mudar_a)

atualizar()
while True:
    rate(30)
