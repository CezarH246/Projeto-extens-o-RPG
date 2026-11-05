"""Deixa um mapa animado com poucos quadros mais lento e suave.

Uso (na pasta do projeto):
    python ferramentas/suavizar_mapa_animado.py <pasta_do_mapa> [--passos 6] [--fps 10]
    ex.: python ferramentas/suavizar_mapa_animado.py "assets/mapas_animados/mapa_covil_tritão"

Com poucos quadros (ex.: 10 imagens frame_*.jpg), a animação dá voltas rápidas
e "pula" de uma imagem para a outra. Este script cria `passos` quadros de
transição entre cada par vizinho (inclusive do último de volta ao primeiro,
fechando o loop) e grava tudo como quadro_*.jpg + info.json na mesma pasta. As
imagens originais ficam intactas; o jogo (mapa_animado.py) usa os quadro_*.jpg
quando eles existem. Para desfazer, basta apagar os quadro_*.jpg e o info.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--passos", type=int, default=6, help="quadros gerados entre cada par de originais")
    parser.add_argument("--fps", type=int, default=10, help="quadros por segundo no jogo")
    parser.add_argument("--qualidade", type=int, default=92, help="qualidade do JPEG (1 a 100)")
    args = parser.parse_args()

    originais = sorted(args.pasta.glob("frame_*.jpg")) or sorted(args.pasta.glob("frame_*.png"))
    if len(originais) < 2:
        raise SystemExit(f"Preciso de pelo menos 2 imagens frame_* em {args.pasta}")
    imagens = [Image.open(arquivo).convert("RGB") for arquivo in originais]
    tamanho = imagens[0].size

    for antigo in args.pasta.glob("quadro_*.jpg"):
        antigo.unlink()
    indice = 0
    for n, atual in enumerate(imagens):
        seguinte = imagens[(n + 1) % len(imagens)]  # o último emenda no primeiro
        for passo in range(args.passos):
            quadro = Image.blend(atual, seguinte, passo / args.passos)
            if quadro.size != tamanho:
                quadro = quadro.resize(tamanho, Image.LANCZOS)
            quadro.save(args.pasta / f"quadro_{indice:03d}.jpg", quality=args.qualidade, subsampling=0, optimize=True)
            indice += 1

    info = {"fps": args.fps, "largura": tamanho[0], "altura": tamanho[1], "quadros": indice}
    (args.pasta / "info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"{args.pasta}: {len(imagens)} originais -> {indice} quadros, {args.fps} fps, {indice / args.fps:.1f} s em loop")


if __name__ == "__main__":
    main()
