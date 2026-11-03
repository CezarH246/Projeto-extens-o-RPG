"""Fachada publica da interface de batalha e dos recursos visuais.

Os assets, sprites, animacoes, carregamento, fluxo e desenho estao separados
em batalha_core/. Os imports existentes continuam funcionando por este modulo.
"""

import pygame
import Combate as regras

from batalha_core.assets import *
from batalha_core.animacoes import (
    AnimacaoAtaque,
    AnimacaoDash,
    AnimacaoEspecialSequencial,
    AnimacaoHabilidadeMago,
    AnimacaoPersonagemProjetil,
    AnimacaoUltimate,
    AnimacaoUltimateCezar,
    AnimacaoUltimateComEfeito,
    AnimacaoUltimateMago,
    FloatingDamage,
)
from batalha_core.helpers import (
    LOG_BATALHA,
    ajustar_quadros_ao_conteudo,
    carregar_quadros_gif,
    cor_barra_hp,
    eh_rei_tritao,
    mediana,
    normalizar_nome,
    registrar_evento,
    resolver_sprite_inimigo,
    tamanho_com_escala,
    tamanho_corpo,
    tamanho_efeito_com_escala_alvo,
)
from batalha_core.interface import BattleUI, criar_batalha, iniciar_janela_batalha, preparar_fundo_animado
from batalha_core.sprites import SpriteCombatente
