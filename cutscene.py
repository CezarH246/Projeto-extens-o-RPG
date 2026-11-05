"""Cutscenes: vídeos curtos que tocam uma vez, com som, e podem ser pulados.

Os quadros vêm de assets/cutscenes/<nome>/, gerados por
    python ferramentas/converter_video_mapa.py "video.mp4" <nome> --cutscene --fps 24
(o som do vídeo fica em audio.ogg, na mesma pasta).

Enter, Espaço, Esc ou clique pulam a cutscene. Se a música estiver desligada
(menu de opções ou tecla M), ela toca muda.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pygame

from mapa_animado import MapaAnimado

PASTA_CUTSCENES = Path(__file__).resolve().parent / "assets" / "cutscenes"
CUTSCENE_KRAKEN = PASTA_CUTSCENES / "entrar_no_covil"

TECLAS_PULAR = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE)
# Segundos até a dica "pular" aparecer, e do escurecimento no fim.
ATRASO_DICA = 1.0
DURACAO_FADE = 0.35


def carregar_camera(pasta: Path) -> list[list[float]] | None:
    """Movimento da câmera medido por ferramentas/rastrear_camera_cutscene.py."""
    arquivo = pasta / "camera.json"
    if not arquivo.is_file():
        return None
    return json.loads(arquivo.read_text(encoding="utf-8"))["quadros"]


def desenhar_personagens(tela: pygame.Surface, personagens, camera_do_quadro) -> None:
    """Desenha os personagens do mapa como se estivessem no vídeo: um ponto p
    do mapa aparece em s*p + t, e o sprite cresce junto com o zoom s."""
    s, tx, ty = camera_do_quadro
    for imagem, retangulo in personagens:
        tamanho = (max(1, round(retangulo.width * s)), max(1, round(retangulo.height * s)))
        tela.blit(pygame.transform.scale(imagem, tamanho), (round(retangulo.x * s + tx), round(retangulo.y * s + ty)))


def tocar_cutscene(
    pasta: Path,
    tela: pygame.Surface,
    apresentar: Callable[[], None],
    relogio: pygame.time.Clock,
    fps: int = 60,
    personagens: list[tuple[pygame.Surface, pygame.Rect]] | None = None,
) -> bool:
    """Toca a cutscene inteira (ou até o jogador pular).

    Desenha na `tela` lógica e chama `apresentar` a cada quadro, como as
    transições do jogo. `personagens` (imagem e retângulo no mapa, já na ordem
    de desenho) aparecem por cima do vídeo acompanhando a câmera, se a cutscene
    tiver camera.json. Devolve False se a janela pediu para fechar."""
    if not (pasta / "info.json").is_file():
        return True  # sem os quadros convertidos, simplesmente não há cutscene
    from Musicas import musica_ligada

    info = json.loads((pasta / "info.json").read_text(encoding="utf-8"))
    duracao = info["quadros"] / info["fps"]
    video = MapaAnimado(pasta, tela.get_size())
    camera = carregar_camera(pasta) if personagens else None

    som = None
    if musica_ligada() and (pasta / "audio.ogg").is_file():
        try:
            pygame.mixer.init()
            som = pygame.mixer.Sound(pasta / "audio.ogg")
            som.play()
        except pygame.error:
            som = None  # sem placa de som: a cutscene toca muda

    fonte = pygame.font.SysFont("georgia,palatinolinotype,timesnewroman", 18, italic=True)
    dica = fonte.render("Enter: pular", True, (230, 222, 200))
    tempo = 0.0
    pulou = False
    while tempo < duracao:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if som is not None:
                    som.stop()
                return False
            pular = (evento.type == pygame.KEYDOWN and evento.key in TECLAS_PULAR and not evento.mod & pygame.KMOD_ALT)
            pular = pular or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
            if pular and tempo > 0.3:  # evita pular sem querer com a tecla que abriu a luta
                pulou = True
        if pulou:
            break

        # O quadro sai pelo tempo real (como o som), mesmo se um frame atrasar.
        video.tempo = tempo
        tela.blit(video.imagem, (0, 0))
        if camera:
            quadro = min(len(camera) - 1, int(tempo * info["fps"]))
            desenhar_personagens(tela, personagens, camera[quadro])
        if tempo > ATRASO_DICA:
            dica.set_alpha(min(200, round((tempo - ATRASO_DICA) * 300)))
            tela.blit(dica, dica.get_rect(bottomright=(tela.get_width() - 18, tela.get_height() - 14)))
        # Escurece nos últimos instantes, para a batalha entrar sem tranco.
        restante = duracao - tempo
        if restante < DURACAO_FADE:
            veu = pygame.Surface(tela.get_size())
            veu.set_alpha(round(255 * (1 - restante / DURACAO_FADE)))
            tela.blit(veu, (0, 0))

        apresentar()
        tempo += relogio.tick(fps) / 1000

    if som is not None:
        som.fadeout(250)
    return True
