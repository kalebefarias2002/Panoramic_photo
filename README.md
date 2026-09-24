# Trabalho prático 01 — panorama navegável

O enunciado completo é o **`projeto_panorama.pdf`**, que veio junto nesta
entrega. Leia-o antes de abrir qualquer arquivo daqui. Este README só diz o que
é cada coisa e como fazer rodar.

## Preparar o ambiente (uma vez)

```bash
cd panorama
python3 -m venv .venv
.venv/bin/pip install numpy pillow
```

Daqui em diante, **rode tudo com `.venv/bin/python`**, nunca com `python3`
direto — é o mesmo combinado dos programas da aula 03 e do DOOM.

Tkinter já vem com o Python; não precisa instalar.

## Os arquivos

| arquivo | o que é |
|---|---|
| `costurar.py` | etapa 1. **Roda e está errado de propósito**: cola as fotos em posições chutadas. Você escreve as duas funções que faltam. |
| `piramide.py` | etapa 2. **Roda e está incompleto**: escreve só o nível 0, e mesmo esse com a borda faltando. Duas lacunas marcadas com `>>> FALTA <<<`. |
| `visor.py` | etapa 3. **Roda e está errado de propósito**: abre o panorama inteiro na memória. Olhe o rodapé e entenda o problema antes de reescrever. |
| `conferir.py` | o juiz. Este está **pronto e correto**. Não precisa mexer, e não adianta mexer. |
| `fotos/` | ponha aqui as suas fotos, em ordem de nome: `01.jpg`, `02.jpg`, ... |

## A ordem

```bash
.venv/bin/python conferir.py --fotos fotos/     # as fotos servem?
.venv/bin/python costurar.py                    # fotos/ -> panorama.jpg
.venv/bin/python piramide.py                    # panorama.jpg -> piramide/
.venv/bin/python conferir.py --piramide piramide/
.venv/bin/python visor.py
```

Rode o `conferir.py --fotos` **ainda no dia da captura**, antes de sair do
lugar. Ele leva dois segundos e evita a viagem de volta.

```
costurar.py  piramide.py  visor.py  pontos.json
fotos/                  as originais, sem reduzir
panorama.jpg            o resultado da sua costura
piramide/               com o info.json
```

**Sem o `.venv`** — ele não é portátil e pesa centenas de MB. Quem precisar
recriar usa o comando lá de cima.
