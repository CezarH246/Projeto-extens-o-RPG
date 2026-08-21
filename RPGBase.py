import random


# ============================================================
# CLASSE BASE - PERSONAGEM
# ============================================================

class Personagem:

    def __init__(self, nome, level=1):

        self.nome = nome
        self.level = max(1, min(level, 10))

        # Atributos básicos
        self.hpMax = 10
        self.hp = 10
        self.ataque = 2
        self.velocidade = 1
        self.defesa = 0

    # ========================================================
    # MOSTRAR STATUS
    # ========================================================

    def mostrar_status(self):

        barra_hp = (
            int((self.hp / self.hpMax) * 20)
            if self.hpMax > 0
            else 0
        )

        barra_hp = max(0, min(20, barra_hp))

        return (
            f"{self.nome} (Lvl {self.level}): "
            f"HP: {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}{'.' * (20 - barra_hp)}] | "
            f"ATQ: {self.ataque} | "
            f"DEF: {self.defesa} | "
            f"VEL: {self.velocidade}"
        )

    # ========================================================
    # VERIFICAR SE ESTÁ VIVO
    # ========================================================

    def estar_vivo(self):

        return self.hp > 0

    # ========================================================
    # RECEBER DANO
    # ========================================================

    def receber_dano(self, dano):

        dano_final = max(
            1,
            dano - self.defesa
        )

        self.hp = max(
            0,
            self.hp - dano_final
        )

        return dano_final


# ============================================================
# CLASSE HEROI
# ============================================================

class Heroi(Personagem):

    def __init__(self, nome, ClasseRPG, Level=1):

        super().__init__(nome, Level)

        self.ClasseRPG = ClasseRPG

        # ====================================================
        # EXPERIÊNCIA
        # ====================================================

        self.Xp = 0
        self.XpMax = 100

        # ====================================================
        # PONTOS DE AÇÃO
        # ====================================================

        self.PAMax = 100

        # Começa com PA cheio
        self.PA = self.PAMax

        # ====================================================
        # POÇÕES
        # ====================================================

        self.pocoesPA = 3

        # Calcula os atributos de acordo com o nível
        self.CalcularAtributosPorLevel()

    # ========================================================
    # CALCULAR ATRIBUTOS POR NÍVEL
    # ========================================================

    def CalcularAtributosPorLevel(self):

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

        # Cura ao calcular atributos
        self.hp = self.hpMax

    # ========================================================
    # STATUS DO HEROI
    # ========================================================

    def mostrar_status(self):

        # Barra de HP
        barra_hp = int(
            (self.hp / self.hpMax) * 20
        )

        barra_hp = max(
            0,
            min(20, barra_hp)
        )

        # Barra de PA
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

        dano = (
            self.ataque
            + random.randint(0, 10)
        )

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
    # SKILL 1
    # DISPONÍVEL DESDE O NÍVEL 1
    # ========================================================

    def habilidade_especial(self, alvo):

        if not alvo or not alvo.estar_vivo():

            return False

        custo = 20

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

        # --------------------------------
        # GUERREIRO
        # --------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Golpe Destruidor"

            dano = (
                self.ataque
                + random.randint(10, 20)
            )

        # --------------------------------
        # MAGO
        # --------------------------------

        elif self.ClasseRPG == "Mago":

            nome_skill = "Elegabete!!!!"

            dano = (
                self.ataque
                + random.randint(15, 25)
            )

        # --------------------------------
        # ARQUEIRO
        # --------------------------------

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Tiro Preciso"

            dano = (
                self.ataque
                + random.randint(10, 25)
            )

        # --------------------------------
        # LADINO
        # --------------------------------

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Golpe Sombrio"

            dano = (
                self.ataque
                + random.randint(15, 30)
            )

        # --------------------------------
        # PALADINO
        # --------------------------------

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Aura Sagrada"

            dano = (
                self.ataque
                + random.randint(10, 20)
            )

        # Gasta PA
        self.PA -= custo

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
    # SKILL 2
    # DESBLOQUEADA NO NÍVEL 5
    # ========================================================

    def segunda_habilidade(self, alvo):

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
                f"{self.nome} não possui "
                f"PA suficiente!"
            )

            print(
                f"Necessário: {custo} PA | "
                f"Atual: {self.PA} PA"
            )

            return False

        # --------------------------------
        # GUERREIRO
        # --------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Investida Brutal"

            dano = (
                self.ataque
                + random.randint(20, 30)
            )

        # --------------------------------
        # MAGO
        # --------------------------------

        elif self.ClasseRPG == "Mago":

            nome_skill = "Chuva de Meteoros"

            dano = (
                self.ataque
                + random.randint(25, 40)
            )

        # --------------------------------
        # ARQUEIRO
        # --------------------------------

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Rajada de Flechas"

            dano = (
                self.ataque
                + random.randint(20, 35)
            )

        # --------------------------------
        # LADINO
        # --------------------------------

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Execução Sombria"

            dano = (
                self.ataque
                + random.randint(25, 40)
            )

        # --------------------------------
        # PALADINO
        # --------------------------------

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Julgamento Divino"

            dano = (
                self.ataque
                + random.randint(20, 35)
            )

        # Gasta PA
        self.PA -= custo

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
    # DESBLOQUEADA NO NÍVEL 10
    # ========================================================

    def ultimate(self, alvo):

        if self.level < 10:

            print(
                f"{self.nome} ainda não "
                f"desbloqueou a Ultimate."
            )

            return False

        if not alvo or not alvo.estar_vivo():

            return False

        custo = 100

        if self.PA < custo:

            print(
                f"{self.nome} não possui "
                f"PA suficiente para usar "
                f"a Ultimate!"
            )

            return False

        # --------------------------------
        # GUERREIRO
        # --------------------------------

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Fúria dos Titãs"

            dano = (
                self.ataque * 3
                + random.randint(20, 40)
            )

        # --------------------------------
        # MAGO
        # --------------------------------

        elif self.ClasseRPG == "Mago":

            nome_skill = "Apocalipse Arcano"

            dano = (
                self.ataque * 4
                + random.randint(30, 50)
            )

        # --------------------------------
        # ARQUEIRO
        # --------------------------------

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Flecha Celestial"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        # --------------------------------
        # LADINO
        # --------------------------------

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Morte Instantânea"

            dano = (
                self.ataque * 4
                + random.randint(20, 40)
            )

        # --------------------------------
        # PALADINO
        # --------------------------------

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Ira Divina"

            dano = (
                self.ataque * 3
                + random.randint(30, 50)
            )

        # Ultimate consome todo o PA
        self.PA = 0

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
    # POÇÃO DE PA
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

        self.PA = min(
            self.PAMax,
            self.PA + recuperacao
        )

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

class Inimigo(Personagem):

    def __init__(self, nome, Level=1):

        super().__init__(nome, Level)

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

        self.XpDrop = 0

        # ====================================================
        # CHANCE DE DROP
        # ====================================================

        # 30% de chance
        self.chanceDropPocao = 0.30

    # ========================================================
    # ATAQUE DO INIMIGO
    # ========================================================

    def atacar(self, alvo):

        if not alvo or not alvo.estar_vivo():

            return False

        dano = (
            self.ataque
            + random.randint(0, 5)
        )

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
# CRIAR HERÓIS
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

def criar_inimigo(level=1):

    nomes = [
        "Goblin",
        "Esqueleto",
        "Slime",
        "Orc",
        "Besta"
    ]

    nome = random.choice(nomes)

    return Inimigo(
        f"{nome} Lv.{level}",
        level
    )


# ============================================================
# STATUS DOS HERÓIS
# ============================================================

def mostrar_status_herois(herois):

    print("\n")
    print("========== STATUS DOS HERÓIS ==========")

    for heroi in herois:

        print(
            heroi.mostrar_status()
        )


# ============================================================
# DROP DE POÇÃO
# ============================================================

def verificar_drop_pocao(inimigo, herois):

    # Sorteia um número entre 0 e 1
    sorteio = random.random()

    # Verifica a chance do inimigo
    if sorteio <= inimigo.chanceDropPocao:

        herois_vivos = [
            heroi
            for heroi in herois
            if heroi.estar_vivo()
        ]

        if herois_vivos:

            # Escolhe um herói vivo
            heroi = random.choice(
                herois_vivos
            )

            # Adiciona uma poção
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

    # Caso não tenha drop
    print(
        f"\n{inimigo.nome} não deixou "
        f"nenhuma poção."
    )

    return False


# ============================================================
# ORDEM DOS TURNOS
# ============================================================

def criar_ordem_turnos(herois, inimigo):

    personagens_vivos = [

        heroi

        for heroi in herois

        if heroi.estar_vivo()

    ]

    # Adiciona o inimigo
    if inimigo.estar_vivo():

        personagens_vivos.append(
            inimigo
        )

    # Em caso de empate na velocidade,
    # a ordem é aleatória.
    random.shuffle(
        personagens_vivos
    )

    # Maior velocidade joga primeiro
    personagens_vivos.sort(
        key=lambda personagem:
        personagem.velocidade,
        reverse=True
    )

    return personagens_vivos


# ============================================================
# TURNO DO JOGADOR
# ============================================================

def turno_jogador(heroi, inimigo):

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

        # Skill 2 só aparece no nível 5
        if heroi.level >= 5:

            print(
                "3 - Segunda habilidade "
                "(40 PA)"
            )

        # Ultimate só aparece no nível 10
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

        escolha = input(
            "\nEscolha sua ação: "
        )

        # ====================================================
        # ATAQUE NORMAL
        # ====================================================

        if escolha == "1":

            if heroi.atacar(inimigo):

                return

        # ====================================================
        # SKILL 1
        # ====================================================

        elif escolha == "2":

            if heroi.habilidade_especial(
                inimigo
            ):

                return

        # ====================================================
        # SKILL 2
        # ====================================================

        elif (
            escolha == "3"
            and heroi.level >= 5
        ):

            if heroi.segunda_habilidade(
                inimigo
            ):

                return

        # ====================================================
        # ULTIMATE
        # ====================================================

        elif (
            escolha == "4"
            and heroi.level >= 10
        ):

            if heroi.ultimate(
                inimigo
            ):

                return

        # ====================================================
        # POÇÃO
        # ====================================================

        elif escolha == "5":

            if heroi.usar_pocao_pa():

                return

        # ====================================================
        # DEFENDER
        # ====================================================

        elif escolha == "6":

            print(
                f"{heroi.nome} se prepara "
                f"para defender."
            )

            heroi.defesa += 5

            return

        # ====================================================
        # OPÇÃO INVÁLIDA
        # ====================================================

        else:

            print(
                "Opção inválida. "
                "Tente novamente."
            )


# ============================================================
# BATALHA
# ============================================================

def batalha():

    herois = criar_herois()

    # Inimigo nível 3
    inimigo = criar_inimigo(3)

    print("\n")
    print("======================================")
    print("        RPG DE TURNOS")
    print("======================================")

    print(
        f"\n👹 Inimigo apareceu: "
        f"{inimigo.nome}"
    )

    print(
        inimigo.mostrar_status()
    )

    mostrar_status_herois(
        herois
    )

    # ========================================================
    # LOOP PRINCIPAL DA BATALHA
    # ========================================================

    while True:

        # Cria a ordem da rodada
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

        for personagem in ordem_turnos:

            print(
                f"  {personagem.nome} "
                f"→ VEL {personagem.velocidade}"
            )

        # ====================================================
        # EXECUTAR TURNOS
        # ====================================================

        for personagem in ordem_turnos:

            # Se morreu antes do turno,
            # não pode agir.
            if not personagem.estar_vivo():

                continue

            # Se o inimigo morreu,
            # termina a rodada.
            if not inimigo.estar_vivo():

                break

            # =================================================
            # TURNO DO HERÓI
            # =================================================

            if isinstance(
                personagem,
                Heroi
            ):

                turno_jogador(
                    personagem,
                    inimigo
                )

            # =================================================
            # TURNO DO INIMIGO
            # =================================================

            elif isinstance(
                personagem,
                Inimigo
            ):

                herois_vivos = [

                    heroi

                    for heroi in herois

                    if heroi.estar_vivo()

                ]

                if herois_vivos:

                    alvo = random.choice(
                        herois_vivos
                    )

                    personagem.atacar(
                        alvo
                    )

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

            print(
                inimigo.mostrar_status()
            )

            # Verifica o drop
            verificar_drop_pocao(
                inimigo,
                herois
            )

            break

        # ====================================================
        # VERIFICAR DERROTA
        # ====================================================

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
        # MOSTRAR STATUS NO FINAL DA RODADA
        # ====================================================

        mostrar_status_herois(
            herois
        )

        print("\n========== STATUS DO INIMIGO ==========")

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

    batalha()