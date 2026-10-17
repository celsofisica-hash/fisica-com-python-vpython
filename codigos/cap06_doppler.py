"""
Capítulo 6 — Acústica no cotidiano: o efeito Doppler da sirene.

Uma ambulância emite frentes de onda sonora a intervalos regulares.
Cada frente é uma circunferência que cresce com a velocidade do som a
partir do ponto onde foi emitida. Dois observadores registram a chegada
das frentes e medem a frequência percebida, que é comparada com a
fórmula f' = f c / (c ∓ v_s). Acima de Mach 1 surge o cone de Mach.
"""
from vpython import *

# %% [1] Parâmetros
c_som = 340.0           # velocidade do som no ar (m/s)
f_fonte = 10.0          # frequência emitida (Hz) — reduzida para visualização
mach = 0.5              # v_fonte / c_som (ajustável pelo controle deslizante)
x_ini, x_fim = -250.0, 250.0
dt = 0.002

# %% [2] Cena: estrada, ambulância, observadores e controle de velocidade
scene.title = "Efeito Doppler: frentes de onda de uma fonte em movimento\n"
scene.width, scene.height = 900, 500
scene.background = color.white
scene.range = 300

box(pos=vector(0, 0, -2), size=vector(700, 20, 1), color=color.gray(0.8))
fonte = box(pos=vector(x_ini, 0, 0), size=vector(16, 8, 8), color=color.red)
obs_frente = sphere(pos=vector(280, -25, 0), radius=6, color=color.blue)
obs_atras = sphere(pos=vector(-280, -25, 0), radius=6, color=color.green)
txt_frente = label(pos=vector(280, -65, 0), box=False, height=12)
txt_atras = label(pos=vector(-280, -65, 0), box=False, height=12)
painel = label(pos=vector(0, 200, 0), box=True, height=13)


def mudar_mach(s):
    global mach
    mach = s.value
    txt_mach.text = f"  Mach = {mach:.2f}  (v = {mach * c_som:.0f} m/s)"


scene.append_to_caption("\nVelocidade da fonte: ")
slider(min=0, max=1.6, value=mach, step=0.05, length=400, bind=mudar_mach)
txt_mach = wtext(text=f"  Mach = {mach:.2f}  (v = {mach * c_som:.0f} m/s)")

# %% [3] Física da detecção e a fórmula do efeito Doppler
frentes = []            # cada item: [anel, ponto de emissão, instante, chegadas]
reserva = []            # anéis já usados, guardados para reaproveitar
chegada = {"frente": None, "atras": None}       # instante da última chegada
f_medida = {"frente": 0.0, "atras": 0.0}


def detectar(nome, observador, frente, t):
    """Registra a primeira vez em que a frente alcança o observador e
    mede a frequência pelo intervalo entre duas chegadas sucessivas."""
    anel, p_emissao, t_emissao, ja_chegou = frente
    if nome in ja_chegou:
        return
    distancia = mag(observador.pos - p_emissao)
    if c_som * (t - t_emissao) >= distancia:
        ja_chegou.add(nome)
        t_chegada = t_emissao + distancia / c_som   # instante exato da chegada
        if chegada[nome] is not None and t_chegada > chegada[nome]:
            f_medida[nome] = 1 / (t_chegada - chegada[nome])
        chegada[nome] = t_chegada


def mostrar_frequencias(t):
    """f' = f/(1 − M) para quem está à frente, f/(1 + M) para quem fica atrás."""
    f_teo_frente = f_fonte / (1 - mach) if mach < 1 else float("inf")
    f_teo_atras = f_fonte / (1 + mach)
    txt_frente.text = (f"medido: {f_medida['frente']:5.1f} Hz\n"
                       f"fórmula: {f_teo_frente:5.1f} Hz")
    txt_atras.text = (f"medido: {f_medida['atras']:5.1f} Hz\n"
                      f"fórmula: {f_teo_atras:5.1f} Hz")
    painel.text = (f"f emitida = {f_fonte:.0f} Hz    Mach = {mach:.2f}    "
                   f"t = {t:5.2f} s")


# %% [4] Laço: a fonte anda, emite, as frentes crescem e são detectadas
t, t_proxima = 0.0, 0.0
while True:
    rate(150)
    t += dt
    fonte.pos = fonte.pos + vector(mach * c_som * dt, 0, 0)
    if fonte.pos.x > x_fim:                      # recomeça a passagem
        fonte.pos = vector(x_ini, 0, 0)
        for frente in frentes:
            frente[0].visible = False
            reserva.append(frente[0])
        frentes.clear()
        chegada["frente"] = chegada["atras"] = None

    if t >= t_proxima:                           # emite nova frente de onda
        if reserva:                              # reaproveita um anel antigo
            anel = reserva.pop()
            anel.pos, anel.visible = vector(fonte.pos), True
        else:
            anel = ring(pos=vector(fonte.pos), axis=vector(0, 0, 1),
                        radius=0.5, thickness=1.0, color=color.magenta)
        frentes.append([anel, vector(fonte.pos), t, set()])
        t_proxima += 1 / f_fonte

    for frente in frentes:                       # raio = c (t − t_emissão)
        frente[0].radius = max(c_som * (t - frente[2]), 0.5)
        detectar("frente", obs_frente, frente, t)
        detectar("atras", obs_atras, frente, t)
    while frentes and frentes[0][0].radius > 800:  # descarta frentes distantes
        anel = frentes.pop(0)[0]
        anel.visible = False
        reserva.append(anel)

    mostrar_frequencias(t)
