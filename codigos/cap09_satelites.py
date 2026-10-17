"""
Capítulo 9 — Satélites artificiais: a Estação Espacial e o geoestacionário.

Dois satélites orbitam a Terra sob a gravitação de Newton (unidades SI):
a Estação Espacial Internacional, a cerca de 420 km de altitude, e um
satélite geoestacionário, cujo período deve coincidir com o dia sideral.
Medimos os períodos e verificamos que T²/r³ é o mesmo para os dois
(3ª lei de Kepler aplicada à Terra como corpo central).
"""
from vpython import *

# %% [1] Constantes e condições iniciais
G = 6.674e-11
M_T = 5.972e24          # massa da Terra (kg)
R_T = 6.371e6           # raio médio da Terra (m)
dia_sideral = 86164.1   # período de rotação da Terra (s)
omega_T = 2 * pi / dia_sideral

r_geo = (G * M_T * dia_sideral**2 / (4 * pi**2))**(1 / 3)
r_iss = R_T + 420e3
print(f"Raio da órbita geoestacionária: {r_geo / 1e3:.0f} km "
      f"(altitude {(r_geo - R_T) / 1e3:.0f} km)")

dt = 5.0                # passo (s)
passos_por_quadro = 40  # 200 s de órbita por quadro


def v_circular(r):
    return sqrt(G * M_T / r)


# %% [2] Cena: Terra com textura, eixo de rotação e satélites
scene.title = "Satélites: ISS (vermelho) e geoestacionário (amarelo)\n"
scene.width, scene.height = 800, 600
scene.background = color.black
scene.range = 1.2 * r_geo
scene.forward = vector(-0.3, -0.55, -1)       # vista oblíqua, de cima

terra = sphere(pos=vector(0, 0, 0), radius=R_T, texture=textures.earth)
cylinder(pos=vector(0, -1.4 * R_T, 0), axis=vector(0, 2.8 * R_T, 0),
         radius=R_T / 50, color=color.white)

inc = radians(51.6)                     # inclinação da órbita da ISS
iss = sphere(pos=vector(r_iss, 0, 0), radius=R_T / 15, color=color.red)
iss.v = v_circular(r_iss) * vector(0, sin(inc), -cos(inc))
geo = sphere(pos=vector(r_geo, 0, 0), radius=R_T / 8, color=color.yellow)
geo.v = v_circular(r_geo) * vector(0, 0, -1)    # no plano do equador
# linha do centro da Terra até o geoestacionário: deve "girar junto"
ligacao = curve(pos=[vector(0, 0, 0), geo.pos], color=color.yellow,
                radius=R_T / 100)
marco = sphere(pos=vector(R_T, 0, 0), radius=R_T / 20, color=color.green)
rastro_iss = curve(color=color.red, radius=R_T / 150, retain=600)
rastro_geo = curve(color=color.yellow, radius=R_T / 100)
painel = label(pos=vector(0, 1.05 * r_geo, 0), box=False, height=13)


# %% [3] Gravitação e integração (Verlet de velocidade)
def acel(r):
    return -G * M_T * r / mag(r)**3


def passo_verlet(sat):
    a1 = acel(sat.pos)
    sat.pos = sat.pos + sat.v * dt + 0.5 * a1 * dt**2
    sat.v = sat.v + 0.5 * (a1 + acel(sat.pos)) * dt


def ang_xz(r):
    """Ângulo da projeção de r no plano do equador (para medir o período)."""
    return atan2(-r.z, r.x) % (2 * pi)


# %% [4] Laço: um dia sideral de simulação
t, passo = 0.0, 0
volta = {"iss": [], "geo": []}
ang_ant = {"iss": 0.0, "geo": 0.0}
while t < 1.02 * dia_sideral:
    rate(60)
    for _ in range(passos_por_quadro):
        for nome, sat in (("iss", iss), ("geo", geo)):
            passo_verlet(sat)
            ang = ang_xz(sat.pos)
            if ang < ang_ant[nome] - pi:         # completou uma volta
                volta[nome].append(t)
            ang_ant[nome] = ang
        terra.rotate(angle=omega_T * dt, axis=vector(0, 1, 0))
        marco.pos = rotate(marco.pos, angle=omega_T * dt, axis=vector(0, 1, 0))
        t += dt
        passo += 1
        if passo % 4 == 0:                       # um ponto do rastro a cada 20 s
            rastro_iss.append(iss.pos)
    rastro_geo.append(geo.pos)
    ligacao.modify(1, pos=geo.pos)
    painel.text = f"t = {t / 3600:5.2f} h    voltas da ISS: {len(volta['iss'])}"

# %% [5] Períodos medidos e a 3ª lei de Kepler
T_iss = (volta["iss"][-1] - volta["iss"][0]) / (len(volta["iss"]) - 1)
T_geo = volta["geo"][0]
print(f"Período da ISS: {T_iss / 60:.1f} min "
      f"(teórico {2 * pi * r_iss / v_circular(r_iss) / 60:.1f} min)")
print(f"Período do geoestacionário: {T_geo / 3600:.3f} h "
      f"(dia sideral = {dia_sideral / 3600:.3f} h)")
print(f"T²/r³: ISS = {T_iss**2 / r_iss**3:.4e} s²/m³ | "
      f"GEO = {T_geo**2 / r_geo**3:.4e} s²/m³ | "
      f"4π²/GM = {4 * pi**2 / (G * M_T):.4e} s²/m³")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
