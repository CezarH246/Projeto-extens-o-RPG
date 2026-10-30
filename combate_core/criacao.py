"""Factories for heroes, enemies, and encounters."""

import random

from .configuracao import ESCALAS
from .inimigos import Inimigo
from .personagens import Heroi

def criar_herois():

    herois = [

        Heroi(
            "Lucas",
            "Berserk",
            5,
            escala=ESCALAS.get("Lucas", 1.0)
        ),

        Heroi(
            "Guilherme",
            "Mago",
            5,
            escala=ESCALAS.get("Guilherme", 1.0)
        ),

        Heroi(
            "Cezar",
            "Ladino",
            5,
            escala=ESCALAS.get("Cezar", 1.0)
        )
    ]

    return herois


def criar_inimigo(level=1, tipo="Normal", tipo_inimigo=None):

    nomes = {
        "Xama": [
            "Cantor dos Rios",
            "Tritã das Névoas",
            "Biomante Bêntico"
            
        ],
        "Soldado": [
            "Seguidor de Harkbal",
            "Mestre do Tridente Perolado",
            "Elite da Raiz Profunda"
        ],
        "Batedor": [
            "Mergulhadora da Caverna tritã",
            "Mergulhadora Celeste",
            "Nicanzil, Condutora da Corrente"

        ]
    }

    if tipo_inimigo is None:
        tipo_inimigo = random.choice(
            list(nomes)
        )

    nome = random.choice(nomes[tipo_inimigo])

    return Inimigo(
        f"{nome} Lv.{level}",
        level,
        tipo,
        tipo_inimigo
    )


def criar_inimigo_normal(level=1):

    return criar_inimigo(level, "Normal")


def criar_inimigo_elite(level=1):

    return criar_inimigo(level, "Elite")


def criar_inimigo_boss(level=1):

    return criar_inimigo(level, "Boss")


def criar_rei_tritao(level=1):
    """Boss especial que aparece após limpar todos os inimigos do mapa teste."""
    # Escala bem maior que a dos heróis: o Rei Tritão precisa dominar a tela
    # no combate, já que encara o grupo sozinho.
    rei = Inimigo("Rei Tritão", level, "Boss", "Soldado", escala=1.95)
    # Mais forte que um Boss comum para marcar o primeiro confronto especial.
    rei.hpMax = int(rei.hpMax * 2.10)
    rei.hp = rei.hpMax
    rei.ataque = int(rei.ataque * 1.60)
    rei.defesa = int(rei.defesa * 1.45)
    rei.velocidade *= 1.10
    rei.XpDrop = int(rei.XpDrop * 2)
    return rei


def criar_inimigo_xama(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Xama")


def criar_inimigo_soldado(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Soldado")


def criar_inimigo_batedor(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Batedor")


def criar_cenario_batalha(nivel_jogador, quantidade=3):

    categorias = random.choices(
        ["Normal", "Elite", "Boss"],
        weights=[70, 20, 10],
        k=quantidade
    )

    return [
        criar_inimigo(nivel_jogador, categoria)
        for categoria in categorias
    ]
