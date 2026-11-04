"""Criacao, escala e posicionamento da janela do jogo.

O jogo sempre desenha em uma "tela logica" de tamanho fixo (720x480 no mapa e
1280x720 na batalha). Isso mantem todas as coordenadas previsiveis. Esta classe
mixin cuida apenas de transformar essa tela logica no tamanho real da janela,
sem mexer nas regras do mapa.
"""

from __future__ import annotations

# warnings silencia o aviso de API antiga ao obter a janela do pygame.
import warnings

# pygame cria a janela, mede o monitor e faz a escala das superficies.
import pygame

# area_util_da_tela ja desconta a barra de tarefas do sistema.
from mapa_config import area_util_da_tela


class JanelaMixin:
    """Metodos de janela usados pela classe Jogo (heranca por mixin)."""

    # Espaco que o sistema usa em volta da janela: barra de titulo e bordas.
    ALTURA_BARRA_TITULO = 32
    MARGEM_BORDAS = 8

    # Ate ~1600x900 a escala suave cabe nos 60 FPS; acima disso usa a rapida.
    LIMITE_ESCALA_SUAVE = 1_300_000

    def criar_janela(self, tamanho_logico: tuple[int, int]) -> pygame.Surface:
        """Abre a janela e devolve a "tela logica" em que o jogo desenha.

        O jogo sempre desenha em resolucao fixa (720x480 no mapa, 1280x720 na
        batalha), entao nenhuma coordenada muda. A cada frame, `apresentar`
        escala essa tela para o tamanho real da janela ou do monitor."""
        # Em tela cheia, "0, 0" pede ao pygame a resolucao do monitor.
        if self.tela_cheia:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Em janela, calcula o maior tamanho proporcional que cabe na tela.
            pygame.display.set_mode(
                self.tamanho_ideal_da_janela(tamanho_logico),
                pygame.RESIZABLE,
            )

            # Centraliza a janela na area util do monitor.
            self.centralizar_janela()

        # Cria a superficie logica e a converte para o formato da tela.
        return pygame.Surface(tamanho_logico).convert()

    def tamanho_ideal_da_janela(self, tamanho_logico: tuple[int, int]) -> tuple[int, int]:
        """O maior tamanho que cabe na tela sem distorcer a imagem.

        Num notebook 1366x768 a batalha encolhe para caber acima da barra de
        tarefas; num monitor Full HD ou 4K o jogo cresce."""
        # Descobre a area livre do monitor.
        area = area_util_da_tela()

        # Desconta as bordas laterais e a barra de titulo.
        largura_livre = area.width - 2 * self.MARGEM_BORDAS
        altura_livre = area.height - self.ALTURA_BARRA_TITULO - self.MARGEM_BORDAS

        # Usa a menor escala entre largura e altura para nao distorcer.
        escala = min(largura_livre / tamanho_logico[0], altura_livre / tamanho_logico[1])

        # Nunca deixa a janela com menos de 1 pixel.
        return max(1, round(tamanho_logico[0] * escala)), max(1, round(tamanho_logico[1] * escala))

    def centralizar_janela(self) -> None:
        """Posiciona a janela no centro da area util do monitor."""
        try:
            # A API Window e recente; o filtro evita avisos de depreciacao.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                janela = pygame.Window.from_display_module()

            # Area disponivel e tamanho real da janela.
            area = area_util_da_tela()
            largura, altura = janela.size

            # Altura livre abaixo da barra de titulo.
            altura_livre = area.height - self.ALTURA_BARRA_TITULO - self.MARGEM_BORDAS

            # A posicao e a da area de desenho; a barra de titulo fica logo acima.
            x = area.x + (area.width - largura) // 2
            y = area.y + self.ALTURA_BARRA_TITULO + max(0, (altura_livre - altura) // 2)
            janela.position = (x, y)
        except (AttributeError, pygame.error, IndexError):
            # Sem a API de janela, o sistema decide a posicao.
            pass

    def apresentar(self) -> None:
        'Escala a tela lógica para a janela real, com faixas pretas se a proporção diferir.'
        # Superficie real da janela e tamanho logico do jogo.
        janela = pygame.display.get_surface()
        largura_janela, altura_janela = janela.get_size()
        largura, altura = self.tela.get_size()

        # Calcula a escala que faz a tela caber inteira na janela.
        escala = min(largura_janela / largura, altura_janela / altura)

        # Tamanho final da imagem depois da escala.
        destino = (max(1, round(largura * escala)), max(1, round(altura * escala)))

        # Se o tamanho ja coincide, nao precisa copiar a imagem.
        if destino == (largura, altura):
            imagem = self.tela
        elif destino[0] * destino[1] <= self.LIMITE_ESCALA_SUAVE:
            # Escala suave: texto e linhas finas sem serrilhado em escalas quebradas.
            imagem = pygame.transform.smoothscale(self.tela, destino)
        else:
            # Telas grandes: vizinho mais proximo, bem mais barato e nitido para pixel art.
            imagem = pygame.transform.scale(self.tela, destino)

        # As faixas pretas so precisam ser pintadas quando o tamanho muda.
        if getattr(self, "_tamanho_apresentado", None) != (janela.get_size(), destino):
            janela.fill((0, 0, 0))
            self._tamanho_apresentado = (janela.get_size(), destino)

        # Desenha a imagem centralizada, deixando faixas pretas nas sobras.
        janela.blit(imagem, imagem.get_rect(center=(largura_janela // 2, altura_janela // 2)))

        # Mostra o resultado no monitor.
        pygame.display.flip()

    def alternar_tela_cheia(self) -> None:
        """Troca entre janela e tela cheia sem perder o estado do jogo."""
        # Inverte a flag e recria a janela com o mesmo tamanho logico.
        self.tela_cheia = not self.tela_cheia
        self.tela = self.criar_janela(self.tela.get_size())

        # A batalha e o editor guardam a superficie da tela; atualiza os dois.
        if self.batalha is not None:
            self.batalha.tela = self.tela
        if self.editor is not None:
            self.editor.tela = self.tela

    def mouse_na_tela(self, posicao: tuple[int, int]) -> tuple[int, int]:
        'Posição do mouse na janela -> posição na tela lógica (veja `apresentar`).'
        # Tamanho da janela real e da tela logica.
        largura_janela, altura_janela = pygame.display.get_surface().get_size()
        largura, altura = self.tela.get_size()

        # A mesma escala usada em apresentar().
        escala = min(largura_janela / largura, altura_janela / altura)

        # Origem das faixas pretas (offset horizontal e vertical).
        x0 = (largura_janela - largura * escala) / 2
        y0 = (altura_janela - altura * escala) / 2

        # Converte para coordenadas da tela logica.
        return round((posicao[0] - x0) / escala), round((posicao[1] - y0) / escala)
