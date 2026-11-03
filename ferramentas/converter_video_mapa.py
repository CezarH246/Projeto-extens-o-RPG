"""Converte um vídeo (MP4 etc.) em um mapa animado para o jogo.

Uso (na pasta do projeto):
    pip install imageio-ffmpeg        # só para converter; o jogo não precisa
    python ferramentas/converter_video_mapa.py "caminho/do/video.mp4" nome_do_mapa

Gera assets/mapas_animados/<nome_do_mapa>/ com os quadros (JPEG) e o info.json,
prontos para a classe MapaAnimado (mapa_animado.py). O último segundo do vídeo
é fundido ao começo (crossfade), para o loop não dar "pulo".
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

PROJETO = Path(__file__).resolve().parent.parent


def extrair_quadros(video: Path, pasta: Path) -> tuple[list[Image.Image], float]:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(video), "-vsync", "0", str(pasta / "q_%05d.png")],
        check=True,
    )
    leitor = imageio_ffmpeg.read_frames(str(video))
    fps = next(leitor)["fps"]
    leitor.close()
    quadros = [Image.open(arquivo).convert("RGB") for arquivo in sorted(pasta.glob("q_*.png"))]
    return quadros, fps


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("nome", help="nome da pasta do mapa em assets/mapas_animados")
    parser.add_argument("--fps", type=int, default=12, help="quadros por segundo no jogo (padrão 12)")
    parser.add_argument("--largura", type=int, default=1280)
    parser.add_argument("--altura", type=int, default=720)
    parser.add_argument("--qualidade", type=int, default=90, help="qualidade do JPEG (1 a 100)")
    parser.add_argument("--transicao", type=float, default=1.0, help="segundos de crossfade no loop")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temporaria:
        quadros, fps_video = extrair_quadros(args.video, Path(temporaria))

    total = len(quadros)
    transicao = max(1, round(fps_video * args.transicao))
    emendados = []
    for i in range(total - transicao):
        if i < transicao:
            emendados.append(Image.blend(quadros[total - transicao + i], quadros[i], i / transicao))
        else:
            emendados.append(quadros[i])

    passo = max(1, round(fps_video / args.fps))
    selecionados = emendados[::passo]
    saida = PROJETO / "assets" / "mapas_animados" / args.nome
    saida.mkdir(parents=True, exist_ok=True)
    for antigo in saida.glob("quadro_*.jpg"):
        antigo.unlink()
    for indice, quadro in enumerate(selecionados):
        if quadro.size != (args.largura, args.altura):
            quadro = quadro.resize((args.largura, args.altura), Image.LANCZOS)
        # subsampling=0 guarda a cor de cada pixel (sem 4:2:0): bordas de pixel art nítidas.
        quadro.save(saida / f"quadro_{indice:03d}.jpg", quality=args.qualidade, subsampling=0, optimize=True)
    fps_final = round(fps_video / passo)
    info = {"fps": fps_final, "largura": args.largura, "altura": args.altura, "quadros": len(selecionados)}
    (saida / "info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    tamanho = sum(p.stat().st_size for p in saida.glob("quadro_*.jpg"))
    print(
        f"{saida}: {len(selecionados)} quadros, {fps_final} fps, "
        f"{len(selecionados) / fps_final:.1f} s em loop, {tamanho / 1e6:.1f} MB"
    )


if __name__ == "__main__":
    main()
