"""
Capítulo 10 — Dualidade onda–partícula: elétrons, um de cada vez, na fenda dupla.

Cada elétron chega ao detector como um ponto (partícula), mas o lugar do
impacto é sorteado com a densidade de probabilidade |ψ|² do padrão de
interferência de uma onda de comprimento λ = h/p (de Broglie). Com muitos
elétrons as franjas surgem. Ligando o "detector de caminho" nas fendas,
a interferência desaparece (complementaridade de Bohr).
"""
from vpython import *
from random import random, uniform

# %% [1] Comprimento de onda de de Broglie do elétron
h = 6.62607015e-34
m_e = 9.1093837e-31
q_e = 1.602176634e-19
c = 2.99792458e8
V_ac = 50e3             # tensão de aceleração (V), como em microscópios eletrônicos

p_classico = sqrt(2 * m_e * q_e * V_ac)
p_relat = sqrt(2 * m_e * q_e * V_ac * (1 + q_e * V_ac / (2 * m_e * c**2)))
lam = h / p_relat
print(f"λ de de Broglie: {lam * 1e12:.2f} pm (sem correção relativística: "
      f"{h / p_classico * 1e12:.2f} pm)")

d = 1.0e-6              # separação entre as fendas (m)
a = 0.2e-6              # largura de cada fenda (m)
D = 1.0                 # distância até o detector (m)
Y = 40e-6               # meia largura do detector considerada (m)
print(f"Distância entre franjas λD/d = {lam * D / d * 1e6:.2f} μm")


# %% [2] Densidade de probabilidade e sorteio por rejeição
def prob(y, com_detector):
    beta = pi * a * y / (lam * D)
    envelope = 1.0 if abs(beta) < 1e-12 else (sin(beta) / beta)**2
    if com_detector:                     # sabemos a fenda: somam-se |ψ1|² + |ψ2|²
        return envelope
    delta = pi * d * y / (lam * D)       # não sabemos: soma-se ψ1 + ψ2
    return cos(delta)**2 * envelope


def sortear_impacto(com_detector):
    """Método da rejeição: aceita y com probabilidade prob(y) (máximo = 1)."""
    while True:
        y = uniform(-Y, Y)
        if random() < prob(y, com_detector):
            return y


# %% [3] Cena: canhão, fendas, detector e histograma
scene.title = "Elétrons um a um na fenda dupla\n"
scene.width, scene.height = 900, 450
scene.background = color.black
scene.forward = vector(0.8, -0.2, -1)
scene.center = vector(2, 0, 0)
scene.range = 9

escala = 8 / Y          # metros reais → unidades da cena no detector
cylinder(pos=vector(-12, 0, 0), axis=vector(2, 0, 0), radius=0.5,
         color=color.gray(0.5))
for y_placa, altura in ((3.2, 6), (-3.2, 6), (0, 0.2)):
    box(pos=vector(-2, y_placa, 0), size=vector(0.1, altura, 6),
        color=color.gray(0.4))
box(pos=vector(10, 0, 0), size=vector(0.05, 16.5, 8), color=color.gray(0.08))
impactos = points(radius=2, color=color.green)
eletron = sphere(radius=0.15, color=color.cyan, emissive=True)
painel = label(pos=vector(2, 7.5, 0), box=False, height=13)

n_bins = 80
contagem = [0] * n_bins
g = graph(title="Contagem de elétrons por posição", xtitle="y (μm)",
          ytitle="contagem", width=900, height=230)
barras = gvbars(graph=g, delta=2 * Y * 1e6 / n_bins, color=color.green)

estado = {"detector": False, "total": 0}


def alternar_detector(b):
    estado["detector"] = not estado["detector"]
    b.text = "Desligar detector de caminho" if estado["detector"] \
        else "Ligar detector de caminho"
    impactos.clear()
    for i in range(n_bins):
        contagem[i] = 0
    estado["total"] = 0


button(text="Ligar detector de caminho", bind=alternar_detector)

# %% [4] Laço: um elétron por vez (a janela continua aberta no fim)
while True:
    if estado["total"] >= 20000:      # terminou: só espera o usuário
        rate(30)
        continue
    y_real = sortear_impacto(estado["detector"])
    z_real = uniform(-3.5, 3.5)                  # ao longo das fendas
    alvo = vector(10, y_real * escala, z_real)
    if estado["total"] < 40:                     # os primeiros, devagar
        eletron.visible = True
        eletron.pos = vector(-10, 0, 0)
        while eletron.pos.x < 10:
            rate(240)
            if eletron.pos.x < -2:
                eletron.pos += vector(0.4, 0, 0)
            else:
                eletron.pos += 0.4 * norm(alvo - vector(-2, 0, 0))
        eletron.visible = False
    else:
        rate(400)
    impactos.append(alvo)
    i = int((y_real + Y) / (2 * Y) * n_bins)
    contagem[min(i, n_bins - 1)] += 1
    estado["total"] += 1
    if estado["total"] % 100 == 0 or estado["total"] < 40:
        barras.delete()
        barras.plot([[(-Y + (k + 0.5) * 2 * Y / n_bins) * 1e6, contagem[k]]
                     for k in range(n_bins)])
    modo = "COM" if estado["detector"] else "SEM"
    painel.text = f"{estado['total']} elétrons — {modo} detector de caminho"
