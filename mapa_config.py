"""Configuracao compartilhada do mapa principal.

Este modulo concentra tudo o que precisa existir uma unica vez no jogo:
- ajustes de DPI que devem rodar antes de abrir a primeira janela;
- caminhos de imagens e dimensoes logicas do mapa;
- a lista de obstaculos e o dicionario da cena atual (CENA).

Os outros modulos do mapa importam estes valores em vez de repeti-los. Como
CENA e um dicionario, quem recebe a referencia consegue alterar a mesma cena
sem precisar de variaveis globais espalhadas pelo projeto.
"""

from __future__ import annotations

# builtins permite injetar "pygame" no espaco global dos modulos antigos de
# personagem, que usam pygame sem fazer o import (veja abaixo).
import builtins

# ctypes e usado para conversar com a API do Windows (DPI e area util).
import ctypes

# os permite trocar a pasta de trabalho para a raiz do projeto.
import os

# sys identifica o sistema operacional (Windows ou outro).
import sys

# Path monta caminhos de arquivo de forma segura em qualquer sistema.
from pathlib import Path

# pygame desenha o mapa, cria as superficies e mede areas na tela.
import pygame


def preparar_tela_do_sistema() -> None:
    """Ajustes que precisam acontecer antes de a primeira janela ser criada."""
    # Esses ajustes so fazem sentido no Windows; em outros sistemas o bloco e
    # ignorado e o pygame cuida da escala sozinho.
    if sys.platform == "win32":
        # Com a escala do Windows em 125%/150%, um programa que nao se declara
        # "DPI aware" e ampliado pelo sistema: fica borrado e maior que a tela.
        try:
            # SetProcessDpiAwareness(2) liga a consciencia de DPI por monitor.
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            # Em Windows antigos a funcao acima nao existe; tentamos a API
            # classica, que tambem evita a ampliacao automatica.
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                # Se nenhuma API estiver disponivel, seguimos sem o ajuste.
                pass


def area_util_da_tela() -> pygame.Rect:
    'Área do monitor que a janela pode ocupar, descontando a barra de tarefas.'
    # No Windows, a API SystemParametersInfoW devolve a "work area": a parte da
    # tela que nao esta coberta pela barra de tarefas.
    if sys.platform == "win32":
        try:
            # wintypes fornece a estrutura RECT esperada pela API do Windows.
            from ctypes import wintypes

            # area recebera os limites esquerdo, superior, direito e inferior.
            area = wintypes.RECT()

            # Codigo da consulta "obtenha a area de trabalho".
            SPI_GETWORKAREA = 0x0030

            # A chamada retorna um valor verdadeiro quando deu certo.
            if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(area), 0):
                # Convertemos a estrutura do Windows para um Rect do pygame.
                return pygame.Rect(area.left, area.top, area.right - area.left, area.bottom - area.top)
        except (AttributeError, OSError):
            # Sem a API, caimos no calculo generico logo abaixo.
            pass

    # Outros sistemas: usa o monitor inteiro e reserva 48 pixels para a barra
    # de tarefas (Windows) ou o dock (macOS/Linux).
    largura, altura = pygame.display.get_desktop_sizes()[0]
    return pygame.Rect(0, 0, largura, altura - 48)


# Executa o ajuste de DPI no momento em que este modulo e importado, antes de
# qualquer pygame.display.set_mode criar a janela.
preparar_tela_do_sistema()

# Os arquivos atuais dos personagens utilizam pygame sem importa-lo.
# A referencia abaixo permite usa-los sem editar seus modulos individuais.
builtins.pygame = pygame

# BASE_DIR e a pasta onde este arquivo esta (a raiz do projeto).
BASE_DIR = Path(__file__).resolve().parent

# Muda a pasta de trabalho para a raiz: assim os caminhos relativos usados
# pelos assets continuam funcionando mesmo que o jogo seja iniciado de fora.
os.chdir(BASE_DIR)


# ============================================================================
# CONFIGURACAO DO MAPA
# ============================================================================

# Resolucao logica do mapa antigo (o jogo desenha nesse tamanho e depois
# escala a imagem para a janela real).
LARGURA_MAPA = 720
ALTURA_MAPA = 480

# Quadros por segundo alvo do mapa.
FPS = 60

# Imagem usada na segunda cena do mapa de teste (o "Scene Overview").
MAPA_INICIAL = (
    BASE_DIR
    / "mapas"
    / "Mapa_teste"
    / "tilesets"
    / "Pixel Art Top Down - Basic v1.2.3"
    / "Scene Overview.png"
)

# Imagem do mapa inicial (mapateste.jpeg).
MAPA_CAMINHO = BASE_DIR / "assets" / "mapa_teste" / "mapateste.jpeg"

# Somente as construcoes, caixas e barris bloqueiam o movimento.
# Caminhos, escada e arvores permanecem livres para o grupo atravessar.
COLISOES_TERRENO = []
COLISOES_MAPA = [
    pygame.Rect(0, 0, 245, 120),
    pygame.Rect(535, 0, 185, 145),
    pygame.Rect(290, 255, 150, 35),
    pygame.Rect(290, 305, 150, 35),
    pygame.Rect(185, 365, 110, 60),
]

# Guarda a superficie carregada do mapa; None significa "ainda nao carregou".
MAPA_COLISAO = None

# Nome do mapa em uso no momento (usado pelo desenho provisorio).
MAPA_ATUAL = "mapateste"

# Onde o jogo comeca: "covil" (Covil do Rei Tritao, mapa animado) ou
# "mapateste" (o mapa antigo, que abre uma passagem para o covil no fim).
CENA_INICIAL = "covil"

# Passagem que se abre no mapa de teste depois de vencer todos os inimigos e
# leva o grupo ao Covil do Rei Tritao.
PASSAGEM_COVIL = pygame.Rect(568, 212, 44, 44)

# Cena em que o grupo esta: tamanho, retangulos que bloqueiam e, no covil, a
# mascara do chao (os pes so podem pisar onde a mascara marca chao).
CENA = {"tamanho": (LARGURA_MAPA, ALTURA_MAPA), "bloqueios": COLISOES_MAPA, "chao": None}
