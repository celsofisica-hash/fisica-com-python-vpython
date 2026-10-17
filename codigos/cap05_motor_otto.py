"""
Capítulo 5 — Leis da termodinâmica: o ciclo Otto de um motor a gasolina.

Um pistão acionado por um sistema biela–manivela comprime e expande uma
amostra de ar (modelo ar-padrão). O diagrama p–V é traçado em tempo
real; o trabalho do ciclo é obtido somando p ΔV e o rendimento simulado
é comparado com η = 1 − r^(1−γ).
"""
from vpython import *

# %% [1] Parâmetros do motor e do gás
R_gas = 8.314           # constante dos gases (J/mol·K)
gama = 1.4              # Cp/Cv do ar
Cv = R_gas / (gama - 1)  # capacidade térmica molar a volume constante

cilindrada = 500.0      # V1 − V2 (cm³)
r = 10.0                # taxa de compressão V1/V2
curso = 8.0             # curso do pistão (cm)
Ap = cilindrada / curso         # área do pistão (cm²)
V2 = cilindrada / (r - 1)       # volume da câmara de combustão (cm³)
V1 = V2 + cilindrada            # volume máximo (cm³)

T1, p1 = 300.0, 1.0e5   # estado 1: admissão (K, Pa)
T3 = 2200.0             # temperatura após a combustão (K)
n = p1 * V1 * 1e-6 / (R_gas * T1)   # mols de gás (constante no ciclo)

# %% [2] Cinemática biela–manivela: ângulo → volume
r_m = curso / 2         # raio da manivela (cm)
L_b = 14.0              # comprimento da biela (cm)


def y_pino(phi):
    """Altura do pino do pistão acima do eixo da manivela."""
    return r_m * cos(phi) + sqrt(L_b**2 - (r_m * sin(phi))**2)


def volume(phi):
    """Volume do gás (cm³): x = distância do pistão ao ponto morto superior."""
    x = (r_m + L_b) - y_pino(phi)
    return V2 + Ap * x


# %% [3] Cena: cilindro, gás, pistão, biela e manivela
scene.title = "Ciclo Otto (ar-padrão): motor de quatro tempos simplificado\n"
scene.width, scene.height = 500, 550
scene.background = color.white
scene.center = vector(0, 10, 0)
scene.range = 16

raio_cil = sqrt(Ap / pi)
y_cabecote = (r_m + L_b) + 1.5 + V2 / Ap      # face interna do cabeçote
cylinder(pos=vector(0, y_cabecote - curso - 4, 0), axis=vector(0, curso + 4, 0),
         radius=raio_cil + 0.3, color=color.gray(0.7), opacity=0.2)
box(pos=vector(0, y_cabecote + 0.75, 0), size=vector(2 * raio_cil + 1, 1.5, 3),
    color=color.gray(0.5))
vela = cylinder(pos=vector(0, y_cabecote + 1.5, 0), axis=vector(0, 1.5, 0),
                radius=0.3, color=color.gray(0.3))
gas = cylinder(pos=vector(0, y_cabecote, 0), radius=raio_cil * 0.98)
pistao = cylinder(radius=raio_cil * 0.97, axis=vector(0, 3, 0),
                  color=color.gray(0.4))
biela = cylinder(radius=0.35, color=color.gray(0.2))
manivela = cylinder(pos=vector(0, 0, 0), radius=0.5, color=color.red)
ring(pos=vector(0, 0, -0.5), axis=vector(0, 0, 1), radius=r_m + 0.6,
     thickness=0.3, color=color.gray(0.5))
painel = label(pos=vector(0, -7, 0), height=12, box=True)

g_pv = graph(title="Diagrama p–V", xtitle="V (cm³)", ytitle="p (bar)",
             width=500, height=300, align="right")
curva_pv = gcurve(graph=g_pv, color=color.blue)


def cor_temperatura(T):
    """Azul (300 K) → vermelho (2200 K ou mais)."""
    f = min(max((T - 300) / 1900, 0), 1)
    return color.hsv_to_rgb(vector(0.66 * (1 - f), 1, 1))


def desenhar(phi, p, T):
    yp = y_pino(phi)
    pino_m = vector(r_m * sin(phi), r_m * cos(phi), 0)
    pistao.pos = vector(0, yp - 1.5, 0)
    biela.pos = pino_m
    biela.axis = vector(0, yp, 0) - pino_m
    manivela.axis = pino_m
    gas.axis = vector(0, (yp + 1.5) - y_cabecote, 0)
    gas.color = cor_temperatura(T)
    curva_pv.plot(volume(phi), p / 1e5)
    painel.text = (f"V = {volume(phi):5.1f} cm³   p = {p / 1e5:5.1f} bar   "
                   f"T = {T:5.0f} K")


# %% [4] As quatro etapas do ciclo e a 1ª lei da termodinâmica
dphi = 0.02
ciclos, n_ciclos = 0, 2
while ciclos < n_ciclos:
    W = 0.0                                  # trabalho líquido (J)

    # 1 → 2: compressão adiabática (PMI → PMS): Q = 0, W < 0
    phi = pi
    while phi < 2 * pi:
        rate(100)
        V_a = volume(phi)
        phi = min(phi + dphi, 2 * pi)
        V_b = volume(phi)
        p = p1 * (V1 / V_b)**gama
        p_med = p1 * (V1 / (0.5 * (V_a + V_b)))**gama
        W += p_med * (V_b - V_a) * 1e-6
        desenhar(phi, p, p * V_b * 1e-6 / (n * R_gas))
    T2 = p * V2 * 1e-6 / (n * R_gas)

    # 2 → 3: combustão a volume constante: W = 0, Q_in = n Cv (T3 − T2)
    vela.color = color.yellow
    for i in range(41):
        rate(60)
        T = T2 + (T3 - T2) * i / 40
        desenhar(phi, n * R_gas * T / (V2 * 1e-6), T)
    vela.color = color.gray(0.3)
    p3 = n * R_gas * T3 / (V2 * 1e-6)
    Q_in = n * Cv * (T3 - T2)

    # 3 → 4: expansão adiabática (tempo motor): Q = 0, W > 0
    while phi < 3 * pi:
        rate(100)
        V_a = volume(phi)
        phi = min(phi + dphi, 3 * pi)
        V_b = volume(phi)
        p = p3 * (V2 / V_b)**gama
        p_med = p3 * (V2 / (0.5 * (V_a + V_b)))**gama
        W += p_med * (V_b - V_a) * 1e-6
        desenhar(phi, p, p * V_b * 1e-6 / (n * R_gas))
    T4 = p * V1 * 1e-6 / (n * R_gas)

    # 4 → 1: rejeição de calor a volume constante (escape)
    for i in range(41):
        rate(60)
        T = T4 + (T1 - T4) * i / 40
        desenhar(phi, n * R_gas * T / (V1 * 1e-6), T)
    Q_out = n * Cv * (T4 - T1)

    ciclos += 1
    print(f"Ciclo {ciclos}: T2 = {T2:5.0f} K, T4 = {T4:5.0f} K")
    print(f"  Q_in = {Q_in:6.1f} J, Q_out = {Q_out:6.1f} J, W = {W:6.1f} J")
    print(f"  1ª lei: Q_in − Q_out − W = {Q_in - Q_out - W:+.2e} J")
    print(f"  rendimento: simulado = {W / Q_in:.4f} | "
          f"teórico 1 − r^(1−γ) = {1 - r**(1 - gama):.4f}")

# %% [5] Potência do motor a 3000 rpm (um ciclo a cada duas voltas)
rpm = 3000
P_motor = W * (rpm / 60) / 2
print(f"\nPotência indicada por cilindro a {rpm} rpm: {P_motor / 1000:.1f} kW "
      f"({P_motor / 735.5:.1f} cv)")

# %% [6] Mantém a janela aberta depois do fim da animação
scene.append_to_caption("\n<b>Simulação concluída.</b> A cena continua ativa: gire com o "
                        "botão direito do mouse e aproxime com a roda.\n")
print("Simulação concluída. Feche a aba do navegador (ou tecle Ctrl+C) para sair.")
while True:
    rate(30)
