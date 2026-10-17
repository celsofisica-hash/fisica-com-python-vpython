"""
Capítulo 5 — Transferência de calor: a aleta de arrefecimento de um motor.

Um pino de alumínio, preso ao bloco quente do motor (100 °C), troca calor
com o ar ambiente (25 °C) por convecção. A equação do calor com perda
convectiva é resolvida por diferenças finitas (método explícito FTCS) e
o perfil de temperatura é comparado com a solução estacionária analítica.
"""
from vpython import *

# %% [1] Propriedades do material, da geometria e do ar
k = 237.0               # condutividade térmica do alumínio (W/m·K)
rho = 2700.0            # densidade (kg/m³)
c = 900.0               # calor específico (J/kg·K)
alfa = k / (rho * c)    # difusividade térmica (m²/s)

L = 0.30                # comprimento do pino (m)
D = 0.005               # diâmetro do pino (m)
h_conv = 25.0           # coeficiente de convecção do ar (W/m²·K)
T_base, T_ar = 100.0, 25.0

m2 = h_conv * (4 / D) / k          # m² = hP/(kA), P/A = 4/D para o cilindro
m_fin = sqrt(m2)

# %% [2] Discretização e critério de estabilidade
N = 60
dx = L / N
dt = 0.1
Fo = alfa * dt / dx**2             # número de Fourier da malha
print(f"Número de Fourier = {Fo:.3f} (o método explícito exige Fo ≤ 0,5)")
T = [T_ar] * (N + 1)               # o pino começa à temperatura ambiente
T[0] = T_base


def passo_ftcs(T):
    """Um passo de tempo: difusão + perda por convecção lateral."""
    novo = T[:]
    for i in range(1, N):
        difusao = Fo * (T[i + 1] - 2 * T[i] + T[i - 1])
        conveccao = alfa * dt * m2 * (T[i] - T_ar)
        novo[i] = T[i] + difusao - conveccao
    # ponta isolada: derivada nula → usa um "nó fantasma" espelhado
    novo[N] = T[N] + 2 * Fo * (T[N - 1] - T[N]) - alfa * dt * m2 * (T[N] - T_ar)
    novo[0] = T_base
    return novo


def T_estacionario(x):
    """Solução analítica, ponta isolada: θ/θb = cosh m(L−x) / cosh mL."""
    return T_ar + (T_base - T_ar) * cosh(m_fin * (L - x)) / cosh(m_fin * L)


# %% [3] Cena: bloco do motor e o pino dividido em segmentos coloridos
scene.title = "Aleta (pino) de alumínio: condução + convecção\n"
scene.width, scene.height = 900, 300
scene.background = color.gray(0.15)
scene.center = vector(15, 0, 0)
scene.range = 10

escala = 100            # 1 unidade da cena = 1 cm
box(pos=vector(-2, 0, 0), size=vector(4, 10, 6), color=color.red)
segmentos = [cylinder(pos=vector(i * dx * escala, 0, 0),
                      axis=vector(dx * escala, 0, 0), radius=0.8)
             for i in range(N + 1)]
rotulo = label(pos=vector(15, 5, 0), height=14, color=color.white)


def cor(T):
    f = (T - T_ar) / (T_base - T_ar)               # 0 (frio) → 1 (quente)
    return color.hsv_to_rgb(vector(0.66 * (1 - f), 1, 1))


g_perfil = graph(title="Perfil de temperatura", xtitle="x (cm)",
                 ytitle="T (°C)", width=600, height=300, ymin=20, ymax=100)
c_num = gcurve(graph=g_perfil, color=color.red, label="FTCS")
c_ana = gdots(graph=g_perfil, color=color.blue, label="estacionária",
              radius=2)
c_ana.plot([[100 * i * dx, T_estacionario(i * dx)] for i in range(0, N + 1, 3)])

# %% [4] Evolução temporal
t, t_final, passos_por_quadro = 0.0, 600.0, 50
while t < t_final:
    rate(30)
    for _ in range(passos_por_quadro):
        T = passo_ftcs(T)
        t += dt
    for seg, Ti in zip(segmentos, T):
        seg.color = cor(Ti)
    rotulo.text = f"t = {t:5.0f} s    T(ponta) = {T[N]:5.1f} °C"
    c_num.delete()
    c_num.plot([[100 * i * dx, T[i]] for i in range(N + 1)])

# %% [5] Calor dissipado e eficiência da aleta
A_sec = pi * D**2 / 4
q_ana = sqrt(h_conv * pi * D * k * A_sec) * (T_base - T_ar) * tanh(m_fin * L)
# lei de Fourier na base, com derivada de 2ª ordem (3 pontos)
q_num = -k * A_sec * (-3 * T[0] + 4 * T[1] - T[2]) / (2 * dx)
q_max = h_conv * pi * D * L * (T_base - T_ar)      # se o pino todo estivesse a T_base
print(f"T(ponta): numérico = {T[N]:.2f} °C | analítico = {T_estacionario(L):.2f} °C")
print(f"Calor pela base: numérico = {q_num:.2f} W | analítico = {q_ana:.2f} W")
print(f"Eficiência da aleta = {q_ana / q_max:.2f}")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
