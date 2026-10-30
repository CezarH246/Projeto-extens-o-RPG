"""Base character and playable hero models."""

from .habilidades import HeroiHabilidades
from .texto import print

class Personagem:

    # --------------------------------------------------------
    # CONSTRUTOR
    # --------------------------------------------------------

    def __init__(self, nome, level=1, escala=1.0):

        # combate (atributos e barras) junto dos métodos que o atualizam.
        # Nome do personagem.
        self.nome = nome
        self.escala = float(escala)

        # O nível fica limitado entre 1 e 10.
        self.level = max(1, min(level, 10))

        # Atributos básicos.
        self.hpMax = 10
        self.hp = 10

        self.ataque = 2
        self.velocidade = 1
        self.defesa = 0

        # Armazena o último dano recebido para exibição visual
        self._ultimo_dano_recebido = 0

        # ----------------------------------------------------
        # BARRA DE AÇÃO
        # ----------------------------------------------------

        # Barra atual.
        self.atb_barra = 0.0

        # Valor necessário para executar uma ação.
        self.atb_max = 100.0

    # --------------------------------------------------------
    # MOSTRAR STATUS
    # --------------------------------------------------------

    def mostrar_status(self):

        # Calcula o tamanho da barra de HP.
        barra_hp = (
            int((self.hp / self.hpMax) * 20)
            if self.hpMax > 0
            else 0
        )

        # Mantém a barra entre 0 e 20.
        barra_hp = max(0, min(20, barra_hp))

        return (
            f"{self.nome} (Lvl {self.level}): "
            f"HP: {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}{'.' * (20 - barra_hp)}] | "
            f"ATQ: {self.ataque} | "
            f"DEF: {self.defesa} | "
            f"VEL: {self.velocidade}"
        )

    # --------------------------------------------------------
    # VERIFICAR SE ESTÁ VIVO
    # --------------------------------------------------------

    def estar_vivo(self):
        # Consulta o HP por um método, sem repetir essa regra em cada sistema.
        # Pilar: Encapsulamento — o estado do objeto é consultado por seu comportamento.
        return self.hp > 0

    # --------------------------------------------------------
    # RECEBER DANO
    # --------------------------------------------------------

    def receber_dano(self, dano):

        # Subtrai a defesa do ataque, mas garante pelo menos 1 de dano.
        # Pilar: Encapsulamento — concentra a alteração de HP nesta operação.
        # A defesa reduz o dano recebido.
        dano_final = max(
            1,
            dano - self.defesa
        )

        # Reduz o HP.
        self.hp = max(
            0,
            self.hp - dano_final
        )

        # Armazena o dano recebido para exibição visual
        self._ultimo_dano_recebido = dano_final

        # Devolve o valor aplicado para que o atacante possa informar o resultado.
        return dano_final

    # --------------------------------------------------------
    # CARREGAR ATB
    # --------------------------------------------------------

    def carregar_atb(self, multiplicador_tempo):

        # Só combatentes vivos avançam a barra, limitada ao valor necessário
        # para agir. Pilar: Encapsulamento — atualiza a ATB dentro do objeto.
        # Personagem morto não carrega a barra.
        if self.estar_vivo():

            self.atb_barra = min(
                self.atb_max,
                self.atb_barra
                + (self.velocidade * multiplicador_tempo)
            )

    # --------------------------------------------------------
    # RESETAR ATB
    # --------------------------------------------------------

    def resetar_atb(self):
        # Zera a barra depois do turno para iniciar a próxima contagem.
        # Pilar: Encapsulamento — o objeto controla a própria prontidão.
        self.atb_barra = 0.0

class Heroi(Personagem, HeroiHabilidades):
    """Playable character with attributes, resources, and progression."""

    def __init__(self, nome, ClasseRPG, Level=1, escala=1.0):

        # Inicializa a classe pai.
        super().__init__(nome, Level, escala)

        # Classe do personagem.
        self.ClasseRPG = ClasseRPG

        # ----------------------------------------------------
        # EXPERIÊNCIA
        # ----------------------------------------------------

        self.Xp = 0

        # XP necessária para próximo nível.
        self.XpMax = 100

        # ----------------------------------------------------
        # PONTOS DE AÇÃO
        # ----------------------------------------------------

        self.PAMax = 100

        # Começa com PA cheio.
        self.PA = self.PAMax

        # ----------------------------------------------------
        # POÇÕES
        # ----------------------------------------------------

        self.pocoesPA = 3

        # ----------------------------------------------------
        # ESTATÍSTICAS PARA ULTIMATES
        # ----------------------------------------------------

        # Quanto PA o personagem gastou desde a última Ultimate.
        self.pa_gasto_ultimate = 0

        # Quanto dano o personagem recebeu desde a última Ultimate.
        self.dano_recebido_ultimate = 0

        # Quantas ações o personagem realizou desde a última Ultimate.
        self.acoes_realizadas = 0

        # Calcula os atributos da classe.
        self.CalcularAtributosPorLevel()

    def CalcularAtributosPorLevel(self):

        # A classe escolhida define os atributos iniciais e os ganhos por nível.
        # Pilar: Encapsulamento — o cálculo dos atributos do herói fica na classe.
        # ----------------------------------------------------
        # BERSERK
        # ----------------------------------------------------

        if self.ClasseRPG == "Berserk":

            self.hpMax = 80 + (self.level * 20)

            self.ataque = 6 + (self.level * 4)

            self.velocidade = 4 + (self.level * 3)

        # ----------------------------------------------------
        # MAGO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Mago":

            self.hpMax = 50 + (self.level * 10)

            self.ataque = 7 + (self.level * 5)

            self.velocidade = 5 + (self.level * 4)

        # ----------------------------------------------------
        # ARQUEIRO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Arqueiro":

            self.hpMax = 60 + (self.level * 15)

            self.ataque = 6 + (self.level * 4)

            self.velocidade = 8 + (self.level * 5)

        # ----------------------------------------------------
        # LADINO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Ladino":

            self.hpMax = 65 + (self.level * 12)

            self.ataque = 8 + (self.level * 4)

            self.velocidade = 12 + (self.level * 6)

        # ----------------------------------------------------
        # PALADINO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Paladino":

            self.hpMax = 90 + (self.level * 25)

            self.ataque = 5 + (self.level * 3)

            self.velocidade = 3 + (self.level * 2)

        # Começa com HP cheio.
        self.hp = self.hpMax

    def receber_dano(self, dano):

        # Estende o recebimento de dano da classe base para registrar progresso
        # da Ultimate. Pilar: Polimorfismo — esta versão substitui a herdada e
        # é chamada quando um alvo Heroi recebe dano.
        # Guarda o HP antes do ataque.
        hp_antes = self.hp

        # Usa a função da classe Personagem.
        dano_real = super().receber_dano(dano)

        # Calcula quanto HP foi perdido.
        dano_recebido = hp_antes - self.hp

        # Guarda o dano para a Ultimate do Berserk.
        self.dano_recebido_ultimate += dano_recebido

        return dano_real

    def mostrar_status(self):

        # Monta o status com os recursos próprios do herói, incluindo PA.
        # Pilar: Polimorfismo — substitui a versão de Personagem para apresentar
        # os dados adicionais desta subclasse.
        # Barra de HP.
        barra_hp = int(
            (self.hp / self.hpMax) * 20
        )

        barra_hp = max(
            0,
            min(20, barra_hp)
        )

        # Barra de PA.
        barra_pa = int(
            (self.PA / self.PAMax) * 20
        )

        barra_pa = max(
            0,
            min(20, barra_pa)
        )

        return (
            f"{self.nome} "
            f"(Lvl {self.level} - {self.ClasseRPG}) | "

            f"HP: {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}"
            f"{'.' * (20 - barra_hp)}] | "

            f"PA: {self.PA}/{self.PAMax} "
            f"[{'#' * barra_pa}"
            f"{'.' * (20 - barra_pa)}] | "

            f"ATQ: {self.ataque} | "
            f"DEF: {self.defesa} | "
            f"VEL: {self.velocidade} | "

            f"Poções: {self.pocoesPA}"
        )
