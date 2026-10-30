"""ATB system queries and display helpers."""

from .configuracao import ultimates_sem_restricao
from .texto import print

def ultimate_disponivel(heroi):
    """Retorna True quando o herói pode usar a Ultimate no momento atual."""

    # Centraliza a regra consultada pelo combate e pela interface; assim ambos
    # usam os mesmos requisitos em vez de manter cópias divergentes.
    if not getattr(heroi, "ClasseRPG", None):
        return False

    if ultimates_sem_restricao():
        return True

    if heroi.nome not in {"Cezar", "Guilherme"}:
        return False

    if heroi.ClasseRPG == "Mago":
        return heroi.pa_gasto_ultimate >= 60

    if heroi.ClasseRPG == "Berserk":
        return heroi.dano_recebido_ultimate >= 50

    if heroi.ClasseRPG == "Ladino":
        return heroi.nome == "Cezar" or heroi.acoes_realizadas >= 5

    if heroi.ClasseRPG in ("Arqueiro", "Paladino"):
        return heroi.PA >= 100

    return False


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
