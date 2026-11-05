#musicas
def tocar_musica_batalha():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Trilha Sonora/Tema de Batalha.mpeg")
    pygame.mixer.music.play(-1)

def tocar_musica_exploracao():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Trilha Sonora/Tema Exploração mapa1.mpeg")
    pygame.mixer.music.play(-1)

def tocar_musica_Boss():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Trilha Sonora/Tema Final Boss.mpeg")
    pygame.mixer.music.play(-1)

def tocar_musica_vitoria():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Trilha Sonora/Tema Vitória.mp3")
    pygame.mixer.music.play(-1)

def tocar_musica_deepcave():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("Trilha Sonora/Musica Exploracao Deep Cave.ogg")
    pygame.mixer.music.play(-1)