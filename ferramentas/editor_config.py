"""Constantes, geometria e tipos compartilhados pelo editor de colisao.

O editor foi dividido em quatro modulos para ficar abaixo de 500 linhas:
- editor_config.py     -> este arquivo: constantes, camadas e geometria;
- editor_dados.py      -> leitura/escrita do JSON, desfazer e busca de itens;
- editor_interacao.py  -> mouse, teclado e modo de teste;
- editor_desenho.py    -> desenho da interface.
O arquivo editor_colisao.py apenas junta as partes na classe Editor.
"""

from __future__ import annotations

# copy e usado para guardar estados antigos e permitir desfazer.
import copy

# json le e grava o arquivo de colisao.
import json

# math fornece distancia entre pontos.
import math

# sys permite acrescentar a raiz do projeto ao caminho de importacao.
import sys

# Path monta o caminho da raiz do projeto.
from pathlib import Path

# pygame fornece Rect, Surface e as funcoes de desenho.
import pygame

# PROJETO e a pasta que contem a pasta ferramentas.
PROJETO = Path(__file__).resolve().parent.parent

# Garante que "covil_tritao" e "CezarPersonagem" sejam encontrados.
sys.path.insert(0, str(PROJETO))

# Dados do mapa do covil (tamanho, pastas e arquivo de colisao).
import covil_tritao  # noqa: E402

# Tamanho logico do covil (largura e altura da tela do editor).
LARGURA, ALTURA = covil_tritao.TAMANHO

# Chave no JSON: (nome no botao, cor, e contorno? (senao retangulo), explicacao).
CAMADAS = {
    "chao": (
        'Chão', (0, 255, 120), True,
        'Onde dá para andar. Os pés do personagem precisam ficar dentro de um contorno verde.',
    ),
    "chao_posboss": (
        'Chão pós-boss', (0, 200, 255), True,
        'Chão que só passa a valer depois do Rei Tritão (o caminho até o baú). Fundo: mapa pós-boss.',
    ),
    "bloqueios": (
        "Bloqueio", (255, 140, 0), False,
        'Não dá para atravessar, mesmo em cima do chão: base de estátua, trono, baú. Use na BASE do objeto.',
    ),
    "oclusores": (
        'Passar por trás', (200, 110, 255), True,
        'Contorne o DESENHO do objeto alto. Quem anda atrás dele fica escondido. A linha amarela é a base.',
    ),
}

# Ordem dos botoes e atalhos numericos das camadas.
ORDEM_CAMADAS = list(CAMADAS)
TECLAS_CAMADA = {
    pygame.K_1: "chao",
    pygame.K_2: "chao_posboss",
    pygame.K_3: "bloqueios",
    pygame.K_4: "oclusores",
}

# Raios de tolerancia para selecionar pontos, linhas e alcas.
RAIO_PONTO = 8
RAIO_LINHA = 6
LADO_ALCA = 10

# Limite do historico de desfazer.
MAXIMO_DESFAZER = 100

# Alturas das faixas fixas da interface.
ALTURA_BARRA = 40
ALTURA_EXPLICACAO = 24
ALTURA_RODAPE = 26

# Cores da interface.
COR_PAINEL = (8, 14, 28)
COR_TEXTO = (232, 236, 245)
COR_DESTAQUE = (255, 226, 92)

# Referencia ao modulo mapa_teste, carregada apenas no modo de teste.
# Fica aqui para os modulos de interacao e desenho compartilharem o mesmo valor.
mapa_teste = None


def distancia_ate_segmento(p, a, b) -> float:
    """Menor distancia entre o ponto p e o segmento de reta a-b."""
    # Coordenadas dos pontos inicial e final do segmento.
    ax, ay = a
    bx, by = b

    # Vetor do segmento e seu comprimento ao quadrado.
    dx, dy = bx - ax, by - ay
    comprimento = dx * dx + dy * dy

    # Segmento degenerado (a == b): a distancia e ate o proprio ponto.
    if comprimento == 0:
        return math.dist(p, a)

    # Projeta p no segmento e limita o parametro entre 0 e 1.
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / comprimento))

    # Ponto mais proximo no segmento.
    return math.dist(p, (ax + t * dx, ay + t * dy))


def ponto_dentro(p, poligono) -> bool:
    """Teste do raio (par/impar): diz se o ponto esta dentro do poligono."""
    dentro = False
    x, y = p

    # Percorre cada aresta, inclusive a que liga o ultimo ponto ao primeiro.
    for (x1, y1), (x2, y2) in zip(poligono, poligono[1:] + poligono[:1]):
        # Conta quantas arestas o raio horizontal do ponto atravessa.
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            dentro = not dentro
    return dentro


def cantos(retangulo):
    """Devolve os quatro cantos de um retangulo (x, y, largura, altura)."""
    x, y, w, h = retangulo
    return [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]


class Botao:
    """Botao simples da barra superior: area, texto, acao e cor."""

    def __init__(self, retangulo: pygame.Rect, texto: str, acao, cor=(70, 90, 140)):
        # Area clicavel do botao.
        self.retangulo = retangulo

        # Texto exibido.
        self.texto = texto

        # Acao: string ("salvar", "desfazer"...) ou tupla ("camada", chave).
        self.acao = acao

        # Cor da amostra/indicador visual.
        self.cor = cor


# Reexporta copy/json para os outros modulos do editor usarem um unico import.
__all__ = [
    "copy", "json", "math", "pygame", "covil_tritao",
    "PROJETO", "LARGURA", "ALTURA", "CAMADAS", "ORDEM_CAMADAS",
    "TECLAS_CAMADA", "RAIO_PONTO", "RAIO_LINHA", "LADO_ALCA",
    "MAXIMO_DESFAZER", "ALTURA_BARRA", "ALTURA_EXPLICACAO", "ALTURA_RODAPE",
    "COR_PAINEL", "COR_TEXTO", "COR_DESTAQUE", "mapa_teste",
    "distancia_ate_segmento", "ponto_dentro", "cantos", "Botao",
]
