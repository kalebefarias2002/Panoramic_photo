#!/usr/bin/env python3
"""ETAPA 3 — a janela que navega pelo panorama.

    .venv/bin/python visor.py                 # abre panorama.jpg
    .venv/bin/python visor.py --piramide piramide/     # e o que voce vai fazer

ESTE VISOR ESTA ERRADO DE PROPOSITO, E O ERRO E O ASSUNTO DA ETAPA.

Ele abre o panorama INTEIRO na memoria e recorta o pedaco que cabe na janela.
Funciona com uma imagem pequena. Com a sua, olhe o rodape: ele diz quantos MB
o processo comeu so para mostrar 0,7 megapixel de cada vez. Se o Pillow
recusar a imagem antes mesmo de abrir, leia o sintoma 1 da secao 13 — a
mensagem que ele da tem um numero dentro, e esse numero e a resposta.

O que voce vai escrever no lugar:

    - ler o piramide/info.json e trabalhar por NIVEL, nao com a imagem toda;
    - a cada desenho, calcular QUAIS tiles a janela cobre e ler so esses;
    - guardar num dicionario os tiles ja lidos, para nao reler do disco a
      cada movimento do mouse;
    - roda do mouse (ou + e -) troca de nivel.

A conta de quais tiles aparecem, em palavras — o codigo e com voce:
a coluna do primeiro tile visivel e a parte inteira do deslocamento dividida
por 256; dai em diante voce precisa de tantas colunas quantas couberem na
largura da janela, mais uma, porque quase sempre sobra um tile pela metade em
cada ponta. Para as linhas, a mesma coisa com a altura.

E a armadilha do zoom: ao subir um nivel a imagem tem metade do tamanho, mas
o ponto que estava no centro da tela tem de continuar no centro. O
deslocamento nao pode ficar como estava. Descubra a conta — sao duas linhas,
e errar nelas e o defeito mais comum deste trabalho.

REGRAS DA JANELA (valem nota):
    - nada de caixinha colorida, nada de frase explicando o obvio na tela;
    - o rodape e UMA linha monoespacada com numeros;
    - o rodape mostra: nivel, posicao, tiles em memoria, tiles lidos do
      disco desde que abriu, e os ms do ultimo desenho.
"""
import argparse
import os
import time
import tkinter as tk

from PIL import Image, ImageTk

JANELA_L, JANELA_A = 1000, 700
FUNDO = "#16202e"


class Visor:
    def __init__(self, raiz, caminho):
        self.caminho = caminho
        t0 = time.perf_counter()
        try:
            self.img = Image.open(caminho).convert("RGB")
        except Image.DecompressionBombError as e:
            raise SystemExit(
                "O Pillow recusou a imagem:\n  %s\n\n"
                "Isto nao e um defeito do Pillow. Leia o sintoma 1 da secao 13\n"
                "do roteiro: ha duas saidas, e uma delas e a que este trabalho\n"
                "esta pedindo." % e)
        self.abriu_ms = (time.perf_counter() - t0) * 1000
        self.ox, self.oy = 0, 0
        self.arrasto = None
        self.ms = 0.0

        raiz.title("Panorama — %s" % os.path.basename(caminho))
        raiz.configure(bg=FUNDO)
        self.canvas = tk.Canvas(raiz, width=JANELA_L, height=JANELA_A,
                                bg=FUNDO, highlightthickness=0)
        self.canvas.pack()
        self.rodape = tk.Label(raiz, text="", anchor="w", bg=FUNDO, fg="#c7dbff",
                               font=("DejaVu Sans Mono", 10), padx=8, pady=4)
        self.rodape.pack(fill="x")

        self.canvas.bind("<Button-1>", self.pegar)
        self.canvas.bind("<B1-Motion>", self.mover)
        self.canvas.bind("<Configure>", lambda _e: self.desenhar())
        raiz.bind("<Escape>", lambda _e: raiz.destroy())

    # ---- navegacao -------------------------------------------------------
    def pegar(self, e):
        self.arrasto = (e.x, e.y, self.ox, self.oy)

    def mover(self, e):
        x0, y0, ox, oy = self.arrasto
        self.ox = ox - (e.x - x0)
        self.oy = oy - (e.y - y0)
        self.limitar()
        self.desenhar()

    def limitar(self):
        self.ox = max(0, min(self.ox, max(0, self.img.width - JANELA_L)))
        self.oy = max(0, min(self.oy, max(0, self.img.height - JANELA_A)))

    # ---- desenho ---------------------------------------------------------
    def desenhar(self):
        t0 = time.perf_counter()
        # E AQUI que esta o erro: o recorte sai da imagem inteira, que ja
        # esta toda na RAM. Troque isto pela montagem a partir dos tiles.
        pedaco = self.img.crop((self.ox, self.oy,
                                self.ox + JANELA_L, self.oy + JANELA_A))
        self.tk_img = ImageTk.PhotoImage(pedaco)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.ms = (time.perf_counter() - t0) * 1000
        self.status()

    def status(self):
        ram = self.img.width * self.img.height * 3 / 1e6
        self.rodape.config(text=(
            "%d x %d  %.1f MP | RAM da imagem %.0f MB | abertura %.0f ms | "
            "pos %d,%d | desenho %.0f ms | tiles 0/0  <- o visor certo "
            "preenche esta ultima coluna"
            % (self.img.width, self.img.height,
               self.img.width * self.img.height / 1e6, ram, self.abriu_ms,
               self.ox, self.oy, self.ms)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--panorama", default="panorama.jpg")
    ap.add_argument("--piramide", default=None,
                    help="a pasta da piramide — quando o seu visor souber ler")
    args = ap.parse_args()

    if args.piramide:
        raise SystemExit(
            "Ainda nao. Ler a piramide e a etapa 3 do trabalho — veja o\n"
            "cabecalho deste arquivo e a secao 10 do roteiro.")
    if not os.path.exists(args.panorama):
        raise SystemExit("Nao achei %s. Rode o costurar.py primeiro."
                         % args.panorama)

    raiz = tk.Tk()
    Visor(raiz, args.panorama)
    raiz.mainloop()


if __name__ == "__main__":
    main()
