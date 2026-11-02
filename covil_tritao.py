"""Covil do Rei Tritão: mapa animado (convertido de mapa_tristão.mp4 e, depois
do chefe, de mapa_tritãoposboss.mp4) e colisões.

O grupo chega pela entrada da caverna (alto, à direita), atravessa a ponte de
pedra sobre o abismo e enfrenta os guardas e o Rei Tritão na plataforma do
trono. O abismo, a água do mar, as paredes, o trono e as bases das estátuas
bloqueiam o caminho.

Todas as coordenadas estão na resolução do mapa (1280x720). As posições de
personagens são o ponto dos PÉS, assim continuam certas com qualquer tamanho
de sprite.
"""

from __future__ import annotations

import json
from pathlib import Path

import pygame

PASTA_QUADROS = Path(__file__).resolve().parent / "assets" / "mapas_animados" / "mapa_tritao"
TAMANHO = (1280, 720)

# Tamanho dos sprites (lado do quadro, em pixels) nesta escala de mapa.
# Cezar, Guilherme e guardas são desenhados em 64x64: aqui ficam em 1:1, nítidos.
TAMANHOS_SPRITES = {
    "Cezar": 64,
    "Guilherme": 64,
    "Lucas": 84,      # o bárbaro é maior que os outros (desenho original de 128 px)
    "guarda": 64,
    "rei": 140,
}
# Os sprites dobraram de tamanho em relação ao mapa antigo (32 px): a
# velocidade acompanha, para a caminhada não parecer lenta.
FATOR_VELOCIDADE = 2.0

# Colisão do covil, editável no mouse com ferramentas/editor_colisao.py:
# - "chao": polígonos onde se pode andar (os pés precisam estar dentro de um);
# - "chao_posboss": chão a mais depois do Rei Tritão (o caminho até o baú);
# - "bloqueios": retângulos [x, y, largura, altura] sobre o chão que não dá
#   para atravessar (bases do trono e das estátuas, o baú);
# - "oclusores": contornos de objetos altos (estátuas...) que o personagem pode
#   rodear por trás: com os pés acima da base (o ponto mais baixo do
#   contorno), ele é desenhado atrás do objeto.
ARQUIVO_COLISAO = PASTA_QUADROS.parent / "colisao_covil.json"


class Oclusor:
    """Pedaço do mapa redesenhado por cima de quem passa atrás dele."""

    def __init__(self, poligono: list[tuple[int, int]]):
        self.poligono = poligono
        xs = [x for x, _ in poligono]
        ys = [y for _, y in poligono]
        self.base = max(ys)
        self.area = pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
        # Branco opaco dentro do contorno e transparente fora: ao misturar com
        # BLEND_RGBA_MIN, o recorte do mapa fica só com o formato do objeto.
        self.mascara = pygame.Surface(self.area.size, pygame.SRCALPHA)
        pygame.draw.polygon(self.mascara, (255, 255, 255, 255), [(x - self.area.x, y - self.area.y) for x, y in poligono])

    def desenhar(self, tela: pygame.Surface, mapa: pygame.Surface, deslocamento: tuple[int, int] = (0, 0)) -> None:
        recorte = pygame.Surface(self.area.size, pygame.SRCALPHA)
        recorte.blit(mapa, (0, 0), self.area)
        recorte.blit(self.mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        tela.blit(recorte, (self.area.x + deslocamento[0], self.area.y + deslocamento[1]))


def carregar_colisao() -> tuple[list, list, list[pygame.Rect], list]:
    dados = json.loads(ARQUIVO_COLISAO.read_text(encoding="utf-8"))
    chao = [[tuple(ponto) for ponto in poligono] for poligono in dados["chao"]]
    chao_posboss = [[tuple(ponto) for ponto in poligono] for poligono in dados["chao_posboss"]]
    bloqueios = [pygame.Rect(retangulo) for retangulo in dados["bloqueios"]]
    oclusores = [[tuple(ponto) for ponto in poligono] for poligono in dados.get("oclusores", [])]
    return chao, chao_posboss, bloqueios, oclusores


CHAO, CHAO_POSBOSS, BLOQUEIOS, OCLUSORES = carregar_colisao()


def recarregar_colisao() -> None:
    """Relê o arquivo (depois de salvar no editor, com o jogo aberto)."""
    global CHAO, CHAO_POSBOSS, BLOQUEIOS, OCLUSORES
    CHAO, CHAO_POSBOSS, BLOQUEIOS, OCLUSORES = carregar_colisao()

# Centro da base do baú e a que distância (dos pés) o jogador consegue abri-lo.
POSICAO_BAU = (1011, 460)
ALCANCE_BAU = 75
# Depois que o Rei Tritão cai, o mapa troca para este vídeo: uma ponte de pedra
# em arco sai da saliência da ponte, passa pela ilhota do baú e chega ao
# rochedo da direita (o chão dela é o "chao_posboss" da colisão).
PASTA_QUADROS_POSBOSS = PASTA_QUADROS.parent / "mapa_tritao_posboss"

# Pés do líder ao chegar: na ponte, logo em frente à porta da caverna.
ENTRADA = (1172, 190)
# Pés do Rei Tritão, de pé diante do trono.
POSICAO_REI = (380, 420)

# Guardas que patrulham o covil: (pés x, pés y, eixo da patrulha).
# O Rei Tritão só surge no trono depois que todos eles forem derrotados.
PATRULHAS = [
    (780, 368, "horizontal"),   # na ponte, barrando a passagem
    (200, 420, "horizontal"),   # plataforma, à esquerda
    (520, 505, "horizontal"),   # plataforma, no meio (entre o círculo e as estátuas)
    (320, 662, "horizontal"),   # plataforma, embaixo
]


def criar_mascara_chao(pos_boss: bool = False) -> pygame.mask.Mask:
    """Máscara com 1 onde é chão, sem as bases bloqueadas."""
    superficie = pygame.Surface(TAMANHO, pygame.SRCALPHA)
    for poligono in CHAO + (CHAO_POSBOSS if pos_boss else []):
        pygame.draw.polygon(superficie, (255, 255, 255, 255), poligono)
    return pygame.mask.from_surface(superficie)
