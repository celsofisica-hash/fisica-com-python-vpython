"""
Capítulo 2 — Conservação da energia mecânica: usinas hidrelétricas.

Uma "parcela" de água desce pelo conduto forçado de uma usina, do
reservatório até a turbina. Acompanhamos as energias potencial (U),
cinética (K) e mecânica (E = U + K) da parcela, com e sem perdas por
atrito, e estimamos a potência elétrica da usina.
"""
from vpython import *

# %% [1] Parâmetros da usina e da parcela de água
g = 9.8                 # gravidade (m/s²)
rho = 1000.0            # densidade da água (kg/m³)
H = 100.0               # queda bruta: desnível reservatório–turbina (m)
m = 1.0                 # massa da parcela de água acompanhada (kg)
c_perda = 0.0           # coef. de perda (1/m): a_atrito = -c v². Teste 0.002!

topo = vector(-40, H - 5, 0)      # entrada do conduto (5 m abaixo da superfície)
base = vector(50, 0, 0)           # entrada da turbina
L = mag(base - topo)              # comprimento do conduto (m)
u = norm(base - topo)             # versor ao longo do conduto
sen_alfa = -u.y                   # seno da inclinação do conduto

dt = 0.01

# %% [2] Cenário: reservatório, barragem, conduto e turbina
scene.title = "Usina hidrelétrica: da energia potencial à energia elétrica\n"
scene.width, scene.height = 900, 450
scene.background = color.gray(0.95)
scene.center = vector(15, 45, 0)
scene.range = 65

solo = box(pos=vector(0, -2, 0), size=vector(200, 4, 30), color=color.green)
reservatorio = box(pos=vector(-66, H / 2, 0), size=vector(50, H, 26),
                   color=color.blue, opacity=0.3)
barragem = box(pos=vector(-38, H / 2 + 3, 0), size=vector(6, H + 6, 28),
               color=color.gray(0.6))
conduto = cylinder(pos=topo, axis=base - topo, radius=2.5,
                   color=color.gray(0.4), opacity=0.3)
casa_forca = box(pos=vector(58, 8, 0), size=vector(16, 16, 16),
                 color=color.orange, opacity=0.4)

# Rotor da turbina: um cubo central com 6 pás, agrupados em um "compound".
centro_rotor = vector(58, 6, 0)
pecas = [cylinder(pos=centro_rotor - vector(0, 0, 2), axis=vector(0, 0, 4),
                  radius=1.2, color=color.gray(0.3))]
for i in range(6):
    pa = box(pos=centro_rotor + vector(3.5, 0, 0), size=vector(5, 1, 3),
             color=color.yellow)
    pa.rotate(angle=i * pi / 3, axis=vector(0, 0, 1), origin=centro_rotor)
    pecas.append(pa)
rotor = compound(pecas)

parcela = sphere(pos=topo, radius=2, color=color.cyan, make_trail=True,
                 trail_radius=0.4, retain=200)
label(pos=vector(-66, H - 8, 0), text="reservatório", box=False,
      color=color.black)
label(pos=vector(58, 22, 0), text="casa de força", box=False,
      color=color.black)

# %% [3] Barras de energia (U, K, E) desenhadas na própria cena
escala = 0.05           # metros de barra por joule
x_barras = 95


def criar_barra(x, cor, nome):
    label(pos=vector(x, -8, 0), text=nome, box=False, height=12,
          color=color.black)
    return box(pos=vector(x, 0, 0), size=vector(5, 0.01, 5), color=cor)


barra_U = criar_barra(x_barras, color.green, "U")
barra_K = criar_barra(x_barras + 7, color.red, "K")
barra_E = criar_barra(x_barras + 14, color.black, "E")


def ajustar_barra(barra, energia):
    h = max(energia * escala, 0.01)
    barra.size = vector(5, h, 5)
    barra.pos = vector(barra.pos.x, h / 2, 0)


grafico = graph(title="Energias da parcela de 1 kg", xtitle="t (s)",
                ytitle="energia (J)", width=600, height=260)
gU = gcurve(color=color.green, label="U")
gK = gcurve(color=color.red, label="K")
gE = gcurve(color=color.black, label="E")

# %% [4] Dinâmica ao longo do conduto e balanço de energia
s, v, t = 0.0, 0.0, 0.0       # posição ao longo do tubo, velocidade, tempo
E_turbina = 0.0               # energia entregue à turbina (J)
n_parcelas = 0

while n_parcelas < 3:
    rate(100)
    a = g * sen_alfa - c_perda * v**2    # componente do peso − atrito
    v += a * dt
    s += v * dt
    t += dt
    parcela.pos = topo + s * u

    U = m * g * parcela.pos.y            # referência: altura da turbina
    K = 0.5 * m * v**2
    ajustar_barra(barra_U, U)
    ajustar_barra(barra_K, K)
    ajustar_barra(barra_E, U + K)
    gU.plot(t, U)
    gK.plot(t, K)
    gE.plot(t, U + K)

    if s >= L:                           # a parcela chegou à turbina
        E_turbina += K
        n_parcelas += 1
        print(f"Parcela {n_parcelas}: v = {v:5.1f} m/s, E = U + K = {U + K:6.1f} J"
              f" (U inicial = {m * g * topo.y:6.1f} J)")
        for i in range(60):              # a turbina gira com a energia recebida
            rate(60)
            rotor.rotate(angle=0.15, axis=vector(0, 0, 1),
                         origin=centro_rotor)
        parcela.clear_trail()
        s, v = 0.0, 0.0
        parcela.pos = topo

# %% [5] Da parcela à usina: potência P = η ρ g Q H
eta = 0.90          # rendimento do conjunto turbina–gerador
Q = 500.0           # vazão turbinada (m³/s)
P = eta * rho * g * Q * H
print(f"\nVelocidade de Torricelli sqrt(2gh) na turbina: "
      f"{sqrt(2 * g * topo.y):5.1f} m/s")
print(f"Potência elétrica com Q = {Q:.0f} m³/s e H = {H:.0f} m: "
      f"{P / 1e6:6.1f} MW")
label(pos=vector(10, H + 25, 0), box=True, color=color.black,
      text=f"P = η ρ g Q H = {P / 1e6:.0f} MW")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
