"""Modelo e comportamento dos inimigos."""

import random

from .personagens import Personagem
from .texto import print

class Inimigo(Personagem):
    # Pilar: Herança — compartilha os dados e comportamentos de Personagem,
    # acrescentando categoria, tipo, recompensa e ataque próprios do inimigo.

    def __init__(
        self,
        nome,
        Level=1,
        tipo="Normal",
        tipo_inimigo="Soldado",
        escala=1.0
    ):

        super().__init__(
            nome,
            Level,
            escala
        )

        # Categoria do inimigo:
        #
        # Normal
        # Elite
        # Boss

        self.tipo = tipo
        self.tipo_inimigo = tipo_inimigo

        # ----------------------------------------------------
        # ATRIBUTOS
        # ----------------------------------------------------

        # A categoria aumenta os atributos gerais; o tipo ajusta HP, ataque e
        # velocidade. Pilar: Encapsulamento — os atributos são definidos pelo objeto.
        multiplicador = 1

        if self.tipo == "Elite":
            multiplicador = 1.5

        elif self.tipo == "Boss":
            multiplicador = 2.0

        #------------------------------------
        #TIPO DO INIMIGO
        #------------------------------------
        
        multiplicadores_tipo = {
            "Xama": (0.8, 1.3, 3),
            "Soldado": (1.0, 1.0, 2),
            "Batedor": (0.85, 0.9, 4)
        }

        multiplicador_hp, multiplicador_ataque, multiplicador_velocidade = (
            multiplicadores_tipo.get(
                self.tipo_inimigo,
                multiplicadores_tipo["Soldado"]
            )
        )

        self.hpMax = int(
            (60 + (self.level * 18))
            * multiplicador
            * multiplicador_hp
        )

        self.hp = self.hpMax

        self.ataque = int(
            (8 + (self.level * 3))
            * multiplicador
            * multiplicador_ataque
        )

        self.velocidade = (
            2 + self.level
        ) * multiplicador_velocidade

        self.defesa = int(
            (1 + self.level)
            * multiplicador
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        # Calcula a recompensa no próprio inimigo com base no nível e categoria.
        self.XpDrop = self.calcular_xp_drop()

        # ----------------------------------------------------
        # DROP DE POÇÃO
        # ----------------------------------------------------

        # REGRA FIXA:
        #
        # Todo inimigo possui exatamente 30%.
        self.chanceDropPocao = 0.30

    # ========================================================
    # CALCULAR XP
    # ========================================================

    def calcular_xp_drop(self):

        # Define a recompensa do inimigo: nível multiplicado pelo valor da categoria.
        # Pilar: Encapsulamento — a regra de XP pertence ao objeto que a concede.
        # XP base aumenta conforme o nível.
        xp_base = 50 * self.level

        # Multiplicador conforme o tipo.
        if self.tipo == "Normal":

            multiplicador = 1

        elif self.tipo == "Elite":

            multiplicador = 2

        elif self.tipo == "Boss":

            multiplicador = 5

        else:

            multiplicador = 1

        return xp_base * multiplicador

    # ========================================================
    # ATAQUE
    # ========================================================

    def atacar(self, alvo):

        # Não executa ataque se o alvo não existir ou já estiver derrotado.
        if not alvo or not alvo.estar_vivo():
            return False

        # Calcula dano aleatório e delega a aplicação ao alvo.
        # Pilar: Polimorfismo — receber_dano aplica a versão correspondente
        # à classe concreta do alvo.
        dano = (
            self.ataque
            + random.randint(0, 5)
        )

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} ataca "
            f"{alvo.nome} e causa "
            f"{dano_causado} de dano."
        )

        return True
