import random
import sys
import time


# ============================================================
# CONFIGURAÇÕES
# ============================================================

# Tempo entre os caracteres exibidos no terminal.
VELOCIDADE_TEXTO = 0.002


# Função responsável por imprimir o texto lentamente.
def imprimir_lento(*args, sep=" ", end="\n"):
    texto = sep.join(str(arg) for arg in args)

    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(VELOCIDADE_TEXTO)

    sys.stdout.write(end)
    sys.stdout.flush()


# Substitui o print normal pelo nosso print com efeito de texto.
print = imprimir_lento


# ============================================================
# CLASSE BASE - PERSONAGEM
# ============================================================

class Personagem:

    # --------------------------------------------------------
    # CONSTRUTOR
    # --------------------------------------------------------

    def __init__(self, nome, level=1, escala=1.0):

        # Nome do personagem.
        self.nome = nome

        # Escala individual do combatente na tela.
        # Valores menores reduzem o sprite e valores maiores aumentam.
        self.escala = float(escala)

        # O nível fica limitado entre 1 e 10.
        self.level = max(1, min(level, 10))

        # Atributos básicos.
        self.hpMax = 10
        self.hp = 10

        self.ataque = 2
        self.velocidade = 1
        self.defesa = 0

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

        return self.hp > 0

    # --------------------------------------------------------
    # RECEBER DANO
    # --------------------------------------------------------

    def receber_dano(self, dano):

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

        # Retorna o dano realmente recebido.
        return dano_final

    # --------------------------------------------------------
    # CARREGAR ATB
    # --------------------------------------------------------

    def carregar_atb(self, multiplicador_tempo):

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

        self.atb_barra = 0.0


# ============================================================
# CLASSE HEROI
# ============================================================

class Heroi(Personagem):

    # --------------------------------------------------------
    # CONSTRUTOR
    # --------------------------------------------------------

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

    # ========================================================
    # ATRIBUTOS POR CLASSE E NÍVEL
    # ========================================================

    def CalcularAtributosPorLevel(self):

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

    # ========================================================
    # RECEBER DANO
    # ========================================================

    def receber_dano(self, dano):

        # Guarda o HP antes do ataque.
        hp_antes = self.hp

        # Usa a função da classe Personagem.
        dano_real = super().receber_dano(dano)

        # Calcula quanto HP foi perdido.
        dano_recebido = hp_antes - self.hp

        # Guarda o dano para a Ultimate do Berserk.
        self.dano_recebido_ultimate += dano_recebido

        return dano_real

    # ========================================================
    # STATUS DO HERÓI
    # ========================================================

    def mostrar_status(self):

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

    # ========================================================
    # ATAQUE NORMAL
    # ========================================================

    def atacar(self, alvo):

        if not alvo or not alvo.estar_vivo():
            return False

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

    # ========================================================
    # HABILIDADE ESPECIAL 1
    # ========================================================

    def habilidade_especial(self, alvo):

        if not alvo or not alvo.estar_vivo():
            return False

        custo = 20

        # Verifica PA.
        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            return False

        # Define habilidade de acordo com a classe.
        if self.ClasseRPG == "Berserk":

            nome_skill = "Golpe Glamoroso"

            dano = (
                self.ataque
                + random.randint(10, 20)
            )

        elif self.ClasseRPG == "Mago":

            nome_skill = "ELEGEBETEEEEEEEE!!!!"

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

            nome_skill = "Te Passei o Calote"

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

        # Gasta PA.
        self.PA -= custo

        # Registra o PA gasto.
        self.pa_gasto_ultimate += custo

        # Registra ação.
        self.acoes_realizadas += 1

        # Aplica dano.
        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} usa "
            f"{nome_skill} em {alvo.nome} "
            f"e causa {dano_causado} de dano!"
        )

        return True

    # ========================================================
    # HABILIDADE ESPECIAL 2
    # ========================================================

    def segunda_habilidade(self, alvo):

        # Só libera no nível 5.
        if self.level < 5:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou essa habilidade."
            )

            return False

        if not alvo or not alvo.estar_vivo():
            return False

        custo = 40

        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            return False

        if self.ClasseRPG == "Berserk":

            nome_skill = "Investida Fabulosa"

            dano = (
                self.ataque
                + random.randint(20, 30)
            )

        elif self.ClasseRPG == "Mago":

            nome_skill = "TDAH Arcano"

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

            nome_skill = "Passa a Grana"

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

        # Gasta PA.
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

    # ========================================================
    # ULTIMATE
    # ========================================================

    def ultimate(self, alvo):

        # Ultimate só libera no nível 10.
        if self.level < 10:

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

        if self.ClasseRPG == "Mago":

            # O Mago precisa ter gasto pelo menos 60 PA
            # desde a última Ultimate.
            if self.pa_gasto_ultimate < 60:

                print(
                    f"🔥 O Mago precisa gastar "
                    f"pelo menos 60 PA antes da Ultimate."
                )

                print(
                    f"PA gasto atualmente: "
                    f"{self.pa_gasto_ultimate}"
                )

                return False

            nome_skill = "NÃO ME ESTRESSA PORRA"

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
            if self.dano_recebido_ultimate < 50:

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
            if self.acoes_realizadas < 5:

                print(
                    f"🔥 O Ladino precisa realizar "
                    f"5 ações antes da Ultimate!"
                )

                print(
                    f"Ações realizadas: "
                    f"{self.acoes_realizadas}"
                )

                return False

            nome_skill = "A RESSACA BATEU"

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
            if self.PA < 100:

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
            if self.PA < 100:

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

        # A Ultimate consome todo o PA.
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

        # Depois de usar a Ultimate,
        # começamos a contabilizar novamente.
        self.pa_gasto_ultimate = 0
        self.dano_recebido_ultimate = 0
        self.acoes_realizadas = 0

        return True

    # ========================================================
    # USAR POÇÃO
    # ========================================================

    def usar_pocao_pa(self):

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

        # Recupera no máximo até 100.
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


# ============================================================
# CLASSE INIMIGO
# ============================================================

class Inimigo(Personagem):

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

        # A quantidade de XP será calculada
        # de acordo com nível + tipo.
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

        if not alvo or not alvo.estar_vivo():
            return False

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


# ============================================================
# BARRA DE AÇÃO
# ============================================================

def exibir_barra_atb(combatentes):

    print("\n========== BARRA DE AÇÃO ==========")

    for personagem in combatentes:

        if personagem.estar_vivo():

            progressao = int(
                personagem.atb_barra / 10
            )

            barra_visual = (
                "#" * progressao
                + "." * (10 - progressao)
            )

            print(
                f"{personagem.nome:<16} "
                f"ATB: [{barra_visual}] "
                f"{personagem.atb_barra:.1f}/"
                f"{personagem.atb_max:.0f}"
            )


# ============================================================
# ESCALAS DOS COMBATENTES
# ============================================================
# Centraliza a escala visual de cada combatente em um único lugar.
# Ajuste os valores aqui para mudar o tamanho do sprite sem alterar
# a lógica de criação dos personagens.

ESCALAS = {
    "Lucas": 1.5,
    "Guilherme": 0.95,
    "Cezar": 1.1,
}


# ============================================================
# CRIAR HERÓIS
# ============================================================

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
            escala=ESCALAS.get("Cezar", 0.5)
        )
    ]

    return herois


# ============================================================
# CRIAR 3 TIPOS DE INIMIGOS, 
# XAMA, SOLDADO E BATEDOR
# COM 3 CATEGORIAS DIFERENTES, 
# NORMAL, ELITE E BOSS
# ============================================================

def criar_inimigo(level=1, tipo="Normal", tipo_inimigo=None):

    nomes = {
        "Xama": [
            "Cantor dos Rios",
            "Tritã das Névoas",
            "Biomante Bêntico"
            
        ],
        "Soldado": [
            "Harkbal Mestre tritão",
            "Mestre do Tridente Perolado",
            "Tritão do Mar"
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

    escala_padrao = {
        "Xama": 1.2,
        "Soldado": 1.3,
        "Batedor": 1.2,
    }.get(tipo_inimigo, 1.0)

    return Inimigo(
        f"{nome} Lv.{level}",
        level,
        tipo,
        tipo_inimigo,
        escala_padrao
    )


def criar_inimigo_normal(level=1):

    return criar_inimigo(level, "Normal")


def criar_inimigo_elite(level=1):

    return criar_inimigo(level, "Elite")


def criar_inimigo_boss(level=1):

    return criar_inimigo(level, "Boss")


def criar_inimigo_xama(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Xama")


def criar_inimigo_soldado(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Soldado")


def criar_inimigo_batedor(level=1, tipo="Normal"):

    return criar_inimigo(level, tipo, "Batedor")

#================================================================
# Essa função cria um cenário de batalha. quantidade de inimigos
# e uma aleatoridade entre inimigos normais, elite e boss
#=================================================================

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


# ============================================================
# MOSTRAR STATUS DOS HERÓIS
# ============================================================

def mostrar_status_herois(herois):

    print("\n")

    print(
        "========== STATUS DOS HERÓIS =========="
    )

    for heroi in herois:

        print(
            heroi.mostrar_status()
        )


# ============================================================
# DROP DE XP
# ============================================================

def dar_xp(inimigo, herois):

    # XP definido pelo nível e tipo do inimigo.
    xp = inimigo.XpDrop

    # Apenas heróis vivos recebem XP.
    herois_vivos = [
        heroi
        for heroi in herois
        if heroi.estar_vivo()
    ]

    if not herois_vivos:
        return

    # Divide o XP entre os heróis vivos.
    xp_por_heroi = xp // len(herois_vivos)

    print("\n⭐ ===============================")

    print(
        f"⭐ O grupo derrotou um "
        f"{inimigo.tipo}!"
    )

    print(
        f"⭐ XP total: {xp}"
    )

    for heroi in herois_vivos:

        heroi.Xp += xp_por_heroi

        print(
            f"⭐ {heroi.nome} recebeu "
            f"{xp_por_heroi} XP."
        )

        # ----------------------------------------------------
        # LEVEL UP
        # ----------------------------------------------------

        while (
            heroi.Xp >= heroi.XpMax
            and heroi.level < 10
        ):

            heroi.Xp -= heroi.XpMax

            heroi.level += 1

            # Aumenta a XP necessária.
            heroi.XpMax = int(
                heroi.XpMax * 1.5
            )

            # Recalcula os atributos.
            heroi.CalcularAtributosPorLevel()

            print(
                f"🎉 {heroi.nome} subiu "
                f"para o nível "
                f"{heroi.level}!"
            )

    print("⭐ ===============================")


# ============================================================
# DROP DE POÇÃO
# ============================================================

def verificar_drop_pocao(inimigo, herois):

    # REGRA FIXA:
    #
    # Sempre 30%.
    sorteio = random.random()

    if sorteio <= 0.30:

        herois_vivos = [
            heroi
            for heroi in herois
            if heroi.estar_vivo()
        ]

        if herois_vivos:

            heroi = random.choice(
                herois_vivos
            )

            heroi.pocoesPA += 1

            print("\n🧪 ===============================")

            print(
                f"🧪 {inimigo.nome} "
                f"deixou uma Poção de PA!"
            )

            print(
                f"🧪 A poção foi para "
                f"{heroi.nome}."
            )

            print(
                f"🧪 Poções de {heroi.nome}: "
                f"{heroi.pocoesPA}"
            )

            print("🧪 ===============================")

            return True

    print(
        f"\n{inimigo.nome} não deixou "
        f"nenhuma poção."
    )

    return False


# ============================================================
# SISTEMA DE PERGAMINHOS
# ============================================================

def abrir_bau(heroi):

    # Lista de pergaminhos disponíveis.
    pergaminhos = [

        "Pergaminho de Fogo",

        "Pergaminho de Gelo",

        "Pergaminho de Cura",

        "Pergaminho de Trovão",

        "Pergaminho das Sombras"
    ]

    # Chance de encontrar um pergaminho.
    if random.random() <= 0.50:

        pergaminho = random.choice(
            pergaminhos
        )

        print("\n📜 ===============================")

        print(
            f"📜 {heroi.nome} abriu o baú!"
        )

        print(
            f"📜 Encontrou: {pergaminho}"
        )

        print("📜 ===============================")

        return pergaminho

    print(
        f"\n📦 {heroi.nome} abriu o baú, "
        f"mas não encontrou um pergaminho."
    )

    return None


# ============================================================
# Escolher inimigo para atacar
# ============================================================

def escolher_inimigo(inimigos):

    inimigos_vivos = [
        inimigo
        for inimigo in inimigos
        if inimigo.estar_vivo()
    ]

    print("\nEscolha qual inimigo atacar:")

#=================================================================
# Este loop exibe os inimigos vivos com seus índices e informações de status,
# permitindo que o jogador escolha um alvo para atacar.
#====================================================================

    for indice, inimigo in enumerate(inimigos_vivos, start=1):

        print(
            f"{indice} - {inimigo.nome} "
            f"({inimigo.tipo_inimigo} - {inimigo.tipo}) | "
            f"HP: {inimigo.hp}/{inimigo.hpMax}"
        )
#=================================================================
# Este loop continua solicitando ao jogador que escolha um inimigo até
# que uma opção válida seja fornecida.
#====================================================================
# O método .isdigit() é uma função do Python usada para verificar se um texto (string)
#  contém apenas números inteiros e positivos.
#==============================================================================
    while True:

        escolha = input("Número do inimigo: ")

        if escolha.isdigit():

            indice = int(escolha) - 1

            if 0 <= indice < len(inimigos_vivos):

                return inimigos_vivos[indice]

        print("Opção inválida. Escolha um inimigo vivo.")

# ============================================================
# TURNO DO JOGADOR
# ============================================================

def turno_jogador(heroi, inimigos):

    while True:

        print("\n")

        print(
            f"========== TURNO DE "
            f"{heroi.nome} =========="
        )

        print(
            f"HP: {heroi.hp}/{heroi.hpMax}"
        )

        print(
            f"PA: {heroi.PA}/{heroi.PAMax}"
        )

        print(
            f"Poções: {heroi.pocoesPA}"
        )

        # Informações úteis para as Ultimates.
        print(
            f"PA gasto para Ultimate: "
            f"{heroi.pa_gasto_ultimate}"
        )

        print(
            f"Dano recebido para Ultimate: "
            f"{heroi.dano_recebido_ultimate}"
        )

        print(
            f"Ações realizadas: "
            f"{heroi.acoes_realizadas}"
        )

        print("\nEscolha sua ação:")

        print("1 - Ataque normal")

        print(
            "2 - Habilidade especial "
            "(20 PA)"
        )

        if heroi.level >= 5:

            print(
                "3 - Segunda habilidade "
                "(40 PA)"
            )

        if heroi.level >= 10:

            print(
                "4 - Ultimate"
            )

        print(
            "5 - Usar Poção de PA"
        )

        print(
            "6 - Defender"
        )

        escolha = input(
            "\nEscolha sua ação: "
        )

        # ----------------------------------------------------
        # ATAQUE
        # ----------------------------------------------------

        if escolha == "1":

            alvo = escolher_inimigo(inimigos)

            if heroi.atacar(alvo):
                return

        # ----------------------------------------------------
        # SKILL 1
        # ----------------------------------------------------

        elif escolha == "2":

            alvo = escolher_inimigo(inimigos)

            if heroi.habilidade_especial(alvo):
                return

        # ----------------------------------------------------
        # SKILL 2
        # ----------------------------------------------------

        elif (
            escolha == "3"
            and heroi.level >= 5
        ):

            alvo = escolher_inimigo(inimigos)

            if heroi.segunda_habilidade(alvo):
                return

        # ----------------------------------------------------
        # ULTIMATE
        # ----------------------------------------------------

        elif (
            escolha == "4"
            and heroi.level >= 10
        ):

            alvo = escolher_inimigo(inimigos)

            if heroi.ultimate(alvo):
                return

        # ----------------------------------------------------
        # POÇÃO
        # ----------------------------------------------------

        elif escolha == "5":

            if heroi.usar_pocao_pa():
                return

        # ----------------------------------------------------
        # DEFENDER
        # ----------------------------------------------------

        elif escolha == "6":

            print(
                f"{heroi.nome} se prepara "
                f"para defender."
            )

            # Aumenta a defesa.
            heroi.defesa += 5

            # Conta como uma ação.
            heroi.acoes_realizadas += 1

            return

        else:

            print(
                "Opção inválida. "
                "Tente novamente."
            )


# ============================================================
# HISTÓRIA
# ============================================================

# def mostrar_historia():

#     print("\n")
#     print("======================================")
#     print("              HISTÓRIA")
#     print("======================================")

#     print(
#         "O reino de Eldoria está sendo "
#         "ameaçado por criaturas misteriosas."
#     )

#     print(
#         "Um grupo de aventureiros foi "
#         "convocado para descobrir a origem "
#         "dessa ameaça."
#     )

#     print(
#         "Durante a jornada, os heróis irão "
#         "encontrar monstros, baús, "
#         "pergaminhos e chefes."
#     )

#     print(
#         "A verdadeira origem do conflito "
#         "ainda permanece desconhecida..."
#     )


# ============================================================
# BATALHA
# ============================================================

def batalha():

    # Cria os heróis.
    herois = criar_herois()

    # Cria três inimigos com o nível atual do jogador.
    inimigos = criar_cenario_batalha(herois[0].level)

    print("\n")

    print("======================================")
    print("           RPG DE TURNOS")
    print("======================================")

    for inimigo in inimigos:

        print(
            f"\n👹 Inimigo apareceu: "
            f"{inimigo.nome}"
        )

        print(
            f"Tipo: {inimigo.tipo_inimigo} | "
            f"Categoria: {inimigo.tipo}"
        )

        print(
            f"XP: {inimigo.XpDrop}"
        )

        print(
            inimigo.mostrar_status()
        )

    mostrar_status_herois(
        herois
    )

    # Todos os combatentes.
    combatentes = herois + inimigos

    # Tempo do sistema de ATB.
    tick_rate = 0.1

    multiplicador_tempo = 0.5

    # ========================================================
    # LOOP DA BATALHA
    # ========================================================

    while True:

        # ----------------------------------------------------
        # VERIFICAR VITÓRIA
        # ----------------------------------------------------

        inimigos_vivos = [
            inimigo
            for inimigo in inimigos
            if inimigo.estar_vivo()
        ]

        if not inimigos_vivos:

            print("\n======================================")

            print("              VITÓRIA!")

            print("======================================")

            for inimigo in inimigos:

                print(
                    f"🏆 {inimigo.nome} foi derrotado!"
                )

                print(
                    inimigo.mostrar_status()
                )

                dar_xp(
                    inimigo,
                    herois
                )

                verificar_drop_pocao(
                    inimigo,
                    herois
                )

            break

        # ----------------------------------------------------
        # VERIFICAR DERROTA
        # ----------------------------------------------------

        if not any(
            heroi.estar_vivo()
            for heroi in herois
        ):

            print("\n======================================")

            print("              DERROTA!")

            print("======================================")

            print(
                "💀 Todos os heróis "
                "foram derrotados."
            )

            break

        # ----------------------------------------------------
        # CARREGAR ATB
        # ----------------------------------------------------

        for personagem in combatentes:

            personagem.carregar_atb(
                multiplicador_tempo
            )

        # Mostra a barra.
        exibir_barra_atb(
            combatentes
        )

        time.sleep(
            tick_rate
        )

        # ----------------------------------------------------
        # PROCURAR QUEM ESTÁ PRONTO
        # ----------------------------------------------------

        personagem_pronto = next(

            (
                personagem
                for personagem in combatentes

                if (
                    personagem.estar_vivo()
                    and
                    personagem.atb_barra
                    >= personagem.atb_max
                )
            ),

            None
        )

        if personagem_pronto is None:

            continue

        # ====================================================
        # TURNO DO HERÓI
        # ====================================================

        if isinstance(
            personagem_pronto,
            Heroi
        ):

            turno_jogador(
                personagem_pronto,
                inimigos
            )

        # ====================================================
        # TURNO DO INIMIGO
        # ====================================================

        else:

            herois_vivos = [

                heroi
                for heroi in herois

                if heroi.estar_vivo()
            ]

            if herois_vivos:

                alvo = random.choice(
                    herois_vivos
                )

                print(
                    f"\n🚨 TURNO INIMIGO: "
                    f"{personagem_pronto.nome}"
                )

                personagem_pronto.atacar(
                    alvo
                )

                print(
                    alvo.mostrar_status()
                )

        # ----------------------------------------------------
        # RESET DA ATB
        # ----------------------------------------------------

        personagem_pronto.resetar_atb()

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        mostrar_status_herois(
            herois
        )

        print(
            "\n========== STATUS DOS INIMIGOS =========="
        )

        for inimigo in inimigos:

            print(
                inimigo.mostrar_status()
            )


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    print(
        "Bem-vindo ao RPG de Turnos!"
    )

    # Mostra a introdução da história.
    # mostrar_historia()

    # Inicia a batalha.
    batalha()