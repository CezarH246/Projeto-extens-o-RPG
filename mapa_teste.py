"""Mapa principal do jogo.

Substitua integralmente o arquivo mapa_teste.py por este conteúdo.
Quando o grupo encosta em um inimigo, este arquivo abre batalha_ui.py.
A tela de batalha usa o fundo, os sprites animados e as regras de Combate.py.
"""

from __future__ import annotations

import builtins
import ctypes
import math
import os
import sys
import warnings
from pathlib import Path

import pygame


def preparar_tela_do_sistema() -> None:
    """Ajustes que precisam acontecer antes de a primeira janela ser criada."""
    if sys.platform == "win32":
        # Com a escala do Windows em 125%/150%, um programa que não se declara
        # "DPI aware" é ampliado pelo sistema: fica borrado e maior que a tela.
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass


def area_util_da_tela() -> pygame.Rect:
    """Área do monitor que a janela pode ocupar, descontando a barra de tarefas."""
    if sys.platform == "win32":
        try:
            from ctypes import wintypes

            area = wintypes.RECT()
            SPI_GETWORKAREA = 0x0030
            if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(area), 0):
                return pygame.Rect(area.left, area.top, area.right - area.left, area.bottom - area.top)
        except (AttributeError, OSError):
            pass
    # Outros sistemas: o monitor inteiro, com folga para barra de tarefas/dock.
    largura, altura = pygame.display.get_desktop_sizes()[0]
    return pygame.Rect(0, 0, largura, altura - 48)


preparar_tela_do_sistema()

# Os arquivos atuais dos personagens utilizam pygame sem importá-lo.
# A referência abaixo permite usá-los sem editar seus módulos individuais.
builtins.pygame = pygame

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

import covil_tritao
from recompensa_bau import RecompensaBau
from mapa_animado import MapaAnimado
from CezarPersonagem import Cezar
from LucasPersonagem import Lucas
from GuilhermePersonagem import Guilherme
from InimigoPersonagem import InimigoPeixe, ReiTritaoMapa
from Combate import criar_herois
from batalha_ui import ALTURA as ALTURA_COMBATE
from batalha_ui import LARGURA as LARGURA_COMBATE
from batalha_ui import FUNDO_BATALHA_GUARDAS, criar_batalha, preparar_fundo_animado


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

MAPA_COLISAO = None
MAPA_ATUAL = "mapateste"

# Onde o jogo começa: "covil" (Covil do Rei Tritão, mapa animado) ou
# "mapateste" (o mapa antigo, que abre uma passagem para o covil no fim).
CENA_INICIAL = "covil"

# Passagem que se abre no mapa de teste depois de vencer todos os inimigos e
# leva o grupo ao Covil do Rei Tritão.
PASSAGEM_COVIL = pygame.Rect(568, 212, 44, 44)

# Cena em que o grupo está: tamanho, retângulos que bloqueiam e, no covil, a
# máscara do chão (os pés só podem pisar onde a máscara marca chão).
CENA = {"tamanho": (LARGURA_MAPA, ALTURA_MAPA), "bloqueios": COLISOES_MAPA, "chao": None}
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


def altura_dos_pes(sprite: pygame.sprite.Sprite) -> int:
    """Distância do topo do sprite até a sola dos pés (parte visível mais baixa)."""
    if not hasattr(sprite, "altura_pes"):
        imagens_parado = getattr(sprite, "imagens_parado", None)
        imagem = imagens_parado["south"] if imagens_parado else sprite.image
        sprite.altura_pes = imagem.get_bounding_rect().bottom
    return sprite.altura_pes


def posicionar_pelos_pes(sprite: pygame.sprite.Sprite, pes: tuple[int, int]) -> None:
    """Coloca o sprite de modo que a sola dos pés fique no ponto indicado."""
    sprite.rect.topleft = (round(pes[0] - sprite.rect.width / 2), round(pes[1] - altura_dos_pes(sprite)))
    sprite.posicao = pygame.Vector2(sprite.rect.topleft)


def retangulo_colisao(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """Área que bate no terreno.

    No mapa antigo é quase o sprite inteiro. No covil (visão de cima, com chão
    desenhado) é só a sola dos pés: o corpo pode passar na frente de paredes e
    estátuas, como em RPGs vistos de cima, mas os pés não saem do chão."""
    if CENA["chao"] is None:
        return sprite.rect.inflate(-8, -8)
    caixa = pygame.Rect(0, 0, max(8, sprite.rect.width * 45 // 100), max(6, sprite.rect.height // 7))
    caixa.midbottom = (sprite.rect.centerx, sprite.rect.top + altura_dos_pes(sprite))
    return caixa


def retangulo_encontro(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """Área do corpo que inicia a batalha quando herói e inimigo se encostam."""
    if CENA["chao"] is None:
        return retangulo_colisao(sprite)
    return sprite.rect.inflate(-sprite.rect.width * 2 // 5, -sprite.rect.height // 3)


def colide_com_terreno(rect: pygame.Rect) -> bool:
    limites_mapa = pygame.Rect((0, 0), CENA["tamanho"])
    if not limites_mapa.contains(rect):
        return True
    chao = CENA["chao"]
    if chao is not None:
        # Os pés (base do retângulo) precisam estar sobre o chão: assim ninguém
        # anda sobre o abismo, a água ou as paredes do covil.
        y = rect.bottom - 1
        if not all(chao.get_at((x, y)) for x in (rect.left, rect.centerx, rect.right - 1)):
            return True
    return any(rect.colliderect(obstaculo) for obstaculo in CENA["bloqueios"])


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
        self.tela_cheia = False
        tamanho_inicial = covil_tritao.TAMANHO if CENA_INICIAL == "covil" else (LARGURA_MAPA, ALTURA_MAPA)
        self.tela = self.criar_janela(tamanho_inicial)
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
        self.inimigo_ignorado = None
        self.rei_tritao_spawnado = False
        self.rei_tritao_derrotado = False
        self.bau_aberto = False
        self.recompensa: RecompensaBau | None = None
        self.editor = None  # editor de colisão (F3 no covil)
        self.oclusores = [covil_tritao.Oclusor(poligono) for poligono in covil_tritao.OCLUSORES]
        self.cena = "mapateste"
        self.passagem_aberta = False
        self.mapa_animado: MapaAnimado | None = None
        self.escurecimento = 0.0  # 1 = tela preta; diminui até 0 ao entrar numa cena
        self.mensagem = "WASD/setas: mover | Encoste no inimigo para lutar | F3: colisões | F11: tela cheia"
        self.mapa_atual = "mapateste"

        self.grupo_herois = pygame.sprite.Group()
        self.grupo_inimigos = pygame.sprite.Group()
        self.grupo_objetos = pygame.sprite.Group()
        self.criar_personagens(covil_tritao.TAMANHOS_SPRITES if CENA_INICIAL == "covil" else None)
        if CENA_INICIAL == "covil":
            self.entrar_no_covil()
        else:
            self.criar_inimigos_mapa_teste()

        # Estes mesmos objetos são enviados à batalha e preservam nível, HP, PA, XP e poções.
        self.herois_combate = criar_herois()

    def criar_janela(self, tamanho_logico: tuple[int, int]) -> pygame.Surface:
        """Abre a janela e devolve a "tela lógica" em que o jogo desenha.

        O jogo sempre desenha em resolução fixa (720x480 no mapa, 1280x720 na
        batalha), então nenhuma coordenada muda. A cada frame, `apresentar`
        escala essa tela para o tamanho real da janela ou do monitor."""
        if self.tela_cheia:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(self.tamanho_ideal_da_janela(tamanho_logico), pygame.RESIZABLE)
            self.centralizar_janela()
        return pygame.Surface(tamanho_logico).convert()

    # Espaço que o sistema usa em volta da janela: barra de título e bordas.
    ALTURA_BARRA_TITULO = 32
    MARGEM_BORDAS = 8
    # Até ~1600x900 a escala suave cabe nos 60 FPS; acima disso usa a rápida.
    LIMITE_ESCALA_SUAVE = 1_300_000

    def tamanho_ideal_da_janela(self, tamanho_logico: tuple[int, int]) -> tuple[int, int]:
        """O maior tamanho que cabe na tela sem distorcer a imagem.

        Num notebook 1366x768 a batalha encolhe para caber acima da barra de
        tarefas; num monitor Full HD ou 4K o jogo cresce."""
        area = area_util_da_tela()
        largura_livre = area.width - 2 * self.MARGEM_BORDAS
        altura_livre = area.height - self.ALTURA_BARRA_TITULO - self.MARGEM_BORDAS
        escala = min(largura_livre / tamanho_logico[0], altura_livre / tamanho_logico[1])
        return max(1, round(tamanho_logico[0] * escala)), max(1, round(tamanho_logico[1] * escala))

    def centralizar_janela(self) -> None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                janela = pygame.Window.from_display_module()
            area = area_util_da_tela()
            largura, altura = janela.size
            altura_livre = area.height - self.ALTURA_BARRA_TITULO - self.MARGEM_BORDAS
            # A posição é a da área de desenho; a barra de título fica logo acima.
            x = area.x + (area.width - largura) // 2
            y = area.y + self.ALTURA_BARRA_TITULO + max(0, (altura_livre - altura) // 2)
            janela.position = (x, y)
        except (AttributeError, pygame.error, IndexError):
            pass  # sem a API de janela, o sistema decide a posição

    def apresentar(self) -> None:
        """Escala a tela lógica para a janela real, com faixas pretas se a proporção diferir."""
        janela = pygame.display.get_surface()
        largura_janela, altura_janela = janela.get_size()
        largura, altura = self.tela.get_size()
        escala = min(largura_janela / largura, altura_janela / altura)
        destino = (max(1, round(largura * escala)), max(1, round(altura * escala)))
        if destino == (largura, altura):
            imagem = self.tela
        elif destino[0] * destino[1] <= self.LIMITE_ESCALA_SUAVE:
            # Escala suave: texto e linhas finas sem serrilhado em escalas quebradas.
            imagem = pygame.transform.smoothscale(self.tela, destino)
        else:
            # Telas grandes: vizinho mais próximo, bem mais barato e nítido para pixel art.
            imagem = pygame.transform.scale(self.tela, destino)
        # As faixas pretas só precisam ser pintadas quando o tamanho muda.
        if getattr(self, "_tamanho_apresentado", None) != (janela.get_size(), destino):
            janela.fill((0, 0, 0))
            self._tamanho_apresentado = (janela.get_size(), destino)
        janela.blit(imagem, imagem.get_rect(center=(largura_janela // 2, altura_janela // 2)))
        pygame.display.flip()

    def alternar_tela_cheia(self) -> None:
        self.tela_cheia = not self.tela_cheia
        self.tela = self.criar_janela(self.tela.get_size())
        if self.batalha is not None:
            self.batalha.tela = self.tela
        if self.editor is not None:
            self.editor.tela = self.tela

    def criar_personagens(self, tamanhos: dict[str, int] | None = None) -> None:
        """Cria o grupo. `tamanhos` define o lado de cada sprite (padrão: 32 px)."""
        tamanhos = tamanhos or {}
        self.cezar = Cezar(tamanho=tamanhos.get("Cezar", 32))
        self.lucas = Lucas(self.cezar, tamanho=tamanhos.get("Lucas", 32))
        self.guilherme = Guilherme(self.lucas, tamanho=tamanhos.get("Guilherme", 32))

        posicoes = [(250, 150), (285, 150), (320, 150)]
        for personagem, posicao in zip((self.cezar, self.lucas, self.guilherme), posicoes):
            personagem.posicao = pygame.Vector2(posicao)
            personagem.rect.topleft = posicao
            personagem.historico_posicoes = [pygame.Vector2(posicao)]

        # Só o líder anda pelo mapa; a equipe completa aparece na batalha.
        self.grupo_herois.add(self.cezar)

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

    def atualizar_lider(self, tempo_frame: float) -> None:
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(0, 0)
        # WASD e as setas do teclado movem o líder do grupo.
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            direcao.x += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            direcao.x -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            direcao.y += 1
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
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
        if getattr(inimigo, "eh_rei_tritao", False):
            inimigo.atualizar_idle(tempo_frame)
            return
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
        tocando_ignorado = False
        for heroi in self.grupo_herois:
            for inimigo in self.grupo_inimigos:
                if retangulo_encontro(heroi).colliderect(retangulo_encontro(inimigo)):
                    # O inimigo da última batalha não reabre a luta enquanto o
                    # grupo ainda estiver encostado nele (o grupo volta ao mapa
                    # no mesmo lugar e entraria em batalha de novo no mesmo frame).
                    if inimigo is self.inimigo_ignorado:
                        tocando_ignorado = True
                        continue
                    return inimigo
        if not tocando_ignorado:
            self.inimigo_ignorado = None
        return None

    def abrir_batalha(self, inimigo: InimigoPeixe) -> None:
        """Troca a janela do mapa pela tela definida em batalha_ui.py."""
        self.inimigo_em_batalha = inimigo
        self.tela = self.criar_janela((LARGURA_COMBATE, ALTURA_COMBATE))
        pygame.display.set_caption("RPG Saga dos Falidos - Batalha")
        self.batalha = criar_batalha(
            self.tela, self.herois_combate, inimigo.quantidade_combate,
            rei_tritao=getattr(inimigo, "eh_rei_tritao", False),
            fundo_animado=FUNDO_BATALHA_GUARDAS if getattr(inimigo, "eh_guarda_covil", False) else None,
        )
        self.modo = "combate"

    def fechar_batalha(self) -> None:
        """Volta ao mapa após o fim do combate. Em vitória, remove o inimigo tocado."""
        if self.batalha.resultado is True and self.inimigo_em_batalha is not None:
            era_rei_tritao = getattr(self.inimigo_em_batalha, "eh_rei_tritao", False)
            self.inimigo_em_batalha.kill()
            if era_rei_tritao:
                self.rei_tritao_derrotado = True
                self.mostrar_covil_pos_boss()
            else:
                self.mensagem = "Vitória! O inimigo foi removido e as recompensas foram aplicadas."
        else:
            self.mensagem = "O grupo retornou ao mapa após a batalha."
            self.inimigo_ignorado = self.inimigo_em_batalha

        self.tela = self.criar_janela(CENA["tamanho"])
        pygame.display.set_caption("RPG Saga dos Falidos - Mapa")
        self.batalha = None
        self.inimigo_em_batalha = None
        self.modo = "mapa"

    def processar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                continue

            # F11 ou Alt+Enter alternam a tela cheia no mapa e na batalha.
            if evento.type == pygame.KEYDOWN and (
                evento.key == pygame.K_F11
                or (evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and evento.mod & pygame.KMOD_ALT)
            ):
                self.alternar_tela_cheia()
                continue

            if self.modo == "combate":
                self.batalha.processar_evento(evento)
            elif self.modo == "bau":
                self.recompensa.processar_evento(evento)
            elif self.modo == "editor":
                self.editor.processar(evento)
                if not self.editor.rodando:
                    self.fechar_editor_colisao()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F3:
                if self.cena == "covil":
                    self.abrir_editor_colisao()
                else:
                    self.mostrar_colisoes = not self.mostrar_colisoes
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F4:
                self.mostrar_colisoes = not self.mostrar_colisoes
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_e and self.pode_abrir_bau():
                self.recompensa = RecompensaBau(self.tela.get_size())
                self.modo = "bau"

    def mouse_na_tela(self, posicao: tuple[int, int]) -> tuple[int, int]:
        """Posição do mouse na janela -> posição na tela lógica (veja `apresentar`)."""
        largura_janela, altura_janela = pygame.display.get_surface().get_size()
        largura, altura = self.tela.get_size()
        escala = min(largura_janela / largura, altura_janela / altura)
        x0 = (largura_janela - largura * escala) / 2
        y0 = (altura_janela - altura * escala) / 2
        return round((posicao[0] - x0) / escala), round((posicao[1] - y0) / escala)

    def abrir_editor_colisao(self) -> None:
        """F3 no covil: o editor de colisão abre por cima do jogo, que fica pausado."""
        from ferramentas.editor_colisao import Editor

        self.editor = Editor(
            tela=self.tela,
            converter_mouse=self.mouse_na_tela,
            ao_salvar=self.aplicar_colisao_salva,
            fundo="posboss" if self.rei_tritao_derrotado else "inicial",
        )
        self.modo = "editor"

    def aplicar_colisao_salva(self) -> None:
        """Relê a colisão salva no editor e passa a usá-la sem reiniciar o jogo."""
        covil_tritao.recarregar_colisao()
        CENA["bloqueios"] = covil_tritao.BLOQUEIOS
        CENA["chao"] = covil_tritao.criar_mascara_chao(pos_boss=self.rei_tritao_derrotado)
        self.oclusores = [covil_tritao.Oclusor(poligono) for poligono in covil_tritao.OCLUSORES]

    def fechar_editor_colisao(self) -> None:
        self.editor = None
        self.modo = "mapa"

    def atualizar_mapa(self, tempo_frame: float) -> None:
        self.atualizar_lider(tempo_frame)

        for inimigo in self.grupo_inimigos:
            self.atualizar_inimigo(inimigo, tempo_frame)

        if self.mapa_animado is not None:
            self.mapa_animado.atualizar(tempo_frame)
        self.escurecimento = max(0.0, self.escurecimento - tempo_frame / 0.8)

        # Depois de exterminar todos os inimigos comuns, abre-se a passagem
        # para o Covil do Rei Tritão.
        if self.cena == "mapateste" and not self.grupo_inimigos and not self.passagem_aberta:
            self.passagem_aberta = True
            self.mensagem = "A água estremece... Uma passagem para o Covil do Rei Tritão se abriu!"
        # No covil, o rei surge no trono quando o último guarda cai.
        if (
            self.cena == "covil" and not self.grupo_inimigos
            and not self.rei_tritao_spawnado and not self.rei_tritao_derrotado
        ):
            self.surgir_rei_tritao()
        if self.passagem_aberta and self.cena == "mapateste":
            if retangulo_colisao(self.cezar).colliderect(PASSAGEM_COVIL):
                self.entrar_no_covil()
                return

        inimigo = self.encontrar_colisao_com_inimigo()
        if inimigo is not None:
            self.abrir_batalha(inimigo)

    def entrar_no_covil(self) -> None:
        """Leva o grupo ao Covil do Rei Tritão (também é onde o jogo começa)."""
        self.cena = "covil"
        CENA["tamanho"] = covil_tritao.TAMANHO
        CENA["bloqueios"] = covil_tritao.BLOQUEIOS
        CENA["chao"] = covil_tritao.criar_mascara_chao()
        if self.tela.get_size() != covil_tritao.TAMANHO:
            self.tela = self.criar_janela(covil_tritao.TAMANHO)
        self.mapa_animado = MapaAnimado(covil_tritao.PASTA_QUADROS)
        # O fundo da batalha dos guardas é pesado: já vai sendo lido em segundo
        # plano enquanto o grupo anda, para a primeira luta não demorar a abrir.
        preparar_fundo_animado(FUNDO_BATALHA_GUARDAS)

        tamanhos = covil_tritao.TAMANHOS_SPRITES
        # Vindo do mapa antigo (sprites de 32 px), o grupo é recriado no tamanho do covil.
        if self.cezar.tamanho != tamanhos["Cezar"]:
            for heroi in (self.cezar, self.lucas, self.guilherme):
                heroi.kill()
            self.criar_personagens(tamanhos)

        # O grupo chega pela entrada da caverna, no alto da ponte.
        for heroi in (self.cezar, self.lucas, self.guilherme):
            heroi.velocidade_base = getattr(heroi, "velocidade_base", heroi.velocidade)
            heroi.velocidade = heroi.velocidade_base * covil_tritao.FATOR_VELOCIDADE
            posicionar_pelos_pes(heroi, covil_tritao.ENTRADA)
            heroi.historico_posicoes = [pygame.Vector2(heroi.posicao)]
            heroi.direcao_atual = "west"
            heroi.image = heroi.imagens_parado["west"]

        # Os guardas do rei patrulham a ponte e a plataforma do trono.
        for x, y, eixo in covil_tritao.PATRULHAS:
            guarda = InimigoPeixe(0, 0, eixo=eixo, tamanho=tamanhos["guarda"])
            guarda.velocidade *= covil_tritao.FATOR_VELOCIDADE
            posicionar_pelos_pes(guarda, (x, y))
            guarda.quantidade_combate = 3
            guarda.eh_guarda_covil = True
            self.grupo_inimigos.add(guarda)
            self.grupo_objetos.add(guarda)

        self.escurecimento = 1.0
        self.mensagem = "Covil do Rei Tritão: derrote os guardas | WASD/setas: mover | F3: editar colisão | F11: tela cheia"

    def surgir_rei_tritao(self) -> None:
        rei = ReiTritaoMapa(0, 0, tamanho=covil_tritao.TAMANHOS_SPRITES["rei"])
        posicionar_pelos_pes(rei, covil_tritao.POSICAO_REI)
        self.grupo_inimigos.add(rei)
        self.grupo_objetos.add(rei)
        self.rei_tritao_spawnado = True
        self.mensagem = "A água estremece... O REI TRITÃO surgiu diante do trono!"

    def mostrar_covil_pos_boss(self) -> None:
        """Troca o covil pelo vídeo pós-chefe, com a ponte até o baú liberada."""
        self.mapa_animado = MapaAnimado(covil_tritao.PASTA_QUADROS_POSBOSS)
        CENA["chao"] = covil_tritao.criar_mascara_chao(pos_boss=True)
        self.escurecimento = 1.0
        self.mensagem = "O REI TRITÃO FOI DERROTADO! Um caminho de pedra agora leva até o baú!"

    def pode_abrir_bau(self) -> bool:
        """O baú só abre depois do chefe, uma vez, com o líder perto dele."""
        if self.cena != "covil" or not self.rei_tritao_derrotado or self.bau_aberto:
            return False
        pes = pygame.Vector2(self.cezar.rect.centerx, self.cezar.rect.top + altura_dos_pes(self.cezar))
        return pes.distance_to(covil_tritao.POSICAO_BAU) <= covil_tritao.ALCANCE_BAU

    def desenhar_aviso_bau(self) -> None:
        """Balão "[E] Abrir o baú" pulsando acima do baú quando dá para abrir."""
        if self.modo != "mapa" or not self.pode_abrir_bau():
            return
        texto = self.fonte.render("[E] Abrir o baú", True, (255, 235, 160))
        caixa = texto.get_rect().inflate(16, 10)
        flutuar = math.sin(pygame.time.get_ticks() / 250) * 3
        caixa.midbottom = (covil_tritao.POSICAO_BAU[0], covil_tritao.POSICAO_BAU[1] - 52 + flutuar)
        pygame.draw.rect(self.tela, (20, 14, 6), caixa, border_radius=6)
        pygame.draw.rect(self.tela, (222, 181, 83), caixa, 2, border_radius=6)
        self.tela.blit(texto, texto.get_rect(center=caixa.center))

    def fechar_recompensa(self) -> None:
        self.bau_aberto = True
        self.recompensa = None
        self.modo = "mapa"
        self.mensagem = "Baú aberto! O tesouro supremo era um bolo... e um aviso."

    def desenhar_passagem(self) -> None:
        """Redemoinho de água brilhante que marca a passagem para o covil."""
        tempo = pygame.time.get_ticks() / 1000
        camada = pygame.Surface(PASSAGEM_COVIL.inflate(40, 40).size, pygame.SRCALPHA)
        centro = (camada.get_width() // 2, camada.get_height() // 2)
        for anel in range(5):
            fase = (tempo * 1.5 + anel / 5) % 1.0
            raio = int(8 + fase * 32)
            alfa = int(220 * (1 - fase))
            pygame.draw.circle(camada, (90, 210, 255, alfa), centro, raio, 3)
        pygame.draw.circle(camada, (200, 245, 255, 200), centro, 8 + int(math.sin(tempo * 4) * 2))
        self.tela.blit(camada, camada.get_rect(center=PASSAGEM_COVIL.center))

    def desenhar_mapa(self) -> None:
        if self.cena == "covil" and self.mapa_animado is not None:
            self.tela.blit(self.mapa_animado.imagem, (0, 0))
        elif self.mapa_imagem is None:
            desenhar_mapa_provisorio(self.tela)
        else:
            self.tela.blit(self.mapa_imagem, (0, 0))
        if self.passagem_aberta and self.cena == "mapateste":
            self.desenhar_passagem()

        # Quem tem os pés mais abaixo é desenhado por cima (fica "na frente").
        # No covil, as estátuas ("oclusores") entram nessa ordem pela base: quem
        # passa atrás delas fica escondido.
        camadas = [(objeto.rect.top + altura_dos_pes(objeto), objeto) for objeto in self.grupo_objetos]
        if self.cena == "covil" and self.mapa_animado is not None:
            camadas += [(oclusor.base, oclusor) for oclusor in self.oclusores]
        for _, item in sorted(camadas, key=lambda camada: camada[0]):
            if isinstance(item, covil_tritao.Oclusor):
                item.desenhar(self.tela, self.mapa_animado.imagem)
                continue
            imagem = item.image
            if personagem_atras_de_oclusor(item):
                imagem = item.image.copy()
                imagem.set_alpha(145)
            self.tela.blit(imagem, item.rect)
        self.desenhar_aviso_bau()

        texto = self.fonte.render(self.mensagem, True, (240, 240, 245))
        caixa = pygame.Rect(7, 7, texto.get_width() + 16, 30)
        pygame.draw.rect(self.tela, (5, 17, 34), caixa, border_radius=5)
        self.tela.blit(texto, (14, 13))

        if self.mostrar_colisoes:
            if self.cena == "covil":
                extra = covil_tritao.CHAO_POSBOSS if self.rei_tritao_derrotado else []
                for poligono in covil_tritao.CHAO + extra:
                    pygame.draw.polygon(self.tela, (0, 255, 120), poligono, 2)
                for oclusor in self.oclusores:
                    pygame.draw.polygon(self.tela, (200, 110, 255), oclusor.poligono, 2)
            for obstaculo in CENA["bloqueios"]:
                pygame.draw.rect(self.tela, (255, 120, 0), obstaculo, 2)
            for objeto in self.grupo_objetos:
                pygame.draw.rect(self.tela, (255, 0, 255), retangulo_colisao(objeto), 1)
            aviso = self.fonte_auxiliar.render("Colisões: verde = chão; laranja = bloqueio; roxo = passar por trás; rosa = pés", True, (255, 225, 110))
            self.tela.blit(aviso, (10, 43))

        # Fade de entrada ao chegar numa cena nova.
        if self.escurecimento > 0:
            veu = pygame.Surface(self.tela.get_size())
            veu.set_alpha(int(255 * self.escurecimento))
            self.tela.blit(veu, (0, 0))

    def executar(self) -> None:
        while self.rodando:
            tempo_frame = self.relogio.tick(FPS) / 1000
            self.processar_eventos()

            if self.modo == "mapa":
                self.atualizar_mapa(tempo_frame)
                self.desenhar_mapa()
            elif self.modo == "bau":
                # O mapa continua animado por trás do bolo e da carta.
                if self.mapa_animado is not None:
                    self.mapa_animado.atualizar(tempo_frame)
                self.desenhar_mapa()
                self.recompensa.atualizar(tempo_frame)
                self.recompensa.desenhar(self.tela)
                if self.recompensa.concluida:
                    self.fechar_recompensa()
            elif self.modo == "editor":
                self.editor.desenhar()
            else:
                self.batalha.atualizar(tempo_frame)
                self.batalha.desenhar()
                if self.batalha.concluida:
                    self.fechar_batalha()

            self.apresentar()

        pygame.quit()


if __name__ == "__main__":
    Jogo().executar()