"""Combat actions available to heroes."""

import random

from .configuracao import ultimates_sem_restricao
from .texto import print

class HeroiHabilidades:
    """Keep hero attacks and abilities separate from the base model."""

    def atacar(self, alvo):

        # Impede gastar o turno contra um alvo inexistente ou derrotado.
        if not alvo or not alvo.estar_vivo():
            return False

        # Sorteia o dano e delega ao próprio alvo a aplicação da defesa/HP.
        # Pilar: Polimorfismo — alvo.receber_dano usa a implementação adequada
        # ao tipo real do alvo (Heroi ou Inimigo).
        # Ataque base + dano aleatório.
        dano = (
            self.ataque
            + random.randint(0, 10)
        )

        # Aplica o dano.
        dano_causado = alvo.receber_dano(dano)

        # Registra uma ação para a Ultimate do Ladino.
        self.acoes_realizadas += 1

        print(
            f"{self.nome} ataca "
            f"{alvo.nome} e causa "
            f"{dano_causado} de dano."
        )

        return True

    def habilidade_especial(self, alvo):

        # Valida alvo e PA antes de alterar qualquer recurso.
        if not alvo or not alvo.estar_vivo():
            return False

        custo = 20

        # Verifica PA.
        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            return False

        # Seleciona nome e dano de acordo com a classe RPG do objeto.
        # Pilar: Encapsulamento — a regra da habilidade e seu custo ficam no herói.
        if self.ClasseRPG == "Berserk":

            nome_skill = "Golpe Glamoroso"

            dano = (
                self.ataque
                + random.randint(10, 20)
            )

        elif self.ClasseRPG == "Mago":

            nome_skill = "Explosão Arcana"

            dano = (
                self.ataque
                + random.randint(15, 25)
            )

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Tiro Preciso"

            dano = (
                self.ataque
                + random.randint(10, 25)
            )

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Ataque Fugaz"

            dano = (
                self.ataque
                + random.randint(15, 30)
            )

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Aura Sagrada"

            dano = (
                self.ataque
                + random.randint(10, 20)
            )

        # Cobra o custo e atualiza os contadores usados para liberar a Ultimate.
        self.PA -= custo

        # Registra o PA gasto.
        self.pa_gasto_ultimate += custo

        # Registra ação.
        self.acoes_realizadas += 1

        # Aplica o dano através do método do alvo, que calcula sua defesa.
        # Pilar: Polimorfismo — a implementação depende da classe concreta do alvo.
        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} usa "
            f"{nome_skill} em {alvo.nome} "
            f"e causa {dano_causado} de dano!"
        )

        return True

    def segunda_habilidade(self, alvo):

        # Bloqueia a habilidade até o nível 5, sem consumir recursos.
        # Pilar: Encapsulamento — a classe Heroi valida sua própria regra de uso.
        if self.level < 5:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou essa habilidade."
            )

            return False

        # Exige um alvo válido e vivo antes de cobrar PA ou causar dano.
        if not alvo or not alvo.estar_vivo():
            return False

        custo = 40

        # Confere o recurso necessário antes de executar a habilidade.
        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            return False

        # Cada classe recebe seu nome de habilidade e faixa de dano próprios.
        if self.ClasseRPG == "Berserk":

            nome_skill = "Investida Fabulosa"

            dano = (
                self.ataque
                + random.randint(20, 30)
            )

        elif self.ClasseRPG == "Mago":

            nome_skill = "Inversão da Realidade"

            dano = (
                self.ataque
                + random.randint(25, 40)
            )

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Rajada de Flechas"

            dano = (
                self.ataque
                + random.randint(20, 35)
            )

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Adaga Venenosa"

            dano = (
                self.ataque
                + random.randint(25, 40)
            )

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Julgamento Divino"

            dano = (
                self.ataque
                + random.randint(20, 35)
            )

        # Cobra PA, atualiza os contadores da Ultimate e aplica o dano no alvo.
        self.PA -= custo

        # Guarda o PA gasto para a Ultimate.
        self.pa_gasto_ultimate += custo

        # Conta como uma ação.
        self.acoes_realizadas += 1

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} usa "
            f"{nome_skill} em {alvo.nome} "
            f"e causa {dano_causado} de dano!"
        )

        return True

    def ultimate(self, alvo):

        # Confere se a Ultimate está implementada para este herói e se o alvo
        # pode recebê-la antes de alterar o estado da batalha.
        # Pilar: Encapsulamento — os requisitos de uso são verificados no herói.
        # Cezar e Guilherme já possuem Ultimate implementada.
        if not ultimates_sem_restricao() and self.nome not in {"Cezar", "Guilherme"}:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou a Ultimate."
            )

            return False

        if not alvo or not alvo.estar_vivo():
            return False

        # ====================================================
        # MAGO
        # ====================================================

        # A classe define os requisitos e a fórmula de dano da Ultimate.
        # Pilar: Encapsulamento — cada herói aplica as regras do seu próprio golpe.
        if self.ClasseRPG == "Mago":

            # O Mago precisa ter gasto pelo menos 60 PA
            # desde a última Ultimate.
            if not ultimates_sem_restricao() and self.pa_gasto_ultimate < 60:

                print(
                    f"🔥 O Mago precisa gastar "
                    f"pelo menos 60 PA antes da Ultimate."
                )

                print(
                    f"PA gasto atualmente: "
                    f"{self.pa_gasto_ultimate}"
                )

                return False

            nome_skill = "NÃO ME ESTRESSA PORRA (O VAZIO SUSURRA)"

            # Quanto mais PA gastou, mais forte.
            dano = (
                self.ataque * 4
                + self.pa_gasto_ultimate
                + random.randint(30, 50)
            )

        # ====================================================
        # BERSERK
        # ====================================================

        elif self.ClasseRPG == "Berserk":

            # O Berserk precisa ter levado pelo menos
            # 50 de dano.
            if not ultimates_sem_restricao() and self.dano_recebido_ultimate < 50:

                print(
                    f"🔥 O Berserk precisa levar "
                    f"pelo menos 50 de dano!"
                )

                print(
                    f"Dano recebido: "
                    f"{self.dano_recebido_ultimate}"
                )

                return False

            nome_skill = "NÃO TOCA NO CABELO"

            # Quanto mais dano recebeu,
            # mais forte fica a Ultimate.
            dano = (
                self.ataque * 3
                + self.dano_recebido_ultimate
                + random.randint(20, 40)
            )

        # ====================================================
        # LADINO
        # ====================================================

        elif self.ClasseRPG == "Ladino":

            # O Ladino precisa realizar pelo menos
            # 5 ações.
            if not ultimates_sem_restricao() and self.nome != "Cezar" and self.acoes_realizadas < 5:

                print(
                    f"🔥 O Ladino precisa realizar "
                    f"5 ações antes da Ultimate!"
                )

                print(
                    f"Ações realizadas: "
                    f"{self.acoes_realizadas}"
                )

                return False

            nome_skill = "AS SOMBRAS ME GUIAM(È A GARRAFA DE CERVEJA FALANDO)"

            # Quanto mais ações realizou,
            # maior o dano.
            dano = (
                self.ataque * 4
                + (self.acoes_realizadas * 10)
                + random.randint(20, 40)
            )

        # ====================================================
        # OUTRAS CLASSES
        # ====================================================

        elif self.ClasseRPG == "Arqueiro":

            # Arqueiro precisa de PA cheio.
            if not ultimates_sem_restricao() and self.PA < 100:

                print(
                    "🏹 O Arqueiro precisa estar "
                    "com PA cheio!"
                )

                return False

            nome_skill = "Flecha Celestial"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        elif self.ClasseRPG == "Paladino":

            # Paladino precisa de PA cheio.
            if not ultimates_sem_restricao() and self.PA < 100:

                print(
                    "🛡️ O Paladino precisa estar "
                    "com PA cheio!"
                )

                return False

            nome_skill = "Ira Divina"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        else:
            return False

        # ====================================================
        # EXECUTAR ULTIMATE
        # ====================================================

        # Executa a Ultimate: consome PA, aplica dano e limpa os contadores para
        # iniciar o próximo ciclo de carregamento.
        self.PA = 0

        # Aplica o dano.
        dano_causado = alvo.receber_dano(dano)

        print("\n🔥 ===============================")

        print(
            f"🔥 {self.nome} usa "
            f"a ULTIMATE {nome_skill}!"
        )

        print(
            f"💥 Causa {dano_causado} de dano!"
        )

        print("🔥 ===============================")

        # ----------------------------------------------------
        # RESET DAS CONDIÇÕES DA ULTIMATE
        # ----------------------------------------------------

        # Zera os requisitos acumulados para a próxima Ultimate.
        self.pa_gasto_ultimate = 0
        self.dano_recebido_ultimate = 0
        self.acoes_realizadas = 0

        return True

    def usar_pocao_pa(self):

        # Evita consumir uma poção sem estoque ou quando o PA já está cheio.
        # Pilar: Encapsulamento — o herói valida e altera seus próprios recursos.
        if self.pocoesPA <= 0:

            print(
                f"{self.nome} não possui "
                f"poções de PA."
            )

            return False

        if self.PA >= self.PAMax:

            print(
                f"{self.nome} já está "
                f"com o PA cheio."
            )

            return False

        recuperacao = 50

        # Recupera até 50 PA sem ultrapassar o máximo e consome uma poção.
        self.PA = min(
            self.PAMax,
            self.PA + recuperacao
        )

        self.pocoesPA -= 1

        # Usar poção também conta como ação.
        self.acoes_realizadas += 1

        print(
            f"🧪 {self.nome} usou "
            f"uma Poção de PA!"
        )

        print(
            f"PA: {self.PA}/{self.PAMax}"
        )

        print(
            f"Poções restantes: "
            f"{self.pocoesPA}"
        )

        return True
