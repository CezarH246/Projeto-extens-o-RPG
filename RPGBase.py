import random


# ============================================================
# CLASSE BASE
# ============================================================

class Personagem:

    def __init__(self, nome, level=1):
        self.nome = nome
        self.level = max(1, min(level, 10))

        self.hpMax = 10
        self.hp = 10
        self.ataque = 2
        self.velocidade = 1
        self.defesa = 0

    def mostrar_status(self):

        barra_hp = int((self.hp / self.hpMax) * 20) if self.hpMax > 0 else 0
        barra_hp = max(0, min(20, barra_hp))

        return (
            f"{self.nome} (Lvl {self.level}): "
            f"HP {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}{'.' * (20 - barra_hp)}] | "
            f"ATQ: {self.ataque} | "
            f"DEF: {self.defesa} | "
            f"VEL: {self.velocidade}"
        )

    def estar_vivo(self):
        return self.hp > 0

    def receber_dano(self, dano):

        dano_final = max(1, dano - self.defesa)

        self.hp = max(0, self.hp - dano_final)

        return dano_final


# ============================================================
# CLASSE HEROI
# ============================================================

class Heroi(Personagem):

    def __init__(self, nome, ClasseRPG, Level=1):

        super().__init__(nome, Level)

        self.ClasseRPG = ClasseRPG

        # XP
        self.Xp = 0
        self.XpMax = 100

        # Pontos de ação
        self.PAMax = 100
        self.PA = 0

        # Poções de PA
        self.pocoesPA = 3

        self.CalcularAtributosPorLevel()

    # ========================================================
    # ATRIBUTOS POR NÍVEL
    # ========================================================

    def CalcularAtributosPorLevel(self):

        if self.ClasseRPG == "Guerreiro":

            self.hpMax = 80 + (self.level * 20)
            self.ataque = 5 + (self.level * 3)
            self.velocidade = 4 + (self.level * 3)

        elif self.ClasseRPG == "Mago":

            self.hpMax = 50 + (self.level * 10)
            self.ataque = 7 + (self.level * 5)
            self.velocidade = 5 + (self.level * 4)

        elif self.ClasseRPG == "Arqueiro":

            self.hpMax = 60 + (self.level * 15)
            self.ataque = 6 + (self.level * 4)
            self.velocidade = 8 + (self.level * 5)

        elif self.ClasseRPG == "Ladino":

            self.hpMax = 55 + (self.level * 12)
            self.ataque = 6 + (self.level * 4)
            self.velocidade = 10 + (self.level * 6)

        elif self.ClasseRPG == "Paladino":

            self.hpMax = 90 + (self.level * 25)
            self.ataque = 5 + (self.level * 3)
            self.velocidade = 3 + (self.level * 2)

        self.hp = self.hpMax

    # ========================================================
    # STATUS DO HEROI
    # ========================================================

    def mostrar_status(self):

        barra_hp = int((self.hp / self.hpMax) * 20)
        barra_hp = max(0, min(20, barra_hp))

        barra_pa = int((self.PA / self.PAMax) * 20)
        barra_pa = max(0, min(20, barra_pa))

        return (
            f"{self.nome} (Lvl {self.level} - {self.ClasseRPG}) | "
            f"HP: {self.hp}/{self.hpMax} "
            f"[{'#' * barra_hp}{'.' * (20 - barra_hp)}] | "
            f"PA: {self.PA}/{self.PAMax} "
            f"[{'#' * barra_pa}{'.' * (20 - barra_pa)}] | "
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

        dano = self.ataque + random.randint(0, 10)

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} ataca {alvo.nome} "
            f"e causa {dano_causado} de dano."
        )

        return True

    # ========================================================
    # HABILIDADE 1
    # DISPONÍVEL DESDE O NÍVEL 1
    # ========================================================

    def habilidade_especial(self, alvo):

        if not alvo or not alvo.estar_vivo():
            return False

        custo = 20

        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            print(
                f"PA necessário: {custo} | "
                f"PA atual: {self.PA}"
            )

            return False

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Golpe Destruidor"
            dano = self.ataque + random.randint(10, 20)

        elif self.ClasseRPG == "Mago":

            nome_skill = "Elegabete!!!!"
            dano = self.ataque + random.randint(15, 25)

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Tiro Preciso"
            dano = self.ataque + random.randint(10, 25)

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Golpe Sombrio"
            dano = self.ataque + random.randint(15, 30)

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Aura Sagrada"
            dano = self.ataque + random.randint(10, 20)

        self.PA -= custo

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} usa {nome_skill} "
            f"em {alvo.nome} e causa "
            f"{dano_causado} de dano!"
        )

        print(
            f"PA restante: {self.PA}/{self.PAMax}"
        )

        return True

    # ========================================================
    # HABILIDADE 2
    # DESBLOQUEADA NO NÍVEL 5
    # ========================================================

    def segunda_habilidade(self, alvo):

        if self.level < 5:

            print(
                f"{self.nome} ainda não desbloqueou "
                f"a segunda habilidade."
            )

            return False

        if not alvo or not alvo.estar_vivo():
            return False

        custo = 40

        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente!"
            )

            print(
                f"PA necessário: {custo} | "
                f"PA atual: {self.PA}"
            )

            return False

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Investida Brutal"
            dano = self.ataque + random.randint(20, 30)

        elif self.ClasseRPG == "Mago":

            nome_skill = "Chuva de Meteoros"
            dano = self.ataque + random.randint(25, 40)

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Rajada de Flechas"
            dano = self.ataque + random.randint(20, 35)

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Execução Sombria"
            dano = self.ataque + random.randint(25, 40)

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Julgamento Divino"
            dano = self.ataque + random.randint(20, 35)

        self.PA -= custo

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} usa {nome_skill} "
            f"em {alvo.nome} e causa "
            f"{dano_causado} de dano!"
        )

        print(
            f"PA restante: {self.PA}/{self.PAMax}"
        )

        return True

    # ========================================================
    # ULTIMATE
    # DESBLOQUEADA NO NÍVEL 10
    # ========================================================

    def ultimate(self, alvo):

        if self.level < 10:

            print(
                f"{self.nome} ainda não desbloqueou "
                f"a Ultimate."
            )

            return False

        if not alvo or not alvo.estar_vivo():
            return False

        custo = 100

        if self.PA < custo:

            print(
                f"{self.nome} não possui PA suficiente "
                f"para usar a Ultimate!"
            )

            print(
                f"PA necessário: {custo} | "
                f"PA atual: {self.PA}"
            )

            return False

        if self.ClasseRPG == "Guerreiro":

            nome_skill = "Fúria dos Titãs"
            dano = self.ataque * 3 + random.randint(20, 40)

        elif self.ClasseRPG == "Mago":

            nome_skill = "Apocalipse Arcano"
            dano = self.ataque * 4 + random.randint(30, 50)

        elif self.ClasseRPG == "Arqueiro":

            nome_skill = "Flecha Celestial"
            dano = self.ataque * 3 + random.randint(30, 50)

        elif self.ClasseRPG == "Ladino":

            nome_skill = "Morte Instantânea"
            dano = self.ataque * 4 + random.randint(20, 40)

        elif self.ClasseRPG == "Paladino":

            nome_skill = "Ira Divina"
            dano = self.ataque * 3 + random.randint(30, 50)

        self.PA -= custo

        dano_causado = alvo.receber_dano(dano)

        print(
            f"\n🔥 {self.nome} usa a ULTIMATE "
            f"{nome_skill}!"
        )

        print(
            f"💥 Causa {dano_causado} de dano!"
        )

        print(
            f"PA restante: {self.PA}/{self.PAMax}"
        )

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
            f"{self.nome} usou uma Poção de PA!"
        )

        print(
            f"PA: {self.PA}/{self.PAMax}"
        )

        print(
            f"Poções restantes: {self.pocoesPA}"
        )

        return True


# ============================================================
# CLASSE INIMIGO
# ============================================================

class Inimigo(Personagem):

    def __init__(self, nome, Level=1):

        super().__init__(nome, Level)

        self.hpMax = 60 + (self.level * 18)
        self.hp = self.hpMax

        self.ataque = 8 + (self.level * 3)

        self.velocidade = 2 + self.level

        self.defesa = 1 + self.level

        self.XpDrop = 0

    # ========================================================
    # ATAQUE DO INIMIGO
    # ========================================================

    def atacar(self, alvo):

        if not alvo or not alvo.estar_vivo():
            return False

        dano = self.ataque + random.randint(0, 5)

        dano_causado = alvo.receber_dano(dano)

        print(
            f"{self.nome} ataca {alvo.nome} "
            f"e causa {dano_causado} de dano."
        )

        return True


# ============================================================
# CRIAÇÃO DOS HERÓIS
# ============================================================

def criar_herois():

    herois = [

        Heroi("Lucas", "Guerreiro", 1),

        Heroi("Guilherme", "Mago", 1),

        Heroi("Cezar", "Arqueiro", 1),

    ]

    return herois


# ============================================================
# CRIAÇÃO DO INIMIGO
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

    print("\n--- STATUS DOS HERÓIS ---")

    for heroi in herois:

        print(heroi.mostrar_status())


# ============================================================
# ORDEM DOS TURNOS
# ============================================================

def criar_ordem_turnos(herois, inimigo):

    personagens_vivos = [
        heroi
        for heroi in herois
        if heroi.estar_vivo()
    ]

    if inimigo.estar_vivo():

        personagens_vivos.append(inimigo)

    # Ordena pela velocidade
    # maior velocidade = primeiro
    #
    # O segundo número aleatório serve
    # para desempatar velocidades iguais.

    random.shuffle(personagens_vivos)

    personagens_vivos.sort(
        key=lambda personagem: personagem.velocidade,
        reverse=True
    )

    return personagens_vivos


# ============================================================
# TURNO DO JOGADOR
# ============================================================

def turno_jogador(heroi, inimigo):

    while True:

        print(
            f"\n===== TURNO DE {heroi.nome} ====="
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
                "4 - Ultimate "
                "(100 PA)"
            )

        print("5 - Usar Poção de PA")

        print("6 - Defender")

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

            if heroi.habilidade_especial(inimigo):

                return

        # ====================================================
        # SKILL 2
        # ====================================================

        elif escolha == "3" and heroi.level >= 5:

            if heroi.segunda_habilidade(inimigo):

                return

        # ====================================================
        # ULTIMATE
        # ====================================================

        elif escolha == "4" and heroi.level >= 10:

            if heroi.ultimate(inimigo):

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
                f"{heroi.nome} se prepara para defender."
            )

            heroi.defesa += 5

            return

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

    inimigo = criar_inimigo(3)

    print("\n")
    print("===================================")
    print("       BATALHA INICIADA!")
    print("===================================")

    print(
        f"\nInimigo apareceu: "
        f"{inimigo.nome}"
    )

    print(
        f"HP: {inimigo.hp}/{inimigo.hpMax}"
    )

    mostrar_status_herois(herois)

    # ========================================================
    # LOOP DA BATALHA
    # ========================================================

    while True:

        # Cria a ordem da rodada
        ordem_turnos = criar_ordem_turnos(
            herois,
            inimigo
        )

        print("\n")
        print("===================================")
        print("          NOVA RODADA")
        print("===================================")

        print("\nOrdem dos turnos:")

        for personagem in ordem_turnos:

            print(
                f"- {personagem.nome} "
                f"(VEL: {personagem.velocidade})"
            )

        # ====================================================
        # EXECUTA CADA TURNO
        # ====================================================

        for personagem in ordem_turnos:

            # Personagem morto não joga
            if not personagem.estar_vivo():

                continue

            # Se inimigo morreu
            if not inimigo.estar_vivo():

                break

            # =================================================
            # TURNO DO HERÓI
            # =================================================

            if isinstance(personagem, Heroi):

                turno_jogador(
                    personagem,
                    inimigo
                )

            # =================================================
            # TURNO DO INIMIGO
            # =================================================

            elif isinstance(personagem, Inimigo):

                herois_vivos = [
                    heroi
                    for heroi in herois
                    if heroi.estar_vivo()
                ]

                if herois_vivos:

                    alvo = random.choice(
                        herois_vivos
                    )

                    personagem.atacar(alvo)

                    print(
                        alvo.mostrar_status()
                    )

        # ====================================================
        # VERIFICA VITÓRIA
        # ====================================================

        if not inimigo.estar_vivo():

            print("\n")
            print("===================================")
            print("             VITÓRIA!")
            print("===================================")

            print(
                f"{inimigo.nome} "
                f"foi derrotado!"
            )

            break

        # ====================================================
        # VERIFICA DERROTA
        # ====================================================

        if not any(
            heroi.estar_vivo()
            for heroi in herois
        ):

            print("\n")
            print("===================================")
            print("             DERROTA!")
            print("===================================")

            print(
                "Todos os heróis "
                "foram derrotados."
            )

            break

        # ====================================================
        # MOSTRA STATUS
        # ====================================================

        mostrar_status_herois(herois)

        print(
            f"\nInimigo:"
        )

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