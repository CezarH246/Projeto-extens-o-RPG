"""Regras e fluxo principal do combate por turnos.

Este modulo coordena a luta: cria os combatentes, carrega as barras ATB,
encaminha cada turno e trata vitoria ou derrota. As regras especificas ficam
nas classes de combate_core/.

ONDE APARECEM OS QUATRO PILARES
--------------------------------
ABSTRACAO (interface comum, sem classe abstrata formal)
    Em batalha(), a lista combatentes reúne Heroi e Inimigo. O fluxo chama
    operações que ambos possuem, como estar_vivo(), carregar_atb() e
    resetar_atb(), sem precisar calcular o HP ou a barra ATB por conta própria.
    Personagem não usa abc nem métodos abstratos: é uma classe base concreta.

HERANCA
    As declarações estão em combate_core/personagens.py:
    Heroi(Personagem, HeroiHabilidades) recebe estado e operações comuns de
    Personagem e as ações de HeroiHabilidades. Em combate_core/inimigos.py,
    Inimigo(Personagem) reutiliza a base e acrescenta regras de inimigo.
    As chamadas super() nos construtores inicializam a parte herdada.

POLIMORFISMO
    Uma chamada de mesmo nome pode executar uma regra diferente conforme o
    objeto. Heroi usa atacar() de HeroiHabilidades; Inimigo define seu próprio
    atacar() em combate_core/inimigos.py. Heroi também sobrescreve
    receber_dano() e mostrar_status() em combate_core/personagens.py. Por
    exemplo, pronto.atacar(alvo) chama a implementação do objeto pronto, e
    alvo.receber_dano(dano) chama a do tipo concreto do alvo.

ENCAPSULAMENTO
    Regras como calcular/aplicar dano e carregar/resetar ATB ficam em métodos
    de Personagem; custo de habilidades e uso de poções ficam nos métodos de
    HeroiHabilidades (combate_core/habilidades.py). Assim, o fluxo pede que o
    objeto execute a regra. O encapsulamento é parcial: hp, PA e defesa são
    atributos públicos e alguns são lidos ou alterados diretamente, por
    exemplo na exibição de status e na ação de defender.
"""

# random escolhe o alvo dos inimigos.
import random

# time controla a pausa entre os ticks da barra ATB no modo terminal.
import time


# Configuracoes gerais (escalas, testes de ultimate e velocidade do texto).
from combate_core.configuracao import (
    ESCALAS,
    TESTE_ULTIMATES_SEM_RESTRICAO,
    VELOCIDADE_TEXTO,
)

# Fabricas que montam herois, inimigos e o cenario de batalha.
from combate_core.criacao import (
    criar_cenario_batalha,
    criar_herois,
    criar_inimigo,
    criar_inimigo_batedor,
    criar_inimigo_boss,
    criar_inimigo_elite,
    criar_inimigo_normal,
    criar_inimigo_soldado,
    criar_inimigo_xama,
    criar_rei_tritao,
)

# Classes base e concretas usadas para isinstance() e para a API publica.
from combate_core.inimigos import Inimigo
from combate_core.personagens import Heroi, Personagem

# Funcoes de recompensa e status.
from combate_core.recompensas import (
    abrir_bau,
    dar_xp,
    mostrar_status_herois,
    verificar_drop_pocao,
)

# Saida de texto centralizada (permite redirecionar o print para a interface).
from combate_core.texto import definir_saida, imprimir_lento, print

# Utilitarios de barra ATB e disponibilidade da ultimate.
from combate_core.utilitarios import exibir_barra_atb, ultimate_disponivel


def escolher_inimigo(inimigos):
    """Mostra somente alvos vivos e devolve o escolhido pelo jogador."""
    # Filtrar aqui evita que as regras de entrada precisem conhecer inimigos mortos.
    # Encapsulamento: quem sabe se o inimigo esta vivo e o proprio inimigo.
    inimigos_vivos = [inimigo for inimigo in inimigos if inimigo.estar_vivo()]

    # Cabecalho e lista numerada dos alvos disponiveis.
    print("\nEscolha qual inimigo atacar:")
    for indice, inimigo in enumerate(inimigos_vivos, start=1):
        print(
            f"{indice} - {inimigo.nome} "
            f"({inimigo.tipo_inimigo} - {inimigo.tipo}) | "
            f"HP: {inimigo.hp}/{inimigo.hpMax}"
        )

    # Repete a pergunta ate o jogador digitar um numero valido.
    while True:
        escolha = input("Número do inimigo: ")

        # isdigit() evita converter texto ou numero negativo.
        if escolha.isdigit():
            indice = int(escolha) - 1

            # Confere se o indice existe na lista de vivos.
            if 0 <= indice < len(inimigos_vivos):
                return inimigos_vivos[indice]

        # Mensagem de erro e nova tentativa.
        print("Opção inválida. Escolha um inimigo vivo.")


def turno_jogador(heroi, inimigos):
    """Executa escolhas até o herói realizar uma ação válida."""
    # O menu fica no fluxo, mas as regras de cada ação ficam no objeto heroi.
    # Por exemplo, habilidade_especial() valida alvo e PA, cobra o custo e
    # aplica o dano. Se retornar False, a ação não foi feita e o menu reaparece.
    # O laco so termina quando uma acao e realmente executada.
    while True:
        # Cabecalho com o estado atual do heroi.
        # Encapsulamento: os dados sao lidos dos atributos do objeto.
        print(f"\n========== TURNO DE {heroi.nome} ==========")
        print(f"HP: {heroi.hp}/{heroi.hpMax}")
        print(f"PA: {heroi.PA}/{heroi.PAMax}")
        print(f"Poções: {heroi.pocoesPA}")
        print(f"PA gasto para Ultimate: {heroi.pa_gasto_ultimate}")
        print(f"Dano recebido para Ultimate: {heroi.dano_recebido_ultimate}")
        print(f"Ações realizadas: {heroi.acoes_realizadas}")

        # Menu de acoes.
        print("\nEscolha sua ação:")
        print("1 - Ataque normal")
        print("2 - Habilidade especial (20 PA)")

        # A segunda habilidade so aparece a partir do nivel 5.
        if heroi.level >= 5:
            print("3 - Segunda habilidade (40 PA)")

        # A ultimate so aparece a partir do nivel 10.
        if heroi.level >= 10:
            print("4 - Ultimate")

            print("5 - Usar Poção de PA")
        print("6 - Defender")

        # Le a escolha do jogador.
        escolha = input("\nEscolha sua ação: ")

        # Mapa entre a tecla digitada, o metodo do Heroi e o nivel minimo.
        # Os niveis 5 e 10 desbloqueiam, respectivamente, a segunda habilidade
        # e a Ultimate; essas condicoes espelham as opcoes mostradas no menu.
        acoes_com_alvo = {
            "1": ("atacar", 1),
            "2": ("habilidade_especial", 1),
            "3": ("segunda_habilidade", 5),
            "4": ("ultimate", 10),
        }

        # Acoes que precisam escolher um inimigo.
        if escolha in acoes_com_alvo:
            # Recupera o nome do metodo e o nivel minimo exigido.
            metodo, nivel_minimo = acoes_com_alvo[escolha]

            # Bloqueia a acao se o heroi ainda nao tiver o nivel necessario.
            if heroi.level < nivel_minimo:
                print(f"{heroi.nome} ainda não desbloqueou essa ação.")
                continue

            # Pede o alvo e executa a acao.
            alvo = escolher_inimigo(inimigos)

            # Encapsulamento: custo, requisitos e dano pertencem ao Heroi.
            # Polimorfismo: o metodo do alvo calcula o dano conforme seu tipo.
            if getattr(heroi, metodo)(alvo):
                return

        # Pocao de PA: o proprio heroi valida e aplica o efeito.
        elif escolha == "5":
            # O heroi controla seu inventario e a recuperacao de PA.
            if heroi.usar_pocao_pa():
                return

        # Defender soma 5 pontos temporarios de defesa e consome uma acao.
        elif escolha == "6":
            heroi.defesa += 5
            heroi.acoes_realizadas += 1
            print(f"{heroi.nome} se prepara para defender.")
            return

        # Qualquer outra tecla reinicia o menu.
        else:
            print("Opção inválida. Tente novamente.")


def batalha(herois=None):
    """Executa o ciclo ATB completo e retorna True na vitória."""
    # Permite reutilizar os herois do mapa ou criar um grupo para teste.
    if herois is None:
        herois = criar_herois()

    # Cria inimigos de acordo com o nivel do primeiro heroi.
    inimigos = criar_cenario_batalha(herois[0].level)

    # Apresentacao inicial da luta.
    print("\n======================================")
    print("           RPG DE TURNOS")
    print("======================================")

    # Mostra cada inimigo que apareceu.
    for inimigo in inimigos:
        print(f"\n👹 Inimigo apareceu: {inimigo.nome}")
        print(f"Tipo: {inimigo.tipo_inimigo} | Categoria: {inimigo.tipo}")
        print(f"XP: {inimigo.XpDrop}")
        print(inimigo.mostrar_status())

    # Mostra o status do grupo.
    mostrar_status_herois(herois)

    # ABSTRAÇÃO: junta heróis e inimigos na mesma lista porque ambos oferecem
    # operações definidas em Personagem. O loop abaixo não precisa de uma
    # lista de HP/ATB separada nem conhecer os detalhes internos das classes.
    # Personagem é uma base concreta, não uma classe abstrata feita com abc.
    combatentes = herois + inimigos

    # A cada 0.1 s, todos ganham 0.5 * velocidade pontos na barra ATB.
    # Sao valores de ritmo do modo terminal; velocidade varia por combatente.
    intervalo_tick = 0.1
    multiplicador_tempo = 0.5

    # Laco infinito: so termina em vitoria ou derrota.
    while True:
        # Lista apenas quem ainda pode lutar.
        inimigos_vivos = [inimigo for inimigo in inimigos if inimigo.estar_vivo()]

        # VITORIA: nao sobrou nenhum inimigo vivo.
        if not inimigos_vivos:
            print("\n======================================")
            print("              VITÓRIA!")
            print("======================================")

            # Aplica XP e drops de cada inimigo derrotado.
            for inimigo in inimigos:
                print(f"🏆 {inimigo.nome} foi derrotado!")
                print(inimigo.mostrar_status())
                dar_xp(inimigo, herois)
                verificar_drop_pocao(inimigo, herois)
            return True

        # DERROTA: nenhum heroi continua vivo.
        if not any(heroi.estar_vivo() for heroi in herois):
            print("\n======================================")
            print("              DERROTA!")
            print("======================================")
            print("💀 Todos os heróis foram derrotados.")
            return False

        # HERANÇA: Heroi e Inimigo reaproveitam carregar_atb() de Personagem.
        # ENCAPSULAMENTO: cada objeto calcula e atualiza sua própria ATB;
        # o loop informa apenas o multiplicador de tempo.
        for personagem in combatentes:
            personagem.carregar_atb(multiplicador_tempo)

        # Desenha as barras no terminal e espera o intervalo do tick.
        exibir_barra_atb(combatentes)
        time.sleep(intervalo_tick)

        # Cada turno comeca quando a ATB alcanca 100 (atb_max do Personagem).
        # next(...) devolve o primeiro combatente pronto ou None.
        pronto = next(
            (
                personagem
                for personagem in combatentes
                if personagem.estar_vivo()
                and personagem.atb_barra >= personagem.atb_max
            ),
            None,
        )

        # Ninguem pronto ainda: volta a carregar as barras.
        if pronto is None:
            continue

        # Esta condição escolhe o fluxo de entrada do turno (jogador ou IA).
        # O polimorfismo aparece nas chamadas de métodos dos objetos concretos,
        # como atacar(), receber_dano() e mostrar_status(), não neste if.
        if isinstance(pronto, Heroi):
            # Heroi: o jogador escolhe a acao.
            turno_jogador(pronto, inimigos)
        else:
            # Inimigo: a IA escolhe um heroi vivo aleatorio e ataca.
            herois_vivos = [heroi for heroi in herois if heroi.estar_vivo()]
            if herois_vivos:
                alvo = random.choice(herois_vivos)
                print(f"\n🚨 TURNO INIMIGO: {pronto.nome}")

                # POLIMORFISMO: pronto é um Inimigo e executa Inimigo.atacar().
                # Dentro dele, alvo.receber_dano() usa Heroi.receber_dano()
                # para um herói ou Personagem.receber_dano() para um inimigo.
                pronto.atacar(alvo)
                print(alvo.mostrar_status())

        # ENCAPSULAMENTO: resetar_atb() centraliza a regra de zerar a barra.
        pronto.resetar_atb()

        # Mostra o estado atualizado do grupo e dos inimigos.
        mostrar_status_herois(herois)
        print("\n========== STATUS DOS INIMIGOS ==========")
        for inimigo in inimigos:
            print(inimigo.mostrar_status())


# API publica preservada para o mapa, a interface e imports antigos.
# Reexportar aqui evita que outros modulos precisem conhecer combate_core/.
__all__ = [
    "ESCALAS", "TESTE_ULTIMATES_SEM_RESTRICAO", "VELOCIDADE_TEXTO",
    "Personagem", "Heroi", "Inimigo", "imprimir_lento", "definir_saida", "print",
    "ultimate_disponivel", "exibir_barra_atb", "criar_herois", "criar_inimigo",
    "criar_inimigo_normal", "criar_inimigo_elite", "criar_inimigo_boss",
    "criar_rei_tritao", "criar_inimigo_xama", "criar_inimigo_soldado",
    "criar_inimigo_batedor", "criar_cenario_batalha", "mostrar_status_herois",
    "dar_xp", "verificar_drop_pocao", "abrir_bau", "escolher_inimigo",
    "turno_jogador", "batalha",
]
