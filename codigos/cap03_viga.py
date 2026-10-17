"""
Capítulo 3 — Equilíbrio de corpos rígidos e mecânica dos sólidos.

Um caminhão atravessa uma ponte modelada como viga de aço biapoiada.
A cada instante calculamos as reações nos apoios pelas condições de
equilíbrio (ΣF = 0 e Στ = 0), a flecha (deflexão) da viga pela teoria
de Euler-Bernoulli e a tensão máxima de flexão.
"""
from vpython import *

# %% [1] Parâmetros da viga e da carga
g = 9.8
L = 10.0                # vão entre os apoios (m)
E = 200e9               # módulo de Young do aço (Pa)
I = 8.0e-5              # momento de inércia de área da seção (m^4)
c = 0.20                # distância da linha neutra à fibra mais externa (m)
sigma_esc = 250e6       # tensão de escoamento do aço (Pa)
m_viga = 1000.0         # massa da viga (kg) → carga distribuída w
w = m_viga * g / L      # peso por metro (N/m)
P = 1000.0 * g          # peso do caminhão (N)
exagero = 100           # fator de exagero visual da flecha


# %% [2] Equilíbrio estático: reações nos apoios A (x=0) e B (x=L)


def reacoes(a):
    """Carga P na posição a. Retorna (R_A, R_B).
    Στ_A = 0  →  R_B L − P a − (wL)(L/2) = 0
    ΣF_y = 0  →  R_A + R_B − P − wL = 0
    """
    R_B = (P * a + w * L * L / 2) / L
    R_A = P + w * L - R_B
    return R_A, R_B


# %% [3] Mecânica dos sólidos: flecha y(x) e tensão de flexão
def flecha(x, a):
    """Deflexão (m, positiva para baixo) no ponto x, carga P em a.
    Superpõe a carga concentrada e o peso próprio distribuído."""
    b = L - a
    if x <= a:
        y_P = P * b * x * (L**2 - b**2 - x**2) / (6 * E * I * L)
    else:
        xr = L - x
        y_P = P * a * xr * (L**2 - a**2 - xr**2) / (6 * E * I * L)
    y_w = w * x * (L**3 - 2 * L * x**2 + x**3) / (24 * E * I)
    return y_P + y_w


def momento_fletor(x, a):
    """Momento interno na seção x: soma dos torques à esquerda de x."""
    R_A, R_B = reacoes(a)
    M = R_A * x - w * x**2 / 2
    if x > a:
        M -= P * (x - a)
    return M


def tensao_maxima(a, n=200):
    """Varre a viga e devolve a maior tensão de flexão σ = M c / I."""
    M_max = max(momento_fletor(L * i / n, a) for i in range(n + 1))
    return M_max * c / I


# %% [4] Cena: viga, apoios, caminhão e setas de força
scene.title = "Ponte biapoiada: reações nos apoios e flecha (exagerada ×100)\n"
scene.width, scene.height = 900, 400
scene.background = color.white
scene.center = vector(L / 2, 0, 0)
scene.range = 7

N = 101
xs = [L * i / (N - 1) for i in range(N)]
viga = curve(pos=[vector(x, 0, 0) for x in xs], radius=0.12,
             color=color.gray(0.4))
for x_apoio in (0, L):
    cone(pos=vector(x_apoio, -1.2, 0), axis=vector(0, 1.05, 0), radius=0.5,
         color=color.gray(0.2))

caminhao = box(pos=vector(0, 0.8, 0), size=vector(1.6, 1.4, 1),
               color=color.red)
seta_P = arrow(color=color.red, shaftwidth=0.12)
seta_A = arrow(color=color.blue, shaftwidth=0.12)
seta_B = arrow(color=color.blue, shaftwidth=0.12)
texto_A = label(pos=vector(0, -3.5, 0), box=False, height=12)
texto_B = label(pos=vector(L, -3.5, 0), box=False, height=12)
painel = label(pos=vector(L / 2, 4.5, 0), box=True, height=13)
escala_F = 1 / 8000     # comprimento de seta por newton

g_reac = graph(title="Reações × posição do caminhão", xtitle="a (m)",
               ytitle="força (kN)", width=450, height=250, align="left")
cRA = gcurve(graph=g_reac, color=color.blue, label="R_A")
cRB = gcurve(graph=g_reac, color=color.cyan, label="R_B")
g_flecha = graph(title="Flecha no meio do vão", xtitle="a (m)",
                 ytitle="y(L/2) (mm)", width=450, height=250, align="left")
cY = gcurve(graph=g_flecha, color=color.magenta)

# %% [5] O caminhão atravessa a ponte
a, v_caminhao, dt = 0.0, 1.0, 0.02
sigma_pior = 0
while a <= L:
    rate(50)
    R_A, R_B = reacoes(a)

    # Deforma a viga (para baixo) com a flecha exagerada
    for i, x in enumerate(xs):
        viga.modify(i, pos=vector(x, -exagero * flecha(x, a), 0))
    y_carga = -exagero * flecha(a, a)
    caminhao.pos = vector(a, y_carga + 0.8, 0)

    seta_P.pos = vector(a, y_carga + 1.5 + P * escala_F, 0)
    seta_P.axis = vector(0, -P * escala_F, 0)
    seta_A.pos = vector(0, -1.2 - R_A * escala_F, 0)
    seta_A.axis = vector(0, R_A * escala_F, 0)
    seta_B.pos = vector(L, -1.2 - R_B * escala_F, 0)
    seta_B.axis = vector(0, R_B * escala_F, 0)

    sigma = tensao_maxima(a)
    sigma_pior = max(sigma_pior, sigma)
    texto_A.text = f"R_A = {R_A / 1000:5.1f} kN"
    texto_B.text = f"R_B = {R_B / 1000:5.1f} kN"
    painel.text = (f"ΣF = {R_A + R_B - P - w * L:+.1e} N   "
                   f"σ_máx = {sigma / 1e6:5.1f} MPa   "
                   f"fator de segurança = {sigma_esc / sigma:4.1f}")

    cRA.plot(a, R_A / 1000)
    cRB.plot(a, R_B / 1000)
    cY.plot(a, 1000 * flecha(L / 2, a))
    a += v_caminhao * dt

print(f"Flecha máxima (carga no meio): {1000 * flecha(L / 2, L / 2):.1f} mm")
print(f"Limite usual de norma L/360 = {1000 * L / 360:.1f} mm")
print(f"Maior tensão de flexão: {sigma_pior / 1e6:.1f} MPa "
      f"(escoamento: {sigma_esc / 1e6:.0f} MPa)")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
