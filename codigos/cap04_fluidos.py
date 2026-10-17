"""
Capítulo 4 — Mecânica dos fluidos: hidrostática, continuidade e Bernoulli.

Uma caixa d'água cilíndrica, apoiada em uma torre, esvazia por um
pequeno orifício na base. A pressão hidrostática nas paredes é
mostrada por setas; a velocidade de saída vem da equação de Bernoulli
(Torricelli) e o nível cai segundo a equação da continuidade.
"""
from vpython import *
from random import uniform

# %% [1] Parâmetros do reservatório e do orifício
g = 9.8
rho = 1000.0                  # densidade da água (kg/m³)
p_atm = 1.013e5               # pressão atmosférica (Pa)
R_tanque = 0.5                # raio do tanque (m)
A = pi * R_tanque**2          # área da superfície livre (m²)
d_orif = 0.05                 # diâmetro do orifício (m)
a = pi * (d_orif / 2)**2      # área do orifício (m²)
h0 = 2.0                      # nível inicial da água (m)
H_torre = 3.0                 # altura do fundo do tanque em relação ao solo (m)

dt = 0.05                     # passo de tempo (s)
acelerar = 4                  # passos de simulação por quadro (câmera rápida)

# %% [2] Cena: torre, tanque, água e setas de pressão
scene.title = "Esvaziamento de uma caixa d'água (Torricelli)\n"
scene.width, scene.height = 900, 500
scene.background = color.white
scene.center = vector(2.5, 2.5, 0)
scene.range = 4

box(pos=vector(3, -0.05, 0), size=vector(12, 0.1, 4), color=color.green)
for x in (-0.45, 0.45):
    box(pos=vector(x, H_torre / 2, 0), size=vector(0.1, H_torre, 0.1),
        color=color.gray(0.4))
cylinder(pos=vector(0, H_torre, 0), axis=vector(0, h0 + 0.3, 0),
         radius=R_tanque, color=color.gray(0.8), opacity=0.25)
agua = cylinder(pos=vector(0, H_torre, 0), axis=vector(0, h0, 0),
                radius=R_tanque * 0.98, color=color.blue, opacity=0.5)

prof = [0.2 * (i + 1) for i in range(10)]          # alturas acima do fundo
setas = [arrow(pos=vector(-R_tanque, H_torre + z, 0), axis=vector(0, 0, 0),
               color=color.red, shaftwidth=0.05) for z in prof]
escala_p = 1 / 12000          # metros de seta por pascal (manométrica)
manometro = label(pos=vector(-2.2, H_torre + 0.5, 0), height=12)

# %% [3] O jato: gotas lançadas horizontalmente (Capítulo 1!)
gotas = []
for i in range(120):
    gota = sphere(pos=vector(R_tanque, H_torre, 0), radius=0.03,
                  color=color.cyan, visible=False)
    gota.v = vector(0, 0, 0)
    gotas.append(gota)
proxima = 0

g_nivel = graph(title="Nível da água", xtitle="t (s)", ytitle="h (m)",
                width=450, height=250, align="left")
c_sim = gcurve(graph=g_nivel, color=color.blue, label="simulação")
c_teo = gdots(graph=g_nivel, color=color.red, label="analítica", radius=2)
g_vel = graph(title="Velocidade de saída", xtitle="t (s)",
              ytitle="v (m/s)", width=450, height=250, align="left")
c_vel = gcurve(graph=g_vel, color=color.magenta)


def h_analitico(t):
    """Solução de A dh/dt = −a√(2gh):  √h = √h0 − (a/A)√(g/2) t."""
    raiz = sqrt(h0) - (a / A) * sqrt(g / 2) * t
    return max(raiz, 0)**2


# %% [4] Laço: Bernoulli + continuidade a cada passo
h, t, passo = h0, 0.0, 0
while h > 0:
    rate(30)
    for _ in range(acelerar):
        v_saida = sqrt(2 * g * h)          # Bernoulli/Torricelli
        Q = a * v_saida                    # vazão (m³/s)
        h -= (Q / A) * dt                  # continuidade: A dh = −Q dt
        h = max(h, 0)
        t += dt
        passo += 1

    agua.axis = vector(0, h, 0)
    for z, seta in zip(prof, setas):       # p − p_atm = ρ g (h − z)
        p_man = rho * g * max(h - z, 0)
        seta.axis = vector(-p_man * escala_p, 0, 0)
    p_fundo = p_atm + rho * g * h
    manometro.text = (f"h = {h:4.2f} m\np_fundo = {p_fundo / 1e3:6.1f} kPa"
                      f"\nv_saída = {v_saida:4.2f} m/s\nt = {t:5.0f} s")

    # Lança duas gotas por quadro e move as que estão no ar
    for _ in range(2):
        gota = gotas[proxima]
        gota.pos = vector(R_tanque, H_torre + 0.03, uniform(-0.01, 0.01))
        gota.v = vector(v_saida, 0, 0)
        gota.visible = True
        proxima = (proxima + 1) % len(gotas)
    for gota in gotas:
        if gota.visible:
            gota.v.y -= g * 0.02
            gota.pos += gota.v * 0.02
            if gota.pos.y < 0:
                gota.visible = False

    c_sim.plot(t, h)
    c_vel.plot(t, v_saida)
    if passo % 100 < acelerar:
        c_teo.plot(t, h_analitico(t))

# %% [5] Tempo de esvaziamento: simulação × teoria
t_teo = (A / a) * sqrt(2 * h0 / g)
print(f"Tempo para esvaziar: simulado = {t:6.1f} s | teórico = {t_teo:6.1f} s")
print(f"Alcance inicial do jato: "
      f"{sqrt(2 * g * h0) * sqrt(2 * H_torre / g):4.2f} m "
      f"(= 2·sqrt(h0·H_torre) = {2 * sqrt(h0 * H_torre):4.2f} m)")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
