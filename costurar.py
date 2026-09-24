#!/usr/bin/env python3
"""ETAPA 1 — junta as fotos de fotos/ num panorama unico.

    .venv/bin/python costurar.py                 # fotos/  ->  panorama.jpg
    .venv/bin/python costurar.py --pasta outra   # outra pasta de fotos

ESTE ARQUIVO RODA E ESTA ERRADO DE PROPOSITO.

Rode-o antes de mexer em qualquer coisa. Ele vai produzir um panorama.jpg
com as fotos empilhadas em posicoes chutadas: linhas partidas no meio, poste
cortado, telhado que nao continua. Olhe o resultado. E esse resultado que
voce foi contratado para consertar.

O que esta pronto aqui: ler as fotos em ordem, converter para numpy, colar
uma ao lado da outra, cronometrar e gravar o JPEG. Encanamento.

O que falta e so isto, e e o trabalho todo:

    deslocamento(a, b)  ->  hoje devolve um chute fixo.
                            Tem de DESCOBRIR quantos pixels a foto b esta
                            deslocada em relacao a foto a.

    colar(...)          ->  hoje sobrescreve. A emenda aparece como uma
                            barra vertical. Some as duas na faixa comum.

Leia a secao 8 do roteiro antes de comecar. A figura da curva de erro que
esta la e exatamente o que a sua funcao tem de calcular.
"""
import argparse
import os
import time

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def carregar(pasta):
    """Le as fotos JPEG da pasta, em ordem de nome, como matrizes uint8."""
    if not os.path.isdir(pasta):
        raise SystemExit("Nao existe a pasta %s/. Crie-a e ponha as fotos "
                         "la dentro, como 01.jpg, 02.jpg, ..." % pasta)
    nomes = sorted(n for n in os.listdir(pasta)
                   if n.lower().endswith((".jpg", ".jpeg")))
    if not nomes:
        raise SystemExit("Nenhum JPEG em %s/. Leia a secao 7 do roteiro." % pasta)
    fotos = []
    for n in nomes:
        with Image.open(os.path.join(pasta, n)) as img:
            fotos.append(np.asarray(img.convert("RGB")))
        print("  lida  %-24s %d x %d" % (n, fotos[-1].shape[1], fotos[-1].shape[0]))
    return nomes, fotos


# --------------------------------------------------------------------------
# >>> AQUI E O SEU TRABALHO <<<
# --------------------------------------------------------------------------
def deslocamento(a, b):
    """Quantos pixels para a direita a foto `b` esta, em relacao a `a`?

    Contrato: devolve um inteiro dx tal que a coluna dx de `a` corresponde a
    coluna 0 de `b`. Se as duas fotos tem 3024 px de largura e um terco de
    sobreposicao, o dx certo fica perto de 2016 — mas "perto" nao serve, e o
    seu programa nao pode saber isso de antemao.

    A ideia, em uma frase: para cada dx candidato, as duas fotos tem uma
    faixa em comum; sobreponha essa faixa e veja o quanto elas discordam,
    pixel a pixel. O dx de menor discordancia e a resposta.

    Tres decisoes que sao suas, e que vao ser perguntadas na apresentacao:
      1. qual o intervalo de dx que vale a pena testar, e por que nao [0, W);
      2. comparar em cor ou em cinza, com a foto inteira ou com uma faixa;
      3. como fazer isso caber em segundos, e nao em minutos. Uma dica que
         vale uma hora do seu tempo: procure primeiro numa copia reduzida
         das duas fotos, ache o dx grosso, multiplique de volta e refine
         numa vizinhanca pequena na resolucao cheia.

    A linha abaixo e um CHUTE FIXO — a mesma fracao para todo par, o que
    nenhuma mao humana consegue repetir. Apague-a.
    """
    return int(a.shape[1] * 0.55)


def colar(pano, foto, x):
    """Escreve `foto` no panorama a partir da coluna x.

    Como esta, a foto nova sobrescreve o que ja estava la, e a emenda fica
    visivel: as duas fotos nao tem exatamente o mesmo brilho nas bordas
    (vinheta da lente) e a troca e abrupta.

    O conserto: na faixa em que as duas se sobrepoem, o pixel de saida e uma
    MISTURA das duas, com peso que vai de 1 para 0 ao longo da faixa. Duas
    linhas de numpy resolvem. Descubra quais.
    """
    a = foto.shape[0]
    pano[:a, x:x + foto.shape[1]] = foto
# --------------------------------------------------------------------------


def costurar(fotos):
    alt = max(f.shape[0] for f in fotos)
    larg_total = sum(f.shape[1] for f in fotos)          # folga de sobra
    pano = np.zeros((alt, larg_total, 3), dtype=np.uint8)

    x = 0
    colar(pano, fotos[0], 0)
    direita = fotos[0].shape[1]
    print()
    print("  par        dx     tempo da busca")
    for i in range(1, len(fotos)):
        t0 = time.perf_counter()
        dx = deslocamento(fotos[i - 1], fotos[i])
        ms = (time.perf_counter() - t0) * 1000
        x += dx
        colar(pano, fotos[i], x)
        direita = max(direita, x + fotos[i].shape[1])
        print("  %2d -> %-3d %6d     %8.0f ms" % (i, i + 1, dx, ms))

    return pano[:, :direita]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pasta", default="fotos")
    ap.add_argument("--saida", default="panorama.jpg")
    ap.add_argument("--qualidade", type=int, default=90)
    args = ap.parse_args()

    print("Lendo %s/" % args.pasta)
    _nomes, fotos = carregar(args.pasta)

    t0 = time.perf_counter()
    pano = costurar(fotos)
    seg = time.perf_counter() - t0

    Image.fromarray(pano).save(args.saida, quality=args.qualidade)
    print()
    print("  panorama    %d x %d  (%.1f MP)"
          % (pano.shape[1], pano.shape[0], pano.size / 3 / 1e6))
    print("  na memoria  %.0f MB" % (pano.nbytes / 1e6))
    print("  em disco    %.1f MB  (%s, qualidade %d)"
          % (os.path.getsize(args.saida) / 1e6, args.saida, args.qualidade))
    print("  tempo       %.1f s" % seg)
    print()
    print("Agora ABRA o %s e olhe as emendas." % args.saida)


if __name__ == "__main__":
    main()
