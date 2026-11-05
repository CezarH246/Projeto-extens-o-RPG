"""Efeitos de transicao reutilizaveis entre cenas do jogo."""

from collections.abc import Callable
from typing import Literal

import pygame


def executar_transicao(
    tela: pygame.Surface,
    desenhar: Callable[[], None],
    apresentar: Callable[[], None],
    relogio: pygame.time.Clock,
    fps: int = 60,
    direcao: Literal["fechar", "abrir"] = "fechar",
    duracao: float = 0.45,
) -> bool:
    """Fecha ou revela uma cena com um mosaico de blocos pretos.

    Retorna False se a janela receber um pedido para fechar durante o efeito.
    """
    colunas, linhas = 12, 8
    largura, altura = tela.get_size()
    quadros = max(8, round(fps * duracao))
    faixas = []

    for linha in range(linhas):
        for coluna in range(colunas):
            centro_x = (coluna + 0.5) / colunas
            centro_y = (linha + 0.5) / linhas
            distancia = max(abs(centro_x - 0.5), abs(centro_y - 0.5)) * 2
            faixa = min(quadros - 1, int(distancia * quadros))
            faixas.append((faixa, coluna, linha))

    for quadro in range(quadros):
        if pygame.event.get(pygame.QUIT):
            return False

        desenhar()
        for faixa, coluna, linha in faixas:
            coberto = faixa <= quadro if direcao == "fechar" else faixa > quadro
            if coberto:
                esquerda = coluna * largura // colunas
                topo = linha * altura // linhas
                direita = (coluna + 1) * largura // colunas
                base = (linha + 1) * altura // linhas
                pygame.draw.rect(
                    tela,
                    (0, 0, 0),
                    (esquerda, topo, direita - esquerda, base - topo),
                )

        apresentar()
        relogio.tick(fps)

    return True
