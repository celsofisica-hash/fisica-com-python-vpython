"""
Capítulo 10 — O átomo de Bohr (1913) e a onda de de Broglie (1924).

O elétron do hidrogênio ocupa órbitas permitidas de raio r_n = n² a0 e
energia E_n = −13,6 eV / n². Ao saltar de n_i para n_f < n_i, emite um
fóton com h f = E_i − E_f. O programa sorteia excitações e decaimentos,
desenha os fótons com a cor do seu comprimento de onda e registra as
linhas num "espectroscópio". A órbita mostra a onda estacionária de de
Broglie: exatamente n comprimentos de onda cabem na circunferência.
"""
from vpython import *
from random import random, randint

# %% [1] Constantes e níveis de energia
E1 = -13.6057           # energia do estado fundamental (eV)
hc = 1239.84            # h·c em eV·nm
n_max = 6


def energia(n):
    return E1 / n**2


def comprimento_de_onda(n_i, n_f):
    """λ (nm) do fóton emitido na transição n_i → n_f."""
    return hc / (energia(n_i) - energia(n_f))


def cor_do_comprimento(lam_nm):
    """λ (nm) → cor RGB; fora do visível usa cinza (UV) ou marrom (IV)."""
    if lam_nm < 380:
        return color.gray(0.6)
    if lam_nm < 440:
        return vector((440 - lam_nm) / 60, 0, 1)
    if lam_nm < 490:
        return vector(0, (lam_nm - 440) / 50, 1)
    if lam_nm < 510:
        return vector(0, 1, (510 - lam_nm) / 20)
    if lam_nm < 580:
        return vector((lam_nm - 510) / 70, 1, 0)
    if lam_nm < 645:
        return vector(1, (645 - lam_nm) / 65, 0)
    if lam_nm <= 780:
        return vector(1, 0, 0)
    return vector(0.5, 0.25, 0.1)


# %% [2] Cena: núcleo, órbitas permitidas e espectroscópio
scene.title = "Átomo de Bohr: saltos quânticos e espectro do hidrogênio\n"
scene.width, scene.height = 900, 600
scene.background = color.black
scene.center = vector(10, 0, 0)
scene.range = 25

escala = 0.6            # unidades da cena por a0
nucleo = sphere(radius=0.6, color=color.red, emissive=True)
for n in range(1, n_max + 1):
    ring(pos=vector(0, 0, 0), axis=vector(0, 0, 1), radius=escala * n**2,
         thickness=0.05, color=color.gray(0.4))
    label(pos=vector(escala * n**2, 0.8, 0), text=f"n={n}", box=False,
          height=10, color=color.gray(0.7))

# espectroscópio: régua de 380 a 780 nm, à direita
x0_esp, largura_esp, y_esp = 24, 20, -18
box(pos=vector(x0_esp + largura_esp / 2, y_esp, 0),
    size=vector(largura_esp, 3, 0.1), color=color.gray(0.15))
for lam_ref in range(400, 801, 100):
    label(pos=vector(x0_esp + largura_esp * (lam_ref - 380) / 400, y_esp - 2.8, 0),
          text=f"{lam_ref}", box=False, height=10)
painel = label(pos=vector(34, 18, 0), box=False, height=13)

# %% [3] Elétron e onda de de Broglie sobre a órbita
eletron = sphere(radius=0.4, color=color.cyan, emissive=True)
onda = curve(color=color.cyan, radius=0.06)
N_pts = 240
for j in range(N_pts + 1):
    onda.append(vector(0, 0, 0))


def desenhar_onda(n, fase):
    """r(θ) = r_n + A cos(nθ − fase): n comprimentos de onda na órbita."""
    r_n = escala * n**2
    amp = 0.25 + 0.08 * n
    for j in range(N_pts + 1):
        th = 2 * pi * j / N_pts
        r = r_n + amp * cos(n * th - fase)
        onda.modify(j, pos=vector(r * cos(th), r * sin(th), 0))


foton = sphere(radius=0.35, emissive=True, visible=False)


def emitir_foton(pos, lam_nm):
    """Fóton viaja para fora; linhas visíveis são anotadas no espectroscópio."""
    cor = cor_do_comprimento(lam_nm)
    foton.pos, foton.color, foton.visible = vector(pos), cor, True
    direcao = norm(pos)
    for _ in range(60):
        rate(120)
        foton.pos = foton.pos + 0.6 * direcao
    foton.visible = False
    if 380 <= lam_nm <= 780:
        x = x0_esp + largura_esp * (lam_nm - 380) / 400
        box(pos=vector(x, y_esp, 0.1), size=vector(0.25, 3, 0.1), color=cor,
            emissive=True)


# %% [4] Laço: o elétron orbita, é excitado e decai emitindo fótons
n, theta, fase, t = 2, 0.0, 0.0, 0.0
linhas = {}
while True:
    rate(60)
    omega_vis = 1.5 / n**3                # ω ∝ 1/n³ no modelo de Bohr
    theta += omega_vis
    fase += 0.15
    t += 1
    r_n = escala * n**2
    eletron.pos = vector(r_n * cos(theta), r_n * sin(theta), 0)
    desenhar_onda(n, fase)
    painel.text = (f"n = {n}   E = {energia(n):6.2f} eV   r = {n**2} a0   "
                   f"L = {n} ħ")

    if t % 45 == 0:                       # de tempos em tempos, um salto
        if n == 1 or (n < n_max and random() < 0.35):
            n = randint(n + 1, n_max)     # absorção (colisão ou fóton)
        else:
            n_f = randint(1, n - 1)       # emissão espontânea
            lam = comprimento_de_onda(n, n_f)
            emitir_foton(eletron.pos, lam)
            nova = (n, n_f) not in linhas
            linhas[(n, n_f)] = lam
            if nova and len(linhas) % 3 == 0:
                print("Linhas observadas:",
                      ", ".join(f"{a}→{b}: {l:.1f} nm"
                                for (a, b), l in sorted(linhas.items())))
            n = n_f
