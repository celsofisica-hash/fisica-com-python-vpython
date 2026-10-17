"""
Capítulo 7 — Óptica geométrica: formação de imagens por uma lente delgada.

Os três raios notáveis partem do topo de um objeto, atravessam uma lente
convergente e se cruzam (ou parecem se cruzar) no topo da imagem. A
posição e o tamanho da imagem são comparados com a equação de Gauss,
1/f = 1/p + 1/p'. Controles deslizantes movem o objeto e mudam o foco,
permitindo "montar" uma lupa, um projetor ou a câmera de um celular.
"""
from vpython import *

# %% [1] Parâmetros iniciais (unidades: cm)
f = 10.0                # distância focal da lente
p = 25.0                # distância do objeto à lente
h_obj = 3.0             # altura do objeto
x_max = 60.0            # até onde os raios são desenhados

# %% [2] Cena: eixo óptico, lente, focos, objeto e imagem
scene.title = "Lente delgada convergente: raios notáveis\n"
scene.width, scene.height = 950, 420
scene.background = color.white
scene.center = vector(5, 0, 0)
scene.range = 16

curve(pos=[vector(-60, 0, 0), vector(60, 0, 0)], color=color.gray(0.5),
      radius=0.05)
ellipsoid(pos=vector(0, 0, 0), length=0.8, height=16, width=16,
          color=color.cyan, opacity=0.35)
foco_obj = sphere(radius=0.3, color=color.black)
foco_img = sphere(radius=0.3, color=color.black)
rot_F = label(box=False, text="F", height=12)
rot_F2 = label(box=False, text="F'", height=12)

objeto = arrow(shaftwidth=0.35, color=color.green)
imagem = arrow(shaftwidth=0.35, color=color.orange)
raios = [curve(color=c, radius=0.07) for c in (color.red, color.blue, color.magenta)]
prolong = [curve(color=color.gray(0.6), radius=0.04) for _ in range(3)]
painel = label(pos=vector(5, 13, 0), box=True, height=13)


# %% [3] Óptica: equação de Gauss e traçado dos três raios notáveis
def gauss(p, f):
    """Retorna (p', aumento). p' > 0: imagem real; p' < 0: virtual."""
    if abs(p - f) < 1e-6:
        return float("inf"), float("inf")
    p_img = p * f / (p - f)
    return p_img, -p_img / p


def raio(curva, pontos):
    curva.clear()
    for P in pontos:
        curva.append(P)


def atualizar():
    topo = vector(-p, h_obj, 0)
    objeto.pos, objeto.axis = vector(-p, 0, 0), vector(0, h_obj, 0)
    foco_obj.pos, foco_img.pos = vector(-f, 0, 0), vector(f, 0, 0)
    rot_F.pos, rot_F2.pos = vector(-f, -1.2, 0), vector(f, -1.2, 0)

    # Raio 1: paralelo ao eixo → refrata passando por F'
    s1 = -h_obj / f                                # declive após a lente
    raio(raios[0], [topo, vector(0, h_obj, 0), vector(x_max, h_obj + s1 * x_max, 0)])
    # Raio 2: pelo centro óptico → não desvia
    s2 = -h_obj / p
    raio(raios[1], [topo, vector(x_max, h_obj + s2 * (x_max + p), 0)])
    # Raio 3: passando por F → sai paralelo ao eixo
    y3 = -h_obj * f / (p - f) if abs(p - f) > 1e-6 else 1e3
    raio(raios[2], [topo, vector(0, y3, 0), vector(x_max, y3, 0)])

    p_img, aumento = gauss(p, f)
    if p_img == float("inf"):
        imagem.visible = False
        painel.text = "p = f: os raios saem paralelos — imagem no infinito"
        for c in prolong:
            c.clear()
        return
    h_img = aumento * h_obj
    imagem.visible = True
    imagem.pos, imagem.axis = vector(p_img, 0, 0), vector(0, h_img, 0)
    if p_img > 0:                                  # imagem real
        imagem.opacity = 1
        for c in prolong:
            c.clear()
        natureza = "REAL, invertida"
    else:                                          # imagem virtual (lupa)
        imagem.opacity = 0.4
        fim = vector(p_img, h_img, 0)
        raio(prolong[0], [vector(0, h_obj, 0), fim])
        raio(prolong[1], [topo, fim])
        raio(prolong[2], [vector(0, y3, 0), fim])
        natureza = "VIRTUAL, direita"
    painel.text = (f"f = {f:.1f} cm   p = {p:.1f} cm   →   p' = {p_img:.1f} cm   "
                   f"A = {aumento:+.2f}   imagem {natureza}")


# %% [4] Controles deslizantes e laço de espera
def mudar_p(s):
    global p
    p = s.value
    atualizar()


def mudar_f(s):
    global f
    f = s.value
    atualizar()


scene.append_to_caption("\nDistância do objeto p (cm): ")
slider(min=2, max=50, value=p, step=0.5, length=400, bind=mudar_p)
scene.append_to_caption("\n\nDistância focal f (cm):        ")
slider(min=4, max=20, value=f, step=0.5, length=400, bind=mudar_f)
scene.append_to_caption("\n")

atualizar()
while True:
    rate(30)
