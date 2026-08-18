import random


class Personagem: #classe base para todos os personagens
    def __init__(self, nome, level=1):
        self.nome = nome
        self.level = max(1, min(level, 10))  # Garante que o level esteja entre 1 e 10
        #atributos base dos personagens seram calculados pela classe filha
        self.hpMax = 10
        self.hp = 10
        self.ataque = 2
        self.velocidade = 1  
        self.defesa = 0

    def mostrar_status(self):
            barra = int((self.hp / self.hpMax) * 20) if self.hpMax > 0 else 0
            barra = max(0, min(20, barra))
            return (f"{self.nome} (Lvl {self.level}): HP {self.hp}/{self.hpMax} "
                f"[{'#' * barra}{'.' * (20 - barra)}] | "
                f"ATQ: {self.ataque} | DEF: {self.defesa} | VEL: {self.velocidade}")

    def estar_vivo(self):
                    return self.hp > 0
        
    def receber_dano(self, dano):
            dano_final = max(1, dano - self.defesa)
            self.hp = max(0, self.hp - dano_final)
            return dano_final

 

        #Criar uma função para exibir vida e estatus.

#classe filha evolução por nivel dos heróis
class Heroi(Personagem):
    def __init__(self, nome, ClasseRPG, Level=1):
        super().__init__(nome, Level)
        self.ClasseRPG = ClasseRPG
        self.Xp = 0
        self.XpMax = 100
        self.CalcularAtributosPorLevel()

    def CalcularAtributosPorLevel(self):
        if self.ClasseRPG == "Guerreiro":
            self.hpMax = 80 + (self.level * 20)  # Ganha mais vida
            self.ataque = 5 + (self.level * 3)
            self.velocidade = 4 + (self.level * 3)

        elif self.ClasseRPG == "Mago":
            self.hpMax = 50 + (self.level * 10)  # Menos vida
            self.ataque = 7 + (self.level * 5)  # Mais ataque
            self.velocidade = 5 + (self.level * 4)

        elif self.ClasseRPG == "Arqueiro":
            self.hpMax = 60 + (self.level * 15)  # Vida média
            self.ataque = 6 + (self.level * 4)  # Ataque médio
            self.velocidade = 8 + (self.level * 5)  # Velocidade alta

        elif self.ClasseRPG == "Ladino":
            self.hpMax = 55 + (self.level * 12)  # Vida média
            self.ataque = 6 + (self.level * 4)  # Ataque médio
            self.velocidade = 10 + (self.level * 6)  # Velocidade muito alta

        elif self.ClasseRPG == "Paladino":
            self.hpMax = 90 + (self.level * 25)  # Vida muito alta
            self.ataque = 5 + (self.level * 3)  # Ataque médio
            self.velocidade = 3 + (self.level * 2)  # Velocidade baixa

        self.hp = self.hpMax # Cura o personagem para o hp máximo ao subir de nivel

     
      #sistema de atque basico contra inimigo alvo
    def atacar(self, alvo):
        if not alvo or not alvo.estar_vivo():
            return False

        dano = self.ataque + random.randint(0, 10)
        alvo.receber_dano(dano)
        print(f"{self.nome} ataca {alvo.nome} e causa {dano} de dano.")
        return True
    
      #sistma de habilidade especial do heroi 
    def habilidade_especial(self, alvo):
        if not alvo or not alvo.estar_vivo():
            return False

        if self.ClasseRPG == "Guerreiro":
            dano = self.atacar(alvo) + random.randint(5, 10) + random.randint(5, 10)
            alvo.receber_dano(dano)
            print(f"{self.nome} usa Golpe Destruidor em {alvo.nome} e causa {dano} de dano.")

        elif self.ClasseRPG == "Mago":
            dano = self.atacar(alvo) + random.randint(10, 20) + random.randint(5, 10)
            alvo.receber_dano(dano)
            print(f"{self.nome} usa Elegabete!!!! em {alvo.nome} e causa {dano} de dano.")

        elif self.ClasseRPG == "Arqueiro":
            dano = self.atacar(alvo) + random.randint(5, 15) + random.randint(5, 10)
            alvo.receber_dano(dano)
            print(f"{self.nome} usa Tiro Preciso em {alvo.nome} e causa {dano} de dano.")

        elif self.ClasseRPG == "Ladino":
            dano = self.atacar(alvo) + random.randint(10, 20) + random.randint(5, 10)
            alvo.receber_dano(dano)
            print(f"{self.nome} usa Golpe Sombrio em {alvo.nome} e causa {dano} de dano.")

        elif self.ClasseRPG == "Paladino":
            dano = self.atacar(alvo) + random.randint(5, 10) + random.randint(5, 10)
            alvo.receber_dano(dano)
            print(f"{self.nome} usa Aura Sagrada em {alvo.nome} e causa {dano} de dano.")

        return True

      #criar classe filha inmimigo temos que analisar os status
class Inimigo(Personagem):
    def __init__(self, nome, Level=1):
        super().__init__(nome, Level)
        self.hpMax = 60 + (self.level * 18)
        self.hp = self.hpMax
        self.ataque = 8 + (self.level * 3)
        self.velocidade = 2 + self.level
        self.defesa = 1 + self.level
        self.XpDrop = 0

       #sistema de ataque basico do inimigo contra o heroi alvo
    def atacar(self, alvo):
            if not alvo or not alvo.estar_vivo():
                return False

            dano = self.ataque + random.randint(0, 5)
            alvo.receber_dano(dano)
            print(f"{self.nome} ataca {alvo.nome} e causa {dano} de dano.")
            return True



    #Parte criação dos players depois colocar opcoes de escolha de classes
def criar_herois():
    herois = [
        Heroi("Lucas", "Guerreiro", 1),
        Heroi("Guilherme", "Mago", 1),
        Heroi("Cezar", "Arqueiro", 1),
    ]
    return herois

    #parte de criação de inimigos
def criar_inimigo(level=1):
    nomes = ["Goblin", "Esqueleto", "Slime", "Orc", "Besta"]
    nome = random.choice(nomes)
    return Inimigo(f"{nome} Lv.{level}", level)


#status dos players
def mostrar_status_herois(herois):
    print("\n--- Status dos Herois ---")
    for heroi in herois:
        print(heroi.mostrar_status())


#turno jogador
def turno_jogador(heroi, inimigo):
    while True:
        print(f"\nSua vez: {heroi.nome}")
        print("1 - Ataque normal")
        print("2 - Habilidade especial")
        print("3 - Defender")
        escolha = input("Escolha sua acao: ")

        if escolha == "1":
            heroi.atacar(inimigo)
            return
        elif escolha == "2":
            heroi.habilidade_especial(inimigo)
            return
        elif escolha == "3":
            print(f"{heroi.nome} se prepara para defender.")
            heroi.defesa += 5
            return
        else:
            print("Opção inválida. Tente novamente.")


#criar def de batlha
def batalha():    
    herois = criar_herois()
    inimigo = criar_inimigo(3)

    print("\n=== BATALHA INICIADA ===")
    print(f"Inimigo apareceu: {inimigo.nome} (HP: {inimigo.hp}/{inimigo.hpMax})")
    mostrar_status_herois(herois)

    while True:
        for heroi in herois:
            if not heroi.estar_vivo():
                continue
            if not inimigo.estar_vivo():
                break

            turno_jogador(heroi, inimigo)
            
            if not inimigo.estar_vivo():
                break

        if not inimigo.estar_vivo():
            print(f"\nVitória! {inimigo.nome} foi derrotado.")
            break

        if not any(heroi.estar_vivo() for heroi in herois):
            print("\nDerrota! Todos os heróis foram derrotados.")
            break

        if inimigo.estar_vivo():
            alvo = random.choice([h for h in herois if h.estar_vivo()])
            inimigo.atacar(alvo)
            print(alvo.mostrar_status())
            

        mostrar_status_herois(herois)
        print(f"\nInimigo: {inimigo.mostrar_status()}")


if __name__ == "__main__":
    print("Bem-vindo ao RPG de Turnos!")
    batalha()
     #teste de mudança pra ele enxergar o bagulho do git