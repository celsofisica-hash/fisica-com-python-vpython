"""
Capítulo 8 — Transmissão de energia elétrica: por que alta tensão?

Uma usina entrega a potência P a uma cidade distante através de uma linha
de resistência R. Para P fixa, a corrente é I = P/V e a perda por efeito
Joule é P_perda = R I² = R P²/V². Um controle deslizante muda a tensão de
transmissão; as cargas na linha andam com velocidade proporcional a I e
o cabo "esquenta" conforme a fração perdida.
"""
from vpython import *

# %% [1] Parâmetros da linha (valores típicos, ordem de grandeza)
P = 1000e6              # potência transmitida (W)
comprimento = 800e3     # distância usina–cidade (m)
rho_Al = 2.8e-8         # resistividade do alumínio (Ω·m)
A_cabo = 2.0e-3         # seção condutora total por fase/polo (m²)
R = 2 * rho_Al * comprimento / A_cabo     # ida e volta (Ω)
V = 500e3               # tensão de transmissão inicial (V)


def perdas(V):
    I = P / V
    return I, R * I**2


# %% [2] Gráfico: fração perdida em função da tensão
g = graph(title="Perdas por efeito Joule numa linha de 800 km",
          xtitle="tensão de transmissão (kV)", ytitle="perda (% de P)",
          width=800, height=280, ymin=0, ymax=60)
c_perda = gcurve(graph=g, color=color.red)
for kV in range(200, 1001, 10):
    c_perda.plot(kV, 100 * perdas(kV * 1e3)[1] / P)
padroes = gdots(graph=g, color=color.blue, radius=4, label="tensões usuais")
for kV in (230, 345, 440, 500, 600, 765):
    padroes.plot(kV, 100 * perdas(kV * 1e3)[1] / P)

# %% [3] Cena: usina, torres, cabo e cidade
scene.title = "Transmissão de energia: a mesma potência, tensões diferentes\n"
scene.width, scene.height = 900, 380
scene.background = color.white
scene.center = vector(0, 6, 0)
scene.range = 22

box(pos=vector(0, -0.5, 0), size=vector(90, 1, 20), color=color.green)
box(pos=vector(-38, 4, 0), size=vector(8, 8, 8), color=color.gray(0.5))
label(pos=vector(-38, 10, 0), text="usina + transformador elevador", box=False,
      height=11)
for i in range(6):
    box(pos=vector(30 + 2.2 * (i % 3), 2 + i // 3 * 2, 2 * (i % 2)),
        size=vector(1.8, 4 + i // 3 * 4, 1.8), color=color.gray(0.7))
label(pos=vector(32, 12, 0), text="cidade", box=False, height=11)

x_torres = [-30, -15, 0, 15, 28]
for x in x_torres:
    cylinder(pos=vector(x, 0, 0), axis=vector(0, 12, 0), radius=0.25,
             color=color.gray(0.3))
    box(pos=vector(x, 11.5, 0), size=vector(0.4, 0.4, 4), color=color.gray(0.3))

# O cabo pende entre as torres como uma parábola (aproximação da catenária).
pontos_cabo = []
for x0, x1 in zip(x_torres[:-1], x_torres[1:]):
    for j in range(21):
        x = x0 + (x1 - x0) * j / 20
        flecha = 1.5 * 4 * (j / 20) * (1 - j / 20)
        pontos_cabo.append(vector(x, 11.5 - flecha, 1.5))
cabo = curve(pos=pontos_cabo, radius=0.15)
cargas = [sphere(radius=0.3, color=color.blue) for _ in range(20)]
posicoes = [k * len(pontos_cabo) / 20 for k in range(20)]
painel = label(pos=vector(0, 18, 0), box=True, height=13)


def no_cabo(s):
    """Ponto do cabo para um índice fracionário s (interpolação linear)."""
    s = s % (len(pontos_cabo) - 1)
    i = int(s)
    return pontos_cabo[i] + (s - i) * (pontos_cabo[i + 1] - pontos_cabo[i])


# %% [4] Controle de tensão e laço da animação
def mudar_V(s):
    global V
    V = s.value * 1e3


scene.append_to_caption("\nTensão de transmissão (kV): ")
slider(min=100, max=800, value=V / 1e3, step=5, length=450, bind=mudar_V)
scene.append_to_caption("\n")

while True:
    rate(60)
    I, P_perda = perdas(V)
    fracao = min(P_perda / P, 1)
    cabo.color = vector(0.3 + 0.7 * fracao, 0.3, 0.3 * (1 - fracao))
    for k, q in enumerate(cargas):
        posicoes[k] += I / 4000             # velocidade visual ∝ corrente
        q.pos = no_cabo(posicoes[k])
    entregue = max(P - P_perda, 0)
    painel.text = (f"V = {V / 1e3:.0f} kV   I = {I:.0f} A   "
                   f"perda = {P_perda / 1e6:.0f} MW ({100 * fracao:.1f}%)   "
                   f"entregue = {entregue / 1e6:.0f} MW")
