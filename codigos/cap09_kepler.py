"""
Capítulo 9 — Leis de Kepler e gravitação universal.

Um planeta em órbita elíptica em torno do Sol, integrado pelo método de
Verlet (velocidade) com a lei da gravitação de Newton. Pintamos as áreas
varridas pelo raio vetor em intervalos de tempo iguais (2ª lei) e medimos
o período e o semieixo maior para conferir a 3ª lei, T² = a³.
Unidades: UA, ano e massa solar, de modo que G M_sol = 4π².
"""
from vpython import *

# %% [1] Parâmetros da órbita
GM = 4 * pi**2          # G M_sol em UA³/ano²
a_orb = 1.0             # semieixo maior (UA)
e = 0.5                 # excentricidade (a Terra tem e ≈ 0,017!)
r_p = a_orb * (1 - e)                    # periélio
v_p = sqrt(GM * (1 + e) / r_p)           # velocidade no periélio (vis-viva)
T_kepler = sqrt(a_orb**3)                # período esperado (anos)

n_fatias = 12           # número de intervalos iguais por órbita
passos_fatia = 200      # passos de integração em cada intervalo
dt = T_kepler / (n_fatias * passos_fatia)       # passo (anos)

# %% [2] Cena: Sol, planeta, raio vetor
scene.title = "2ª lei de Kepler: áreas iguais em tempos iguais\n"
scene.width, scene.height = 800, 600
scene.background = color.black
scene.range = 1.3
scene.center = vector(-0.5, 0, 0)

sol = sphere(pos=vector(0, 0, 0), radius=0.08, color=color.yellow,
             emissive=True)
local_light(pos=vector(0, 0, 0), color=color.white)
planeta = sphere(pos=vector(r_p, 0, 0), radius=0.04, color=color.cyan)
orbita = curve(color=color.cyan, radius=0.004)
raio_vetor = curve(pos=[sol.pos, planeta.pos], color=color.white, radius=0.003)
v = vector(0, v_p, 0)
painel = label(pos=vector(-0.5, 1.15, 0), height=13, box=False)


def aceleracao(r):
    """Lei da gravitação: a = −GM r / |r|³ (aponta para o Sol)."""
    return -GM * r / mag(r)**3


# %% [3] Laço: Verlet + preenchimento das áreas varridas
cores = [color.orange, color.blue]
fatia, t = 0, 0.0
area_fatia, areas = 0.0, []
y_ant = planeta.pos.y
periodos, t_cruzamento = [], None
r_min, r_max = mag(planeta.pos), mag(planeta.pos)
r_tri = vector(planeta.pos)          # último vértice usado no preenchimento
passos = 0

while len(periodos) < 3:
    rate(1000)
    r_ant = vector(planeta.pos)
    a1 = aceleracao(planeta.pos)
    planeta.pos = planeta.pos + v * dt + 0.5 * a1 * dt**2      # Verlet
    a2 = aceleracao(planeta.pos)
    v = v + 0.5 * (a1 + a2) * dt
    t += dt
    passos += 1
    raio_vetor.modify(1, pos=planeta.pos)
    r_min, r_max = min(r_min, mag(planeta.pos)), max(r_max, mag(planeta.pos))

    # área do triângulo (Sol, r_ant, r) = |r_ant × r| / 2
    area_fatia += 0.5 * mag(cross(r_ant, planeta.pos))
    if t <= T_kepler and passos % 4 == 0:      # pinta só a 1ª órbita
        cor = cores[fatia % 2]
        triangle(v0=vertex(pos=sol.pos, color=cor),
                 v1=vertex(pos=r_tri, color=cor),
                 v2=vertex(pos=vector(planeta.pos), color=cor))
        r_tri = vector(planeta.pos)
        orbita.append(r_tri)
    if passos % passos_fatia == 0:           # fecha uma fatia de tempo
        areas.append(area_fatia)
        area_fatia = 0.0
        fatia += 1

    # período: instantes em que o planeta cruza o semieixo +x (y: − → +)
    if y_ant < 0 <= planeta.pos.y and planeta.pos.x > 0:
        if t_cruzamento is not None:
            periodos.append(t - t_cruzamento)
        t_cruzamento = t
    y_ant = planeta.pos.y
    painel.text = f"t = {t:5.2f} anos   |v| = {mag(v):5.2f} UA/ano"

# %% [4] Verificação das três leis
print("Áreas das 12 primeiras fatias (UA²):")
print("  ".join(f"{A:.4f}" for A in areas[:n_fatias]))
print(f"Área esperada por fatia: π a b / {n_fatias} = "
      f"{pi * a_orb * a_orb * sqrt(1 - e**2) / n_fatias:.4f} UA²")
a_med = (r_min + r_max) / 2
e_med = (r_max - r_min) / (r_max + r_min)
T_med = sum(periodos) / len(periodos)
print(f"Semieixo maior medido a = {a_med:.4f} UA, excentricidade = {e_med:.4f}")
print(f"Período medido T = {T_med:.4f} anos  →  T²/a³ = {T_med**2 / a_med**3:.4f}")

# %% [5] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
