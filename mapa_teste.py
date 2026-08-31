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

LARGURA_MAPA = 840
ALTURA_MAPA = 480
FPS = 60

# Áreas sólidas aproximadas da imagem de mapa fornecida.
# Cada item possui: x, y, largura, altura.
# Pressione F3 dentro do jogo para mostrar os limites laranja e ajustá-los.
COLISOES_TERRENO = [
    # Casa do canto superior esquerdo.
    (0, 0, 280, 145),
    # Construção, muros e escada do canto superior direito.
    (585, 0, 255, 133),
    (646, 113, 96, 43),
    # Fileira de caixotes e caixas centrais.
    (338, 255, 170, 35),
    (340, 306, 162, 33),
    # Barris do lado inferior esquerdo.
    (228, 374, 104, 45),
    # Arbustos e árvores da área inferior.
    (451, 337, 250, 34),
    (397, 390, 75, 90),
    (500, 390, 75, 90),
    (606, 390, 75, 90),
    (712, 390, 75, 90),
]


# ============================================================================
# FUNÇÕES DE MAPA E COLISÃO
# ============================================================================


def carregar_mapa() -> pygame.Surface | None:
    """Carrega a imagem do mapa na pasta assets/mapa_teste ou subpastas."""
    candidatos = [
        BASE_DIR / "assets" / "mapa_teste" / "mapateste.jpeg",
        BASE_DIR / "assets" / "mapa_teste" / "mapa_teste.jpeg",
        BASE_DIR / "assets" / "mapa_teste" / "mapa_teste.jpg",
        BASE_DIR / "assets" / "mapateste.jpeg",
        BASE_DIR / "mapateste.jpeg",
    ]

    for caminho in candidatos:
        if caminho.exists():
            try:
                imagem = pygame.image.load(caminho).convert()
                return pygame.transform.smoothscale(imagem, (LARGURA_MAPA, ALTURA_MAPA))
            except pygame.error:
                continue
    return None

def desenhar_mapa_provisorio(tela: pygame.Surface) -> None:
    """Mantém o jogo funcional caso a imagem de mapa não seja encontrada."""
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
    return sprite.rect.inflate(-18, -16)


def colide_com_terreno(rect: pygame.Rect) -> bool:
    limites_mapa = pygame.Rect(0, 0, LARGURA_MAPA, ALTURA_MAPA)
    if not limites_mapa.contains(rect):
        return True
    return any(rect.colliderect(obstaculo) for obstaculo in COLISOES_TERRENO)


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

        self.mapa_imagem = carregar_mapa()
        self.rodando = True
        self.modo = "mapa"
        self.mostrar_colisoes = False
        self.batalha = None
        self.inimigo_em_batalha = None
        self.mensagem = "WASD: mover | Encoste no inimigo para lutar | F3: colisões"

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

        # Posições livres, fora do prédio superior esquerdo.
        posicoes = [(170, 180), (135, 180), (100, 180)]
        for personagem, posicao in zip((self.cezar, self.lucas, self.guilherme), posicoes):
            personagem.posicao = pygame.Vector2(posicao)
            personagem.rect.topleft = posicao
            personagem.historico_posicoes = [pygame.Vector2(posicao)]

        self.grupo_herois.add(self.cezar, self.lucas, self.guilherme)

        # Inimigos caminham, respeitam as colisões de terreno e mudam de direção quando bloqueados.
        inimigo_horizontal = InimigoPeixe(420, 155, eixo="horizontal")
        inimigo_vertical = InimigoPeixe(670, 180, eixo="vertical")
        inimigo_horizontal.quantidade_combate = 3
        inimigo_vertical.quantidade_combate = 3
        self.grupo_inimigos.add(inimigo_horizontal, inimigo_vertical)

        self.grupo_objetos.add(self.grupo_herois, self.grupo_inimigos)

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

        inimigo = self.encontrar_colisao_com_inimigo()
        if inimigo is not None:
            self.abrir_batalha(inimigo)

    def desenhar_mapa(self) -> None:
        if self.mapa_imagem is None:
            desenhar_mapa_provisorio(self.tela)
        else:
            self.tela.blit(self.mapa_imagem, (0, 0))

        self.grupo_objetos.draw(self.tela)

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