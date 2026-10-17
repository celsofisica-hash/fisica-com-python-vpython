"""
Capítulo 1 — Força e movimento: as leis de Newton no lançamento de projéteis.

Simula, lado a lado, uma bola de futebol chutada no vácuo e a mesma bola
chutada no ar (arrasto quadrático). A 2ª lei de Newton é integrada pelo
método de Euler-Cromer.
"""
from vpython import *

# %% [1] Parâmetros físicos do problema
g = vector(0, -9.8, 0)        # aceleração da gravidade (m/s²)
m = 0.43                      # massa de uma bola de futebol (kg)
R = 0.11                      # raio da bola (m)
rho_ar = 1.2                  # densidade do ar (kg/m³)
Cd = 0.25                     # coeficiente de arrasto (adimensional)
A = pi * R**2                 # área da seção transversal (m²)
k = 0.5 * rho_ar * Cd * A     # constante do arrasto: |F_ar| = k v²

v0 = 25.0                     # módulo da velocidade inicial (m/s)
theta = radians(40)           # ângulo de lançamento

dt = 0.005                    # passo de tempo (s)

# %% [2] Cena 3D: campo, bolas e rastros
scene.title = "Lançamento oblíquo: vácuo (vermelho) × ar (azul)\n"
scene.width, scene.height = 900, 400
scene.background = color.white
scene.center = vector(35, 8, 0)
scene.range = 18

campo = box(pos=vector(35, -0.25, 0), size=vector(80, 0.5, 10),
            color=color.green)

# O raio visual (0,8 m) é exagerado para que a bola apareça na tela.
bola_vacuo = sphere(pos=vector(0, 0, 0), radius=0.8, color=color.red)
bola_ar = sphere(pos=vector(0, 0, 0), radius=0.8, color=color.blue)
rastro_vacuo = curve(color=color.red, radius=0.15)      # trajetórias na cena
rastro_ar = curve(color=color.blue, radius=0.15)

# Cada bola guarda sua própria velocidade como um atributo extra.
bola_vacuo.v = v0 * vector(cos(theta), sin(theta), 0)
bola_ar.v = v0 * vector(cos(theta), sin(theta), 0)

# %% [3] Gráficos: trajetória y(x) e rapidez |v|(t)
g_traj = graph(title="Trajetória", xtitle="x (m)", ytitle="y (m)",
               width=450, height=250, align="left")
c_vacuo = gcurve(graph=g_traj, color=color.red, label="vácuo")
c_ar = gcurve(graph=g_traj, color=color.blue, label="ar")

g_vel = graph(title="Rapidez", xtitle="t (s)", ytitle="|v| (m/s)",
              width=450, height=250, align="left")
v_vacuo = gcurve(graph=g_vel, color=color.red)
v_ar = gcurve(graph=g_vel, color=color.blue)


# %% [4] A 2ª lei de Newton: força resultante sobre cada bola
def forca_vacuo(v):
    """Única força: o peso."""
    return m * g


def forca_ar(v):
    """Peso + arrasto quadrático, sempre oposto à velocidade."""
    return m * g - k * mag(v) * v


def passo_euler_cromer(bola, forca):
    """Avança a bola de um intervalo dt: atualiza v e depois a posição."""
    a = forca(bola.v) / m               # 2ª lei: a = F/m
    bola.v = bola.v + a * dt            # primeiro a velocidade...
    bola.pos = bola.pos + bola.v * dt   # ...depois a posição (Euler-Cromer)


# %% [5] Laço temporal
t = 0
h_max = {"vacuo": 0, "ar": 0}
dados = []                          # (t, x, y) da bola no ar, para exportar

while bola_vacuo.pos.y >= 0 or bola_ar.pos.y >= 0:
    rate(200)                       # 200 passos por segundo ≈ tempo real
    if bola_vacuo.pos.y >= 0:
        passo_euler_cromer(bola_vacuo, forca_vacuo)
        rastro_vacuo.append(bola_vacuo.pos)
        h_max["vacuo"] = max(h_max["vacuo"], bola_vacuo.pos.y)
        c_vacuo.plot(bola_vacuo.pos.x, bola_vacuo.pos.y)
        v_vacuo.plot(t, mag(bola_vacuo.v))
    if bola_ar.pos.y >= 0:
        passo_euler_cromer(bola_ar, forca_ar)
        rastro_ar.append(bola_ar.pos)
        h_max["ar"] = max(h_max["ar"], bola_ar.pos.y)
        c_ar.plot(bola_ar.pos.x, bola_ar.pos.y)
        v_ar.plot(t, mag(bola_ar.v))
        dados.append((t, bola_ar.pos.x, bola_ar.pos.y))
    t += dt

# %% [6] Resultados e comparação com a teoria
alcance_teo = v0**2 * sin(2 * theta) / mag(g)
hmax_teo = (v0 * sin(theta))**2 / (2 * mag(g))

print(f"Alcance no vácuo: simulado = {bola_vacuo.pos.x:6.2f} m | "
      f"teórico = {alcance_teo:6.2f} m")
print(f"Altura máx. no vácuo: simulada = {h_max['vacuo']:5.2f} m | "
      f"teórica = {hmax_teo:5.2f} m")
print(f"Alcance no ar: {bola_ar.pos.x:6.2f} m "
      f"({100 * bola_ar.pos.x / alcance_teo:4.1f}% do alcance no vácuo)")
print(f"Velocidade terminal: {sqrt(m * mag(g) / k):5.1f} m/s")

# Exporta a trajetória no ar para comparar com uma videoanálise (Tracker).
with open("trajetoria_ar.csv", "w") as arquivo:
    arquivo.write("t_s,x_m,y_m\n")
    for linha in dados:
        arquivo.write("{:.3f},{:.4f},{:.4f}\n".format(*linha))

# %% [7] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
