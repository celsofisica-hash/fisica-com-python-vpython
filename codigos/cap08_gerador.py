"""
Capítulo 8 — Eletromagnetismo e indução: o gerador de corrente alternada.

Uma bobina retangular de N espiras gira com velocidade angular constante
entre os polos de um ímã. O fluxo magnético Φ = N B A cos(ωt) é calculado
a partir da orientação da bobina, e a força eletromotriz é obtida
numericamente pela lei de Faraday, ε = −dΦ/dt, sendo comparada com a
expressão analítica ε = N B A ω sen(ωt). Uma lâmpada brilha com ε².
"""
from vpython import *

# %% [1] Parâmetros do gerador
N_esp = 100             # número de espiras
B = 0.20                # campo magnético uniforme (T), na direção +x
larg, alt = 0.10, 0.08  # dimensões da bobina (m)
A = larg * alt          # área de uma espira (m²)
f = 60.0                # frequência de rotação (Hz), como na rede brasileira
omega = 2 * pi * f
eps_max = N_esp * B * A * omega
dt = 1e-4               # passo de tempo (s); a animação roda em câmera lenta

# %% [2] Cena: polos do ímã, linhas de campo, bobina e lâmpada
scene.title = "Gerador elementar de corrente alternada (60 Hz em câmera lenta)\n"
scene.width, scene.height = 800, 420
scene.background = color.white
scene.forward = vector(-0.4, -0.3, -1)
scene.range = 0.17

box(pos=vector(-0.12, 0, 0), size=vector(0.05, 0.14, 0.14), color=color.red)
box(pos=vector(0.12, 0, 0), size=vector(0.05, 0.14, 0.14), color=color.blue)
label(pos=vector(-0.12, 0.09, 0), text="N", box=False)
label(pos=vector(0.12, 0.09, 0), text="S", box=False)
for y in (-0.05, 0, 0.05):
    for z in (-0.05, 0, 0.05):
        arrow(pos=vector(-0.095, y, z), axis=vector(0.19, 0, 0),
              shaftwidth=0.002, color=color.gray(0.7))

# A bobina é desenhada a partir dos 4 vértices no referencial da própria bobina.
vertices0 = [vector(0, -alt / 2, -larg / 2), vector(0, alt / 2, -larg / 2),
             vector(0, alt / 2, larg / 2), vector(0, -alt / 2, larg / 2)]
bobina = curve(pos=vertices0 + [vertices0[0]], radius=0.003, color=color.orange)
normal = arrow(pos=vector(0, 0, 0), axis=vector(0.06, 0, 0), shaftwidth=0.004,
               color=color.magenta)
eixo = cylinder(pos=vector(0, -0.08, 0), axis=vector(0, 0.16, 0), radius=0.002,
                color=color.gray(0.3))
lampada = sphere(pos=vector(0, 0.11, -0.12), radius=0.02, emissive=True,
                 color=color.black)

g = graph(title="Fluxo e força eletromotriz", xtitle="t (ms)",
          ytitle="Φ (Wb·espira) | ε (V)", width=800, height=280)
c_fluxo = gcurve(graph=g, color=color.blue, label="Φ × 1000")
c_eps_num = gdots(graph=g, color=color.red, label="ε numérica", radius=2)
c_eps_teo = gcurve(graph=g, color=color.black, label="ε = NBAω sen ωt")


# %% [3] Fluxo magnético a partir da geometria
def fluxo(theta):
    """Φ = N (B·n) A, com o versor normal n = (cos θ, 0, −sen θ)."""
    n_hat = vector(cos(theta), 0, -sin(theta))
    return N_esp * dot(vector(B, 0, 0), n_hat) * A


# %% [4] Laço: gira a bobina, calcula Φ e aplica a lei de Faraday
t, theta = 0.0, 0.0
phi_ant = fluxo(theta)
eps_rms_acum, n_amostras = 0.0, 0
while t < 3 / f:                             # três voltas completas
    rate(60)
    t += dt
    theta = omega * t
    for i, v in enumerate(vertices0 + [vertices0[0]]):
        bobina.modify(i, pos=rotate(v, angle=theta, axis=vector(0, 1, 0)))
    normal.axis = rotate(vector(0.06, 0, 0), angle=theta, axis=vector(0, 1, 0))

    phi_atual = fluxo(theta)
    eps = -(phi_atual - phi_ant) / dt       # lei de Faraday (diferença finita)
    phi_ant = phi_atual
    eps_rms_acum += eps**2
    n_amostras += 1

    lampada.color = vector(1, 1, 0) * (eps / eps_max)**2
    c_fluxo.plot(1000 * t, 1000 * phi_atual)
    c_eps_num.plot(1000 * t, eps)
    c_eps_teo.plot(1000 * t, eps_max * sin(theta))

# %% [5] Valores de pico e eficaz
eps_rms = sqrt(eps_rms_acum / n_amostras)
print(f"ε de pico (teórico) = {eps_max:.1f} V")
print(f"ε eficaz: simulado = {eps_rms:.1f} V | teórico ε_max/√2 = "
      f"{eps_max / sqrt(2):.1f} V")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
