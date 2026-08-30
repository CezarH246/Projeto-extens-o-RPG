import pygame
from pathlib import Path
from RPGBase import criar_herois, criar_cenario_batalha


# ============================================================
# CONFIGURAÇÃO
# ============================================================
# Define o tamanho da janela da batalha e a taxa de quadros por
# segundo. Isso controla a resolução e a velocidade da interface.

LARGURA = 1280
ALTURA = 720

FPS = 60


# ============================================================
# PASTAS DE ASSETS
# ============================================================
# Localiza a pasta de recursos do jogo e a pasta 'assets' para
# carregar fundo, personagens e inimigos corretamente.

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR

for candidate in [
    PROJECT_DIR.parent.parent,
    PROJECT_DIR.parent,
    PROJECT_DIR,
]:
    if (candidate / "assets").exists():
        BASE_DIR = candidate
        break

ASSETS = BASE_DIR / "assets"


# ============================================================
# CENÁRIO DA BATALHA
# ============================================================
# Determina qual imagem será usada como background da tela de combate.
# Caso a imagem não exista, o jogo vai criar um fundo simples.

# ============================================================
# ADICIONE O FUNDO DA BATALHA AQUI
# ============================================================

FUNDO_BATALHA = ASSETS / "backgrounds" / "docas_batalha.jpg"



# ============================================================
# SPRITES DOS HERÓIS
# ============================================================
# Mapeia cada herói ao caminho do sprite que aparecerá na batalha.
# A chave é o nome do personagem e o valor é o arquivo da imagem.

# ============================================================
# ADICIONE OU TROQUE OS SPRITES DOS PERSONAGENS AQUI
# ============================================================

SPRITES_HEROIS = {

    "Lucas":
        ASSETS / "personagens" / "Lucas_Protagonista" / "Idle" / "rotations" / "east.png",

    "Guilherme":
        ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "rotations" / "east.png",

    "Cezar":
        ASSETS / "personagens" / "Cezar_Protagonista" / "Idle"/ "rotations" / "east.png"

   
}


# ============================================================
# SPRITES DOS INIMIGOS
# ============================================================
# Guarda os caminhos de imagem dos inimigos para que o jogo escolha
# o sprite correto de acordo com o tipo do inimigo da batalha.
#
# O seu código já possui:
#
# Xama
# Soldado
# Batedor
#
# Por isso vamos usar esses nomes para escolher automaticamente
# o sprite correto.

SPRITES_INIMIGOS = {

    "Xama":
        ASSETS / "inimigos" / "xama" / "Cantor_dos_Rios_inimigo" / "Idle" / "rotations" / "west.png",

    "Soldado":
        ASSETS / "inimigos" / "soldado" / "Tritão_do_Mar" / "Idle" / "rotations" / "west.png",

    "Batedor":
        ASSETS / "inimigos" / "batedor" / "Mergulhadora_da_Caverna_inimigo" / "Idle" / "rotations" / "west.png",

    "Boss":
        ASSETS / "inimigos" / "rei_tritao.png",
}


# ============================================================
# CLASSE VISUAL DO COMBATENTE
# ============================================================
# Representa um combatente na tela de batalha, incluindo sua imagem,
# posição e comportamento visual quando é selecionado ou derrotado.

class SpriteCombatente:

    def __init__(
        self,
        personagem,
        posicao,
        sprite_path,
        tamanho=(180, 180)
    ):

        self.personagem = personagem

        self.x = posicao[0]
        self.y = posicao[1]

        self.tamanho = tamanho

        self.sprite_path = sprite_path

        self.imagem = self.carregar_sprite()

        # Usado futuramente para animações.
        self.offset_x = 0
        self.offset_y = 0

        self.selecionado = False


    # ========================================================
    # CARREGAR SPRITE
    # ========================================================
    # Carrega a imagem do sprite e o redimensiona para o tamanho
    # desejado. Caso a imagem não exista, gera um bloco cinza como
    # substituto para evitar erro na execução.

    def carregar_sprite(self):

        try:

            imagem = pygame.image.load(
                self.sprite_path
            ).convert_alpha()

            imagem = pygame.transform.scale(
                imagem,
                self.tamanho
            )

            return imagem

        except (FileNotFoundError, pygame.error):

            print(
                f"Sprite não encontrado: "
                f"{self.sprite_path}"
            )

            # Cria um quadrado provisório caso ainda
            # não exista sprite.
            imagem = pygame.Surface(
                self.tamanho,
                pygame.SRCALPHA
            )

            imagem.fill(
                (100, 100, 100, 255)
            )

            return imagem


    # ========================================================
    # DESENHAR
    # ========================================================
    # Desenha o sprite na tela e aplica efeito visual quando o
    # personagem estiver morto ou selecionado como alvo.

    def desenhar(self, tela):

        if not self.personagem.estar_vivo():

            # Personagem derrotado fica transparente.
            imagem = self.imagem.copy()

            imagem.set_alpha(80)

        else:

            imagem = self.imagem


        rect = imagem.get_rect(

            center=(
                self.x + self.offset_x,
                self.y + self.offset_y
            )
        )


        tela.blit(
            imagem,
            rect
        )


        # Se estiver selecionado como alvo.
        if self.selecionado:

            pygame.draw.rect(
                tela,
                (255, 255, 0),
                rect,
                4
            )


# ============================================================
# INTERFACE DA BATALHA
# ============================================================
# Controla toda a interface visual da batalha: fundo, sprites,
# HUDs, posições e atualização da tela.

class BattleUI:

    def __init__(
        self,
        tela,
        herois,
        inimigos
    ):

        self.tela = tela

        self.herois = herois
        self.inimigos = inimigos

        self.fonte = pygame.font.Font(
            None,
            30
        )

        self.fonte_hud = pygame.font.Font(
            None,
            16
        )

        self.cor_heroi = (19, 42, 58)
        self.cor_inimigo = (58, 25, 25)
        self.cor_borda = (206, 211, 224)

        self.fundo = self.carregar_fundo()

        self.sprites_herois = []

        self.sprites_inimigos = []

        self.criar_sprites()


    # ========================================================
    # FUNDO
    # ========================================================
    # Carrega a imagem do cenário principal da batalha. Se a imagem
    # não for encontrada, usa um fundo sólido para não quebrar a tela.

    def carregar_fundo(self):

        try:

            fundo = pygame.image.load(
                FUNDO_BATALHA
            ).convert()

            fundo = pygame.transform.scale(
                fundo,
                (LARGURA, ALTURA)
            )

            return fundo

        except (FileNotFoundError, pygame.error):

            print(
                f"Fundo não encontrado: "
                f"{FUNDO_BATALHA}"
            )

            fundo = pygame.Surface(
                (LARGURA, ALTURA)
            )

            fundo.fill(
                (40, 60, 80)
            )

            return fundo


    # ========================================================
    # CRIAR SPRITES
    # ========================================================
    # Define as posições dos heróis e inimigos na tela e monta os
    # objetos visuais (sprites) de cada combatente.

    def criar_sprites(self):

        # ----------------------------------------------------
        # POSIÇÃO DOS HERÓIS
        # ----------------------------------------------------

        posicoes_herois = [

            (240, 300),

            (180, 460),

            (320, 560),

            (150, 420),
        ]


        # ----------------------------------------------------
        # HERÓIS
        # ----------------------------------------------------

        for indice, heroi in enumerate(
            self.herois
        ):

            if indice >= len(posicoes_herois):
                break


            sprite_path = SPRITES_HEROIS.get(
                heroi.nome
            )


            # Caso não encontre pelo nome,
            # tenta encontrar pela classe.

            if sprite_path is None:

                sprite_path = (
                    ASSETS
                    / "personagens"
                    / "placeholder.png"
                )


            sprite = SpriteCombatente(

                personagem=heroi,

                posicao=
                posicoes_herois[indice],

                sprite_path=sprite_path,

                tamanho=(170, 170)
            )


            self.sprites_herois.append(
                sprite
            )


        # ----------------------------------------------------
        # POSIÇÃO DOS INIMIGOS
        # ----------------------------------------------------

        posicoes_inimigos = [

            (1040, 300),

            (980, 460),

            (1110, 560),
        ]


        # ----------------------------------------------------
        # INIMIGOS
        # ----------------------------------------------------

        for indice, inimigo in enumerate(
            self.inimigos
        ):

            if indice >= len(posicoes_inimigos):
                break


            # Boss recebe sprite especial.
            if inimigo.tipo == "Boss":

                sprite_path = (
                    SPRITES_INIMIGOS["Boss"]
                )

            else:

                sprite_path = (
                    SPRITES_INIMIGOS.get(
                        inimigo.tipo_inimigo
                    )
                )


            if sprite_path is None:

                sprite_path = (
                    ASSETS
                    / "inimigos"
                    / "placeholder.png"
                )


            sprite = SpriteCombatente(

                personagem=inimigo,

                posicao=
                posicoes_inimigos[indice],

                sprite_path=sprite_path,

                tamanho=(190, 190)
            )


            self.sprites_inimigos.append(
                sprite
            )


    # Cria um painel translúcido para ser usado no HUD sobre cada
    # combatente. Esse painel serve como base visual para o status.
    def desenhar_painel(self, x, y, largura, altura, cor, cor_borda, alpha=180):

        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 0))

        pygame.draw.rect(
            painel,
            (*cor[:3], alpha),
            (0, 0, largura, altura),
            border_radius=10
        )
        pygame.draw.rect(
            painel,
            (*cor_borda[:3], 220),
            (0, 0, largura, altura),
            2,
            border_radius=10
        )

        self.tela.blit(painel, (x, y))


    # Desenha um mini HUD acima de cada combatente com seu nome e uma
    # barra de vida simples, tornando o estado do personagem visível na tela.
    def desenhar_hud_combatente(self, sprite):

        combatente = sprite.personagem
        x = sprite.x
        y = sprite.y - 75

        largura = 110
        altura = 34
        painel_x = x - largura // 2
        painel_y = y - altura // 2

        cor_panel = self.cor_heroi if combatente in self.herois else self.cor_inimigo

        self.desenhar_painel(
            painel_x,
            painel_y,
            largura,
            altura,
            cor_panel,
            self.cor_borda,
            180
        )

        nome = self.fonte_hud.render(
            combatente.nome,
            True,
            (255, 255, 255)
        )
        self.tela.blit(nome, (painel_x + 6, painel_y + 5))

        barra_largura = 90
        barra_x = painel_x + 10
        barra_y = painel_y + 18
        hp_max = max(1, combatente.hpMax)
        hp_ratio = max(0, min(1, combatente.hp / hp_max))

        pygame.draw.rect(
            self.tela,
            (25, 25, 25),
            (barra_x, barra_y, barra_largura, 7),
            border_radius=4
        )
        pygame.draw.rect(
            self.tela,
            (90, 220, 120),
            (barra_x, barra_y, int(barra_largura * hp_ratio), 7),
            border_radius=4
        )


    # ========================================================
    # HUD DOS HERÓIS
    # ========================================================
    # Itera sobre os heróis para desenhar o HUD de cada um sobre o
    # sprite correspondente.

    def desenhar_status_herois(self):

        for sprite in self.sprites_herois:
            self.desenhar_hud_combatente(sprite)


    # ========================================================
    # STATUS DOS INIMIGOS
    # ========================================================
    # Faz a mesma função do HUD dos heróis, porém para os inimigos.

    def desenhar_status_inimigos(self):

        for sprite in self.sprites_inimigos:
            self.desenhar_hud_combatente(sprite)


    # ========================================================
    # DESENHAR TUDO
    # ========================================================
    # Ordena a renderização da tela: fundo, personagens e HUDs.

    def desenhar(self):

        self.tela.blit(self.fundo, (0, 0))

        for sprite in self.sprites_herois:
            sprite.desenhar(self.tela)

        for sprite in self.sprites_inimigos:
            sprite.desenhar(self.tela)

        self.desenhar_status_herois()
        self.desenhar_status_inimigos()


# ============================================================
# JANELA PRINCIPAL
# ============================================================
# Inicializa o pygame, cria a janela de batalha e executa o loop
# principal do jogo, redesenhando a tela em cada frame.


def iniciar_janela_batalha():
    pygame.init()
    pygame.display.set_caption("RPG - Batalha")
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    relogio = pygame.time.Clock()

    herois = criar_herois()
    inimigos = criar_cenario_batalha(herois[0].level)
    ui = BattleUI(tela, herois, inimigos)

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

        ui.desenhar()
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    iniciar_janela_batalha()