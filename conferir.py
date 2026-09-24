#!/usr/bin/env python3
"""O juiz do trabalho pratico 01. Nao conserta nada — so diz o que esta errado.

    .venv/bin/python conferir.py --fotos fotos/
    .venv/bin/python conferir.py --piramide piramide/
    .venv/bin/python conferir.py --pontos pontos.json
    .venv/bin/python conferir.py --tudo

O que ele confere:

    --fotos      se as fotos servem: quantas sao, se tem todas o mesmo
                 tamanho, se estao na vertical, se sao grandes o bastante e
                 se a EXIF mostra exposicao/ISO/foco travados. Se a exposicao
                 variou de uma foto para a outra, voce nao travou o AE — e a
                 emenda vai aparecer.

    --piramide   se a piramide obedece ao contrato do roteiro (secao 9):
                 info.json completo, um nivel por metade, colunas e linhas
                 certas, todo tile no lugar e com o tamanho certo, inclusive
                 os parciais da ultima coluna e da ultima linha.

    --pontos     se o pontos.json tem tres pontos dentro do panorama.

No fim ele imprime os numeros que vao ser perguntados na apresentacao. Ele
NAO olha se a sua costura ficou bonita: costura feia passa aqui e perde nota na
frente da turma. As duas coisas sao diferentes.
"""
import json
import math
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None          # aqui pode: e so para medir

LADO = 256
MIN_FOTOS = 6
MIN_MP = 8.0

OK, ERRO, AVISO = "  ok  ", " ERRO ", "aviso "
_falhas = 0


def diz(marca, texto):
    global _falhas
    if marca == ERRO:
        _falhas += 1
    print("[%s] %s" % (marca, texto))


def titulo(t):
    print()
    print(t)
    print("-" * len(t))


def mb(bytes_):
    return bytes_ / 1024 / 1024


# --------------------------------------------------------------------------
# fotos
# --------------------------------------------------------------------------
def exif(img, etiqueta):
    try:
        return img.getexif().get(etiqueta)
    except Exception:
        return None


def conferir_fotos(pasta):
    titulo("FOTOS — %s" % pasta)
    if not os.path.isdir(pasta):
        diz(ERRO, "a pasta nao existe")
        return None

    nomes = sorted(n for n in os.listdir(pasta)
                   if n.lower().endswith((".jpg", ".jpeg")))
    outros = [n for n in os.listdir(pasta)
              if not n.lower().endswith((".jpg", ".jpeg")) and
              not n.startswith(".")]
    if outros:
        diz(AVISO, "tem arquivo que nao e JPEG na pasta: %s" % ", ".join(outros[:4]))
        if any(n.lower().endswith((".heic", ".heif")) for n in outros):
            diz(ERRO, "HEIC nao abre no Pillow — mude o formato da camera "
                      "para JPEG e transfira de novo (secao 5 do roteiro)")

    if len(nomes) < MIN_FOTOS:
        diz(ERRO, "%d fotos; a entrega minima sao %d" % (len(nomes), MIN_FOTOS))
    else:
        diz(OK, "%d fotos" % len(nomes))

    tamanhos, exposicoes, isos, focais = set(), set(), set(), set()
    menor_mp = 1e9
    for n in nomes:
        with Image.open(os.path.join(pasta, n)) as img:
            tamanhos.add(img.size)
            menor_mp = min(menor_mp, img.size[0] * img.size[1] / 1e6)
            exposicoes.add(str(exif(img, 33434)))
            isos.add(str(exif(img, 34855)))
            focais.add(str(exif(img, 37386)))

    if not nomes:
        return None

    if len(tamanhos) > 1:
        diz(ERRO, "as fotos tem tamanhos diferentes: %s — voce mudou de lente "
                  "ou de modo no meio do giro" % ", ".join(map(str, tamanhos)))
    else:
        l, a = tamanhos.pop()
        diz(OK, "todas em %d x %d" % (l, a))
        if l >= a:
            diz(ERRO, "as fotos estao na horizontal; o roteiro pede o celular "
                      "na VERTICAL")
        if l * a / 1e6 < MIN_MP:
            diz(ERRO, "%.1f MP por foto; o minimo e %.0f MP" % (l * a / 1e6, MIN_MP))
        else:
            diz(OK, "%.1f MP por foto" % (l * a / 1e6))
        if l * a / 1e6 < 3:
            diz(AVISO, "tamanho de foto reprocessada por aplicativo de mensagem; "
                       "transfira o original por cabo ou como ARQUIVO")

    for rotulo, conjunto in (("exposicao", exposicoes), ("ISO", isos),
                             ("distancia focal", focais)):
        if conjunto == {"None"}:
            diz(AVISO, "a EXIF nao traz %s — nao da para conferir o travamento"
                % rotulo)
        elif len(conjunto) == 1:
            diz(OK, "%s igual nas %d fotos" % (rotulo, len(nomes)))
        else:
            diz(ERRO, "%s mudou durante o giro (%d valores diferentes): o AE/AF "
                      "nao estava travado" % (rotulo, len(conjunto)))

    return {"fotos": len(nomes), "mp": menor_mp}


# --------------------------------------------------------------------------
# piramide
# --------------------------------------------------------------------------
def dims_do_nivel(largura, altura, n):
    l, a = largura, altura
    for _ in range(n):
        l, a = max(1, l // 2), max(1, a // 2)
    return l, a


def niveis_esperados(largura, altura):
    n = 0
    while True:
        l, a = dims_do_nivel(largura, altura, n)
        if math.ceil(l / LADO) == 1 and math.ceil(a / LADO) == 1:
            return n + 1
        n += 1
        if n > 40:
            return n


def conferir_piramide(pasta):
    titulo("PIRAMIDE — %s" % pasta)
    if not os.path.isdir(pasta):
        diz(ERRO, "a pasta nao existe")
        return None

    caminho = os.path.join(pasta, "info.json")
    if not os.path.exists(caminho):
        diz(ERRO, "falta o info.json")
        return None
    try:
        info = json.load(open(caminho, encoding="utf-8"))
    except Exception as e:
        diz(ERRO, "info.json ilegivel: %s" % e)
        return None

    for chave in ("largura", "altura", "tile", "niveis"):
        if chave not in info:
            diz(ERRO, "info.json sem a chave '%s'" % chave)
            return None
    largura, altura = int(info["largura"]), int(info["altura"])
    if int(info["tile"]) != LADO:
        diz(ERRO, "tile = %s; o roteiro fixa %d" % (info["tile"], LADO))
        return None

    diz(OK, "panorama de %d x %d = %.1f MP" % (largura, altura,
                                               largura * altura / 1e6))
    esperado = niveis_esperados(largura, altura)
    if int(info["niveis"]) != esperado:
        diz(ERRO, "info.json diz %s niveis; para este tamanho sao %d "
                  "(reduzir ate caber num tile so)" % (info["niveis"], esperado))
    else:
        diz(OK, "%d niveis" % esperado)

    total_tiles, total_bytes, faltando, errados = 0, 0, [], []
    print()
    print("  nivel        tamanho     grade        tiles      MB")
    for n in range(esperado):
        l, a = dims_do_nivel(largura, altura, n)
        col, lin = math.ceil(l / LADO), math.ceil(a / LADO)
        pasta_n = os.path.join(pasta, "L%d" % n)
        bytes_n, achados = 0, 0
        for c in range(col):
            for li in range(lin):
                arq = os.path.join(pasta_n, "%d_%d.jpg" % (c, li))
                if not os.path.exists(arq):
                    faltando.append("L%d/%d_%d.jpg" % (n, c, li))
                    continue
                achados += 1
                bytes_n += os.path.getsize(arq)
                esp = (min(LADO, l - c * LADO), min(LADO, a - li * LADO))
                with Image.open(arq) as t:
                    if t.size != esp:
                        errados.append("L%d/%d_%d.jpg tem %s, devia ter %s"
                                       % (n, c, li, t.size, esp))
        total_tiles += achados
        total_bytes += bytes_n
        print("  L%-3d %8d x %-6d %3d x %-3d %6d/%-6d %7.1f"
              % (n, l, a, col, lin, achados, col * lin, mb(bytes_n)))

    print()
    if faltando:
        diz(ERRO, "faltam %d tiles. Os primeiros: %s"
            % (len(faltando), ", ".join(faltando[:6])))
        diz(AVISO, "se o que falta e sempre a ultima coluna ou a ultima "
                   "linha, o seu corte esta arredondando para baixo")
    else:
        diz(OK, "todos os %d tiles no lugar" % total_tiles)

    if errados:
        diz(ERRO, "%d tiles com tamanho errado. Os primeiros:" % len(errados))
        for e in errados[:5]:
            print("         " + e)
    elif total_tiles:
        diz(OK, "tamanho certo em todos, inclusive os parciais da borda")

    diz(OK, "a piramide ocupa %.1f MB em disco" % mb(total_bytes))
    print("        carregar o nivel 0 inteiro na memoria custaria %.0f MB"
          % (largura * altura * 3 / 1e6))
    return {"largura": largura, "altura": altura, "niveis": esperado,
            "tiles": total_tiles, "mb": mb(total_bytes)}


# --------------------------------------------------------------------------
# pontos
# --------------------------------------------------------------------------
def conferir_pontos(caminho, info=None):
    titulo("PONTOS — %s" % caminho)
    if not os.path.exists(caminho):
        diz(ERRO, "o arquivo nao existe")
        return
    try:
        pontos = json.load(open(caminho, encoding="utf-8"))
    except Exception as e:
        diz(ERRO, "json ilegivel: %s" % e)
        return
    if not isinstance(pontos, list) or len(pontos) < 3:
        diz(ERRO, "o roteiro pede tres pontos; achei %s"
            % (len(pontos) if isinstance(pontos, list) else "coisa que nao e lista"))
        return
    diz(OK, "%d pontos" % len(pontos))
    for i, pt in enumerate(pontos):
        falta = [c for c in ("x", "y", "titulo", "texto") if c not in pt]
        if falta:
            diz(ERRO, "ponto %d sem %s" % (i + 1, ", ".join(falta)))
            continue
        if info and not (0 <= pt["x"] < info["largura"] and
                         0 <= pt["y"] < info["altura"]):
            diz(ERRO, "ponto %d em (%s, %s) cai fora do panorama de %d x %d — "
                      "as coordenadas sao as do NIVEL 0"
                % (i + 1, pt["x"], pt["y"], info["largura"], info["altura"]))
        else:
            diz(OK, "ponto %d: %s" % (i + 1, pt["titulo"]))


# --------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    tudo = "--tudo" in args or not args

    def valor(bandeira, padrao):
        if bandeira in args:
            i = args.index(bandeira)
            return args[i + 1] if i + 1 < len(args) else padrao
        return padrao

    fotos = info = None
    if tudo or "--fotos" in args:
        fotos = conferir_fotos(valor("--fotos", "fotos"))
    if tudo or "--piramide" in args:
        info = conferir_piramide(valor("--piramide", "piramide"))
    if tudo or "--pontos" in args:
        conferir_pontos(valor("--pontos", "pontos.json"), info)

    titulo("OS NUMEROS DA APRESENTACAO")
    if fotos:
        print("  fotos usadas ................ %d" % fotos["fotos"])
        print("  megapixels por foto ......... %.1f" % fotos["mp"])
    if info:
        print("  panorama .................... %d x %d px" % (info["largura"],
                                                              info["altura"]))
        print("  megapixels do panorama ...... %.1f"
              % (info["largura"] * info["altura"] / 1e6))
        print("  RAM se abrisse tudo ......... %.0f MB"
              % (info["largura"] * info["altura"] * 3 / 1e6))
        print("  niveis / tiles .............. %d / %d" % (info["niveis"],
                                                           info["tiles"]))
        print("  piramide em disco ........... %.1f MB" % info["mb"])
    print("  os demais numeros quem mede e voce")

    print()
    if _falhas:
        print("=> %d problema(s). Conserte e rode de novo." % _falhas)
        return 1
    print("=> passou. Isto NAO quer dizer que a costura ficou boa —")
    print("   isso quem julga e o olho, na apresentacao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
