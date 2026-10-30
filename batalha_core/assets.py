"""Paths for sprites, animations, and visual dimensions."""

from pathlib import Path

LARGURA = 1280
ALTURA = 720
FPS = 60

PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_DIR / "assets"
FUNDO_BATALHA = ASSETS / "backgrounds" / "docas_batalha.jpg"

ULTIMATE_CEZAR = ASSETS / "ultimates" / "Cezar_Ultimate" / "Cezar_Ultimate"
ULTIMATE_CEZAR_GIF = ULTIMATE_CEZAR / "Cezar_ultimate.gif"
ULTIMATE_CEZAR_ATAQUE = ASSETS / "ultimates" / "Cezar_Ultimate" / "Efeito_ult"
EFEITO_CEZAR = [
    ULTIMATE_CEZAR_ATAQUE / "inicio.gif",
    ULTIMATE_CEZAR_ATAQUE / "meio.gif",
    ULTIMATE_CEZAR_ATAQUE / "meio2.gif",
    ULTIMATE_CEZAR_ATAQUE / "fim.gif",
]
ULTIMATE_GUILHERME = ASSETS / "ultimates" / "Guilherme_Ultimate" / "pixellab-O-mago--que-inicialmente-mant--1788880617530"
ULTIMATE_GUILHERME_ATAQUE = ASSETS / "ultimates" / "Guilherme_Ultimate" / "pixellab-The-black-hole-slowly-rotates--1788882096725"
GUILHERME_ULTIMATE_PRONTA = ASSETS / "personagens" / "Guilherme_Protagonista" / "Ultimate_Pronta" / "guilherme_ultimate_pronta.gif"
ENTIDADE_COSMICA_GUILHERME = ASSETS / "efeitos" / "Entidade_Cosmica" / "entidade_cosmica.gif"
ENTIDADE_MAIOR_CEZAR = ASSETS / "efeitos" / "Entidade_maior" / "Idle_custom-The_serpent_goddess_remains_in_south-east (1).gif"
# Entidade maior atrás do Lucas: o Rei Antigo Caído, na MESMA escala da
# serpente do Cezar (mesmo arquivo de tamanho base e mesmo deslocamento).
ENTIDADE_MAIOR_LUCAS = ASSETS / "efeitos" / "Entidade_maior" / "Idle_custom-The_ancient_Fallen_King_of_Ete_south-east.gif"
REI_TRITAO_IDLE = ASSETS / "inimigos" / "Rei_Tritao" / "rei_tritao_idle.gif"

CEZAR_ANIMACOES = ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations"

ATAQUE_BASICO_CEZAR = CEZAR_ANIMACOES / "Ataque_Basico"
ATAQUE_BASICO_GUILHERME = ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Ataque_Basico"
ATAQUE_BASICO_GUILHERME_GIF = ASSETS / "personagens" / "Guilherme_Protagonista" / "ataque-basico" / "pixellab-Create-a-smooth-and-powerful-e-1792330609816 (1).gif"
EFEITO_ATAQUE_BASICO_GUILHERME = ASSETS / "personagens" / "Guilherme_Protagonista" / "ataque-basico" / "efeito-ataque-basico" / "pixellab-Create-a-smooth-pixel-art-anim-1792332655276.gif"

DASH_CEZAR = CEZAR_ANIMACOES / "Dash_Combate"

# Habilidade especial do Cezar: ele conjura a magia e o projétil sai dela.
MAGIA_CEZAR = CEZAR_ANIMACOES / "Cezar_Magia"
PROJETIL_CEZAR_GIF = CEZAR_ANIMACOES / "Cezar_Projetil" / "gif_Projetil_Cezar.gif"

# Segunda habilidade do Cezar.
ESPECIAL_CEZAR = CEZAR_ANIMACOES / "Cezar_Especial"

# Efeito do Cezar enquanto a Ultimate estiver pronta.
ULTIMATE_PRONTA_CEZAR = CEZAR_ANIMACOES / "UltimateOn_Cezar" / "Idle_custom-The_rogue_remains_in_his_origi_east.gif"

# Assets do Lucas (todos em gif).
LUCAS_PASTA = ASSETS / "personagens" / "Lucas_Protagonista"
ATAQUE_BASICO_LUCAS = LUCAS_PASTA / "ataque-basico" / "pixellab-Sim--Para-a-Skill-1--eu-deixar-1791222561909.gif"
CORRIDA_LUCAS = LUCAS_PASTA / "corrida" / "pixellab-Create-a-powerful-and-aggressi-1792291730927.gif"
# Especial: o rugido anima o Lucas; o efeito separado termina como impacto no inimigo.
ESPECIAL_LUCAS = LUCAS_PASTA / "especial" / "pixellab-Spirit-Bear-Roar--Keep-the-exa-1791222794389.gif"
EFEITO_ESPECIAL_LUCAS = LUCAS_PASTA / "especial" / "efeito-especial" / "pixellab-Create-ONLY-the-visual-effects-1791224098878.gif"
# Skill: dash de fogo até perto do inimigo.
SKILL_LUCAS = LUCAS_PASTA / "skill" / "pixellab-Skill-1---Flaming-Berserker-Ch-1791222772863.gif"
# Ultimate: igual ao especial, mas sem projétil — o efeito aparece no inimigo
# já no começo da animação.
ULTIMATE_LUCAS = LUCAS_PASTA / "ultimate" / "pixellab-Sim---o-problema---que-o-promp-1791224532715.gif"
EFEITO_ULTIMATE_LUCAS = LUCAS_PASTA / "ultimate" / "efeito-ultimate" / "pixellab-Pixel-art-ice-impact-effect-on-1791224973868.gif"

SKILL1_GUILHERME = ASSETS / "personagens" / "Guilherme_Protagonista" / "skill-1"
ANIMACAO_MAGO_HABILIDADE = SKILL1_GUILHERME / "pixellab-Create-a-smooth-pixel-art-fire-1792330513653.gif"
BOLA_FOGO_MAGO = SKILL1_GUILHERME / "efeito-skill1" / "Idle_custom-Create_only_the_fireball_attack_particle_effect._D_south.gif"

# Especial do Guilherme em quatro estágios, nessa ordem:
#   1. o mago toca a animação dele (Idle_custom-The_character...), parado;
#   2. a magia se forma na posição dele (pixellab-fa-a-a-magia);
#   3. a bola de fogo viaja até o inimigo (pixellab-bola-de-fogo-pulsa);
#   4. o impacto aparece dentro do inimigo (pixellab-the-dark--fiery).
GUILHERME_ESPECIAL_PASTA = ASSETS / "personagens" / "Guilherme_Protagonista" / "especial"
ANIMACAO_GUILHERME_ESPECIAL = GUILHERME_ESPECIAL_PASTA / "Idle_custom-The_character_performs_a_dark_south-east (1).gif"
MAGIA_GUILHERME = GUILHERME_ESPECIAL_PASTA / "efeito_especial" / "pixellab-Fa-a-a-magia-do-mago-aumentar-1788878475120 (1).gif"
BOLA_GUILHERME = GUILHERME_ESPECIAL_PASTA / "efeito_especial" / "pixellab-Bola-de-fogo-pulsando-de-energ-1788878970060 (1).gif"
EFEITO_GUILHERME = GUILHERME_ESPECIAL_PASTA / "efeito_especial" / "pixellab-The-dark--fiery-sphere-streaks-1788879210316 (1).gif"

ATAQUE_INIMIGO = ASSETS / "inimigos" / "Ataque_inimigo" 


# ============================================================
# TAMANHOS VISUAIS
# ============================================================
# Cada arquivo de animação tem uma margem transparente maior ou menor, por isso
# o tamanho do personagem é medido pelo desenho visível (a margem é descartada)
# e não pela caixa do arquivo. Assim todos os combatentes ocupam a mesma altura
# de tela e a "escala" do personagem vira um multiplicador desse tamanho padrão.
TAMANHO_CORPO_BASE = 125          # altura do corpo de um combatente de escala 1.0
TAMANHO_ATAQUE = 125              # ataque básico: o mesmo tamanho do corpo
TAMANHO_DASH = 140                # investida do ladino, levemente maior
TAMANHO_ULTIMATE = 175            # conjuração da ultimate, maior que o corpo
TAMANHO_ENTIDADE_COSMICA = 220    # entidade atrás do mago: bem maior que o corpo do herói
TAMANHO_ENTIDADE_MAIOR = 150      # serpente atrás do Cezar: maior que o corpo, mas discreta
TAMANHO_PROJETIL = 96             # projétil lançado pela habilidade especial
TAMANHO_ULTIMATE_CEZAR = (220, 220)      # personagem ampliado da ultimate do Cezar
TAMANHO_ULTIMATE_CEZAR_EFEITO = (275, 275)  # efeito do golpe da ultimate do Cezar
TAMANHO_ANIMACAO_PERSONAGEM = TAMANHO_ULTIMATE_CEZAR
# Padrão de projéteis/efeitos de especial e ultimate: o mesmo tamanho do
# corpo do INIMIGO ALVO (tamanho_corpo do alvo), nunca um tamanho fixo.
# Bola de fogo do especial do Guilherme: menor que o inimigo (uma fração
# do corpo do alvo) e nasce um pouco à frente do mago, não grudada nele.
PROPORCAO_BOLA_FOGO = 0.40            # fração do tamanho do inimigo
DISTANCIA_NASCIMENTO_BOLA = 80        # px à frente do mago onde a bola surge


# ============================================================
# POSIÇÕES NO CAMPO DE BATALHA
# ============================================================
# Arena: os heróis ficam à esquerda e os inimigos à direita. O confronto contra o
# Rei Tritão é uma luta de chefe contra o grupo inteiro, então o boss entra sozinho
# no meio do campo, entre os dois lados, para ocupar o centro da tela.
POSICAO_BOSS_CENTRAL = (LARGURA // 2, 330)


#CRIAR LISTA DE ATAQUES DE INIMIGOS
ATAQUES_INIMIGOS = {
    "cantor_dos_rios": ATAQUE_INIMIGO,
    "trita_das_nevoas": ATAQUE_INIMIGO,
    "biomante_bentico": ATAQUE_INIMIGO,
    "seguidor_de_harkbal": ATAQUE_INIMIGO,
    "mestre_do_tridente_perolado": ATAQUE_INIMIGO,
    "elite_da_raiz_profunda": ATAQUE_INIMIGO,
    "mergulhadora_da_caverna_trita": ATAQUE_INIMIGO,
    "mergulhadora_celeste": ATAQUE_INIMIGO,
    "nicanzil_condutora_da_corrente": ATAQUE_INIMIGO,
    "boss": ATAQUE_INIMIGO,
}
#CRIAR LISTA DE ATQUES BASICOS
ATAQUES_BASICOS = {
    "Cezar": ATAQUE_BASICO_CEZAR, 
    "Guilherme": ATAQUE_BASICO_GUILHERME,
    "Lucas": ATAQUE_BASICO_LUCAS,
}

#CRIAR LISTA DE DASH
DASHES = {
    "Cezar": DASH_CEZAR,
    "Lucas": CORRIDA_LUCAS,
}

#CRIAR LISTA DE ATQUES ESPECIAIS
#Habilidade especial (tecla 2): conjuração + projétil que sai da magia.
HABILIDADES_ESPECIAIS = {
    "Cezar": (MAGIA_CEZAR, PROJETIL_CEZAR_GIF),
}

# Segunda habilidade (tecla 3): animação própria do personagem.
# O Lucas não entra aqui: a tecla 2 dele abre a skill1 (dash) e a tecla 3
# abre o especial do rugido, tratadas direto em iniciar_animacao_acao.
SEGUNDAS_HABILIDADES = {
    "Cezar": ESPECIAL_CEZAR,
}

# LISTA DE ULTIMATES
ULTIMATES = {
    "Cezar": ULTIMATE_CEZAR,
    "Guilherme": ULTIMATE_GUILHERME,
}

# Efeito que fica atrás do herói enquanto a Ultimate estiver pronta.
# Cada entrada define o arquivo, o tamanho base e o deslocamento do centro.
ENTIDADES_ATRAS = {
    "Guilherme": (ENTIDADE_COSMICA_GUILHERME, TAMANHO_ENTIDADE_COSMICA, (-48, -18)),
    # A serpente fica menor e mais acima: o corpo do Cezar cobre só a base
    # dela, deixando o resto visível atrás/por cima dos ombros dele.
    "Cezar": (ENTIDADE_MAIOR_CEZAR, TAMANHO_ENTIDADE_MAIOR, (-48, -80)),
    # O Rei Antigo Caído do Lucas usa exatamente o mesmo tamanho base e o
    # mesmo deslocamento da serpente do Cezar: mesma escala, não grudado.
    "Lucas": (ENTIDADE_MAIOR_LUCAS, TAMANHO_ENTIDADE_MAIOR, (-48, -80)),
}

# Cada herói pode ter até duas animações de batalha:
#   - "standard": a pose/idle normal, usada quando a batalha começa.
#   - "ultimate": a animação de "carga pronta", usada enquanto a Ultimate
#     do herói estiver disponível (ver ultimate_disponivel em Combate.py).
# Heróis que ainda não têm a segunda animação reutilizam a mesma da standard,
# então nada muda para eles. O Lucas já ganhou as duas novas em gif.
ANIMACOES_HEROIS = {
    "Lucas": (
        ASSETS / "personagens" / "Lucas_Protagonista" / "standard-animation.gif",
        ASSETS / "personagens" / "Lucas_Protagonista" / "Idle_custom-Idle_animation._Keep_the_same_south-east.gif",
    ),
    "Guilherme": (
        ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Guilherme_Batalha" / "south-east",
        GUILHERME_ULTIMATE_PRONTA,
    ),
    "Cezar": (
        ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations" / "Cezar_Posicao_de_combate" / "east",
        ULTIMATE_PRONTA_CEZAR,
    ),
}

SPRITES_INIMIGOS = {
    "cantor_dos_rios": ASSETS / "inimigos" / "Cantor_dos_Rios_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "trita_das_nevoas": ASSETS / "inimigos" / "Trita_das_Nevoas_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "biomante_bentico": ASSETS / "inimigos" / "Biomante_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "seguidor_de_harkbal": ASSETS / "inimigos" / "Hakbal_inimigo" / "Idle" / "animations" / "battle_position" / "west",
    "mestre_do_tridente_perolado": ASSETS / "inimigos" / "Mestre_do_Tridente_Perolado_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "elite_da_raiz_profunda": ASSETS / "inimigos" / "tritao_guerreiro_do_mar_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "mergulhadora_da_caverna_trita": ASSETS / "inimigos" / "Mergulhadora_da_Caverna_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "mergulhadora_celeste": ASSETS / "inimigos" / "Mergulhadora_Celeste_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "nicanzil_condutora_da_corrente": ASSETS / "inimigos" / "Nicanzil_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
    "boss": ASSETS / "inimigos" / "Deusa_Trita_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",
}

__all__ = [nome for nome in globals() if nome.isupper()]
