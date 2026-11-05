"""Fachada publica da interface de batalha e dos recursos visuais.

Este arquivo e pequeno de proposito. Ele nao desenha nada sozinho: apenas
escolhe o que deve ficar visivel para o resto do jogo e reexporta as classes
dos modulos especializados em batalha_core/:

- assets.py        -> caminhos, constantes e listas de imagens;
- sprites.py       -> SpriteCombatente (sprite de heroi/inimigo na arena);
- animacoes.py     -> efeitos visuais (dano flutuante, dash, ultimate...);
- helpers.py       -> funcoes de apoio (cores, nomes, medidas, log);
- carregadores.py  -> leitura de imagens/gifs e montagem da tela;
- acoes.py         -> execucao das acoes escolhidas pelo jogador;
- fluxo.py         -> turnos, ATB, IA e fim de batalha;
- renderizacao.py  -> desenho dos paineis, barras e sprites;
- interface.py     -> classe BattleUI e funcoes de entrada.

POR QUE UMA FACHADA?
    O mapa e os testes antigos fazem "from batalha_ui import ...". Se fossem
    obrigados a conhecer batalha_core.interface, batalha_core.renderizacao etc.,
    qualquer mudanca interna quebraria esses imports. A fachada mantem um
    contrato estavel: quem esta fora continua importando daqui.

PILARES DE POO NA INTERFACE
---------------------------
HERANCA MULTIPLA (mixins)
    BattleUI(CarregadoresBattleUI, AcoesBattleUI, FluxoBattleUI,
    RenderizacaoBattleUI) junta quatro comportamentos. Cada mixin cuida de uma
    responsabilidade e a classe final apenas combina os metodos. E o mesmo
    padrao usado pela classe Jogo do mapa.

HERANCA SIMPLES
    AnimacaoAtaque, AnimacaoDash e AnimacaoUltimateMago herdam de classes
    maiores (AnimacaoUltimate e AnimacaoHabilidadeMago) e reaproveitam
    atualizar()/desenhar(), mudando apenas o que precisam.

POLIMORFISMO
    Todos os sprites e animacoes respondem a atualizar() e desenhar(). O loop
    da batalha chama esses metodos sem perguntar qual classe concreta esta ali.

ENCAPSULAMENTO
    BattleUI guarda a lista de herois/inimigos e delega as regras para os
    objetos de Combate.py. A interface nao recalcula dano: ela pede a acao e
    mostra o resultado que o modelo devolveu.

ABSTRACAO
    "SpriteCombatente", "AnimacaoUltimate" e os mixins escondem detalhes de
    carregamento de arquivos, quadros e posicoes. Quem usa so precisa saber o
    que o objeto faz, nao como ele faz.
"""

# pygame e a base de toda a interface (superficies, eventos, fontes).
import pygame

# "regras" e o modulo Combate.py: a interface nunca duplica as regras da luta.
import Combate as regras

# Reexporta TUDO de assets (LARGURA, ALTURA, FPS, caminhos, listas de quadros).
# O asterisco e intencional: assets.py define __all__ com os nomes publicos.
from batalha_core.assets import *

# Classes de animacao visual. Sao reexportadas para imports antigos e para o
# mapa poder criar efeitos sem conhecer o caminho interno de batalha_core.
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

# Funcoes e variaveis de apoio usadas pelos paineis e pelo log de batalha.
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

# A classe principal e as funcoes de entrada da batalha.
from batalha_core.interface import (
    BattleUI,
    criar_batalha,
    iniciar_janela_batalha,
    preparar_fundo_animado,
)

# Sprite usado para desenhar cada combatente na arena.
from batalha_core.sprites import SpriteCombatente


# Sem __all__: o modulo continua reexportando todos os nomes importados,
# inclusive os que vem de "from batalha_core.assets import *". Assim, qualquer
# "from batalha_ui import *" antigo continua funcionando exatamente como antes.
