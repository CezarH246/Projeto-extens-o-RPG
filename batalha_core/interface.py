"""Visual interface composition and battle entry points."""

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import pygame
import Combate as regras
from mapa_animado import MapaAnimado

from .acoes import AcoesBattleUI
from .assets import *
from .carregadores import CarregadoresBattleUI
from .fluxo import FluxoBattleUI
from .helpers import LOG_BATALHA, criar_fonte, registrar_evento
from .renderizacao import RenderizacaoBattleUI

# Fundos animados já lidos do disco (ou sendo lidos): as batalhas seguintes
# reaproveitam os quadros em vez de reler dezenas de MB a cada encontro.
_FUNDOS_ANIMADOS: dict[Path, Future] = {}
_LEITOR_FUNDOS = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fundo_batalha")


def preparar_fundo_animado(pasta: Path) -> None:
    """Começa a ler o fundo numa thread, para estar pronto quando a batalha abrir."""
    if pasta not in _FUNDOS_ANIMADOS:
        _FUNDOS_ANIMADOS[pasta] = _LEITOR_FUNDOS.submit(MapaAnimado, pasta, (LARGURA, ALTURA))


def carregar_fundo_animado(pasta: Path) -> MapaAnimado:
    preparar_fundo_animado(pasta)
    return _FUNDOS_ANIMADOS[pasta].result()  # espera só se a leitura ainda não acabou

class BattleUI(CarregadoresBattleUI, AcoesBattleUI, FluxoBattleUI, RenderizacaoBattleUI):
    """Combine loading, actions, flow, and rendering in one battle screen."""

    def __init__(self, tela: pygame.Surface, herois: list, inimigos: list, fundo_animado: Path | None = None):
        self.tela = tela
        # Mantém referências aos modelos do combate; a interface consulta e
        # solicita alterações a esses objetos em vez de duplicar suas regras.
        self.herois = herois
        self.inimigos = inimigos
        self.fonte_titulo = criar_fonte(42, negrito=True)
        self.fonte = criar_fonte(28, negrito=True)
        self.fonte_pequena = criar_fonte(17)
        self.fonte_menor = criar_fonte(15)
        self.fonte_dano = criar_fonte(34, negrito=True)  # Fonte para números de dano
        self.animacao_dash = None
        self.animacao_ataque = None
        self.animacao_ataque_inimigo = None
        self.animacao_ultimate = None
        self.animacao_habilidade_mago = None
        self.animacao_apos_dash = None
        self.posicao_final_dash = None

        self.fundo = self.carregar_fundo()
        # Quando há fundo animado (pasta de quadros), ele é desenhado no lugar da imagem fixa.
        self.fundo_animado = carregar_fundo_animado(fundo_animado) if fundo_animado else None
        # Alguns fundos têm formação própria (veja posicoes_da_formacao).
        self.pasta_fundo_animado = fundo_animado
        self.sprites_herois: list[SpriteCombatente] = []
        self.sprites_inimigos: list[SpriteCombatente] = []
        self.entidades_atras: list[SpriteCombatente] = []
        self.criar_sprites()

        self.heroi_ativo = None
        self.acao_pendente: str | None = None
        # Opção sob o cursor do menu de comandos do tema Moderno (0 a 5).
        self.cursor_acao = 0
        self.indice_alvo = 0
        self.resultado: bool | None = None
        self.concluida = False
        self.recompensas_aplicadas = False
        # Golpes já calculados pelas regras, mas ainda não mostrados na tela
        # (a vida só cai e o dano só aparece quando a animação termina).
        self.impactos_pendentes: list = []
        self.log_retido_desde: int | None = None
        # Respiro inicial, para os inimigos não agirem no primeiro instante.
        self.pausa_turno = PAUSA_ENTRE_ACOES
        self.mensagem = "A batalha começou. Aguarde a barra ATB encher."

        LOG_BATALHA.clear()
        LOG_BATALHA.append("Um grupo de inimigos apareceu.")
        LOG_BATALHA.append("F2: trocar o visual (Clássico / Moderno).")
        regras.definir_saida(registrar_evento)

def criar_batalha(
    tela: pygame.Surface, herois: list, quantidade_inimigos: int = 3, rei_tritao: bool = False,
    fundo_animado: Path | None = None,
) -> BattleUI:
    """Cria a batalha comum ou o confronto especial contra o Rei Tritão."""
    nivel_grupo = max(heroi.level for heroi in herois)
    if rei_tritao:
        inimigos = [regras.criar_rei_tritao(nivel_grupo)]
    else:
        inimigos = regras.criar_cenario_batalha(nivel_grupo, quantidade=quantidade_inimigos)
    return BattleUI(tela, herois, inimigos, fundo_animado)


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
