#musicas
# Todas as musicas passam por _tocar: assim da para desligar/ligar a trilha
# sonora (opcao do menu ou tecla M) e, ao religar, volta a musica do momento.
import pygame

_musica_ligada = True
_faixa_atual = None  # musica que deveria estar tocando agora


def _tocar(caminho):
    global _faixa_atual
    _faixa_atual = caminho
    pygame.mixer.init()
    if not _musica_ligada:
        return
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play(-1)


def musica_ligada():
    return _musica_ligada


def alternar_musica():
    """Liga/desliga a trilha sonora e devolve se ela ficou ligada."""
    global _musica_ligada
    _musica_ligada = not _musica_ligada
    if not pygame.mixer.get_init():
        return _musica_ligada
    if _musica_ligada and _faixa_atual is not None:
        pygame.mixer.music.load(_faixa_atual)
        pygame.mixer.music.play(-1)
    elif not _musica_ligada:
        pygame.mixer.music.stop()
    return _musica_ligada


def tocar_musica_batalha():
    _tocar("Trilha Sonora/Tema de Batalha.mpeg")

def tocar_musica_exploracao():
    _tocar("Trilha Sonora/Tema Exploração mapa1.mpeg")

def tocar_musica_Boss():
    _tocar("Trilha Sonora/Tema Final Boss.mpeg")

def tocar_musica_vitoria():
    _tocar("Trilha Sonora/Tema Vitória.mp3")

def tocar_musica_deepcave():
    _tocar("Trilha Sonora/Musica Exploracao Deep Cave.ogg")
