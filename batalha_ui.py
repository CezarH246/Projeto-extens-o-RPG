"""Interface visual de batalha.

Substitua integralmente o arquivo batalha_ui.py por este conteúdo.
O módulo usa as regras de Combate.py para dano, habilidades, PA, ATB, XP e
poções. Ele recebe os heróis do mapa, gera a batalha visual e devolve o
resultado para mapa_teste.py.
"""

from __future__ import annotations

import random
import unicodedata
from pathlib import Path

import pygame
import Combate as regras

LARGURA = 1280
ALTURA = 720
FPS = 60

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS = PROJECT_DIR / "assets"
FUNDO_BATALHA = ASSETS / "backgrounds" / "docas_batalha.jpg"

SPRITES_HEROIS = {
    "Lucas": ASSETS / "personagens" / "Lucas_Protagonista" / "Idle" / "animations" / "Lucas_Batalha" / "south-east",
    "Guilherme": ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Guilherme_Batalha" / "south-east",
    "Cezar": ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations" / "Cezar_Posicao_de_combate" / "east",
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

LOG_BATALHA: list[str] = []


def registrar_evento(*args, sep=" ", **_kwargs) -> None:
    """Recebe as mensagens produzidas pelas regras e as mostra na tela."""
    texto = sep.join(str(item) for item in args).strip()
    if texto:
        LOG_BATALHA.append(texto)
        del LOG_BATALHA[:-6]


def normalizar_nome(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    for caractere in (" ", "-", ".", ",", "'", '"'):
        texto = texto.replace(caractere, "_")
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto


def resolver_sprite_inimigo(inimigo) -> Path | None:
    if inimigo.tipo == "Boss":
        return SPRITES_INIMIGOS["boss"]

    nome_sem_nivel = inimigo.nome.split(" Lv.")[0]
    return SPRITES_INIMIGOS.get(normalizar_nome(nome_sem_nivel))


class SpriteCombatente:
    """Representação visual animada de um combatente das regras de Combate.py."""

    def __init__(self, personagem, centro: tuple[int, int], caminho: Path | None, tamanho: tuple[int, int]):
        self.personagem = personagem
        self.centro = centro
        self.tamanho = tamanho
        self.frames: list[pygame.Surface] = []
        self.indice_frame = 0
        self.ultimo_frame = 0
        self.imagem = self.carregar(caminho)

    def placeholder(self) -> pygame.Surface:
        imagem = pygame.Surface(self.tamanho, pygame.SRCALPHA)
        imagem.fill((100, 100, 110, 255))
        pygame.draw.rect(imagem, (230, 230, 230), imagem.get_rect(), 2)
        return imagem

    def carregar(self, caminho: Path | None) -> pygame.Surface:
        try:
            if caminho is not None and caminho.is_dir():
                arquivos = sorted(caminho.glob("frame_*.png"))[:16]
                self.frames = [
                    pygame.transform.smoothscale(pygame.image.load(arquivo).convert_alpha(), self.tamanho)
                    for arquivo in arquivos
                ]
                if self.frames:
                    return self.frames[0]

            if caminho is not None and caminho.is_file():
                return pygame.transform.smoothscale(pygame.image.load(caminho).convert_alpha(), self.tamanho)
        except pygame.error:
            pass
        return self.placeholder()

    def atualizar(self) -> None:
        if len(self.frames) < 2:
            return
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_frame >= 100:
            self.ultimo_frame = agora
            self.indice_frame = (self.indice_frame + 1) % len(self.frames)
            self.imagem = self.frames[self.indice_frame]

    def desenhar(self, tela: pygame.Surface, selecionado: bool = False) -> None:
        self.atualizar()
        imagem = self.imagem.copy()
        if not self.personagem.estar_vivo():
            imagem.set_alpha(85)

        rect = imagem.get_rect(center=self.centro)
        tela.blit(imagem, rect)
        if selecionado:
            pygame.draw.rect(tela, (255, 226, 92), rect.inflate(10, 10), 4, border_radius=8)


class BattleUI:
    """Tela de batalha visual que utiliza objetos Heroi e Inimigo de Combate.py."""

    def __init__(self, tela: pygame.Surface, herois: list, inimigos: list):
        self.tela = tela
        self.herois = herois
        self.inimigos = inimigos
        self.fonte_titulo = pygame.font.SysFont("arial", 36, bold=True)
        self.fonte = pygame.font.SysFont("arial", 20, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial", 15)
        self.fonte_menor = pygame.font.SysFont("arial", 13)

        self.fundo = self.carregar_fundo()
        self.sprites_herois: list[SpriteCombatente] = []
        self.sprites_inimigos: list[SpriteCombatente] = []
        self.criar_sprites()

        self.heroi_ativo = None
        self.acao_pendente: str | None = None
        self.indice_alvo = 0
        self.resultado: bool | None = None
        self.concluida = False
        self.recompensas_aplicadas = False
        self.mensagem = "A batalha começou. Aguarde a barra ATB encher."

        LOG_BATALHA.clear()
        LOG_BATALHA.append("Um grupo de inimigos apareceu.")
        regras.print = registrar_evento

    def carregar_fundo(self) -> pygame.Surface:
        try:
            imagem = pygame.image.load(FUNDO_BATALHA).convert()
            return pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))
        except (FileNotFoundError, pygame.error):
            fundo = pygame.Surface((LARGURA, ALTURA))
            fundo.fill((39, 73, 90))
            return fundo

    def criar_sprites(self) -> None:
        posicoes_herois = [(220, 280), (170, 455), (390, 430)]
        posicoes_inimigos = [(1060, 270), (970, 445), (835, 360)]

        for indice, heroi in enumerate(self.herois[:3]):
            caminho = SPRITES_HEROIS.get(heroi.nome)
            self.sprites_herois.append(SpriteCombatente(heroi, posicoes_herois[indice], caminho, (180, 180)))

        for indice, inimigo in enumerate(self.inimigos[:3]):
            caminho = resolver_sprite_inimigo(inimigo)
            self.sprites_inimigos.append(SpriteCombatente(inimigo, posicoes_inimigos[indice], caminho, (175, 175)))

    def inimigos_vivos(self) -> list:
        return [inimigo for inimigo in self.inimigos if inimigo.estar_vivo()]

    def herois_vivos(self) -> list:
        return [heroi for heroi in self.herois if heroi.estar_vivo()]

    def verificar_resultado(self) -> None:
        if not self.inimigos_vivos():
            if not self.recompensas_aplicadas:
                for inimigo in self.inimigos:
                    regras.dar_xp(inimigo, self.herois)
                    regras.verificar_drop_pocao(inimigo, self.herois)
                self.recompensas_aplicadas = True

            self.resultado = True
            self.mensagem = "Vitória! Pressione ENTER para retornar ao mapa."
            LOG_BATALHA.append("Vitória! O inimigo do mapa será removido.")

        elif not self.herois_vivos():
            self.resultado = False
            self.mensagem = "Derrota. Pressione ENTER para retornar ao mapa."
            LOG_BATALHA.append("O grupo foi derrotado.")

    def atualizar(self, tempo_frame: float) -> None:
        if self.resultado is not None or self.heroi_ativo is not None:
            return

        for combatente in self.herois + self.inimigos:
            combatente.carregar_atb(tempo_frame * 3.0)

        pronto = next(
            (
                combatente for combatente in self.herois + self.inimigos
                if combatente.estar_vivo() and combatente.atb_barra >= combatente.atb_max
            ),
            None,
        )
        if pronto is None:
            return

        if isinstance(pronto, regras.Heroi):
            self.heroi_ativo = pronto
            self.mensagem = f"Turno de {pronto.nome}. Use as teclas 1 a 6."
            LOG_BATALHA.append(f"Turno de {pronto.nome}.")
            return

        alvo = random.choice(self.herois_vivos())
        pronto.atacar(alvo)
        pronto.resetar_atb()
        self.mensagem = f"{pronto.nome} atacou {alvo.nome}."
        self.verificar_resultado()

    def escolher_acao(self, numero: int) -> None:
        if self.heroi_ativo is None:
            return

        acoes = {
            1: ("Ataque normal", "atacar"),
            2: ("Habilidade especial", "habilidade_especial"),
            3: ("Segunda habilidade", "segunda_habilidade"),
            4: ("Ultimate", "ultimate"),
            5: ("Usar poção", "usar_pocao_pa"),
            6: ("Defender", "defender"),
        }
        if numero not in acoes:
            return

        nome, acao = acoes[numero]
        if acao in {"usar_pocao_pa", "defender"}:
            self.executar_acao(acao)
            return

        self.acao_pendente = acao
        self.indice_alvo = 0
        self.mensagem = f"{nome}: use ESQUERDA/DIREITA para o alvo e ENTER para confirmar."

    def executar_acao(self, acao: str) -> None:
        if self.heroi_ativo is None:
            return

        executou = False
        if acao == "defender":
            self.heroi_ativo.defesa += 5
            self.heroi_ativo.acoes_realizadas += 1
            LOG_BATALHA.append(f"{self.heroi_ativo.nome} se prepara para defender (+5 DEF).")
            executou = True
        elif acao == "usar_pocao_pa":
            executou = self.heroi_ativo.usar_pocao_pa()
        else:
            vivos = self.inimigos_vivos()
            if vivos:
                alvo = vivos[self.indice_alvo % len(vivos)]
                executou = getattr(self.heroi_ativo, acao)(alvo)

        if not executou:
            self.acao_pendente = None
            self.mensagem = "Ação indisponível. Escolha outra opção."
            return

        self.verificar_resultado()
        if self.resultado is None:
            self.heroi_ativo.resetar_atb()
            self.heroi_ativo = None
            self.acao_pendente = None
            self.mensagem = "Aguardando a próxima barra ATB ficar cheia."

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type != pygame.KEYDOWN:
            return

        if self.resultado is not None:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.concluida = True
            return

        if self.heroi_ativo is None:
            return

        if self.acao_pendente is not None:
            total = len(self.inimigos_vivos())
            if total == 0:
                return
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                self.indice_alvo = (self.indice_alvo - 1) % total
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.indice_alvo = (self.indice_alvo + 1) % total
            elif evento.key == pygame.K_RETURN:
                self.executar_acao(self.acao_pendente)
            elif evento.key == pygame.K_ESCAPE:
                self.acao_pendente = None
                self.mensagem = "Seleção de alvo cancelada. Escolha uma ação."
            return

        if pygame.K_1 <= evento.key <= pygame.K_6:
            self.escolher_acao(evento.key - pygame.K_0)

    def desenhar_barra(self, x: int, y: int, largura: int, valor: float, maximo: float, cor: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.tela, (25, 27, 39), (x, y, largura, 10), border_radius=4)
        proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
        preenchimento = int(largura * proporcao)
        if preenchimento:
            pygame.draw.rect(self.tela, cor, (x, y, preenchimento, 10), border_radius=4)
        pygame.draw.rect(self.tela, (238, 238, 242), (x, y, largura, 10), 1, border_radius=4)

    def desenhar_painel_herois(self) -> None:
        painel = pygame.Rect(15, ALTURA - 170, 710, 155)
        pygame.draw.rect(self.tela, (16, 28, 75), painel, border_radius=12)
        pygame.draw.rect(self.tela, (222, 181, 83), painel, 3, border_radius=12)

        for indice, heroi in enumerate(self.herois):
            x = 35 + indice * 225
            cor = (255, 230, 135) if heroi is self.heroi_ativo else (255, 255, 255)
            texto = self.fonte_pequena.render(f"{heroi.nome}  Nv.{heroi.level}", True, cor)
            self.tela.blit(texto, (x, ALTURA - 153))
            self.desenhar_barra(x, ALTURA - 126, 190, heroi.hp, heroi.hpMax, (75, 221, 115))
            self.desenhar_barra(x, ALTURA - 101, 190, heroi.PA, heroi.PAMax, (239, 191, 53))
            self.desenhar_barra(x, ALTURA - 76, 190, heroi.atb_barra, heroi.atb_max, (70, 145, 245))
            detalhes = self.fonte_menor.render(
                f"HP      PA {heroi.PA:3.0f}      ATB {heroi.atb_barra:3.0f}", True, (230, 230, 235)
            )
            self.tela.blit(detalhes, (x, ALTURA - 52))

    def desenhar_painel_acoes(self) -> None:
        painel = pygame.Rect(745, ALTURA - 170, 520, 155)
        pygame.draw.rect(self.tela, (16, 28, 75), painel, border_radius=12)
        pygame.draw.rect(self.tela, (222, 181, 83), painel, 3, border_radius=12)

        acoes = ["1  ATTACK", "2  MAGIC", "3  SPECIAL", "4  ULTIMATE", "5  ITEM", "6  GUARD"]
        for indice, acao in enumerate(acoes):
            coluna = indice // 3
            linha = indice % 3
            texto = self.fonte_pequena.render(acao, True, (255, 255, 255))
            self.tela.blit(texto, (765 + coluna * 225, ALTURA - 150 + linha * 24))

        mensagem = self.fonte_menor.render(self.mensagem[:76], True, (255, 225, 135))
        self.tela.blit(mensagem, (765, ALTURA - 65))
        ajuda = self.fonte_menor.render("Setas: alvo | ENTER: confirmar | ESC: cancelar", True, (225, 225, 235))
        self.tela.blit(ajuda, (765, ALTURA - 40))

    def desenhar(self) -> None:
        self.tela.blit(self.fundo, (0, 0))
        escurecimento = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escurecimento.fill((0, 0, 0, 38))
        self.tela.blit(escurecimento, (0, 0))

        titulo = self.fonte_titulo.render("BATALHA", True, (255, 225, 135))
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 38)))

        alvos_vivos = self.inimigos_vivos()
        for sprite in self.sprites_herois:
            sprite.desenhar(self.tela)
        for sprite in self.sprites_inimigos:
            selecionado = (
                self.acao_pendente is not None
                and sprite.personagem in alvos_vivos
                and alvos_vivos.index(sprite.personagem) == self.indice_alvo
            )
            sprite.desenhar(self.tela, selecionado)

        y_log = 78
        for texto_log in LOG_BATALHA:
            texto = self.fonte_menor.render(texto_log[:125], True, (250, 250, 250))
            sombra = self.fonte_menor.render(texto_log[:125], True, (20, 20, 25))
            self.tela.blit(sombra, (31, y_log + 1))
            self.tela.blit(texto, (30, y_log))
            y_log += 19

        self.desenhar_painel_herois()
        self.desenhar_painel_acoes()

        if self.resultado is not None:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((0, 0, 0, 155))
            self.tela.blit(camada, (0, 0))
            palavra = "VITÓRIA" if self.resultado else "DERROTA"
            cor = (88, 235, 125) if self.resultado else (245, 93, 93)
            resultado = self.fonte_titulo.render(palavra, True, cor)
            instrucao = self.fonte.render("Pressione ENTER para retornar ao mapa", True, (255, 255, 255))
            self.tela.blit(resultado, resultado.get_rect(center=(LARGURA // 2, 305)))
            self.tela.blit(instrucao, instrucao.get_rect(center=(LARGURA // 2, 355)))


def criar_batalha(tela: pygame.Surface, herois: list, quantidade_inimigos: int = 3) -> BattleUI:
    """Cria a tela que mapa_teste.py abre após uma colisão com inimigo."""
    nivel_grupo = max(heroi.level for heroi in herois)
    inimigos = regras.criar_cenario_batalha(nivel_grupo, quantidade=quantidade_inimigos)
    return BattleUI(tela, herois, inimigos)


def iniciar_janela_batalha() -> None:
    """Permite testar somente esta tela, sem abrir o mapa."""
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("RPG - Batalha")
    relogio = pygame.time.Clock()
    batalha = criar_batalha(tela, regras.criar_herois())
    executando = True

    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            else:
                batalha.processar_evento(evento)
        batalha.atualizar(relogio.tick(FPS) / 1000)
        batalha.desenhar()
        pygame.display.flip()
        if batalha.concluida:
            executando = False

    pygame.quit()


if __name__ == "__main__":
    iniciar_janela_batalha()
