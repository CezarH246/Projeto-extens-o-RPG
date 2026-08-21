import random


# ============================================================
# CLASSE BASE - PERSONAGEM
# ============================================================
# Esta é a classe "pai" dos personagens do jogo.
#
# Tanto os HERÓIS quanto os INIMIGOS possuem características
# em comum, como:
#
# - Nome
# - Nível
# - HP
# - Ataque
# - Defesa
# - Velocidade
#
# Por isso criamos esses atributos e funções aqui.
#
# Depois, Heroi e Inimigo irão HERDAR dessa classe.
# ============================================================

class Personagem:

    # --------------------------------------------------------
    # __init__
    # --------------------------------------------------------
    # É o construtor da classe.
    #
    # Ele é executado automaticamente quando criamos um objeto.
    #
    # Exemplo:
    #
    # personagem = Personagem("Guilherme", 1)
    #
    # Nesse momento o Python executa automaticamente
    # o __init__.
    # --------------------------------------------------------

    def __init__(self, nome, level=1):

        # Guarda o nome recebido no objeto.
        self.nome = nome

        # Define o nível do personagem.
        #
        # max(1, ...) impede que o nível seja menor que 1.
        #
        # min(level, 10) impede que o nível seja maior que 10.
        #
        # Portanto o nível sempre ficará entre 1 e 10.
        self.level = max(1, min(level, 10))

        # ----------------------------------------------------
        # ATRIBUTOS BASE
        # ----------------------------------------------------
        # Esses valores são apenas valores iniciais.
        #
        # As classes filhas irão modificar esses atributos
        # de acordo com o tipo do personagem.

        self.hpMax = 10
        self.hp = 10

        self.ataque = 2
        self.velocidade = 1
        self.defesa = 0

    # --------------------------------------------------------
    # mostrar_status
    # --------------------------------------------------------
    # Retorna uma string contendo os atributos do personagem.
    #
    # A função também cria uma pequena barra visual de HP.
    #
    # Exemplo:
    #
    # HP: 80/100 [################....]
    # --------------------------------------------------------

    def mostrar_status(self):

        # Calcula quantos dos 20 espaços da barra devem
        # ser preenchidos com "#".
        #
        # Se o personagem possui 50% de HP:
        #
        # 50 / 100 = 0.5
        # 0.5 * 20 = 10
        #
        # Então teremos 10 "#".
        barra_hp = (
            int((self.hp / self.hpMax) * 20)
            if self.hpMax > 0
            else 0
        )

        # Garante que a barra nunca tenha menos de 0
        # ou mais de 20 caracteres.
        barra_hp = max(0, min(20, barra_hp))

        # Retorna todas as informações em formato de texto.
        return (
            f"{self.nome} (Lvl {self.level}): "
            f"HP: {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}{'.' * (20 - barra_hp)}] | "
            f"ATQ: {self.ataque} | "
            f"DEF: {self.defesa} | "
            f"VEL: {self.velocidade}"
        )

    # --------------------------------------------------------
    # estar_vivo
    # --------------------------------------------------------
    # Verifica se o personagem ainda possui HP.
    #
    # Retorna:
    # True  -> personagem está vivo
    # False -> personagem está morto
    # --------------------------------------------------------

    def estar_vivo(self):

        return self.hp > 0

    # --------------------------------------------------------
    # receber_dano
    # --------------------------------------------------------
    # Calcula quanto dano realmente será recebido.
    #
    # A defesa reduz o dano recebido.
    #
    # Exemplo:
    #
    # Dano recebido = 20
    # Defesa = 5
    #
    # Dano final = 20 - 5 = 15
    #
    # O max(1, ...) garante que o dano mínimo seja sempre 1.
    # --------------------------------------------------------

    def receber_dano(self, dano):

        dano_final = max(
            1,
            dano - self.defesa
        )

        # Reduz o HP do personagem.
        #
        # max(0, ...) impede que o HP fique negativo.
        self.hp = max(
            0,
            self.hp - dano_final
        )

        # Retorna o dano que realmente foi causado.
        return dano_final


# ============================================================
# CLASSE HEROI
# ============================================================
# Heroi herda da classe Personagem.
#
# Isso significa que Heroi já possui:
#
# - nome
# - level
# - HP
# - ataque
# - defesa
# - velocidade
# - receber_dano()
# - estar_vivo()
#
# Além disso, Heroi possui coisas próprias:
#
# - Classe RPG
# - XP
# - Pontos de Ação
# - Poções
# - Habilidades
# ============================================================

class Heroi(Personagem):

    # --------------------------------------------------------
    # CONSTRUTOR DO HERÓI
    # --------------------------------------------------------

    def __init__(self, nome, ClasseRPG, Level=1):

        # super() chama o __init__ da classe Personagem.
        #
        # Assim não precisamos repetir aqui:
        #
        # self.nome
        # self.level
        # self.hp
        # self.ataque
        # etc.
        super().__init__(nome, Level)

        # Guarda a classe do herói.
        #
        # Exemplos:
        # Guerreiro
        # Mago
        # Arqueiro
        # Ladino
        # Paladino
        self.ClasseRPG = ClasseRPG

        # ----------------------------------------------------
        # SISTEMA DE EXPERIÊNCIA
        # ----------------------------------------------------

        self.Xp = 0

        # Quantidade de XP necessária para evoluir.
        self.XpMax = 100

        # ----------------------------------------------------
        # SISTEMA DE PONTOS DE AÇÃO
        # ----------------------------------------------------

        # Quantidade máxima de PA.
        self.PAMax = 100

        # O personagem começa com a barra de PA cheia.
        self.PA = self.PAMax

        # Quantidade inicial de poções.
        self.pocoesPA = 3

        # Calcula os atributos de acordo com a classe
        # e o nível do personagem.
        self.CalcularAtributosPorLevel()

    # ========================================================
    # CALCULAR ATRIBUTOS POR NÍVEL
    # ========================================================
    # Essa função define os atributos de cada classe.
    #
    # Cada classe possui características diferentes.
    #
    # Guerreiro:
    # Muito HP e boa defesa.
    #
    # Mago:
    # Menos HP, mas muito ataque.
    #
    # Arqueiro:
    # Velocidade alta.
    #
    # Ladino:
    # Velocidade muito alta.
    #
    # Paladino:
    # Muito HP, mas pouca velocidade.
    # ========================================================

    def CalcularAtributosPorLevel(self):

        # ----------------------------------------------------
        # GUERREIRO
        # ----------------------------------------------------

        if self.ClasseRPG == "Guerreiro":

            self.hpMax = 80 + (
                self.level * 20
            )

            self.ataque = 5 + (
                self.level * 3
            )

            self.velocidade = 4 + (
                self.level * 3
            )

        # ----------------------------------------------------
        # MAGO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Mago":

            self.hpMax = 50 + (
                self.level * 10
            )

            self.ataque = 7 + (
                self.level * 5
            )

            self.velocidade = 5 + (
                self.level * 4
            )

        # ----------------------------------------------------
        # ARQUEIRO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Arqueiro":

            self.hpMax = 60 + (
                self.level * 15
            )

            self.ataque = 6 + (
                self.level * 4
            )

            self.velocidade = 8 + (
                self.level * 5
            )

        # ----------------------------------------------------
        # LADINO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Ladino":

            self.hpMax = 55 + (
                self.level * 12
            )

            self.ataque = 6 + (
                self.level * 4
            )

            self.velocidade = 10 + (
                self.level * 6
            )

        # ----------------------------------------------------
        # PALADINO
        # ----------------------------------------------------

        elif self.ClasseRPG == "Paladino":

            self.hpMax = 90 + (
                self.level * 25
            )

            self.ataque = 5 + (
                self.level * 3
            )

            self.velocidade = 3 + (
                self.level * 2
            )

        # Depois de calcular os atributos,
        # o personagem começa com HP cheio.
        self.hp = self.hpMax

    # ========================================================
    # STATUS DO HERÓI
    # ========================================================
    # Sobrescrevemos o mostrar_status() da classe Personagem
    # porque o herói possui informações extras:
    #
    # - PA
    # - Poções
    # - Classe
    # ========================================================

    def mostrar_status(self):

        # -----------------------------
        # BARRA DE HP
        # -----------------------------

        barra_hp = int(
            (self.hp / self.hpMax) * 20
        )

        barra_hp = max(
            0,
            min(20, barra_hp)
        )

        # -----------------------------
        # BARRA DE PA
        # -----------------------------

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
    # Ataque básico do herói.
    #
    # O dano é:
    #
    # Ataque do personagem
    # +
    # número aleatório entre 0 e 10.
    # ========================================================

    def atacar(self, alvo):

        # Verifica se existe um alvo e se ele está vivo.
        if not alvo or not alvo.estar_vivo():

            return False

        # Calcula o dano.
        dano = (
            self.ataque
            + random.randint(0, 10)
        )

        # Aplica o dano no alvo.
        #
        # receber_dano() retorna o dano real depois
        # de considerar a defesa do inimigo.
        dano_causado = alvo.receber_dano(
            dano
        )

        print(
            f"{self.nome} ataca "
            f"{alvo.nome} e causa "
            f"{dano_causado} de dano."
        )

        return True

    # ========================================================
    # HABILIDADE ESPECIAL 1
    # ========================================================
    # Essa habilidade está disponível desde o nível 1.
    #
    # Custo: 20 PA
    # ========================================================

    def habilidade_especial(self, alvo):

        if not alvo or not alvo.estar_vivo():

            return False

        # Quantidade de PA necessária.
        custo = 20

        # Verifica se o personagem possui PA suficiente.
        if self.PA < custo:

            print(
                f"{self.nome} não possui "
                f"PA suficiente!"
            )

            print(
                f"Necessário: {custo} PA | "
                f"Atual: {self.PA} PA"
            )

            return False

        # ----------------------------------------------------
        # CADA CLASSE POSSUI UMA HABILIDADE DIFERENTE
        # ----------------------------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Golpe Destruidor"

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

            nome_skill = "Golpe Sombrio"

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

        # Consome os 20 PA.
        self.PA -= custo

        # Aplica o dano.
        dano_causado = alvo.receber_dano(
            dano
        )

        print(
            f"{self.nome} usa "
            f"{nome_skill} em {alvo.nome} "
            f"e causa {dano_causado} de dano!"
        )

        print(
            f"PA restante: "
            f"{self.PA}/{self.PAMax}"
        )

        return True

    # ========================================================
    # HABILIDADE ESPECIAL 2
    # ========================================================
    # Essa habilidade só pode ser utilizada a partir do nível 5.
    #
    # Custo: 40 PA
    # ========================================================

    def segunda_habilidade(self, alvo):

        # Verifica se o herói possui nível suficiente.
        if self.level < 5:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou essa habilidade."
            )

            return False

        if not alvo or not alvo.estar_vivo():

            return False

        # Custo da habilidade.
        custo = 40

        # Verifica se possui PA.
        if self.PA < custo:

            print(
                f"{self.nome} não possui "
                f"PA suficiente!"
            )

            print(
                f"Necessário: {custo} PA | "
                f"Atual: {self.PA} PA"
            )

            return False

        # ----------------------------------------------------
        # HABILIDADES DE CADA CLASSE
        # ----------------------------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Investida Brutal"

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

            nome_skill = "Execução Sombria"

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

        # Gasta os 40 PA.
        self.PA -= custo

        # Aplica o dano.
        dano_causado = alvo.receber_dano(
            dano
        )

        print(
            f"{self.nome} usa "
            f"{nome_skill} em {alvo.nome} "
            f"e causa {dano_causado} de dano!"
        )

        print(
            f"PA restante: "
            f"{self.PA}/{self.PAMax}"
        )

        return True

    # ========================================================
    # ULTIMATE
    # ========================================================
    # A Ultimate só pode ser utilizada no nível 10.
    #
    # Custo: 100 PA
    #
    # Depois de usar a Ultimate, o PA fica em 0.
    # ========================================================

    def ultimate(self, alvo):

        # Verifica se desbloqueou a Ultimate.
        if self.level < 10:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou a Ultimate."
            )

            return False

        if not alvo or not alvo.estar_vivo():

            return False

        # A Ultimate precisa de PA cheio.
        custo = 100

        if self.PA < custo:

            print(
                f"{self.nome} não possui "
                f"PA suficiente para usar "
                f"a Ultimate!"
            )

            return False

        # ----------------------------------------------------
        # ULTIMATE DE CADA CLASSE
        # ----------------------------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Fúria dos Titãs"

            dano = (
                self.ataque * 3
                + random.randint(20, 40)
            )

        elif self.ClasseRPG == "Mago":

            nome_skill = "TESTICULAR TORSION"

            dano = (
                self.ataque * 4
                + random.randint(30, 50)
            )

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Flecha Celestial"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Morte Instantânea"

            dano = (
                self.ataque * 4
                + random.randint(20, 40)
            )

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Ira Divina"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        # A Ultimate consome todos os 100 PA.
        self.PA = 0

        # Aplica o dano.
        dano_causado = alvo.receber_dano(
            dano
        )

        print("\n🔥 ===============================")

        print(
            f"🔥 {self.nome} usa "
            f"a ULTIMATE {nome_skill}!"
        )

        print(
            f"💥 Causa {dano_causado} de dano!"
        )

        print("🔥 ===============================")

        return True

    # ========================================================
    # USAR POÇÃO DE PA
    # ========================================================
    # A poção recupera 50 PA.
    #
    # O PA NÃO é regenerado automaticamente.
    # Só aumenta através da poção.
    # ========================================================

    def usar_pocao_pa(self):

        # Verifica se o personagem possui poções.
        if self.pocoesPA <= 0:

            print(
                f"{self.nome} não possui "
                f"poções de PA."
            )

            return False

        # Não permite usar poção se o PA já estiver cheio.
        if self.PA >= self.PAMax:

            print(
                f"{self.nome} já está "
                f"com o PA cheio."
            )

            return False

        # Quantidade recuperada.
        recuperacao = 50

        # min() impede que o PA ultrapasse 100.
        #
        # Exemplo:
        # PA = 80
        # Recuperação = 50
        #
        # Resultado = 100, e não 130.
        self.PA = min(
            self.PAMax,
            self.PA + recuperacao
        )

        # Remove uma poção do inventário.
        self.pocoesPA -= 1

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
# Inimigo também herda de Personagem.
#
# Ele possui os atributos básicos do personagem, mas possui
# valores próprios de HP, ataque, defesa e velocidade.
#
# Também possui uma chance de dropar poção.
# ============================================================

class Inimigo(Personagem):

    def __init__(self, nome, Level=1):

        # Inicializa os atributos herdados.
        super().__init__(nome, Level)

        # ----------------------------------------------------
        # ATRIBUTOS DO INIMIGO
        # ----------------------------------------------------

        self.hpMax = (
            60
            + (self.level * 18)
        )

        self.hp = self.hpMax

        self.ataque = (
            8
            + (self.level * 3)
        )

        self.velocidade = (
            2
            + self.level
        )

        self.defesa = (
            1
            + self.level
        )

        # XP que o inimigo poderá dar futuramente.
        self.XpDrop = 0

        # ----------------------------------------------------
        # CHANCE DE DROP
        # ----------------------------------------------------
        # 0.30 significa 30%.
        #
        # Esse valor pode ser alterado futuramente.
        #
        # 0.10 = 10%
        # 0.30 = 30%
        # 0.50 = 50%
        # 1.00 = 100%
        # ----------------------------------------------------

        self.chanceDropPocao = 0.30

    # ========================================================
    # ATAQUE DO INIMIGO
    # ========================================================

    def atacar(self, alvo):

        if not alvo or not alvo.estar_vivo():

            return False

        # Ataque base + número aleatório.
        dano = (
            self.ataque
            + random.randint(0, 5)
        )

        # Aplica o dano.
        dano_causado = alvo.receber_dano(
            dano
        )

        print(
            f"{self.nome} ataca "
            f"{alvo.nome} e causa "
            f"{dano_causado} de dano."
        )

        return True


# ============================================================
# CRIAR OS HERÓIS
# ============================================================
# Essa função cria os personagens que irão participar da
# batalha.
#
# O número 1 no final representa o nível inicial.
# ============================================================

def criar_herois():

    herois = [

        Heroi(
            "Lucas",
            "Guerreiro",
            1
        ),

        Heroi(
            "Guilherme",
            "Mago",
            1
        ),

        Heroi(
            "Cezar",
            "Arqueiro",
            1
        )

    ]

    return herois


# ============================================================
# CRIAR INIMIGO
# ============================================================
# Escolhe aleatoriamente um nome para o inimigo.
#
# Depois cria um objeto da classe Inimigo.
#
# Exemplo:
#
# Goblin Lv.3
# Orc Lv.3
# Slime Lv.3
# ============================================================

def criar_inimigo(level=1):

    nomes = [
        "Goblin",
        "Esqueleto",
        "Slime",
        "Orc",
        "Besta"
    ]

    # Escolhe um nome aleatório da lista.
    nome = random.choice(nomes)

    # Cria o inimigo utilizando o nome e o nível.
    return Inimigo(
        f"{nome} Lv.{level}",
        level
    )


# ============================================================
# MOSTRAR STATUS DOS HERÓIS
# ============================================================
# Percorre todos os heróis e mostra o status de cada um.
# ============================================================

def mostrar_status_herois(herois):

    print("\n")
    print("========== STATUS DOS HERÓIS ==========")

    # Percorre cada herói da lista.
    for heroi in herois:

        print(
            heroi.mostrar_status()
        )


# ============================================================
# VERIFICAR DROP DE POÇÃO
# ============================================================
# Essa função é chamada quando o inimigo é derrotado.
#
# O inimigo possui uma chance fixa de drop.
#
# Atualmente:
#
# 30% = dropa poção
# 70% = não dropa
# ============================================================

def verificar_drop_pocao(inimigo, herois):

    # random.random() gera um número entre 0 e 1.
    #
    # Exemplo:
    #
    # 0.12
    # 0.45
    # 0.87
    #
    # Como a chance é 0.30:
    #
    # 0.12 <= 0.30 -> DROP
    # 0.45 <= 0.30 -> NÃO DROP
    sorteio = random.random()

    # Compara o sorteio com a chance configurada
    # no inimigo.
    if sorteio <= inimigo.chanceDropPocao:

        # Pega somente os heróis vivos.
        herois_vivos = [

            heroi

            for heroi in herois

            if heroi.estar_vivo()

        ]

        # Se existir pelo menos um herói vivo...
        if herois_vivos:

            # Escolhe aleatoriamente qual herói receberá
            # a poção.
            heroi = random.choice(
                herois_vivos
            )

            # Adiciona uma poção ao herói.
            heroi.pocoesPA += 1

            print("\n")
            print("🧪 ===============================")

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

    # Caso o sorteio não esteja dentro da chance de drop.
    print(
        f"\n{inimigo.nome} não deixou "
        f"nenhuma poção."
    )

    return False


# ============================================================
# CRIAR ORDEM DOS TURNOS
# ============================================================
# Essa função implementa a regra de VELOCIDADE.
#
# Todos os personagens vivos são colocados em uma lista.
#
# Depois a lista é ordenada pela velocidade.
#
# Maior velocidade = joga primeiro.
#
# Exemplo:
#
# Ladino       VEL 16
# Arqueiro     VEL 13
# Mago         VEL 9
# Guerreiro    VEL 7
# Goblin       VEL 5
#
# A ordem será:
#
# 1 - Ladino
# 2 - Arqueiro
# 3 - Mago
# 4 - Guerreiro
# 5 - Goblin
# ============================================================

def criar_ordem_turnos(herois, inimigo):

    # Cria uma lista contendo somente os heróis vivos.
    personagens_vivos = [

        heroi

        for heroi in herois

        if heroi.estar_vivo()

    ]

    # Se o inimigo estiver vivo, ele também entra na lista.
    if inimigo.estar_vivo():

        personagens_vivos.append(
            inimigo
        )

    # --------------------------------------------------------
    # EMPATE DE VELOCIDADE
    # --------------------------------------------------------
    # shuffle mistura aleatoriamente a lista.
    #
    # Depois o sort organiza pela velocidade.
    #
    # Dessa forma, se dois personagens tiverem a mesma
    # velocidade, a posição entre eles será aleatória.
    random.shuffle(
        personagens_vivos
    )

    # --------------------------------------------------------
    # ORDENAR PELA VELOCIDADE
    # --------------------------------------------------------
    # reverse=True significa ordem decrescente.
    #
    # Portanto:
    #
    # 20 vem antes de 10.
    personagens_vivos.sort(
        key=lambda personagem:
        personagem.velocidade,
        reverse=True
    )

    return personagens_vivos


# ============================================================
# TURNO DO JOGADOR
# ============================================================
# Mostra as ações disponíveis para o jogador.
#
# As opções mudam de acordo com o nível do personagem.
#
# Nível 1:
# Ataque
# Skill 1
# Poção
# Defender
#
# Nível 5:
# Também libera Skill 2.
#
# Nível 10:
# Também libera Ultimate.
# ============================================================

def turno_jogador(heroi, inimigo):

    # while True mantém o menu aberto caso o jogador
    # digite uma opção inválida.
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

        print("\nEscolha sua ação:")

        print(
            "1 - Ataque normal"
        )

        print(
            "2 - Habilidade especial "
            "(20 PA)"
        )

        # A Skill 2 só aparece para personagens nível 5+
        if heroi.level >= 5:

            print(
                "3 - Segunda habilidade "
                "(40 PA)"
            )

        # A Ultimate só aparece para personagens nível 10.
        if heroi.level >= 10:

            print(
                "4 - Ultimate "
                "(100 PA)"
            )

        print(
            "5 - Usar Poção de PA"
        )

        print(
            "6 - Defender"
        )

        # input() espera o jogador digitar uma opção.
        escolha = input(
            "\nEscolha sua ação: "
        )

        # ----------------------------------------------------
        # OPÇÃO 1 - ATAQUE NORMAL
        # ----------------------------------------------------

        if escolha == "1":

            # Se o ataque funcionar, encerra o turno.
            if heroi.atacar(inimigo):

                return

        # ----------------------------------------------------
        # OPÇÃO 2 - SKILL 1
        # ----------------------------------------------------

        elif escolha == "2":

            if heroi.habilidade_especial(
                inimigo
            ):

                return

        # ----------------------------------------------------
        # OPÇÃO 3 - SKILL 2
        # ----------------------------------------------------

        elif (
            escolha == "3"
            and heroi.level >= 5
        ):

            if heroi.segunda_habilidade(
                inimigo
            ):

                return

        # ----------------------------------------------------
        # OPÇÃO 4 - ULTIMATE
        # ----------------------------------------------------

        elif (
            escolha == "4"
            and heroi.level >= 10
        ):

            if heroi.ultimate(
                inimigo
            ):

                return

        # ----------------------------------------------------
        # OPÇÃO 5 - POÇÃO
        # ----------------------------------------------------

        elif escolha == "5":

            if heroi.usar_pocao_pa():

                return

        # ----------------------------------------------------
        # OPÇÃO 6 - DEFENDER
        # ----------------------------------------------------
        # A defesa aumenta em 5.
        #
        # OBS:
        # Neste momento esse bônus não é removido depois.
        # Posteriormente podemos fazer a defesa voltar ao
        # normal no começo da próxima rodada.
        # ----------------------------------------------------

        elif escolha == "6":

            print(
                f"{heroi.nome} se prepara "
                f"para defender."
            )

            heroi.defesa += 5

            return

        # ----------------------------------------------------
        # OPÇÃO INVÁLIDA
        # ----------------------------------------------------

        else:

            print(
                "Opção inválida. "
                "Tente novamente."
            )


# ============================================================
# BATALHA
# ============================================================
# Essa é a principal função do sistema de combate.
#
# Ela:
#
# 1. Cria os heróis.
# 2. Cria o inimigo.
# 3. Inicia a batalha.
# 4. Define a ordem dos turnos.
# 5. Executa os ataques.
# 6. Verifica vitória ou derrota.
# 7. Verifica o drop.
# ============================================================

def batalha():

    # Cria os heróis.
    herois = criar_herois()

    # Cria um inimigo nível 3.
    inimigo = criar_inimigo(3)

    print("\n")
    print("======================================")
    print("        RPG DE TURNOS")
    print("======================================")

    print(
        f"\n👹 Inimigo apareceu: "
        f"{inimigo.nome}"
    )

    # Mostra o status inicial do inimigo.
    print(
        inimigo.mostrar_status()
    )

    # Mostra o status dos heróis.
    mostrar_status_herois(
        herois
    )

    # ========================================================
    # LOOP PRINCIPAL DA BATALHA
    # ========================================================
    # while True mantém a batalha acontecendo.
    #
    # Ela só termina quando:
    #
    # - O inimigo morrer.
    # OU
    # - Todos os heróis morrerem.
    # ========================================================

    while True:

        # Cria uma nova ordem para cada rodada.
        ordem_turnos = criar_ordem_turnos(
            herois,
            inimigo
        )

        print("\n")
        print("======================================")
        print("            NOVA RODADA")
        print("======================================")

        print(
            "\n⚡ Ordem dos turnos:"
        )

        # Mostra quem irá jogar primeiro.
        for personagem in ordem_turnos:

            print(
                f"  {personagem.nome} "
                f"→ VEL {personagem.velocidade}"
            )

        # ====================================================
        # EXECUTAR OS TURNOS
        # ====================================================
        #
        # Percorre a lista já ordenada pela velocidade.
        # ====================================================

        for personagem in ordem_turnos:

            # Se o personagem morreu antes de chegar
            # seu turno, ele não poderá jogar.
            if not personagem.estar_vivo():

                continue

            # Se o inimigo morreu durante a rodada,
            # não precisamos continuar.
            if not inimigo.estar_vivo():

                break

            # ------------------------------------------------
            # SE FOR UM HERÓI
            # ------------------------------------------------

            if isinstance(
                personagem,
                Heroi
            ):

                turno_jogador(
                    personagem,
                    inimigo
                )

            # ------------------------------------------------
            # SE FOR UM INIMIGO
            # ------------------------------------------------

            elif isinstance(
                personagem,
                Inimigo
            ):

                # Cria uma lista apenas com heróis vivos.
                herois_vivos = [

                    heroi

                    for heroi in herois

                    if heroi.estar_vivo()

                ]

                # Se ainda houver algum herói vivo...
                if herois_vivos:

                    # Escolhe um alvo aleatoriamente.
                    alvo = random.choice(
                        herois_vivos
                    )

                    # Inimigo ataca o alvo.
                    personagem.atacar(
                        alvo
                    )

                    # Mostra o novo status do herói.
                    print(
                        alvo.mostrar_status()
                    )

        # ====================================================
        # VERIFICAR VITÓRIA
        # ====================================================

        if not inimigo.estar_vivo():

            print("\n")
            print("======================================")
            print("              VITÓRIA!")
            print("======================================")

            print(
                f"🏆 {inimigo.nome} "
                f"foi derrotado!"
            )

            # Mostra a barra de HP zerada.
            print(
                inimigo.mostrar_status()
            )

            # Verifica se o inimigo deixou uma poção.
            verificar_drop_pocao(
                inimigo,
                herois
            )

            # Encerra a batalha.
            break

        # ====================================================
        # VERIFICAR DERROTA
        # ====================================================

        # any() verifica se existe pelo menos um herói vivo.
        #
        # Se nenhum estiver vivo, todos foram derrotados.

        if not any(
            heroi.estar_vivo()
            for heroi in herois
        ):

            print("\n")
            print("======================================")
            print("              DERROTA!")
            print("======================================")

            print(
                "💀 Todos os heróis "
                "foram derrotados."
            )

            break

        # ====================================================
        # STATUS NO FINAL DA RODADA
        # ====================================================

        mostrar_status_herois(
            herois
        )

        print(
            "\n========== STATUS DO INIMIGO =========="
        )

        print(
            inimigo.mostrar_status()
        )


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================
# Essa condição verifica se este arquivo está sendo executado
# diretamente.
#
# Se estiver, o programa começa aqui.
#
# Isso permite futuramente importar as classes deste arquivo
# sem iniciar automaticamente uma batalha.
# ============================================================

if __name__ == "__main__":

    print(
        "Bem-vindo ao RPG de Turnos!"
    )

    # Inicia o sistema de batalha.
    batalha()