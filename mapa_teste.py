"""Mapa principal do jogo.

Substitua integralmente o arquivo mapa_teste.py por este conteúdo.
Quando o grupo encosta em um inimigo, este arquivo abre batalha_ui.py.
A tela de batalha usa o fundo, os sprites animados e as regras de Combate.py.
"""

from __future__ import annotations

import builtins
import os
from pathlib import Path

import pygame

# Os arquivos atuais dos personagens utilizam pygame sem importá-lo.
# A referência abaixo permite usá-los sem editar seus módulos individuais.
builtins.pygame = pygame

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

from CezarPersonagem import Cezar
from LucasPersonagem import Lucas
from GuilhermePersonagem import Guilherme
from InimigoPersonagem import InimigoPeixe
from Combate import criar_herois
from batalha_ui import ALTURA as ALTURA_COMBATE
from batalha_ui import LARGURA as LARGURA_COMBATE
from batalha_ui import criar_batalha


# ============================================================================
# CONFIGURAÇÃO DO MAPA
# ============================================================================

LARGURA_MAPA = 720
ALTURA_MAPA = 480
FPS = 60
MAPA_INICIAL = (
    BASE_DIR
    / "mapas"
    / "Mapa_teste"
    / "tilesets"
    / "Pixel Art Top Down - Basic v1.2.3"
    / "Scene Overview.png"
)
MAPA_CAMINHO = BASE_DIR / "assets" / "mapa_teste" / "mapateste.jpeg"

# Paredes, arvores e pilares do mapa. Caminhos, escadas e objetos decorativos
# permanecem livres para o grupo atravessar.
COLISOES_TERRENO = []
COLISOES_CAMINHO = [
    pygame.Rect(0, 0, 245, 120),
    pygame.Rect(290, 255, 150, 35),
    pygame.Rect(185, 365, 110, 60),
    pygame.Rect(350, 390, 370, 90),
]

MAPA_COLISAO = None
MAPA_ATUAL = "mapateste"
ESCADAS = [
    pygame.Rect(365, 78, 75, 82),
    pygame.Rect(190, 250, 70, 55),
    pygame.Rect(545, 300, 65, 80),
    pygame.Rect(315, 315, 55, 70),
    pygame.Rect(455, 500, 60, 70),
    pygame.Rect(430, 450, 100, 120),
    pygame.Rect(175, 520, 60, 70),
    pygame.Rect(545, 570, 65, 80),
]
ESCADA_CAMINHO = pygame.Rect(590, 75, 90, 65)
CHEGADA_CAMINHO = pygame.Rect(0, 360, 120, 120)


# ============================================================================
# FUNÇÕES DE MAPA E COLISÃO
# ============================================================================


def carregar_mapa() -> pygame.Surface | None:
    """Carrega o mapa novo que recebe o grupo ao fim do caminho."""
    global MAPA_COLISAO
    candidatos = [
        MAPA_INICIAL,
    ]

    for caminho in candidatos:
        if caminho.exists():
            try:
                imagem = pygame.image.load(caminho).convert()
                imagem = pygame.transform.smoothscale(imagem, (900, 600))
                MAPA_COLISAO = imagem.subsurface(pygame.Rect(90, 60, LARGURA_MAPA, ALTURA_MAPA)).copy()
                return MAPA_COLISAO
            except pygame.error:
                continue
    return None


def carregar_mapa_caminho() -> pygame.Surface | None:
    global MAPA_ATUAL
    global MAPA_COLISAO
    MAPA_ATUAL = "mapateste"
    try:
        imagem = pygame.image.load(MAPA_CAMINHO).convert()
        MAPA_COLISAO = pygame.transform.smoothscale(imagem, (LARGURA_MAPA, ALTURA_MAPA))
        return MAPA_COLISAO
    except pygame.error:
        return None

def desenhar_mapa_provisorio(tela: pygame.Surface) -> None:
    """Mantém o jogo funcional caso a imagem de mapa não seja encontrada."""
    if getattr(Jogo, "mapa_atual", "Casa_teste") == "Casa_teste":
        tela.fill((92, 72, 56))
        pygame.draw.rect(tela, (184, 163, 125), (32, 32, 776, 416))
        pygame.draw.rect(tela, (117, 96, 73), (32, 32, 776, 416), 8)
        pygame.draw.rect(tela, (72, 55, 44), (646, 100, 96, 56))
        pygame.draw.rect(tela, (213, 177, 79), (650, 104, 88, 48), 4)
        for x in range(90, 780, 64):
            pygame.draw.line(tela, (169, 145, 108), (x, 40), (x, 440), 1)
        for y in range(40, 440, 64):
            pygame.draw.line(tela, (169, 145, 108), (40, y), (800, y), 1)
        return

    tela.fill((96, 115, 38))

    # Caminhos de pedra aproximados do mapa de referência.
    pedras = [
        (280, 0, 280, 75),
        (450, 75, 130, 170),
        (0, 210, 250, 38),
        (95, 248, 125, 135),
        (220, 175, 52, 86),
    ]
    for pedra in pedras:
        pygame.draw.rect(tela, (150, 150, 130), pedra)
        pygame.draw.rect(tela, (110, 110, 92), pedra, 1)

    # Desenha referências visuais para os mesmos objetos que bloqueiam o movimento.
    for obstaculo in COLISOES_TERRENO:
        pygame.draw.rect(tela, (79, 70, 59), obstaculo)
        pygame.draw.rect(tela, (45, 40, 35), obstaculo, 2)


def retangulo_colisao(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """A colisão usa uma área menor que o sprite, para um movimento natural."""
    return sprite.rect.inflate(-8, -8)


def colide_com_terreno(rect: pygame.Rect) -> bool:
    limites_mapa = pygame.Rect(0, 0, LARGURA_MAPA, ALTURA_MAPA)
    if not limites_mapa.contains(rect):
        return True
    if MAPA_ATUAL == "mapateste":
        if ESCADA_CAMINHO.colliderect(rect):
            return False
        return any(rect.colliderect(obstaculo) for obstaculo in COLISOES_CAMINHO)
    if MAPA_COLISAO is None:
        return any(rect.colliderect(obstaculo) for obstaculo in COLISOES_TERRENO)

    if any(escada.colliderect(rect) for escada in ESCADAS):
        return False

    pontos_borda = []
    for linha in range(5):
        y = rect.top + round(rect.height * linha / 4)
        for coluna in range(5):
            x = rect.left + round(rect.width * coluna / 4)
            pontos_borda.append((x, y))

    for ponto in pontos_borda:
        vermelho, verde, azul, _ = MAPA_COLISAO.get_at(ponto)
        fundo_cinza = max(vermelho, verde, azul) < 90 and max(vermelho, verde, azul) - min(vermelho, verde, azul) < 12
        if fundo_cinza:
            return True

    for ponto in (rect.center, rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
        vermelho, verde, azul, _ = MAPA_COLISAO.get_at(ponto)
        pedra_escura = 90 <= min(vermelho, verde, azul) <= 119 and max(vermelho, verde, azul) - min(vermelho, verde, azul) < 38
        if pedra_escura:
            return True
    return False


def mover_com_colisao(sprite: pygame.sprite.Sprite, dx: float, dy: float) -> bool:
    """Move separadamente em X e Y para permitir deslizar pelos obstáculos."""
    movimentou = False

    if dx:
        x_anterior = sprite.posicao.x
        sprite.posicao.x += dx
        sprite.rect.x = round(sprite.posicao.x)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.x = x_anterior
            sprite.rect.x = round(sprite.posicao.x)
        else:
            movimentou = True

    if dy:
        y_anterior = sprite.posicao.y
        sprite.posicao.y += dy
        sprite.rect.y = round(sprite.posicao.y)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.y = y_anterior
            sprite.rect.y = round(sprite.posicao.y)
        else:
            movimentou = True

    return movimentou


def personagem_atras_de_oclusor(sprite: pygame.sprite.Sprite) -> bool:
    if MAPA_COLISAO is None or not isinstance(sprite, (Cezar, Lucas, Guilherme)):
        return False

    area = sprite.rect.inflate(-4, -4)
    for linha in range(3):
        y = max(0, min(MAPA_COLISAO.get_height() - 1, area.top + round(area.height * linha / 2)))
        for coluna in range(3):
            x = max(0, min(MAPA_COLISAO.get_width() - 1, area.left + round(area.width * coluna / 2)))
            vermelho, verde, azul, _ = MAPA_COLISAO.get_at((x, y))
            vegetacao = verde > vermelho + 5 and verde > azul + 20 and verde < 125
            pilar = 90 <= min(vermelho, verde, azul) <= 135 and max(vermelho, verde, azul) - min(vermelho, verde, azul) < 12
            if vegetacao or pilar:
                return True
    return False


def atualizar_animacao(sprite: pygame.sprite.Sprite, direcao: pygame.Vector2, tempo_frame: float) -> None:
    """Utiliza as animações de caminhada que já existem nos sprites do mapa."""
    if direcao.length_squared() == 0:
        sprite.quadro_animacao = 0
        sprite.tempo_animacao = 0
        sprite.image = sprite.imagens_parado[sprite.direcao_atual]
        return

    if abs(direcao.x) > abs(direcao.y):
        sprite.direcao_atual = "east" if direcao.x > 0 else "west"
    else:
        sprite.direcao_atual = "south" if direcao.y > 0 else "north"

    sprite.tempo_animacao += tempo_frame
    if sprite.tempo_animacao >= sprite.velocidade_animacao:
        sprite.tempo_animacao -= sprite.velocidade_animacao
        total = len(sprite.imagens_caminhada[sprite.direcao_atual])
        sprite.quadro_animacao = (sprite.quadro_animacao + 1) % total

    sprite.image = sprite.imagens_caminhada[sprite.direcao_atual][sprite.quadro_animacao]


def registrar_posicao(sprite: pygame.sprite.Sprite) -> None:
    """Mantém o caminho que será seguido pelos dois companheiros."""
    sprite.historico_posicoes.append(pygame.Vector2(sprite.posicao))
    if len(sprite.historico_posicoes) > 100:
        sprite.historico_posicoes.pop(0)


# ============================================================================
# JOGO PRINCIPAL
# ============================================================================


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_MAPA, ALTURA_MAPA))
        pygame.display.set_caption("RPG Saga dos Falidos - Mapa")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 23)
        self.fonte_auxiliar = pygame.font.SysFont(None, 18)

        self.mapa_imagem = carregar_mapa_caminho()
        self.rodando = True
        self.modo = "mapa"
        self.mostrar_colisoes = False
        self.batalha = None
        self.inimigo_em_batalha = None
        self.mensagem = "WASD: mover | Encoste no inimigo para lutar | F3: colisões"
        self.mapa_atual = "mapateste"

        self.grupo_herois = pygame.sprite.Group()
        self.grupo_inimigos = pygame.sprite.Group()
        self.grupo_objetos = pygame.sprite.Group()
        self.criar_personagens()

        # Estes mesmos objetos são enviados à batalha e preservam nível, HP, PA, XP e poções.
        self.herois_combate = criar_herois()

    def criar_personagens(self) -> None:
        self.cezar = Cezar()
        self.lucas = Lucas(self.cezar)
        self.guilherme = Guilherme(self.lucas)

        posicoes = [(250, 150), (285, 150), (320, 150)]
        for personagem, posicao in zip((self.cezar, self.lucas, self.guilherme), posicoes):
            personagem.posicao = pygame.Vector2(posicao)
            personagem.rect.topleft = posicao
            personagem.historico_posicoes = [pygame.Vector2(posicao)]

        self.grupo_herois.add(self.cezar, self.lucas, self.guilherme)

        self.grupo_objetos.add(self.grupo_herois, self.grupo_inimigos)

    def criar_inimigos_casa(self) -> None:
        inimigos = [
            InimigoPeixe(420, 155, eixo="horizontal"),
            InimigoPeixe(670, 180, eixo="vertical"),
        ]
        for inimigo in inimigos:
            inimigo.quantidade_combate = 3
            self.grupo_inimigos.add(inimigo)

    def criar_inimigos_mapa_teste(self) -> None:
        inimigos = [
            InimigoPeixe(375, 100, eixo="horizontal"),
            InimigoPeixe(120, 250, eixo="vertical"),
            InimigoPeixe(550, 300, eixo="horizontal"),
            InimigoPeixe(550, 400, eixo="vertical"),
        ]
        for inimigo in inimigos:
            inimigo.quantidade_combate = 3
            self.grupo_inimigos.add(inimigo)
        self.grupo_objetos.add(self.grupo_inimigos)

    def trocar_para_mapa_teste(self) -> None:
        global MAPA_ATUAL
        MAPA_ATUAL = "Mapa_teste"
        self.mapa_atual = "Mapa_teste"
        self.mapa_imagem = carregar_mapa()
        self.grupo_inimigos.empty()
        for personagem, posicao in zip(
            (self.cezar, self.lucas, self.guilherme),
            ((250, 150), (220, 150), (280, 150)),
        ):
            personagem.posicao = pygame.Vector2(posicao)
            personagem.rect.topleft = posicao
            personagem.historico_posicoes = [pygame.Vector2(posicao)]
        self.criar_inimigos_mapa_teste()
        self.mensagem = "Mapa_teste | WASD: mover | Encoste no inimigo para lutar"

    def verificar_fim_do_caminho(self) -> bool:
        if self.mapa_atual != "mapateste":
            return False
        if retangulo_colisao(self.cezar).colliderect(CHEGADA_CAMINHO):
            self.trocar_para_mapa_teste()
            return True
        return False

    def atualizar_lider(self, tempo_frame: float) -> None:
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(0, 0)
        if teclas[pygame.K_d]:
            direcao.x += 1
        if teclas[pygame.K_a]:
            direcao.x -= 1
        if teclas[pygame.K_s]:
            direcao.y += 1
        if teclas[pygame.K_w]:
            direcao.y -= 1

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()
            movimentou = mover_com_colisao(
                self.cezar,
                direcao.x * self.cezar.velocidade * tempo_frame,
                direcao.y * self.cezar.velocidade * tempo_frame,
            )
            if movimentou:
                registrar_posicao(self.cezar)
            atualizar_animacao(self.cezar, direcao if movimentou else pygame.Vector2(), tempo_frame)
        else:
            atualizar_animacao(self.cezar, pygame.Vector2(), tempo_frame)

    def atualizar_seguidor(self, seguidor: pygame.sprite.Sprite, lider: pygame.sprite.Sprite, atraso: int, tempo_frame: float) -> None:
        indice = max(0, len(lider.historico_posicoes) - atraso)
        destino = lider.historico_posicoes[indice]
        diferenca = destino - seguidor.posicao

        if diferenca.length_squared() < 4:
            atualizar_animacao(seguidor, pygame.Vector2(), tempo_frame)
            return

        direcao = diferenca.normalize()
        deslocamento = min(diferenca.length(), seguidor.velocidade * tempo_frame)
        movimentou = mover_com_colisao(seguidor, direcao.x * deslocamento, direcao.y * deslocamento)
        if movimentou:
            registrar_posicao(seguidor)
        atualizar_animacao(seguidor, direcao if movimentou else pygame.Vector2(), tempo_frame)

    def atualizar_inimigo(self, inimigo: InimigoPeixe, tempo_frame: float) -> None:
        direcao = pygame.Vector2(inimigo.sentido, 0) if inimigo.eixo == "horizontal" else pygame.Vector2(0, inimigo.sentido)
        movimentou = mover_com_colisao(
            inimigo,
            direcao.x * inimigo.velocidade * tempo_frame,
            direcao.y * inimigo.velocidade * tempo_frame,
        )

        # Ao tocar em uma parede ou em uma borda, o inimigo inverte sua patrulha.
        if not movimentou:
            inimigo.sentido *= -1
            direcao *= -1

        atualizar_animacao(inimigo, direcao, tempo_frame)

    def encontrar_colisao_com_inimigo(self):
        for heroi in self.grupo_herois:
            for inimigo in self.grupo_inimigos:
                if retangulo_colisao(heroi).colliderect(retangulo_colisao(inimigo)):
                    return inimigo
        return None

    def abrir_batalha(self, inimigo: InimigoPeixe) -> None:
        """Troca a janela do mapa pela tela definida em batalha_ui.py."""
        self.inimigo_em_batalha = inimigo
        self.tela = pygame.display.set_mode((LARGURA_COMBATE, ALTURA_COMBATE))
        pygame.display.set_caption("RPG Saga dos Falidos - Batalha")
        self.batalha = criar_batalha(self.tela, self.herois_combate, inimigo.quantidade_combate)
        self.modo = "combate"

    def fechar_batalha(self) -> None:
        """Volta ao mapa após o fim do combate. Em vitória, remove o inimigo tocado."""
        if self.batalha.resultado is True and self.inimigo_em_batalha is not None:
            self.inimigo_em_batalha.kill()
            self.mensagem = "Vitória! O inimigo foi removido e as recompensas foram aplicadas."
        else:
            self.mensagem = "O grupo retornou ao mapa após a batalha."

        self.tela = pygame.display.set_mode((LARGURA_MAPA, ALTURA_MAPA))
        pygame.display.set_caption("RPG Saga dos Falidos - Mapa")
        self.batalha = None
        self.inimigo_em_batalha = None
        self.modo = "mapa"

    def processar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                continue

            if self.modo == "combate":
                self.batalha.processar_evento(evento)
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F3:
                self.mostrar_colisoes = not self.mostrar_colisoes

    def atualizar_mapa(self, tempo_frame: float) -> None:
        self.atualizar_lider(tempo_frame)
        self.atualizar_seguidor(self.lucas, self.cezar, 28, tempo_frame)
        self.atualizar_seguidor(self.guilherme, self.lucas, 28, tempo_frame)

        for inimigo in self.grupo_inimigos:
            self.atualizar_inimigo(inimigo, tempo_frame)

        if self.verificar_fim_do_caminho():
            return

        inimigo = self.encontrar_colisao_com_inimigo()
        if self.mapa_atual == "Mapa_teste" and inimigo is not None:
            self.abrir_batalha(inimigo)

    def desenhar_mapa(self) -> None:
        if self.mapa_imagem is None:
            desenhar_mapa_provisorio(self.tela)
        else:
            self.tela.blit(self.mapa_imagem, (0, 0))

        for objeto in sorted(self.grupo_objetos, key=lambda item: item.rect.bottom):
            imagem = objeto.image
            if personagem_atras_de_oclusor(objeto):
                imagem = objeto.image.copy()
                imagem.set_alpha(145)
            self.tela.blit(imagem, objeto.rect)

        caixa = pygame.Rect(7, 7, 625, 30)
        pygame.draw.rect(self.tela, (5, 17, 34), caixa, border_radius=5)
        texto = self.fonte.render(self.mensagem, True, (240, 240, 245))
        self.tela.blit(texto, (14, 13))

        if self.mostrar_colisoes:
            for obstaculo in COLISOES_TERRENO:
                pygame.draw.rect(self.tela, (255, 120, 0), obstaculo, 2)
            for objeto in self.grupo_objetos:
                pygame.draw.rect(self.tela, (255, 0, 255), retangulo_colisao(objeto), 1)
            aviso = self.fonte_auxiliar.render("Colisões visíveis: laranja = terreno; rosa = personagens/inimigos", True, (255, 225, 110))
            self.tela.blit(aviso, (10, 43))

    def executar(self) -> None:
        while self.rodando:
            tempo_frame = self.relogio.tick(FPS) / 1000
            self.processar_eventos()

            if self.modo == "mapa":
                self.atualizar_mapa(tempo_frame)
                self.desenhar_mapa()
            else:
                self.batalha.atualizar(tempo_frame)
                self.batalha.desenhar()
                if self.batalha.concluida:
                    self.fechar_batalha()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Jogo().executar()