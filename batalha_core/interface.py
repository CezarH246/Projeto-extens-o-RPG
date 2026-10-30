"""Visual interface composition and battle entry points."""

import pygame
import Combate as regras

from .acoes import AcoesBattleUI
from .assets import *
from .carregadores import CarregadoresBattleUI
from .fluxo import FluxoBattleUI
from .helpers import LOG_BATALHA, registrar_evento
from .renderizacao import RenderizacaoBattleUI

class BattleUI(CarregadoresBattleUI, AcoesBattleUI, FluxoBattleUI, RenderizacaoBattleUI):
    """Combine loading, actions, flow, and rendering in one battle screen."""

    def __init__(self, tela: pygame.Surface, herois: list, inimigos: list):
        self.tela = tela
        # Mantém referências aos modelos do combate; a interface consulta e
        # solicita alterações a esses objetos em vez de duplicar suas regras.
        self.herois = herois
        self.inimigos = inimigos
        self.fonte_titulo = pygame.font.SysFont("arial", 36, bold=True)
        self.fonte = pygame.font.SysFont("arial", 20, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial", 15)
        self.fonte_menor = pygame.font.SysFont("arial", 13)
        self.fonte_dano = pygame.font.SysFont("arial", 24, bold=True)  # Fonte para números de dano
        self.animacao_dash = None
        self.animacao_ataque = None
        self.animacao_ataque_inimigo = None
        self.animacao_ultimate = None
        self.animacao_habilidade_mago = None
        self.animacao_apos_dash = None
        self.posicao_final_dash = None

        self.fundo = self.carregar_fundo()
        self.sprites_herois: list[SpriteCombatente] = []
        self.sprites_inimigos: list[SpriteCombatente] = []
        self.entidades_atras: list[SpriteCombatente] = []
        self.criar_sprites()

        self.heroi_ativo = None
        self.acao_pendente: str | None = None
        self.indice_alvo = 0
        self.resultado: bool | None = None
        self.concluida = False
        self.recompensas_aplicadas = False
        self.mensagem = "A batalha começou. Aguarde a barra ATB encher."

        LOG_BATALHA.clear()
        LOG_BATALHA.append("Um grupo de inimigos apareceu.")
        regras.definir_saida(registrar_evento)

def criar_batalha(tela: pygame.Surface, herois: list, quantidade_inimigos: int = 3, rei_tritao: bool = False) -> BattleUI:
    """Cria a batalha comum ou o confronto especial contra o Rei Tritão."""
    nivel_grupo = max(heroi.level for heroi in herois)
    if rei_tritao:
        inimigos = [regras.criar_rei_tritao(nivel_grupo)]
    else:
        inimigos = regras.criar_cenario_batalha(nivel_grupo, quantidade=quantidade_inimigos)
    return BattleUI(tela, herois, inimigos)


def iniciar_janela_batalha() -> None:
    """Permite testar somente esta tela, sem abrir o mapa."""
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("RPG - Batalha")
    relogio = pygame.time.Clock()
    batalha = criar_batalha(tela, regras.criar_herois())
    executando = True

    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            else:
                batalha.processar_evento(evento)
        batalha.atualizar(relogio.tick(FPS) / 1000)
        batalha.desenhar()
        pygame.display.flip()
        if batalha.concluida:
            executando = False

    pygame.quit()
