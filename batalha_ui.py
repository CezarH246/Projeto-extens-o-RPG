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
ENTIDADE_MAIOR_CEZAR = ASSETS / "efeitos" / "Entidade_maior" / "Idle_custom-The_giant_serpent_remains_in_a_south-east.gif"
REI_TRITAO_IDLE = ASSETS / "inimigos" / "Rei_Tritao" / "rei_tritao_idle.gif"

CEZAR_ANIMACOES = ASSETS / "personagens" / "Cezar_Protagonista" / "Idle" / "animations"

ATAQUE_BASICO_CEZAR = CEZAR_ANIMACOES / "Ataque_Basico"
ATAQUE_BASICO_GUILHERME = ASSETS / "personagens" / "Guilherme_Protagonista" / "Idle" / "animations" / "Ataque_Basico"

DASH_CEZAR = CEZAR_ANIMACOES / "Dash_Combate"

# Habilidade especial do Cezar: ele conjura a magia e o projétil sai dela.
MAGIA_CEZAR = CEZAR_ANIMACOES / "Cezar_Magia"
PROJETIL_CEZAR_GIF = CEZAR_ANIMACOES / "Cezar_Projetil" / "gif_Projetil_Cezar.gif"

# Segunda habilidade do Cezar.
ESPECIAL_CEZAR = CEZAR_ANIMACOES / "Cezar_Especial"

# Efeito do Cezar enquanto a Ultimate estiver pronta.
ULTIMATE_PRONTA_CEZAR = CEZAR_ANIMACOES / "UltimateOn_Cezar"

ANIMACAO_MAGO_HABILIDADE = ASSETS / "efeitos" / "Idle_custom-Animate_the_character_performing_a_magical_firebal_south.gif"
BOLA_FOGO_MAGO = ASSETS / "efeitos" / "Idle_custom-Create_only_the_fireball_attack_particle_effect._D_south.gif"

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
}

#CRIAR LISTA DE DASH
DASHES = {
    "Cezar": DASH_CEZAR,
}

#CRIAR LISTA DE ATQUES ESPECIAIS
#Habilidade especial (tecla 2): conjuração + projétil que sai da magia.
HABILIDADES_ESPECIAIS = {
    "Cezar": (MAGIA_CEZAR, PROJETIL_CEZAR_GIF),
}

# Segunda habilidade (tecla 3): animação própria do personagem.
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
        ASSETS / "personagens" / "Lucas_Protagonista" / "ultimate-pronta.gif",
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

    # Frame da conjuração do Mago em que o buraco negro já começa a
    # aparecer sobre o inimigo (ainda enquanto ele conjura).
    frame_inicio_efeito = 38

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        # O efeito termina junto com o buraco negro, a partir do frame de início.
        return self.indice < self.frame_inicio_efeito + len(self.frames_bola)

    def desenhar(self, tela: pygame.Surface) -> None:
        indice_efeito = self.indice - self.frame_inicio_efeito

        if self.indice < self.duracao_mago:
            # Ainda conjurando: o Mago continua, mas o buraco negro já pode
            # estar aparecendo sobre o inimigo em paralelo.
            imagem = self.frames_mago[self.indice]
            centro = self.origem
            if self.frames_bola and indice_efeito >= 0:
                efeito = self.frames_bola[min(indice_efeito, len(self.frames_bola) - 1)]
                tela.blit(efeito, efeito.get_rect(center=(round(self.alvo.x), round(self.alvo.y))))
        else:
            # Conjuração terminou: segue somente o buraco negro no alvo.
            imagem = self.frames_bola[min(indice_efeito, len(self.frames_bola) - 1)]
            centro = self.alvo

        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoUltimateCezar:
    """Ultimate do Cezar: o personagem avança até perto do inimigo enquanto
    toca o gif completo. Sem efeito sobreposto no alvo."""

    def __init__(self, frames, personagem, origem, alvo, velocidade_animacao: float = 0.06):
        self.frames = frames
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.velocidade_animacao = velocidade_animacao
        self.indice = 0
        self.tempo = 0.0

        # O personagem NÃO atravessa o inimigo: ele para alguns pixels antes
        # do alvo (ponto de contato).
        distancia_parada = 55
        vetor = self.alvo - self.origem
        if vetor.length_squared() > 0 and vetor.length() > distancia_parada:
            self.ponto_contato = self.origem + vetor.normalize() * (vetor.length() - distancia_parada)
        else:
            self.ponto_contato = self.origem

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < len(self.frames)

    def desenhar(self, tela: pygame.Surface) -> None:
        progresso = self.indice / max(1, len(self.frames) - 1)
        # O personagem avança até o ponto de contato (perto do inimigo).
        centro = self.origem.lerp(self.ponto_contato, progresso)
        imagem = self.frames[min(self.indice, len(self.frames) - 1)]
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


def eh_rei_tritao(inimigo) -> bool:
    """Diz se o inimigo é o Rei Tritão, o boss do confronto especial."""
    return normalizar_nome(inimigo.nome.split(" Lv.")[0]) == "rei_tritao"


def resolver_sprite_inimigo(inimigo) -> Path | None:
    if eh_rei_tritao(inimigo):
        return REI_TRITAO_IDLE
    if inimigo.tipo == "Boss":
        return SPRITES_INIMIGOS["boss"]

    nome_sem_nivel = inimigo.nome.split(" Lv.")[0]
    return SPRITES_INIMIGOS.get(normalizar_nome(nome_sem_nivel))


def tamanho_com_escala(tamanho_base: tuple[int, int], personagem) -> tuple[int, int]:
    escala = max(0.01, float(getattr(personagem, "escala", 1.0)))
    return tuple(max(1, round(dimensao * escala)) for dimensao in tamanho_base)


def tamanho_corpo(personagem, tamanho_base: int = TAMANHO_CORPO_BASE) -> tuple[int, int]:
    """Tamanho do corpo do combatente, já contando a escala individual dele."""
    return tamanho_com_escala((tamanho_base, tamanho_base), personagem)


def mediana(valores: list[int]) -> int:
    ordenados = sorted(valores)
    return ordenados[len(ordenados) // 2]


def ajustar_quadros_ao_conteudo(quadros: list[pygame.Surface], tamanho: tuple[int, int]) -> list[pygame.Surface]:
    """Redimensiona os quadros para que o desenho visível ocupe a caixa `tamanho`.

    Cada arquivo de animação tem uma margem transparente maior ou menor, por isso
    a margem é descartada e a escala vem da altura do desenho visível: assim o
    personagem fica com o mesmo corpo em todas as animações dele, sem depender da
    largura da pose. O corte usa a união do conteúdo de todos os quadros, então
    nenhum frame é cortado e o movimento da animação é preservado.
    """
    altura_alvo = tamanho[1]
    limites = [quadro.get_bounding_rect() for quadro in quadros]
    visiveis = [limite for limite in limites if limite.width > 0 and limite.height > 0]
    if not visiveis:
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    x0 = min(limite.left for limite in visiveis)
    y0 = min(limite.top for limite in visiveis)
    largura = max(limite.right for limite in visiveis) - x0
    altura = max(limite.bottom for limite in visiveis) - y0
    escala = altura_alvo / mediana([limite.height for limite in visiveis])
    destino_tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))

    ajustados = []
    for quadro in quadros:
        destino = pygame.Surface(destino_tamanho, pygame.SRCALPHA)
        escalado = pygame.transform.smoothscale(
            quadro,
            (max(1, round(quadro.get_width() * escala)), max(1, round(quadro.get_height() * escala))),
        )
        recorte = pygame.Rect(round(x0 * escala), round(y0 * escala), *destino_tamanho).clip(escalado.get_rect())
        if recorte.width > 0 and recorte.height > 0:
            destino.blit(escalado.subsurface(recorte), (0, 0))
        ajustados.append(destino)
    return ajustados


def carregar_quadros_gif(caminho: Path) -> list[pygame.Surface]:
    """Lê todos os quadros de um gif, sem alterar o tamanho."""
    quadros = []
    with Image.open(caminho) as gif:
        for indice in range(getattr(gif, "n_frames", 1)):
            gif.seek(indice)
            dados = gif.convert("RGBA").tobytes()
            quadros.append(pygame.image.fromstring(dados, gif.size, "RGBA").convert_alpha())
    return quadros


class SpriteCombatente:
    """Representação visual animada de um combatente das regras de Combate.py."""

    def __init__(self, personagem, centro: tuple[int, int], caminho: Path | None, tamanho: tuple[int, int], caminho_ultimate: Path | None = None):
        self.personagem = personagem
        self.centro = centro
        self.centro_inicial = centro
        self.tamanho = tamanho
        self.frames_standard = self._carregar_frames(caminho)
        self.frames_ultimate = self._carregar_frames(caminho_ultimate) if caminho_ultimate else []
        self.frames: list[pygame.Surface] = self.frames_standard
        self.indice_frame = 0
        self.ultimo_frame = 0
        if self.frames_standard:
            self.imagem = self.frames_standard[0]
        elif self.frames_ultimate:
            self.frames = self.frames_ultimate
            self.imagem = self.frames_ultimate[0]
        else:
            self.imagem = self.placeholder()
        self.danos_flutuantes: list[FloatingDamage] = []  # Animações de dano

    def placeholder(self) -> pygame.Surface:
        imagem = pygame.Surface(self.tamanho, pygame.SRCALPHA)
        imagem.fill((100, 100, 110, 255))
        pygame.draw.rect(imagem, (230, 230, 230), imagem.get_rect(), 2)
        return imagem

    def _carregar_frames(self, caminho: Path | None) -> list[pygame.Surface]:
        """Carrega os frames de spritesheet em pasta, de um PNG único ou de um gif.

        O tamanho enviado é o corpo visível do personagem: a margem transparente
        do arquivo é descartada para que a mesma escala sirva para todas as
        animações dele."""
        try:
            if caminho is not None and caminho.is_file() and caminho.suffix.lower() == ".gif":
                return ajustar_quadros_ao_conteudo(carregar_quadros_gif(caminho), self.tamanho)

            if caminho is not None and caminho.is_dir():
                arquivos = sorted(caminho.glob("frame_*.png"))[:16]
                quadros = []
                for arquivo in arquivos:
                    try:
                        quadros.append(pygame.image.load(arquivo).convert_alpha())
                    except pygame.error:
                        continue
                return ajustar_quadros_ao_conteudo(quadros, self.tamanho)

            if caminho is not None and caminho.is_file():
                imagem = pygame.image.load(caminho).convert_alpha()
                return ajustar_quadros_ao_conteudo([imagem], self.tamanho)
        except (OSError, ValueError, pygame.error):
            pass
        return []

    def ultimate_pronta(self) -> bool:
        """A animação de ultimate só entra no ar quando a regra assim permite."""
        if not self.frames_ultimate:
            return False
        return regras.ultimate_disponivel(self.personagem)

    def atualizar(self) -> None:
        if self.ultimate_pronta():
            if self.frames_ultimate and self.frames is not self.frames_ultimate:
                self.frames = self.frames_ultimate
                self.indice_frame = 0
                self.ultimo_frame = 0
        elif self.frames_standard and self.frames is not self.frames_standard:
            self.frames = self.frames_standard
            self.indice_frame = 0
            self.ultimo_frame = 0

        if len(self.frames) < 2:
            return
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_frame >= 100:
            self.ultimo_frame = agora
            self.indice_frame = (self.indice_frame + 1) % len(self.frames)
            self.imagem = self.frames[self.indice_frame]

    def adicionar_dano_flutuante(self, dano: int) -> None:
        """Adiciona animação de dano flutuante acima do sprite."""
        self.danos_flutuantes.append(FloatingDamage(self.centro[0], self.centro[1] - self.imagem.get_height() // 2 - 10, dano))
    
    def desenhar_barra_hp(self, tela: pygame.Surface) -> None:
        """Desenha barra de HP, ATB e nome acima do inimigo."""
        # A barra acompanha o tamanho do desenho: inimigos pequenos mantêm a
        # posição de sempre, enquanto um boss grande tem a barra bem acima dele
        # (e mais larga, para caber o nome) em vez de sobre o próprio corpo.
        escala = max(1.0, min(1.5, float(getattr(self.personagem, "escala", 1.0))))
        largura_barra = int(120 * escala)
        altura_barra = 8
        x_barra = self.centro[0] - largura_barra // 2
        y_barra = min(
            self.centro[1] - 110,
            self.centro[1] - self.imagem.get_height() // 2 - 18,
        )
        
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

    # Pilar: Encapsulamento — a instância reúne o estado do combate (turno,
    # alvos e resultado) e os métodos que controlam as regras da batalha.
    def __init__(self, tela: pygame.Surface, herois: list, inimigos: list):
        self.tela = tela
        # Mantém referências aos modelos do combate; a interface consulta e
        # solicita alterações a esses objetos em vez de duplicar suas regras.
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
        self.entidades_atras: list[SpriteCombatente] = []
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
        caminho = DASHES.get(personagem.nome)
        if caminho is None:
            return []

        tamanho = tamanho_corpo(personagem, TAMANHO_DASH)
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_animacao_ataque(self, personagem) -> list[pygame.Surface]:
        caminho = ATAQUES_BASICOS.get(personagem.nome)
        if caminho is None:
            return []

        tamanho = tamanho_corpo(personagem, TAMANHO_ATAQUE)
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_animacao_ataque_inimigo(self, personagem) -> list[pygame.Surface]:
        caminho = ATAQUES_INIMIGOS.get(normalizar_nome(personagem.nome.split(" Lv.")[0]))
        if caminho is None:
            return []

        # O efeito de ataque acompanha o tamanho do combatente, mas com um teto:
        # um boss muito grande não deve gerar um golpe cobrindo a tela inteira.
        escala_ataque = min(1.35, float(getattr(personagem, "escala", 1.0)))
        tamanho = (int(250 * escala_ataque), int(250 * escala_ataque))
        return self.carregar_frames_pasta(caminho, tamanho, ajustar_ao_conteudo=False)

    def carregar_animacao_ultimate(self, personagem) -> list[pygame.Surface]:
        caminho = ULTIMATES.get(personagem.nome)
        if caminho is None:
            return []

        tamanho = tamanho_corpo(personagem, TAMANHO_ULTIMATE)
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_frames_gif(
        self,
        caminho: Path,
        tamanho: tuple[int, int],
        ajustar_ao_conteudo: bool = False,
    ) -> list[pygame.Surface]:
        try:
            quadros = carregar_quadros_gif(caminho)
        except (OSError, ValueError, pygame.error):
            return []
        if ajustar_ao_conteudo:
            return ajustar_quadros_ao_conteudo(quadros, tamanho)
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    def carregar_animacao_habilidade_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        frames_mago = self.carregar_frames_gif(
            ANIMACAO_MAGO_HABILIDADE,
            tamanho_corpo(personagem),
            ajustar_ao_conteudo=True,
        )
        frames_bola = self.carregar_frames_gif(BOLA_FOGO_MAGO, (96, 96))
        return frames_mago, frames_bola

    def carregar_animacao_habilidade_especial(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        """Habilidade especial (tecla 2): conjuração + projétil de cada herói.

        O Cezar conjura a magia (Cezar_Magia) e o projétil sai dela
        (Cezar_Projetil). Para os demais, usa a conjuração do Mago."""
        caminho = HABILIDADES_ESPECIAIS.get(personagem.nome)
        if caminho is None:
            return self.carregar_animacao_habilidade_mago(personagem)

        pasta_conjuracao, gif_projetil = caminho
        frames_conjuracao = self.carregar_frames_pasta(pasta_conjuracao, tamanho_corpo(personagem))
        frames_projetil = self.carregar_frames_gif(
            gif_projetil,
            tamanho_com_escala((TAMANHO_PROJETIL, TAMANHO_PROJETIL), personagem),
        )
        return frames_conjuracao, frames_projetil

    def carregar_animacao_segunda_habilidade(self, personagem) -> list[pygame.Surface]:
        """Segunda habilidade (tecla 3): animação própria do personagem."""
        caminho = SEGUNDAS_HABILIDADES.get(personagem.nome)
        if caminho is None:
            return []
        return self.carregar_frames_pasta(caminho, tamanho_corpo(personagem, TAMANHO_ATAQUE))

    def carregar_animacao_ultimate_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        tamanho_mago = tamanho_corpo(personagem, TAMANHO_ULTIMATE)
        frames_mago = self.carregar_frames_pasta(ULTIMATE_GUILHERME, tamanho_mago)
        frames_buraco_negro = self.carregar_frames_pasta(ULTIMATE_GUILHERME_ATAQUE, (300, 300), ajustar_ao_conteudo=False)
        return frames_mago, frames_buraco_negro

    def carregar_animacao_ultimate_cezar(self, personagem) -> list[pygame.Surface]:
        """Carrega a ultimate do Cezar com o personagem maior e o efeito menor.

        O gif mistura os dois no mesmo quadro: os frames do personagem são
        recortados na silhueta e ampliados, enquanto os frames do flash de
        efeito (conteúdo ocupando quase todo o quadro de 400x400) são
        renderizados menores."""
        tamanho_personagem = TAMANHO_ULTIMATE_CEZAR
        tamanho_efeito = TAMANHO_ULTIMATE_CEZAR_EFEITO
        largura_personagem, altura_personagem = tamanho_personagem
        frames = []
        try:
            with Image.open(ULTIMATE_CEZAR_GIF) as gif:
                for indice in range(getattr(gif, "n_frames", 1)):
                    gif.seek(indice)
                    quadro = gif.convert("RGBA")
                    bbox = quadro.getbbox()
                    if bbox is None:
                        continue
                    largura = bbox[2] - bbox[0]
                    altura = bbox[3] - bbox[1]
                    # Frame do flash de efeito: mantém o quadro inteiro menor.
                    if largura > 300 or altura > 300:
                        dados = quadro.tobytes()
                        imagem = pygame.image.fromstring(dados, quadro.size, "RGBA").convert_alpha()
                        frames.append(pygame.transform.smoothscale(imagem, tamanho_efeito))
                        continue
                    # Frame do personagem: corta o fundo ocioso e amplia.
                    recorte = quadro.crop(bbox)
                    dados = recorte.tobytes()
                    imagem = pygame.image.fromstring(dados, recorte.size, "RGBA").convert_alpha()
                    escala = min(
                        largura_personagem / max(1, largura),
                        altura_personagem / max(1, altura),
                    )
                    escalado = pygame.transform.smoothscale(
                        imagem,
                        (max(1, round(largura * escala)), max(1, round(altura * escala))),
                    )
                    quadro_final = pygame.Surface(tamanho_personagem, pygame.SRCALPHA)
                    quadro_final.blit(
                        escalado,
                        escalado.get_rect(center=(largura_personagem // 2, altura_personagem // 2)),
                    )
                    frames.append(quadro_final)
        except (OSError, ValueError, pygame.error):
            return []
        return frames

    def carregar_animacao_efeito_cezar(self) -> list[pygame.Surface]:
        """Concatena inicio/meio/meio2/fim.gif do efeito que aparece no inimigo."""
        frames = []
        for caminho in EFEITO_CEZAR:
            frames.extend(self.carregar_frames_gif(caminho, (300, 300)))
        return frames

    def carregar_frames_pasta(
        self,
        caminho: Path,
        tamanho: tuple[int, int],
        ajustar_ao_conteudo: bool = True,
    ) -> list[pygame.Surface]:
        """Carrega `frame_*.png` de uma pasta, no tamanho pedido.

        Por padrão o desenho visível é que ocupa a caixa `tamanho`; efeitos que
        devem manter o enquadramento original passam `ajustar_ao_conteudo=False`.
        """
        quadros = []
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                quadros.append(pygame.image.load(arquivo).convert_alpha())
            except pygame.error:
                continue
        if ajustar_ao_conteudo:
            return ajustar_quadros_ao_conteudo(quadros, tamanho)
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    def criar_sprites(self) -> None:
        posicoes_herois = [(220, 280), (170, 455), (390, 430)]
        posicoes_inimigos = [(1060, 270), (970, 445), (835, 360)]

        for indice, heroi in enumerate(self.herois[:3]):
            caminho, caminho_ultimate = ANIMACOES_HEROIS.get(heroi.nome, (None, None))
            tamanho = tamanho_corpo(heroi)
            sprite = SpriteCombatente(heroi, posicoes_herois[indice], caminho, tamanho, caminho_ultimate)
            self.sprites_herois.append(sprite)

            # Efeito que fica atrás do herói (Guilherme/entidade cósmica e
            # Cezar/serpente) enquanto a Ultimate dele estiver pronta.
            entidade = ENTIDADES_ATRAS.get(heroi.nome)
            if entidade is not None:
                caminho_entidade, tamanho_entidade, deslocamento = entidade
                self.entidades_atras.append(
                    SpriteCombatente(
                        heroi,
                        (posicoes_herois[indice][0] + deslocamento[0], posicoes_herois[indice][1] + deslocamento[1]),
                        caminho_entidade,
                        tamanho_corpo(heroi, tamanho_entidade),
                    )
                )

        for indice, inimigo in enumerate(self.inimigos[:3]):
            caminho = resolver_sprite_inimigo(inimigo)
            tamanho = tamanho_corpo(inimigo)
            # O Rei Tritão luta sozinho: em vez da coluna de inimigos, ele
            # entra no centro do campo, de frente para o grupo de heróis.
            posicao = POSICAO_BOSS_CENTRAL if eh_rei_tritao(inimigo) else posicoes_inimigos[indice]
            self.sprites_inimigos.append(SpriteCombatente(inimigo, posicao, caminho, tamanho))

    def iniciar_animacao_acao(
        self,
        acao: str,
        heroi,
        origem: tuple[int, int] | pygame.Vector2,
        sprite_heroi: SpriteCombatente | None,
        sprite_alvo: SpriteCombatente | None,
    ) -> None:
        """Cria a animação visual da ação, saindo de `origem` até o alvo.

        Concentra o deslocamento/troca de animação que acontece depois do dash
        (ou direto, quando o herói não possui dash) para ataque, habilidades
        especiais, segunda habilidade e ultimate."""
        if sprite_heroi is None or sprite_alvo is None:
            return

        if acao == "atacar":
            frames = self.carregar_animacao_ataque(heroi)
            if frames:
                self.animacao_ataque = AnimacaoAtaque(frames, heroi, origem, sprite_alvo.centro)
            return

        if acao == "habilidade_especial":
            frames_conjuracao, frames_projetil = self.carregar_animacao_habilidade_especial(heroi)
            if frames_conjuracao and frames_projetil:
                self.animacao_habilidade_mago = AnimacaoHabilidadeMago(
                    frames_conjuracao,
                    frames_projetil,
                    heroi,
                    origem,
                    sprite_alvo.centro,
                )
            return

        if acao == "segunda_habilidade":
            frames = self.carregar_animacao_segunda_habilidade(heroi)
            if frames:
                self.animacao_ataque = AnimacaoAtaque(frames, heroi, origem, sprite_alvo.centro)
            return

        if acao == "ultimate":
            if heroi.nome == "Guilherme":
                frames_mago, frames_buraco_negro = self.carregar_animacao_ultimate_mago(heroi)
                if frames_mago and frames_buraco_negro:
                    self.animacao_ultimate = AnimacaoUltimateMago(
                        frames_mago,
                        frames_buraco_negro,
                        heroi,
                        origem,
                        sprite_alvo.centro,
                    )
            elif heroi.nome == "Cezar":
                frames = self.carregar_animacao_ultimate_cezar(heroi)
                if frames:
                    self.animacao_ultimate = AnimacaoUltimateCezar(frames, heroi, origem, sprite_alvo.centro)
            else:
                frames = self.carregar_animacao_ultimate(heroi)
                if frames:
                    self.animacao_ultimate = AnimacaoUltimate(frames, heroi, origem, sprite_alvo.centro)

    def inimigos_vivos(self) -> list:
        return [inimigo for inimigo in self.inimigos if inimigo.estar_vivo()]

    def herois_vivos(self) -> list:
        return [heroi for heroi in self.herois if heroi.estar_vivo()]

    def verificar_resultado(self) -> None:
        # Vitória ocorre quando todos os inimigos foram derrotados. As
        # recompensas são aplicadas uma única vez para evitar duplicação.
        if not self.inimigos_vivos():
            if not self.recompensas_aplicadas:
                for inimigo in self.inimigos:
                    regras.dar_xp(inimigo, self.herois)
                    regras.verificar_drop_pocao(inimigo, self.herois)
                self.recompensas_aplicadas = True

            self.resultado = True
            self.mensagem = "Vitória! Pressione ENTER para retornar ao mapa."
            LOG_BATALHA.append("Vitória! O inimigo do mapa será removido.")

        # Derrota ocorre quando não resta nenhum herói vivo.
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

                    if posicao_final is not None:
                        self.iniciar_animacao_acao(
                            tipo,
                            heroi,
                            (int(posicao_final.x), int(posicao_final.y)),
                            sprite_heroi,
                            sprite_alvo,
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
                animacao_finalizada = self.animacao_habilidade_mago
                self.animacao_habilidade_mago = None
                # O Cezar avança no dash antes de conjurar; ao terminar, ele
                # volta para a posição inicial do campo de batalha.
                self.restaurar_posicao_inicial_heroi(animacao_finalizada.personagem)
        
        if self.resultado is not None or self.heroi_ativo is not None:
            return

        # Enquanto qualquer animação estiver em andamento, o ATB fica pausado
        # para que os inimigos não ataquem antes de a animação e o efeito terminarem.
        animacoes_ativas = (
            self.animacao_dash is not None
            or self.animacao_ataque is not None
            or self.animacao_ultimate is not None
            or self.animacao_habilidade_mago is not None
            or self.animacao_ataque_inimigo is not None
        )
        if animacoes_ativas:
            return

        # Cada modelo Personagem avança sua própria ATB; Heroi e Inimigo
        # compartilham esse comportamento herdado da classe base.
        for combatente in self.herois + self.inimigos:
            combatente.carregar_atb(tempo_frame * 3.0)

        # Escolhe o primeiro combatente vivo que alcançou o limite da barra.
        pronto = next(
            (
                combatente for combatente in self.herois + self.inimigos
                if combatente.estar_vivo() and combatente.atb_barra >= combatente.atb_max
            ),
            None,
        )
        if pronto is None:
            return

        # O tipo do modelo define se o turno aguarda comando do jogador ou se
        # é resolvido automaticamente como turno de inimigo.
        if isinstance(pronto, regras.Heroi):
            self.heroi_ativo = pronto
            self.mensagem = f"Turno de {pronto.nome}. Use as teclas 1 a 6."
            LOG_BATALHA.append(f"Turno de {pronto.nome}.")
            return

        # Inimigos só podem escolher entre heróis que ainda estão vivos.
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

        # Delega o ataque ao modelo do inimigo, que aplica as regras de dano.
        pronto.atacar(alvo)
        # Reinicia a ATB após a ação para começar o próximo ciclo do combatente.
        pronto.resetar_atb()
        self.mensagem = f"{pronto.nome} atacou {alvo.nome}."

        # Mostra dano flutuante para o alvo (se for inimigo)
        if sprite_alvo and hasattr(alvo, '_ultimo_dano_recebido'):
            sprite_alvo.adicionar_dano_flutuante(int(alvo._ultimo_dano_recebido))

        self.verificar_resultado()

    def escolher_acao(self, numero: int) -> None:
        # Sem um herói no turno, uma tecla não pode iniciar uma ação de combate.
        if self.heroi_ativo is None:
            return

        # Traduz a tecla em uma operação do modelo; os custos e efeitos
        # continuam sendo validados pelos métodos do herói.
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
        # Somente o herói cujo ATB liberou o turno pode executar a ação.
        if self.heroi_ativo is None:
            return

        executou = False
        if acao == "defender":
            # Defender altera atributos e contador pertencentes a este herói.
            # Pilar: Encapsulamento — o estado do personagem fica no objeto.
            self.heroi_ativo.defesa += 5
            self.heroi_ativo.acoes_realizadas += 1
            LOG_BATALHA.append(f"{self.heroi_ativo.nome} se prepara para defender (+5 DEF).")
            executou = True
        elif acao == "usar_pocao_pa":
            # A regra de estoque e recuperação é delegada ao método do herói.
            executou = self.heroi_ativo.usar_pocao_pa()
        else:
            # Ataques precisam de um alvo vivo; o modelo recebe a ação e aplica
            # a implementação correspondente ao método solicitado.
            vivos = self.inimigos_vivos()
            if vivos:
                alvo = vivos[self.indice_alvo % len(vivos)]
                # Pilar: Polimorfismo — a ação é enviada ao objeto Heroi ativo
                # pelo nome do método, que executa seu comportamento específico.
                executou = getattr(self.heroi_ativo, acao)(alvo)
                
                # Mostra dano flutuante após ataque
                if executou and acao in {"atacar", "habilidade_especial", "segunda_habilidade", "ultimate"}:
                    if hasattr(alvo, '_ultimo_dano_recebido'):
                        sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)
                        if sprite_alvo:
                            sprite_alvo.adicionar_dano_flutuante(int(alvo._ultimo_dano_recebido))

                    sprite_heroi = next((s for s in self.sprites_herois if s.personagem is self.heroi_ativo), None)
                    sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)

                    # A habilidade especial do Cezar é conjurada parado no
                    # lugar (sem dash): ele saca a pistola na magia e o projétil
                    # sai dela. Os demais ataques continuam usando o dash.
                    usar_dash = acao != "habilidade_especial"
                    dash_frames = self.carregar_animacao_dash(self.heroi_ativo) if usar_dash else []
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
                    else:
                        self.iniciar_animacao_acao(
                            acao,
                            self.heroi_ativo,
                            sprite_heroi.centro,
                            sprite_heroi,
                            sprite_alvo,
                        )

        if not executou:
            # Uma ação recusada pelo modelo não consome o turno; o jogador pode
            # escolher outra sem perder a barra ATB.
            self.acao_pendente = None
            self.mensagem = "Ação indisponível. Escolha outra opção."
            return

        self.verificar_resultado()
        if self.resultado is None:
            # A ação válida consome o turno e reinicia a ATB desse herói.
            self.heroi_ativo.resetar_atb()
            self.heroi_ativo = None
            self.acao_pendente = None
            self.mensagem = "Aguardando a próxima barra ATB ficar cheia."

    def processar_evento(self, evento: pygame.event.Event) -> None:
        # Apenas teclas pressionadas participam do menu de ações por turno.
        if evento.type != pygame.KEYDOWN:
            return

        if self.resultado is not None:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.concluida = True
            return

        if self.heroi_ativo is None:
            return

        if self.acao_pendente is not None:
            # A troca de alvo percorre somente inimigos vivos; ENTER confirma
            # e ESC cancela sem executar a ação.
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

        # As entidades (cósmica do mago e serpente do Cezar) ficam atrás dos
        # heróis enquanto a Ultimate do dono estiver pronta.
        for entidade in self.entidades_atras:
            if regras.ultimate_disponivel(entidade.personagem):
                if entidade.personagem not in personagens_em_animacao:
                    entidade.desenhar(self.tela)

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


def criar_batalha(tela: pygame.Surface, herois: list, quantidade_inimigos: int = 3, rei_tritao: bool = False) -> BattleUI:
    """Cria a batalha comum ou o confronto especial contra o Rei Tritão."""
    nivel_grupo = max(heroi.level for heroi in herois)
    if rei_tritao:
        inimigos = [regras.criar_rei_tritao(nivel_grupo)]
    else:
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
