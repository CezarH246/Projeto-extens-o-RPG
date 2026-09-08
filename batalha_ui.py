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
from PIL import Image

LARGURA = 1280
ALTURA = 720
FPS = 60

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS = PROJECT_DIR / "assets"
FUNDO_BATALHA = ASSETS / "backgrounds" / "docas_batalha.jpg"

ULTIMATE_CEZAR = ASSETS / "ultimates" / "Cezar_Ultimate" / "Cezar_Ultimate"
ULTIMATE_GUILHERME = ASSETS / "ultimates" / "Guilherme_Ultimate" / "pixellab-O-mago--que-inicialmente-mant--1788880617530"
ULTIMATE_GUILHERME_ATAQUE = ASSETS / "ultimates" / "Guilherme_Ultimate" / "pixellab-The-black-hole-slowly-rotates--1788882096725"

ATAQUE_BASICO_CEZAR = ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations" / "Ataque_Basico"
ATAQUE_BASICO_GUILHERME = ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Ataque_Basico"

DASH_CEZAR = ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations" / "Dash_Combate"

ANIMACAO_MAGO_HABILIDADE = ASSETS / "efeitos" / "Idle_custom-Animate_the_character_performing_a_magical_firebal_south.gif"
BOLA_FOGO_MAGO = ASSETS / "efeitos" / "Idle_custom-Create_only_the_fireball_attack_particle_effect._D_south.gif"

ATAQUE_INIMIGO = ASSETS / "inimigos" / "Ataque_inimigo" 


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
}

#CRIAR LISTA DE DASH
DASHES = {
    "Cezar": DASH_CEZAR,
}

#CRIAR LISTA DE ATQUES ESPECIAIS
# LISTA DE ULTIMATES
ULTIMATES = {
    "Cezar": ULTIMATE_CEZAR,
    "Guilherme": ULTIMATE_GUILHERME,
}

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


def cor_barra_hp(valor: float, maximo: float) -> tuple[int, int, int]:
    proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
    if proporcao <= 0.30:
        return (220, 65, 65)
    if proporcao <= 0.60:
        return (245, 166, 35)
    return (75, 221, 115)


class FloatingDamage:
    """Animação de número de dano flutuante acima do sprite do inimigo."""
    def __init__(self, x: float, y: float, dano: int, duracao: float = 1.5):
        self.x = x
        self.y = y
        self.dano = dano
        self.tempo_decorrido = 0.0
        self.duracao = duracao
        self.cor_inicial = (255, 100, 100)  # Vermelho
        self.cor_final = (255, 200, 100)    # Laranja
    
    def atualizar(self, tempo_frame: float) -> bool:
        """Retorna False quando a animação termina."""
        self.tempo_decorrido += tempo_frame
        return self.tempo_decorrido < self.duracao
    
    def desenhar(self, tela: pygame.Surface, fonte: pygame.font.Font) -> None:
        """Desenha o número com transparência decrescente."""
        progresso = self.tempo_decorrido / self.duracao
        alpha = 255 * (1 - progresso)  # Desaparece gradualmente
        y_flutuante = self.y - (progresso * 40)  # Sobe 40 pixels
        
        # Interpola entre as cores
        r = int(self.cor_inicial[0] + (self.cor_final[0] - self.cor_inicial[0]) * progresso)
        g = int(self.cor_inicial[1] + (self.cor_final[1] - self.cor_inicial[1]) * progresso)
        b = int(self.cor_inicial[2] + (self.cor_final[2] - self.cor_inicial[2]) * progresso)
        cor = (r, g, b)
        
        texto = fonte.render(f"-{self.dano}", True, cor)
        texto.set_alpha(int(alpha))
        rect = texto.get_rect(center=(int(self.x), int(y_flutuante)))
        tela.blit(texto, rect)


class AnimacaoUltimate:
    def __init__(self, frames: list[pygame.Surface], personagem, origem: tuple[int, int], alvo: tuple[int, int], velocidade_animacao: float = 0.08):
        self.frames = frames
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.indice = 0
        self.tempo = 0.0
        self.fim_ataque = 22
        self.velocidade_animacao = velocidade_animacao

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        if self.tempo >= self.velocidade_animacao:
            self.tempo = 0.0
            self.indice += 1
        return self.indice < len(self.frames)

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice <= self.fim_ataque:
            progresso = self.indice / self.fim_ataque
            centro = self.origem.lerp(self.alvo, progresso)
        else:
            centro = self.alvo
        imagem = self.frames[self.indice].copy()
        rect = imagem.get_rect(center=(round(centro.x), round(centro.y)))
        tela.blit(imagem, rect)


class AnimacaoAtaque(AnimacaoUltimate):
    """Mesma lógica da animação de ultimate, mas para o ataque básico."""
    pass


class AnimacaoDash(AnimacaoUltimate):
    """Animação curta de deslocamento do personagem antes do ataque."""
    def __init__(self, frames: list[pygame.Surface], personagem, origem: tuple[int, int], alvo: tuple[int, int], velocidade_animacao: float = 0.04):
        super().__init__(frames, personagem, origem, alvo, velocidade_animacao=velocidade_animacao)


class AnimacaoHabilidadeMago:
    """Mostra o Mago conjurando e lança a bola de fogo até o alvo."""
    def __init__(self, frames_mago, frames_bola, personagem, origem, alvo):
        self.frames_mago = frames_mago
        self.frames_bola = frames_bola
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.indice = 0
        self.tempo = 0.0
        self.velocidade_animacao = 0.07

    @property
    def duracao_mago(self) -> int:
        return len(self.frames_mago)

    @property
    def personagem_oculto(self) -> bool:
        return self.indice < self.duracao_mago

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < self.duracao_mago + len(self.frames_bola)

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice < self.duracao_mago:
            imagem = self.frames_mago[self.indice]
            centro = self.origem
        else:
            indice_bola = min(self.indice - self.duracao_mago, len(self.frames_bola) - 1)
            imagem = self.frames_bola[indice_bola]
            progresso = indice_bola / max(1, len(self.frames_bola) - 1)
            centro = self.origem.lerp(self.alvo, progresso)

        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoUltimateMago(AnimacaoHabilidadeMago):
    """Mostra a conjuração do Mago e o buraco negro diretamente no alvo."""
    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice < self.duracao_mago:
            imagem = self.frames_mago[self.indice]
            centro = self.origem
        else:
            indice_ataque = min(self.indice - self.duracao_mago, len(self.frames_bola) - 1)
            imagem = self.frames_bola[indice_ataque]
            centro = self.alvo

        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


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


def tamanho_com_escala(tamanho_base: tuple[int, int], personagem) -> tuple[int, int]:
    escala = max(0.01, float(getattr(personagem, "escala", 1.0)))
    return tuple(max(1, round(dimensao * escala)) for dimensao in tamanho_base)


class SpriteCombatente:
    """Representação visual animada de um combatente das regras de Combate.py."""

    def __init__(self, personagem, centro: tuple[int, int], caminho: Path | None, tamanho: tuple[int, int]):
        self.personagem = personagem
        self.centro = centro
        self.centro_inicial = centro
        self.tamanho = tamanho
        self.frames: list[pygame.Surface] = []
        self.indice_frame = 0
        self.ultimo_frame = 0
        self.imagem = self.carregar(caminho)
        self.danos_flutuantes: list[FloatingDamage] = []  # Animações de dano

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

    def adicionar_dano_flutuante(self, dano: int) -> None:
        """Adiciona animação de dano flutuante acima do sprite."""
        self.danos_flutuantes.append(FloatingDamage(self.centro[0], self.centro[1] - 100, dano))
    
    def desenhar_barra_hp(self, tela: pygame.Surface) -> None:
        """Desenha barra de HP, ATB e nome acima do inimigo."""
        largura_barra = 120
        altura_barra = 8
        x_barra = self.centro[0] - largura_barra // 2
        y_barra = self.centro[1] - 110
        
        # ========== BARRA DE HP ==========
        # Fundo da barra
        pygame.draw.rect(tela, (25, 27, 39), (x_barra, y_barra, largura_barra, altura_barra), border_radius=3)
        
        # Preenchimento da barra (verde para HP)
        proporcao_hp = max(0.0, min(1.0, self.personagem.hp / self.personagem.hpMax)) if self.personagem.hpMax > 0 else 0
        preenchimento_hp = int(largura_barra * proporcao_hp)
        if preenchimento_hp > 0:
            pygame.draw.rect(
                tela,
                cor_barra_hp(self.personagem.hp, self.personagem.hpMax),
                (x_barra, y_barra, preenchimento_hp, altura_barra),
                border_radius=3,
            )
        
        # Borda da barra
        pygame.draw.rect(tela, (238, 238, 242), (x_barra, y_barra, largura_barra, altura_barra), 1, border_radius=3)
        
        # ========== BARRA DE ATB ==========
        y_atb = y_barra + 12  # 12px abaixo da barra de HP
        
        # Fundo da barra ATB
        pygame.draw.rect(tela, (25, 27, 39), (x_barra, y_atb, largura_barra, altura_barra), border_radius=3)
        
        # Preenchimento da barra ATB (azul)
        proporcao_atb = max(0.0, min(1.0, self.personagem.atb_barra / self.personagem.atb_max)) if self.personagem.atb_max > 0 else 0
        preenchimento_atb = int(largura_barra * proporcao_atb)
        if preenchimento_atb > 0:
            pygame.draw.rect(tela, (70, 145, 245), (x_barra, y_atb, preenchimento_atb, altura_barra), border_radius=3)
        
        # Borda da barra ATB
        pygame.draw.rect(tela, (238, 238, 242), (x_barra, y_atb, largura_barra, altura_barra), 1, border_radius=3)
        
        # Nome do inimigo em cima
        fonte_nome = pygame.font.SysFont("arial", 12, bold=True)
        texto_nome = fonte_nome.render(self.personagem.nome[:18], True, (255, 255, 255))
        tela.blit(texto_nome, (self.centro[0] - texto_nome.get_width() // 2, y_barra - 18))

    def desenhar(self, tela: pygame.Surface, selecionado: bool = False, fonte_dano: pygame.font.Font | None = None) -> None:
        self.atualizar()
        imagem = self.imagem.copy()
        if not self.personagem.estar_vivo():
            imagem.set_alpha(85)

        rect = imagem.get_rect(center=self.centro)
        tela.blit(imagem, rect)
        
        # Desenha a barra de HP acima do sprite (apenas para inimigos)
        if not isinstance(self.personagem, regras.Heroi):
            self.desenhar_barra_hp(tela)
        
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
        self.fonte_dano = pygame.font.SysFont("arial", 24, bold=True)  # Fonte para números de dano
        self.animacao_dash = None
        self.animacao_ataque = None
        self.animacao_ataque_inimigo = None
        self.animacao_ultimate = None
        self.animacao_habilidade_mago = None
        self.animacao_apos_dash = None
        self.posicao_final_dash = None

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

    def restaurar_posicao_inicial_heroi(self, heroi):
        sprite_heroi = next((s for s in self.sprites_herois if s.personagem is heroi), None)
        if sprite_heroi is not None:
            sprite_heroi.centro = sprite_heroi.centro_inicial

    def carregar_fundo(self) -> pygame.Surface:
        try:
            imagem = pygame.image.load(FUNDO_BATALHA).convert()
            return pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))
        except (FileNotFoundError, pygame.error):
            fundo = pygame.Surface((LARGURA, ALTURA))
            fundo.fill((39, 73, 90))
            return fundo

    def carregar_animacao_dash(self, personagem) -> list[pygame.Surface]:
        frames = []
        caminho = DASHES.get(personagem.nome)
        if caminho is None:
            return frames

        tamanho = tamanho_com_escala((180, 180), personagem)
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                imagem = pygame.image.load(arquivo).convert_alpha()
                frames.append(pygame.transform.smoothscale(imagem, tamanho))
            except pygame.error:
                continue
        return frames

    def carregar_animacao_ataque(self, personagem) -> list[pygame.Surface]:
        frames = []
        caminho = ATAQUES_BASICOS.get(personagem.nome)
        if caminho is None:
            return frames

        tamanho = tamanho_com_escala((180, 180), personagem)
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                imagem = pygame.image.load(arquivo).convert_alpha()
                frames.append(pygame.transform.smoothscale(imagem, tamanho))
            except pygame.error:
                continue
        return frames

    def carregar_animacao_ataque_inimigo(self, inimigo) -> list[pygame.Surface]:
        frames = []
        nome_sem_nivel = inimigo.nome.split(" Lv.")[0]
        caminho = ATAQUES_INIMIGOS.get(normalizar_nome(nome_sem_nivel))
        if caminho is None:
            return frames

        tamanho = tamanho_com_escala((250, 250), inimigo)
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                imagem = pygame.image.load(arquivo).convert_alpha()
                frames.append(pygame.transform.smoothscale(imagem, tamanho))
            except pygame.error:
                continue
        return frames

    def carregar_animacao_ultimate(self, personagem) -> list[pygame.Surface]:
        frames = []
        caminho = ULTIMATES.get(personagem.nome)
        if caminho is None:
            return frames

        tamanho = tamanho_com_escala((180, 180), personagem)
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                imagem = pygame.image.load(arquivo).convert_alpha()
                frames.append(pygame.transform.smoothscale(imagem, tamanho))
            except pygame.error:
                continue
        return frames

    def carregar_frames_gif(self, caminho: Path, tamanho: tuple[int, int]) -> list[pygame.Surface]:
        frames = []
        try:
            with Image.open(caminho) as gif:
                for indice in range(getattr(gif, "n_frames", 1)):
                    gif.seek(indice)
                    quadro = gif.convert("RGBA")
                    dados = quadro.tobytes()
                    imagem = pygame.image.fromstring(dados, quadro.size, "RGBA").convert_alpha()
                    frames.append(pygame.transform.smoothscale(imagem, tamanho))
        except (OSError, ValueError, pygame.error):
            return []
        return frames

    def carregar_animacao_habilidade_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        frames_mago = self.carregar_frames_gif(ANIMACAO_MAGO_HABILIDADE, (120, 120))
        frames_bola = self.carregar_frames_gif(BOLA_FOGO_MAGO, (96, 96))
        return frames_mago, frames_bola

    def carregar_animacao_ultimate_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        tamanho_mago = tamanho_com_escala((180, 180), personagem)
        frames_mago = self.carregar_frames_pasta(ULTIMATE_GUILHERME, tamanho_mago)
        frames_buraco_negro = self.carregar_frames_pasta(ULTIMATE_GUILHERME_ATAQUE, (300, 300))
        return frames_mago, frames_buraco_negro

    def carregar_frames_pasta(self, caminho: Path, tamanho: tuple[int, int]) -> list[pygame.Surface]:
        frames = []
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                imagem = pygame.image.load(arquivo).convert_alpha()
                frames.append(pygame.transform.smoothscale(imagem, tamanho))
            except pygame.error:
                continue
        return frames

    def criar_sprites(self) -> None:
        posicoes_herois = [(220, 280), (170, 455), (390, 430)]
        posicoes_inimigos = [(1060, 270), (970, 445), (835, 360)]

        for indice, heroi in enumerate(self.herois[:3]):
            caminho = SPRITES_HEROIS.get(heroi.nome)
            tamanho = tamanho_com_escala((180, 180), heroi)
            sprite = SpriteCombatente(heroi, posicoes_herois[indice], caminho, tamanho)
            self.sprites_herois.append(sprite)

        for indice, inimigo in enumerate(self.inimigos[:3]):
            caminho = resolver_sprite_inimigo(inimigo)
            tamanho = tamanho_com_escala((175, 175), inimigo)
            self.sprites_inimigos.append(SpriteCombatente(inimigo, posicoes_inimigos[indice], caminho, tamanho))

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
        # Atualiza danos flutuantes de todos os inimigos
        for sprite in self.sprites_inimigos:
            sprite.danos_flutuantes = [d for d in sprite.danos_flutuantes if d.atualizar(tempo_frame)]

        if self.animacao_dash is not None:
            if not self.animacao_dash.atualizar(tempo_frame):
                self.animacao_dash = None
                if self.animacao_apos_dash is not None:
                    tipo, heroi, alvo, posicao_final = self.animacao_apos_dash
                    sprite_heroi = next((s for s in self.sprites_herois if s.personagem is heroi), None)
                    sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)

                    if sprite_heroi is not None and posicao_final is not None:
                        sprite_heroi.centro = (int(posicao_final.x), int(posicao_final.y))
                        self.posicao_final_dash = posicao_final

                    if tipo == "atacar":
                        frames = self.carregar_animacao_ataque(heroi)
                        if frames and sprite_heroi and sprite_alvo:
                            self.animacao_ataque = AnimacaoAtaque(
                                frames,
                                heroi,
                                (int(posicao_final.x), int(posicao_final.y)),
                                sprite_alvo.centro,
                            )
                    elif tipo == "ultimate":
                        frames = self.carregar_animacao_ultimate(heroi)
                        if frames and sprite_heroi and sprite_alvo:
                            self.animacao_ultimate = AnimacaoUltimate(
                                frames,
                                heroi,
                                (int(posicao_final.x), int(posicao_final.y)),
                                sprite_alvo.centro,
                            )
                    self.animacao_apos_dash = None
                    self.posicao_final_dash = None

        if self.animacao_ataque is not None:
            if not self.animacao_ataque.atualizar(tempo_frame):
                animacao_finalizada = self.animacao_ataque
                self.animacao_ataque = None
                self.restaurar_posicao_inicial_heroi(animacao_finalizada.personagem)

        if self.animacao_ataque_inimigo is not None:
            if not self.animacao_ataque_inimigo.atualizar(tempo_frame):
                self.animacao_ataque_inimigo = None

        if self.animacao_ultimate is not None and not isinstance(self.animacao_ultimate, AnimacaoUltimateMago):
            if not self.animacao_ultimate.atualizar(tempo_frame):
                animacao_finalizada = self.animacao_ultimate
                self.animacao_ultimate = None
                self.restaurar_posicao_inicial_heroi(animacao_finalizada.personagem)

        if isinstance(self.animacao_ultimate, AnimacaoUltimateMago):
            if not self.animacao_ultimate.atualizar(tempo_frame):
                self.animacao_ultimate = None

        if self.animacao_habilidade_mago is not None:
            if not self.animacao_habilidade_mago.atualizar(tempo_frame):
                self.animacao_habilidade_mago = None
        
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
        sprite_inimigo = next((s for s in self.sprites_inimigos if s.personagem is pronto), None)
        sprite_alvo = next((s for s in self.sprites_herois if s.personagem is alvo), None)

        if sprite_inimigo and sprite_alvo:
            frames = self.carregar_animacao_ataque_inimigo(pronto)
            if frames:
                centro_efeito = (sprite_alvo.centro[0], max(0, sprite_alvo.centro[1] + 20))
                self.animacao_ataque_inimigo = AnimacaoAtaque(
                    frames,
                    pronto,
                    centro_efeito,
                    centro_efeito,
                )

        pronto.atacar(alvo)
        pronto.resetar_atb()
        self.mensagem = f"{pronto.nome} atacou {alvo.nome}."

        # Mostra dano flutuante para o alvo (se for inimigo)
        if sprite_alvo and hasattr(alvo, '_ultimo_dano_recebido'):
            sprite_alvo.adicionar_dano_flutuante(int(alvo._ultimo_dano_recebido))

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
                
                # Mostra dano flutuante após ataque
                if executou and acao in {"atacar", "habilidade_especial", "segunda_habilidade", "ultimate"}:
                    if hasattr(alvo, '_ultimo_dano_recebido'):
                        sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)
                        if sprite_alvo:
                            sprite_alvo.adicionar_dano_flutuante(int(alvo._ultimo_dano_recebido))

                    sprite_heroi = next((s for s in self.sprites_herois if s.personagem is self.heroi_ativo), None)
                    sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)

                    dash_frames = self.carregar_animacao_dash(self.heroi_ativo)
                    if dash_frames and sprite_heroi and sprite_alvo:
                        origem_dash = pygame.Vector2(sprite_heroi.centro)
                        alvo_dash = pygame.Vector2(sprite_alvo.centro)
                        vetor = alvo_dash - origem_dash
                        if vetor.length_squared() > 0:
                            # Quanto maior o número, mais rápido e mais longo será o deslocamento do dash.
                            DISTANCIA_DASH = 200
                            vetor = vetor.normalize() * DISTANCIA_DASH
                            alvo_dash = alvo_dash - vetor
                        self.animacao_dash = AnimacaoDash(
                            dash_frames,
                            self.heroi_ativo,
                            origem_dash,
                            alvo_dash,
                            velocidade_animacao=0.04,
                        )
                        self.animacao_apos_dash = (acao, self.heroi_ativo, alvo, alvo_dash.copy())
                    elif acao == "atacar":
                        frames = self.carregar_animacao_ataque(self.heroi_ativo)
                        if frames and sprite_heroi and sprite_alvo:
                            self.animacao_ataque = AnimacaoAtaque(
                                frames,
                                self.heroi_ativo,
                                sprite_heroi.centro,
                                sprite_alvo.centro,
                            )
                    elif acao == "ultimate":
                        if self.heroi_ativo.nome == "Guilherme":
                            frames_mago, frames_buraco_negro = self.carregar_animacao_ultimate_mago(self.heroi_ativo)
                            if frames_mago and frames_buraco_negro and sprite_heroi and sprite_alvo:
                                self.animacao_ultimate = AnimacaoUltimateMago(
                                    frames_mago,
                                    frames_buraco_negro,
                                    self.heroi_ativo,
                                    sprite_heroi.centro,
                                    sprite_alvo.centro,
                                )
                        else:
                            frames = self.carregar_animacao_ultimate(self.heroi_ativo)
                            if frames and sprite_heroi and sprite_alvo:
                                self.animacao_ultimate = AnimacaoUltimate(
                                    frames,
                                    self.heroi_ativo,
                                    sprite_heroi.centro,
                                    sprite_alvo.centro,
                                )
                    elif acao == "habilidade_especial" and self.heroi_ativo.ClasseRPG == "Mago":
                        frames_mago, frames_bola = self.carregar_animacao_habilidade_mago(self.heroi_ativo)
                        if frames_mago and frames_bola and sprite_heroi and sprite_alvo:
                            self.animacao_habilidade_mago = AnimacaoHabilidadeMago(
                                frames_mago,
                                frames_bola,
                                self.heroi_ativo,
                                sprite_heroi.centro,
                                sprite_alvo.centro,
                            )

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
            self.desenhar_barra(x, ALTURA - 126, 190, heroi.hp, heroi.hpMax, cor_barra_hp(heroi.hp, heroi.hpMax))
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
        personagens_em_animacao = {
            anim.personagem
            for anim in (self.animacao_dash, self.animacao_ataque, self.animacao_ultimate, self.animacao_habilidade_mago)
            if anim is not None
            and not (
                anim in (self.animacao_habilidade_mago, self.animacao_ultimate)
                and isinstance(anim, AnimacaoHabilidadeMago)
                and not anim.personagem_oculto
            )
        }

        for sprite in self.sprites_herois:
            if sprite.personagem not in personagens_em_animacao:
                sprite.desenhar(self.tela)
        for sprite in self.sprites_inimigos:
            selecionado = (
                self.acao_pendente is not None
                and sprite.personagem in alvos_vivos
                and alvos_vivos.index(sprite.personagem) == self.indice_alvo
            )
            sprite.desenhar(self.tela, selecionado, self.fonte_dano)
            
            # Desenha danos flutuantes
            for dano in sprite.danos_flutuantes:
                dano.desenhar(self.tela, self.fonte_dano)

        if self.animacao_dash is not None:
            self.animacao_dash.desenhar(self.tela)

        if self.animacao_ataque is not None:
            self.animacao_ataque.desenhar(self.tela)

        if self.animacao_ataque_inimigo is not None:
            self.animacao_ataque_inimigo.desenhar(self.tela)

        if self.animacao_ultimate is not None:
            self.animacao_ultimate.desenhar(self.tela)

        if self.animacao_habilidade_mago is not None:
            self.animacao_habilidade_mago.desenhar(self.tela)

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
