"""Ponto de entrada do mapa principal do jogo.

Este arquivo e de proposito pequeno: ele apenas monta o "quebra-cabeca" de
modulos do mapa e inicia o loop. O codigo real foi dividido para que nenhum
arquivo passe de 500 linhas, sem perder nenhuma funcao:

- mapa_config.py   -> constantes, caminhos, DPI e o dicionario CENA;
- mapa_colisao.py  -> colisao, movimento, animacao e carga do mapa;
- mapa_janela.py   -> criacao/escala/centralizacao da janela (mixin);
- mapa_cenas.py    -> personagens, viagens de cena e batalha (mixin);
- mapa_desenho.py  -> desenho do mapa e dos avisos (mixin);
- mapa_jogo.py     -> classe Jogo e o laco principal.

PILARES DE POO VISIVEIS NO MAPA
-------------------------------
HERANCA
    Jogo(JanelaMixin, CenasMixin, DesenhoMixin) reaproveita metodos prontos dos
    mixins em vez de copiar codigo. Cezar, Lucas e Guilherme tambem herdam de
    uma classe base de personagem.

POLIMORFISMO
    O loop chama atualizar_animacao(...) e mover_com_colisao(...) para herois,
    seguidores e inimigos. Cada objeto responde com suas proprias imagens e
    velocidades, mas o loop trata todos do mesmo jeito.

ENCAPSULAMENTO
    O estado da cena fica em CENA (mapa_config) e cada sprite guarda sua
    posicao, historico e animacao. O loop pede comportamentos (mover, animar,
    colidir) em vez de alterar cada atributo espalhado pelo codigo.

ABSTRACAO
    "Retangulo de colisao" e "retangulo de encontro" escondem a diferenca entre
    o mapa antigo (sprite quase inteiro) e o covil (somente os pes). Quem chama
    nao precisa saber qual regra esta valendo.

METODO ABSTRATO / MODELO
    Python nao exige a biblioteca abc aqui. O padrao usado e o "metodo modelo":
    a classe base define a operacao (ex.: receber_dano) e as classes concretas
    a substituem. No mapa, atualizar_animacao e o ponto comum que todo sprite
    concreto deve oferecer (imagens_parado, imagens_caminhada, etc.).

Para jogar: python mapa_teste.py
"""

from __future__ import annotations

# Importa e executa o ajuste de DPI na primeira carga do modulo.
import mapa_config as config
from mapa_config import (
    ALTURA_MAPA,
    BASE_DIR,
    CENA,
    CENA_INICIAL,
    FPS,
    LARGURA_MAPA,
    MAPA_CAMINHO,
    MAPA_INICIAL,
    PASSAGEM_COVIL,
    area_util_da_tela,
    preparar_tela_do_sistema,
)


def __getattr__(name: str):
    """Mantem MAPA_ATUAL/MAPA_COLISAO sempre atualizados como antes da divisao."""
    if name in ("MAPA_ATUAL", "MAPA_COLISAO"):
        return getattr(config, name)
    raise AttributeError(name)

# Reexporta as funcoes de colisao usadas pelo jogo e pelo editor (F3).
from mapa_colisao import (
    altura_dos_pes,
    atualizar_animacao,
    carregar_mapa,
    carregar_mapa_caminho,
    colide_com_terreno,
    desenhar_mapa_provisorio,
    mover_com_colisao,
    personagem_atras_de_oclusor,
    posicionar_pelos_pes,
    registrar_posicao,
    retangulo_colisao,
    retangulo_encontro,
)

# A classe Jogo esta em mapa_jogo.py para manter este arquivo abaixo de 500 linhas.
from mapa_jogo import Jogo


# __all__ documenta a API publica preservada para imports antigos.
__all__ = [
    "Jogo",
    "CENA",
    "CENA_INICIAL",
    "LARGURA_MAPA",
    "ALTURA_MAPA",
    "FPS",
    "BASE_DIR",
    "MAPA_INICIAL",
    "MAPA_CAMINHO",
    "MAPA_ATUAL",
    "MAPA_COLISAO",
    "PASSAGEM_COVIL",
    "area_util_da_tela",
    "preparar_tela_do_sistema",
    "altura_dos_pes",
    "atualizar_animacao",
    "carregar_mapa",
    "carregar_mapa_caminho",
    "colide_com_terreno",
    "desenhar_mapa_provisorio",
    "mover_com_colisao",
    "personagem_atras_de_oclusor",
    "posicionar_pelos_pes",
    "registrar_posicao",
    "retangulo_colisao",
    "retangulo_encontro",
]


# Quando executado diretamente (python mapa_teste.py), inicia o jogo.
if __name__ == "__main__":
    Jogo().executar()
