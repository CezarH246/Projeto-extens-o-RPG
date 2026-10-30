"""Visual representation of heroes and enemies in the arena."""

import pygame
import Combate as regras

from .animacoes import FloatingDamage
from .helpers import ajustar_quadros_ao_conteudo, carregar_quadros_gif, cor_barra_hp

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
