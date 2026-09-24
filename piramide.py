#!/usr/bin/env python3
"""ETAPA 2 — corta o panorama na piramide de tiles que o visor le.

    .venv/bin/python piramide.py                  # panorama.jpg -> piramide/

ESTE ARQUIVO RODA E ESTA INCOMPLETO DE PROPOSITO.

Rode-o e depois rode o conferir.py. Ele vai apontar dois problemas, e os dois
estao marcados aqui embaixo com >>> FALTA <<<.

O contrato da piramide esta na secao 9 do roteiro e o conferir.py cobra cada
linha dele:

    piramide/info.json     {"largura":L, "altura":A, "tile":256, "niveis":N}
    piramide/L0/c_l.jpg    o nivel 0 e o panorama em tamanho cheio
    piramide/L1/c_l.jpg    metade da largura e metade da altura do L0
    ...                    (divisao inteira: l//2, sempre pelo menos 1)
    piramide/L{N-1}/0_0.jpg  o ultimo nivel cabe num tile so

    c = coluna (0 a esquerda), l = linha (0 em cima)
    colunas = ceil(largura_do_nivel / 256)   linhas = ceil(altura / 256)
    o tile da ultima coluna e o da ultima linha sao MENORES que 256
"""
import argparse
import json
import math
import os
import time

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

LADO = 256


def escrever_info(pasta, largura, altura, niveis):
    """Isto esta pronto e correto. Nao mexa — o conferir.py le este arquivo."""
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "info.json"), "w", encoding="utf-8") as f:
        json.dump({"largura": largura, "altura": altura,
                   "tile": LADO, "niveis": niveis}, f, indent=2)


# --------------------------------------------------------------------------
# >>> AQUI E O SEU TRABALHO <<<
# --------------------------------------------------------------------------
def cortar_nivel(img, pasta):
    """Corta `img` em tiles de LADO x LADO e grava em `pasta` como c_l.jpg.

    >>> FALTA 1 <<<
    As duas divisoes abaixo arredondam PARA BAIXO. Numa imagem de 21970 px
    de largura isso descarta 210 px na ponta direita: a ultima coluna de
    tiles simplesmente nao e escrita, e o conferir.py vai listar os tiles que
    faltam. Corrija o numero de colunas e de linhas, e entao decida o que
    fazer com o tile da borda, que nao tem 256 px de lado.

    Sao duas decisoes diferentes, e a segunda tem mais de uma resposta
    defensavel. Escolha uma e saiba defende-la na apresentacao. (O conferir.py
    aceita so uma delas — descubra qual lendo o que ele cobra.)
    """
    col = img.width // LADO
    lin = img.height // LADO
    os.makedirs(pasta, exist_ok=True)
    n = 0
    for c in range(col):
        for l in range(lin):
            caixa = (c * LADO, l * LADO, (c + 1) * LADO, (l + 1) * LADO)
            img.crop(caixa).save(os.path.join(pasta, "%d_%d.jpg" % (c, l)),
                                 quality=85)
            n += 1
    return n


def construir(caminho, destino):
    img = Image.open(caminho).convert("RGB")
    largura, altura = img.size
    print("  panorama  %d x %d  (%.1f MP)" % (largura, altura,
                                              largura * altura / 1e6))

    t0 = time.perf_counter()
    total = cortar_nivel(img, os.path.join(destino, "L0"))
    print("  L0        %d tiles   %.1f s" % (total, time.perf_counter() - t0))

    # >>> FALTA 2 <<<
    # So o nivel 0 foi escrito. Faltam os outros.
    #
    # O laco que voce tem de escrever aqui: enquanto o nivel atual nao couber
    # num tile so, reduza a imagem a metade (img.resize, com Image.LANCZOS),
    # corte esse nivel novo e siga. Conte quantos niveis sairam — o numero
    # vai para o info.json.
    #
    # Antes de escrever o laco, responda no papel: quantos niveis o SEU
    # panorama vai ter? A conta e curta e esta na secao 9.
    niveis = 1

    escrever_info(destino, largura, altura, niveis)
    print("  info.json escrito com niveis=%d" % niveis)
    return niveis
# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--panorama", default="panorama.jpg")
    ap.add_argument("--destino", default="piramide")
    args = ap.parse_args()

    if not os.path.exists(args.panorama):
        raise SystemExit("Nao achei %s. Rode o costurar.py primeiro."
                         % args.panorama)

    t0 = time.perf_counter()
    construir(args.panorama, args.destino)

    bytes_ = sum(os.path.getsize(os.path.join(r, n))
                 for r, _d, arqs in os.walk(args.destino) for n in arqs)
    print()
    print("  piramide/ ocupa %.1f MB   (%.1f s)"
          % (bytes_ / 1e6, time.perf_counter() - t0))
    print()
    print("Agora rode:  .venv/bin/python conferir.py --piramide %s" % args.destino)


if __name__ == "__main__":
    main()
