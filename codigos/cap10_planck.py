"""
Capítulo 10 — Física quântica pela história: a radiação de corpo negro.

Em 1900, Max Planck explicou o espectro da radiação térmica supondo que a
energia é trocada em pacotes E = h f. Este programa compara a lei de
Planck com a previsão clássica de Rayleigh–Jeans (a "catástrofe do
ultravioleta"), localiza o pico de Wien e integra o espectro para obter
a lei de Stefan–Boltzmann. Um controle muda a temperatura de uma "estrela".
"""
from vpython import *

# %% [1] Constantes físicas (SI)
h = 6.62607015e-34      # constante de Planck (J·s)
c = 2.99792458e8        # velocidade da luz (m/s)
kB = 1.380649e-23       # constante de Boltzmann (J/K)
sigma_SB = 5.670374e-8  # constante de Stefan–Boltzmann (W/m²·K⁴)
b_Wien = 2.897772e-3    # constante de Wien (m·K)


# %% [2] As duas leis de radiação
def planck(lam, T):
    """Radiância espectral B_λ (W·sr⁻¹·m⁻³)."""
    x = h * c / (lam * kB * T)
    if x > 700:                     # evita estouro numérico de exp()
        return 0.0
    return (2 * h * c**2 / lam**5) / (exp(x) - 1)


def rayleigh_jeans(lam, T):
    """Previsão clássica: B_λ = 2 c kB T / λ⁴ (diverge quando λ → 0)."""
    return 2 * c * kB * T / lam**4


# %% [3] Gráfico dos espectros e pico de Wien
g = graph(title="Radiação de corpo negro", xtitle="λ (nm)",
          ytitle="B_λ (10¹³ W·sr⁻¹·m⁻³)", width=800, height=380)
cores_T = {3000: color.red, 4000: color.orange, 5000: color.green,
           5800: color.blue}
picos = gdots(graph=g, color=color.black, radius=4, label="pico de Wien")
for T, cor in cores_T.items():
    curva = gcurve(graph=g, color=cor, label=f"{T} K")
    for lam_nm in range(50, 2501, 10):
        curva.plot(lam_nm, planck(lam_nm * 1e-9, T) / 1e13)
    lam_pico = b_Wien / T
    picos.plot(lam_pico * 1e9, planck(lam_pico, T) / 1e13)
rj = gcurve(graph=g, color=color.magenta, label="Rayleigh–Jeans 5000 K")
for lam_nm in range(500, 2501, 10):
    valor = rayleigh_jeans(lam_nm * 1e-9, 5000) / 1e13
    if valor < 4.5:                         # o resto "explode" para cima
        rj.plot(lam_nm, valor)


# %% [4] Integração numérica: a lei de Stefan–Boltzmann
def potencia_irradiada(T, lam_min=1e-8, lam_max=1e-3, n=20000):
    """M = π ∫ B_λ dλ, pela regra do trapézio em escala logarítmica."""
    soma = 0.0
    razao = (lam_max / lam_min)**(1 / n)
    lam = lam_min
    for i in range(n):
        lam2 = lam * razao
        soma += 0.5 * (planck(lam, T) + planck(lam2, T)) * (lam2 - lam)
        lam = lam2
    return pi * soma


for T in (3000, 5800):
    M = potencia_irradiada(T)
    print(f"T = {T} K: ∫ numérica = {M:.4e} W/m² | "
          f"σT⁴ = {sigma_SB * T**4:.4e} W/m² | λ_max = {b_Wien / T * 1e9:.0f} nm")


# %% [5] A cor de um corpo aquecido: colorimetria CIE 1931
def _g(lam, mu, s1, s2):
    """Gaussiana assimétrica usada no ajuste analítico das funções CIE."""
    s = s1 if lam < mu else s2
    return exp(-0.5 * ((lam - mu) / s)**2)


def funcoes_cie(lam):
    """Funções de cor x, y, z do observador padrão CIE (ajuste de
    Wyman, Sloan e Shirley, 2013)."""
    x = (1.056 * _g(lam, 599.8, 37.9, 31.0) + 0.362 * _g(lam, 442.0, 16.0, 26.7)
         - 0.065 * _g(lam, 501.1, 20.4, 26.2))
    y = 0.821 * _g(lam, 568.8, 46.9, 40.5) + 0.286 * _g(lam, 530.9, 16.3, 31.1)
    z = 1.217 * _g(lam, 437.0, 11.8, 36.0) + 0.681 * _g(lam, 459.0, 26.0, 13.8)
    return x, y, z


def cor_do_corpo(T):
    """Espectro de Planck → (X, Y, Z) → RGB da tela (sRGB), normalizado."""
    X = Y = Z = 0.0
    for lam_nm in range(380, 781, 5):
        B = planck(lam_nm * 1e-9, T)
        x, y, z = funcoes_cie(lam_nm)
        X, Y, Z = X + B * x, Y + B * y, Z + B * z
    rgb = [3.2406 * X - 1.5372 * Y - 0.4986 * Z,
           -0.9689 * X + 1.8758 * Y + 0.0415 * Z,
           0.0557 * X - 0.2040 * Y + 1.0570 * Z]
    rgb = [max(v, 0) for v in rgb]
    maior = max(rgb)
    return vector(*[(v / maior)**(1 / 2.2) for v in rgb])   # correção gama


scene.title = "Um corpo aquecido muda de cor com a temperatura\n"
scene.width, scene.height = 400, 300
scene.background = color.black
estrela = sphere(radius=1, emissive=True, color=cor_do_corpo(3000))
rotulo = label(pos=vector(0, -1.6, 0), box=False, height=14)
curva_T = gcurve(graph=g, color=color.black, width=3)


def mudar_T(s):
    T = s.value
    estrela.color = cor_do_corpo(T)
    rotulo.text = f"T = {T:.0f} K   λ_max = {b_Wien / T * 1e9:.0f} nm"
    curva_T.delete()
    curva_T.plot([[lam_nm, planck(lam_nm * 1e-9, T) / 1e13]
                  for lam_nm in range(50, 2501, 10)])


scene.append_to_caption("\nTemperatura (K): ")
controle = slider(min=1000, max=10000, value=3000, step=50, length=400,
                  bind=mudar_T)
mudar_T(controle)
while True:
    rate(30)
