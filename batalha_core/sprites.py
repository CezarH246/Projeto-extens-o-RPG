"""Visual representation of heroes and enemies in the arena."""

from pathlib import Path

import pygame
import Combate as regras

from .animacoes import FloatingDamage
from .helpers import ajustar_quadros_ao_conteudo, carregar_quadros_gif, cor_barra_hp, criar_fonte, texto_com_sombra

# Quadros já carregados, por (arquivo/pasta, tamanho): cada batalha nova recria
# os sprites, mas os quadros são só lidos (o desenho usa cópias), então dá para
# reaproveitá-los em vez de reler dezenas de PNGs do disco a cada encontro.
_FRAMES_CARREGADOS: dict[tuple[Path, tuple[int, int]], list[pygame.Surface]] = {}


class SpriteCombatente:
    """Representação visual animada de um combatente das regras de Combate.py."""

    _fonte_nome: pygame.font.Font | None = None
    _fonte_numero: pygame.font.Font | None = None

    @staticmethod
    def _garantir_fontes() -> None:
        """Cria as fontes uma única vez, depois do pygame iniciado."""
        if SpriteCombatente._fonte_nome is None:
            SpriteCombatente._fonte_nome = criar_fonte(16, negrito=True)
            SpriteCombatente._fonte_numero = criar_fonte(14, negrito=True)

    # Vida mostrada na tela enquanto um golpe ainda está sendo animado.
    # None = mostra a vida real do personagem.
    hp_exibido: int | None = None

    def hp_visivel(self) -> int:
        return self.personagem.hp if self.hp_exibido is None else self.hp_exibido

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
        if caminho is None:
            return []
        chave = (caminho, tuple(self.tamanho))
        if chave not in _FRAMES_CARREGADOS:
            _FRAMES_CARREGADOS[chave] = self._ler_frames(caminho)
        return list(_FRAMES_CARREGADOS[chave])

    def _ler_frames(self, caminho: Path | None) -> list[pygame.Surface]:
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
        # O número nasce no corpo do alvo e sobe; assim não cobre a barra e o HP dele.
        self.danos_flutuantes.append(FloatingDamage(self.centro[0], self.centro[1] - self.imagem.get_height() // 4, dano))
    
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
        proporcao_hp = max(0.0, min(1.0, self.hp_visivel() / self.personagem.hpMax)) if self.personagem.hpMax > 0 else 0
        preenchimento_hp = int(largura_barra * proporcao_hp)
        if preenchimento_hp > 0:
            pygame.draw.rect(
                tela,
                cor_barra_hp(self.hp_visivel(), self.personagem.hpMax),
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
        self._garantir_fontes()
        # Nome centralizado, mas sem sair pela borda da tela no inimigo da ponta.
        meia_largura = SpriteCombatente._fonte_nome.size(self.personagem.nome[:40])[0] // 2
        x_nome = max(meia_largura + 6, min(tela.get_width() - meia_largura - 6, self.centro[0]))
        texto_com_sombra(
            tela, SpriteCombatente._fonte_nome, self.personagem.nome[:40],
            (255, 255, 255), (x_nome, y_barra - 12), centralizado=True,
        )
        texto_com_sombra(
            tela, SpriteCombatente._fonte_numero, f"{self.hp_visivel()}/{self.personagem.hpMax}",
            (235, 238, 245), (self.centro[0], y_atb + altura_barra + 10), centralizado=True,
        )

    def topo_painel_heroi(self) -> int:
        """Y do topo do painel de status que flutua acima da cabeça do herói."""
        # Usa o primeiro frame do idle para a altura, assim o painel não balança
        # junto com a animação e permanece no lugar durante dashes e ataques.
        altura = self.frames_standard[0].get_height() if self.frames_standard else self.tamanho[1]
        return self.centro_inicial[1] - altura // 2 - 76

    def desenhar_painel_heroi(self, tela: pygame.Surface, ativo: bool = False) -> None:
        """Nome, HP, PA e ATB do herói, acima da cabeça dele."""
        self._garantir_fontes()
        heroi = self.personagem
        largura = 196
        altura_barra = 9
        x = self.centro_inicial[0] - largura // 2
        y = self.topo_painel_heroi()

        fundo = pygame.Surface((largura + 16, 72), pygame.SRCALPHA)
        pygame.draw.rect(fundo, (8, 14, 40, 195), fundo.get_rect(), border_radius=8)
        pygame.draw.rect(fundo, (222, 181, 83, 255) if ativo else (90, 100, 140, 255), fundo.get_rect(), 2, border_radius=8)
        tela.blit(fundo, (x - 8, y - 4))

        cor_nome = (255, 226, 92) if ativo else (255, 255, 255)
        texto_com_sombra(tela, SpriteCombatente._fonte_nome, f"{heroi.nome}  Nv.{heroi.level}", cor_nome, (x, y - 1))
        numero = f"{self.hp_visivel()}/{heroi.hpMax}"
        largura_numero = SpriteCombatente._fonte_numero.size(numero)[0]
        texto_com_sombra(
            tela, SpriteCombatente._fonte_numero, numero, (235, 238, 245), (x + largura - largura_numero, y + 1),
        )

        barras = [
            (self.hp_visivel(), heroi.hpMax, cor_barra_hp(self.hp_visivel(), heroi.hpMax)),
            (heroi.PA, heroi.PAMax, (239, 191, 53)),
            (heroi.atb_barra, heroi.atb_max, (70, 145, 245)),
        ]
        for indice, (valor, maximo, cor) in enumerate(barras):
            y_barra = y + 24 + indice * 14
            pygame.draw.rect(tela, (25, 27, 39), (x, y_barra, largura, altura_barra), border_radius=3)
            proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
            if int(largura * proporcao) > 0:
                pygame.draw.rect(tela, cor, (x, y_barra, int(largura * proporcao), altura_barra), border_radius=3)
            pygame.draw.rect(tela, (238, 238, 242), (x, y_barra, largura, altura_barra), 1, border_radius=3)

    def retrato(self, tamanho: int) -> pygame.Surface:
        """Rosto do personagem (parte de cima do corpo), quadrado, para ícones.

        Usa o primeiro frame do idle e guarda o resultado para não recortar de novo."""
        cache = self.__dict__.setdefault("_retratos", {})
        if tamanho not in cache:
            base = self.frames_standard[0] if self.frames_standard else self.imagem
            corpo = base.get_bounding_rect()
            lado = max(1, min(corpo.width, int(corpo.height * 0.55)))
            recorte = pygame.Rect(0, 0, lado, lado)
            recorte.midtop = (corpo.centerx, corpo.top)
            recorte = recorte.clip(base.get_rect())
            cache[tamanho] = pygame.transform.smoothscale(base.subsurface(recorte), (tamanho, tamanho))
        return cache[tamanho]

    def desenhar(
        self,
        tela: pygame.Surface,
        selecionado: bool = False,
        fonte_dano: pygame.font.Font | None = None,
        mostrar_barra: bool = True,
        cor_selecao: tuple[int, int, int] = (255, 226, 92),
    ) -> None:
        self.atualizar()
        imagem = self.imagem.copy()
        if self.hp_visivel() <= 0:
            imagem.set_alpha(85)

        rect = imagem.get_rect(center=self.centro)
        tela.blit(imagem, rect)
        
        # Inimigos desenham a própria barra aqui; a dos heróis é desenhada à
        # parte (desenhar_painel_heroi), pois eles somem durante as animações.
        if mostrar_barra and not isinstance(self.personagem, regras.Heroi):
            self.desenhar_barra_hp(tela)

        if selecionado:
            pygame.draw.rect(tela, cor_selecao, rect.inflate(10, 10), 4, border_radius=8)
