"""Experience, potions, and exploration rewards."""

import random

from .texto import print

def mostrar_status_herois(herois):

    print("\n")

    print(
        "========== STATUS DOS HERÓIS =========="
    )

    for heroi in herois:

        print(
            heroi.mostrar_status()
        )


def dar_xp(inimigo, herois):

    # Reparte a recompensa entre os heróis vivos; personagens derrotados ficam
    # fora do cálculo para não receber XP.
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

        # Atualiza a experiência individual de cada objeto herói.
        # Pilar: Encapsulamento — o progresso pertence ao estado de cada herói.
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
            # Recalcula os atributos usando a classe RPG do próprio herói.
            heroi.CalcularAtributosPorLevel()

            print(
                f"🎉 {heroi.nome} subiu "
                f"para o nível "
                f"{heroi.level}!"
            )

    print("⭐ ===============================")


def verificar_drop_pocao(inimigo, herois):

    # Sorteia se o inimigo deixa poção; se sim, entrega a um herói ainda vivo.
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

            # A poção é adicionada ao inventário daquele objeto herói.
            # Pilar: Encapsulamento — cada herói mantém seu próprio estoque.
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
