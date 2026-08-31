import pygame
import unicodedata
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
    PROJECT_DIR,
    PROJECT_DIR.parent,
    PROJECT_DIR.parent.parent,
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
# O LOCAL ESTÁ NA BASTA DE ANIMAÇÃO DE BATALHA
# ============================================================

SPRITES_HEROIS = {

   
    "Lucas":
        ASSETS / "personagens" / "Lucas_Protagonista" / "Idle" / "animations" / "Lucas_Batalha" / "south-east",

  
    "Guilherme":
        ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Guilherme_Batalha" / "south-east",

    
    "Cezar":
        ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations" / "Cezar_Posicao_de_combate" / "east"

}


# ============================================================
# SPRITES DOS INIMIGOS
# ============================================================
# Ela normaliza o nome do personagem/inimigo para que o código consiga 
# comparar nomes de forma confiável, mesmo quando eles vêm com ,  ACENTO
# ESPAÇOES ,  HIFENS E PONTUACÕES

def normalizar_nome_sprite(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    texto = texto.replace(" ", "_")
    texto = texto.replace("-", "_")
    texto = texto.replace(".", "")
    texto = texto.replace(",", "")
    texto = texto.replace("'", "")
    texto = texto.replace("\"", "")
    return texto

# ============================================================
# LOCAL DAS ANIMACOES
# ============================================================
SPRITES_INIMIGOS = {
    "cantor_dos_rios":
        ASSETS / "inimigos" / "Cantor_dos_Rios_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "trita_das_nevoas":
        ASSETS / "inimigos" / "Trita_das_Nevoas_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "biomante_bentico":
        ASSETS / "inimigos" / "Biomante_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "harkbal_mestre_tritao":
        ASSETS / "inimigos" / "Hakbal_inimigo" / "Idle" / "animations" / "battle_position" / "west",

    "mestre_do_tridente_perolado":
        ASSETS / "inimigos" / "Mestre_do_Tridente_Perolado_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "tritao_do_mar":
        ASSETS / "inimigos" / "Tritao_guerreiro_do_mar_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "mergulhadora_da_caverna_trita":
        ASSETS / "inimigos" / "Mergulhadora_da_Caverna_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "mergulhadora_celeste":
        ASSETS / "inimigos" / "Mergulhadora_Celeste_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "nicanzil_condutora_da_corrente":
        ASSETS / "inimigos" / "Nicanzil_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

    "boss":
        ASSETS / "inimigos" / "Deusa_Trita_inimigo" / "Idle" / "animations" / "battle_position" / "south-west",

}

#============================================================================
# pega o nome do inimigo sem o nível
# transforma em um texto padronizado
# tenta achar esse nome no dicionário de sprites
# se não achar, tenta achar pelo tipo
# retorna o caminho da imagem correta
#==========================================================================
def resolver_sprite_inimigo(inimigo):
    if inimigo.tipo == "Boss":
        return SPRITES_INIMIGOS.get("boss")

    nome_base = inimigo.nome.split(" Lv.")[0].strip()
    chave = normalizar_nome_sprite(nome_base)

    if chave in SPRITES_INIMIGOS:
        return SPRITES_INIMIGOS[chave]

    chave_tipo = normalizar_nome_sprite(inimigo.tipo_inimigo)
    return SPRITES_INIMIGOS.get(chave_tipo)


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
        tamanho=(180, 180),
        escala=None
    ):

        self.personagem = personagem

        self.x = posicao[0]
        self.y = posicao[1]

        if escala is None:
            escala = getattr(personagem, "escala", 1.0)

        self.escala = float(escala)
        self.tamanho = (
            max(1, int(tamanho[0] * self.escala)),
            max(1, int(tamanho[1] * self.escala))
        )

        self.sprite_path = sprite_path
        self.frames = []
        self.frame_atual = 0
        self.ultimo_tempo_frame = 0
        self.tempo_por_frame = 90

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

        # Essa etapa é a chave da animação: se o caminho informado for uma pasta,
        # o código entende que o sprite é um conjunto de frames e não uma imagem
        # única. Isso é o que acontece com Guilherme e Cezar.
        if self.sprite_path is not None and hasattr(self.sprite_path, "is_dir") and self.sprite_path.is_dir():
            frames = self.carregar_frames_animacao(self.sprite_path)
            if frames:
                # Guarda a lista inteira dos quadros e define o primeiro frame como
                # imagem inicial para evitar tela em branco ao iniciar a animação.
                self.frames = frames
                self.imagem = frames[0]
                return frames[0]

        # Quando o caminho não é uma pasta, significa que o personagem possui uma
        # imagem estática. Então o código carrega apenas um PNG e o redimensiona.
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

            # Se o arquivo não existir, o jogo cria um sprite provisório para
            # evitar crash e manter a interface funcionando.
            imagem = pygame.Surface(
                self.tamanho,
                pygame.SRCALPHA
            )

            imagem.fill(
                (100, 100, 100, 255)
            )

            return imagem


    def carregar_frames_animacao(self, pasta):
        try:
            # Busca apenas os arquivos da sequência de animação, nomeados como
            # frame_000.png, frame_001.png, etc. A ordenação é feita pelo número
            # final do nome, garantindo que os quadros sigam a ordem correta.
            arquivos = sorted(
                pasta.glob("frame_*.png"),
                key=lambda caminho: int(caminho.stem.split("_")[-1])
            )[:16]

            if not arquivos:
                # Se a pasta existir mas não contiver frames válidos, retorna uma
                # lista vazia para que o código saiba que não há animação.
                return []

            # Cada frame é carregado individualmente e redimensionado para o mesmo
            # tamanho do sprite para manter proporção consistente na tela.
            return [
                pygame.transform.scale(
                    pygame.image.load(caminho).convert_alpha(),
                    self.tamanho
                )
                for caminho in arquivos
            ]

        except (FileNotFoundError, pygame.error):
            print(f"Pasta de animação não encontrada: {pasta}")
            return []


    def atualizar_animacao(self):
        # Se houver menos de 2 frames, não faz sentido trocar de imagem, então a
        # função sai imediatamente para evitar processamento desnecessário.
        if len(self.frames) <= 1:
            return

        tempo_atual = pygame.time.get_ticks()

        # Verifica se já passou o tempo definido para trocar de frame.
        # Quando o intervalo é atingido, avança para o próximo frame e faz um
        # ciclo circular na lista, repetindo a animação eternamente.
        if tempo_atual - self.ultimo_tempo_frame >= self.tempo_por_frame:
            self.ultimo_tempo_frame = tempo_atual
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)
            self.imagem = self.frames[self.frame_atual]


    # ========================================================
    # DESENHAR
    # ========================================================
    # Desenha o sprite na tela e aplica efeito visual quando o
    # personagem estiver morto ou selecionado como alvo.

    def desenhar(self, tela):

        self.atualizar_animacao()

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

        self.fonte_pixel = pygame.font.SysFont(
            "monospace",
            16,
            bold=True
        )

        self.fonte_pequena = pygame.font.SysFont(
            "monospace",
            13,
            bold=True
        )

        self.cor_heroi = (19, 42, 58)
        self.cor_inimigo = (58, 25, 25)
        self.cor_borda = (206, 211, 224)

        self.azul_escuro = (16, 24, 72)
        self.azul_claro = (40, 64, 152)
        self.azul_gradiente = (80, 112, 216)
        self.azul_selecao = (32, 88, 200)
        self.borda_dourada = (216, 176, 80)
        self.borda_interna = (248, 224, 144)
        self.branco = (255, 255, 255)
        self.amarelo_ap = (240, 200, 60)
        self.verde_hp = (80, 224, 120)
        self.cinza_fundo = (32, 32, 48)

        self.comandos = [
            "ATTACK",
            "MAGIC",
            "ITEM",
            "GUARD",
            "SPECIAL"
        ]
        self.comando_selecionado = 0

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

            (240, 250),

            (180, 400),

            (320, 500),

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

                tamanho=(120, 120),
                escala=getattr(heroi, "escala", 1.0)
            )


            self.sprites_herois.append(
                sprite
            )


        # ----------------------------------------------------
        # POSIÇÃO DOS INIMIGOS
        # ----------------------------------------------------

        posicoes_inimigos = [

            (1040, 250),

            (980, 400),

            (1110, 500),
        ]


        # ----------------------------------------------------
        # INIMIGOS
        # ----------------------------------------------------

        for indice, inimigo in enumerate(
            self.inimigos
        ):

            if indice >= len(posicoes_inimigos):
                break


            sprite_path = resolver_sprite_inimigo(inimigo)


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

                tamanho=(110, 110),
                escala=getattr(inimigo, "escala", 1.0)
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

 #================================================================
 #  ESTILO DA HUD
 #======================================================================
    def desenhar_caixa_jrpg(self, x, y, largura, altura):
        """Desenha uma caixa com estilo chanfrado azul e borda dourada."""
        pygame.draw.rect(self.tela, self.azul_escuro, (x, y, largura, altura))
        pygame.draw.rect(self.tela, self.azul_claro, (x + 4, y + 3, largura - 6, altura - 6))
        pygame.draw.rect(self.tela, self.borda_dourada, (x, y, largura, altura), 2)
        pygame.draw.rect(self.tela, self.borda_interna, (x + 1, y + 1, largura - 2, altura - 2), 1)

 #================================================================
 #  BARRA DE PORIGRESSÃO
 #======================================================================
    def desenhar_barra(self, x, y, largura, altura, atual, maximo, cor):
        """Desenha barra de progresso com preenchimento proporcional."""
        pygame.draw.rect(self.tela, self.cinza_fundo, (x, y, largura, altura))

        if maximo > 0:
            porcentagem = max(0.0, min(1.0, atual / maximo))
            largura_preenchida = int(largura * porcentagem)
            if largura_preenchida > 0:
                pygame.draw.rect(self.tela, cor, (x, y, largura_preenchida, altura))

        pygame.draw.rect(self.tela, self.branco, (x, y, largura, altura), 1)


     #================================================================
     #  PAINEL PRINCIPAL CONTROLE
     #======================================================================
    def desenhar_hud_jrpg(self):
        """Painel de status principal em estilo JRPG na parte inferior da tela."""
        altura_hud = 150
        y_hud = ALTURA - altura_hud - 10

        largura_painel = 700
        self.desenhar_caixa_jrpg(10, y_hud, largura_painel, altura_hud)

        largura_slot = (largura_painel - 20) // max(1, len(self.herois))

        x_menu = largura_painel + 20
        largura_menu = 550

         #================================================================
         #  LOG BATALHA ESPAÇO
         #======================================================================
        self.desenhar_caixa_jrpg(x_menu, y_hud, largura_menu, altura_hud)
        # Espaço visual reservado para o log da batalha futuramente.
        # Ele fica ao lado do menu de ações, sem cobrir a caixa do menu.
        x_log = x_menu + largura_menu - 430
        largura_log = 410
        altura_log = altura_hud - 20
        y_log = y_hud + 9

        pygame.draw.rect(
            self.tela,
            (240, 240, 240),
            (x_log, y_log, largura_log, altura_log),
            border_radius=8
        )
        pygame.draw.rect(
            self.tela,
            (130, 130, 130),
            (x_log, y_log, largura_log, altura_log),
            2,
            border_radius=8
        )

        espaco_painel = largura_painel - 60
        largura_slot = espaco_painel // max(1, len(self.herois))
        inicio_x = 15 + (largura_painel - espaco_painel) // 2

        for i, heroi in enumerate(self.herois):
            x_slot = inicio_x + i * largura_slot
            largura_ajustada = largura_slot - 18
            deslocamento_central = (largura_slot - largura_ajustada) // 2
            x_slot += deslocamento_central

            if heroi.atb_barra >= heroi.atb_max:
                pygame.draw.rect(
                    self.tela,
                    self.azul_selecao,
                    (x_slot - 5, y_hud + 10, largura_ajustada, altura_hud - 20)
                )

            nome = self.fonte_pixel.render(heroi.nome, True, self.branco)
            self.tela.blit(nome, (x_slot, y_hud + 15))

            hp_texto = self.fonte_pequena.render(f"HP {heroi.hp}/{heroi.hpMax}", True, self.branco)
            self.tela.blit(hp_texto, (x_slot, y_hud + 45))
            self.desenhar_barra(
                x_slot,
                y_hud + 62,
                largura_ajustada - 5,
                6,
                heroi.hp,
                heroi.hpMax,
                self.verde_hp
            )

            pa_texto = self.fonte_pequena.render(f"PA {getattr(heroi, 'PA', 0)}/{getattr(heroi, 'PAMax', 100)}", True, self.branco)
            self.tela.blit(pa_texto, (x_slot, y_hud + 78))
            self.desenhar_barra(
                x_slot,
                y_hud + 95,
                largura_ajustada - 5,
                6,
                getattr(heroi, 'PA', 0),
                getattr(heroi, 'PAMax', 100),
                self.amarelo_ap
            )

            atb_texto = self.fonte_pequena.render(f"ATB {int(heroi.atb_barra)}/{int(heroi.atb_max)}", True, self.branco)
            self.tela.blit(atb_texto, (x_slot, y_hud + 112))
            self.desenhar_barra(
                x_slot,
                y_hud + 126,
                largura_ajustada - 5,
                5,
                heroi.atb_barra,
                heroi.atb_max,
                self.azul_gradiente
            )

        for idx, cmd in enumerate(self.comandos):
            y_cmd = y_hud + 12 + idx * 26
            if idx == self.comando_selecionado:
                cursor = self.fonte_pixel.render(">", True, self.borda_interna)
                self.tela.blit(cursor, (x_menu + 12, y_cmd))

            txt_cmd = self.fonte_pixel.render(cmd, True, self.branco)
            self.tela.blit(txt_cmd, (x_menu + 30, y_cmd))

 #================================================================
 #  MINI PAINEL EM CIMA DE CADA COMBATENTE
 #======================================================================
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
        self.desenhar_hud_jrpg()


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
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_UP:
                    ui.comando_selecionado = (ui.comando_selecionado - 1) % len(ui.comandos)
                elif evento.key == pygame.K_DOWN:
                    ui.comando_selecionado = (ui.comando_selecionado + 1) % len(ui.comandos)

        for heroi in herois:
            if heroi.atb_barra < heroi.atb_max:
                heroi.carregar_atb(1.2)

        ui.desenhar()
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    iniciar_janela_batalha()