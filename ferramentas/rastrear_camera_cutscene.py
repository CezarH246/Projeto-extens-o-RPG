"""Mede o movimento da câmera de uma cutscene em relação a um mapa do jogo.

Uso (na pasta do projeto):
    python ferramentas/rastrear_camera_cutscene.py <pasta_da_cutscene> <pasta_do_mapa>
    ex.: python ferramentas/rastrear_camera_cutscene.py assets/cutscenes/entrar_no_covil "assets/mapas_animados/mapa_covil_tritão"

Para cada quadro da cutscene acha o zoom `s` e o deslocamento `t` em que o mapa
encaixa no vídeo (um ponto p do mapa aparece em s*p + t). A comparação usa as
bordas da imagem, para raios e mudanças de luz não atrapalharem. Os valores são
suavizados (a câmera do vídeo anda de forma contínua) e gravados em camera.json,
que cutscene.py usa para desenhar os personagens acompanhando a câmera.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

LARGURA, ALTURA = 1280, 720
REDUCAO = 4  # a busca é feita em 1/4 da resolução (320x180)
GRAU_SUAVIZACAO = 3  # a curva da câmera é ajustada por um polinômio deste grau


def bordas(imagem: Image.Image) -> np.ndarray:
    pequena = imagem.convert("L").resize((LARGURA // REDUCAO, ALTURA // REDUCAO), Image.BILINEAR)
    g = np.asarray(pequena.filter(ImageFilter.GaussianBlur(1)), dtype=np.float32)
    e = np.abs(np.diff(g, axis=1, prepend=g[:, :1])) + np.abs(np.diff(g, axis=0, prepend=g[:1]))
    return (e - e.mean()) / (e.std() + 1e-6)


def encaixar(mapa: Image.Image, quadro: np.ndarray, escalas) -> tuple[float, float, float, float]:
    """(confiança, s, tx, ty): o mapa ampliado por s e deslocado por t cobre o quadro."""
    espectro = np.fft.rfft2(quadro)
    melhor = (-1e9, 1.0, 0.0, 0.0)
    for s in escalas:
        w, h = round(LARGURA * s), round(ALTURA * s)
        base = ((LARGURA - w) / 2, (ALTURA - h) / 2)
        tela = Image.new("RGB", (LARGURA, ALTURA))
        tela.paste(mapa.resize((w, h), Image.BILINEAR), (round(base[0]), round(base[1])))
        b = bordas(tela)
        correlacao = np.fft.irfft2(espectro * np.conj(np.fft.rfft2(b)), s=b.shape)
        iy, ix = np.unravel_index(np.argmax(correlacao), correlacao.shape)
        pico = correlacao[iy, ix] / b.size
        if pico > melhor[0]:
            altura_busca, largura_busca = b.shape
            dy = iy if iy < altura_busca // 2 else iy - altura_busca
            dx = ix if ix < largura_busca // 2 else ix - largura_busca
            melhor = (float(pico), float(s), dx * REDUCAO + base[0], dy * REDUCAO + base[1])
    return melhor


def main() -> None:
    pasta_cutscene, pasta_mapa = Path(sys.argv[1]), Path(sys.argv[2])
    quadros_mapa = sorted(pasta_mapa.glob("quadro_*.jpg")) or sorted(pasta_mapa.glob("frame_*.jpg"))
    mapa = Image.open(quadros_mapa[0]).convert("RGB").resize((LARGURA, ALTURA))
    quadros = sorted(pasta_cutscene.glob("quadro_*.jpg"))

    medidas = []
    s_anterior = 1.0
    for n, arquivo in enumerate(quadros):
        # A câmera muda pouco de um quadro para o outro: busca o zoom perto do anterior.
        escalas = np.arange(max(0.7, s_anterior - 0.04), s_anterior + 0.041, 0.005) if n else np.arange(0.8, 1.41, 0.01)
        confianca, s, tx, ty = encaixar(mapa, bordas(Image.open(arquivo)), escalas)
        s_anterior = s
        medidas.append((n, confianca, s, tx, ty))
        if n % 24 == 0:
            print(f"{n / 24:5.2f}s  zoom {s:.3f}  deslocamento ({tx:7.1f}, {ty:6.1f})  confiança {confianca:.2f}")

    # Suaviza com um polinômio ponderado pela confiança (quadros duvidosos pesam menos).
    n = np.array([m[0] for m in medidas], dtype=float)
    peso = np.clip(np.array([m[1] for m in medidas]), 0.05, None)
    curvas = [np.polyval(np.polyfit(n, [m[k] for m in medidas], GRAU_SUAVIZACAO, w=peso), n) for k in (2, 3, 4)]
    camera = [[round(float(s), 4), round(float(tx), 2), round(float(ty), 2)] for s, tx, ty in zip(*curvas)]
    destino = pasta_cutscene / "camera.json"
    destino.write_text(json.dumps({"mapa": pasta_mapa.name, "quadros": camera}), encoding="utf-8")
    print(f"{destino}: {len(camera)} quadros")


if __name__ == "__main__":
    main()
