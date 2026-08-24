class personagem:
    def __init__(self, nome, level=1):

        # Nome do personagem.
        self.nome = nome

        # O nível fica limitado entre 1 e 10.
        self.level = max(1, min(level, 10))

        # Atributos básicos.
        self.hpMax = 10
        self.hp = 10

        self.ataque_base = 2
        self.ataque = self.ataque_base
        self.velocidade = 1
        self.defesa = 0
        self.inventario = []

        #Slots
        self.arma = None
        self.anel = None

    def add_item_inv(self, item):
        self.inventario.append(item)
        print(f"{item.nome} foi adicionado no Inventário")

    def mostrar_inv(self):
        self.mostrar_status()
        if not self.inventario:
         print("Inventário está vazio!!")
         return
        for item in self.inventario:
            print(f"{item.nome}")

    def mostrar_status(self):
        arma = self.arma.nome if self.arma else "Nenhuma"
        print(f"\nStatus de {self.nome}")
        print(f"Nível: {self.level}")
        print(f"HP: {self.hp}/{self.hpMax}")
        print(f"Ataque: {self.ataque}")
        print(f"Velocidade: {self.velocidade}")
        print(f"Defesa: {self.defesa}")
        print(f"Arma equipada: {arma}")


    def equipar(self, item):
        if item not in self.inventario:
            print(f"{item.nome} não está disponivel")
            return False

        if item.tipo == "arma":
            if self.arma:
                self.ataque -= self.arma.dano
                print(f"{self.nome} desequipou {self.arma.nome}")
            self.arma = item
            self.ataque += item.dano
        elif item.tipo == "anel":
            if self.anel:
                print(f"{self.nome} desequipou {self.anel.nome}")
            self.anel = item
        else:
            print(f"{item.nome} não pode ser equipado")
            return False

        print(f"{self.nome} equipou {item.nome}")
        self.mostrar_status()
        return True



class Equipamento:
    def __init__(self, nome, dano=0, agilidade=0, valor=0, tipo=None):
        self.nome = nome
        self.dano = dano
        self.agilidade = agilidade
        self.valor = valor
        self.tipo = tipo


def menu_jogador(jogador, espada):
    while True:
        print("\n1 - Ver inventário")
        print("2 - Equipar espada")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            jogador.mostrar_inv()
        elif opcao == "2":
            jogador.equipar(espada)
        elif opcao == "0":
            print("Continuar o Game")
            break
        else:
            print("Opção inválida")


if __name__ == "__main__":
    jogador = personagem("Cezar")
    espada = Equipamento("Espada de Ferro", dano=5, valor=100, tipo="arma")

    jogador.add_item_inv(espada)
    menu_jogador(jogador, espada)

    if jogador.arma is espada:
        assert jogador.ataque == 7
        print(f"{jogador.nome} está usando {jogador.arma.nome} (ATQ: {jogador.ataque})")
