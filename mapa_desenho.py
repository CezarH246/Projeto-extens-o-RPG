"""Desenho do mapa: fundo, personagens, avisos e depuracao de colisoes.

A ordem de desenho e o segredo da sensacao de profundidade: quem tem os pes
mais abaixo na tela e desenhado por ultimo, ficando "na frente". No covil, as
estatuas (oclusores) entram nessa mesma fila, o que permite esconder o heroi
quando ele passa atras delas.
"""

from __future__ import annotations

# math fornece seno e cosseno usados nas animacoes de brilho.
import math

# pygame desenha as superficies, textos e formas.
import pygame

# covil_tritao guarda os poligonos de chao e as posicoes do bau.
import covil_tritao

# config contem a cena atual e a passagem secreta.
import mapa_config as config

# Funcoes de geometria reaproveitadas do modulo de colisao.
from mapa_colisao import (
    altura_dos_pes,
    desenhar_mapa_provisorio,
    personagem_atras_de_oclusor,
    retangulo_colisao,
)


class DesenhoMixin:
    """Metodos de desenho usados pela classe Jogo (heranca por mixin)."""

    def desenhar_aviso_bau(self) -> None:
        'Balão "[E] Abrir o baú" pulsando acima do baú quando dá para abrir.'
        # So desenha no modo mapa e quando o jogador esta perto do bau.
        if self.modo != "mapa" or not self.pode_abrir_bau():
            return

        # Renderiza o texto em amarelo claro.
        texto = self.fonte.render('[E] Abrir o baú', True, (255, 235, 160))

        # Caixa um pouco maior que o texto.
        caixa = texto.get_rect().inflate(16, 10)

        # Flutuacao suave usando o tempo atual do pygame.
        flutuar = math.sin(pygame.time.get_ticks() / 250) * 3

        # Posiciona a caixa acima do bau, com a flutuacao aplicada.
        caixa.midbottom = (
            covil_tritao.POSICAO_BAU[0],
            covil_tritao.POSICAO_BAU[1] - 52 + flutuar,
        )

        # Fundo escuro e borda dourada.
        pygame.draw.rect(self.tela, (20, 14, 6), caixa, border_radius=6)
        pygame.draw.rect(self.tela, (222, 181, 83), caixa, 2, border_radius=6)

        # Texto centralizado na caixa.
        self.tela.blit(texto, texto.get_rect(center=caixa.center))

    def desenhar_passagem(self) -> None:
        'Redemoinho de água brilhante que marca a passagem para o covil.'
        # Tempo em segundos para animar os aneis.
        tempo = pygame.time.get_ticks() / 1000

        # Superficie transparente um pouco maior que a passagem.
        tamanho_camada = config.PASSAGEM_COVIL.inflate(40, 40).size
        camada = pygame.Surface(tamanho_camada, pygame.SRCALPHA)

        # Centro da superficie para desenhar os circulos.
        centro = (camada.get_width() // 2, camada.get_height() // 2)

        # Cinco aneis com fases diferentes, criando a sensacao de redemoinho.
        for anel in range(5):
            fase = (tempo * 1.5 + anel / 5) % 1.0
            raio = int(8 + fase * 32)
            alfa = int(220 * (1 - fase))
            pygame.draw.circle(camada, (90, 210, 255, alfa), centro, raio, 3)

        # Nucleo brilhante que pulsa levemente.
        pygame.draw.circle(
            camada,
            (200, 245, 255, 200),
            centro,
            8 + int(math.sin(tempo * 4) * 2),
        )

        # Desenha a camada centralizada na passagem.
        self.tela.blit(camada, camada.get_rect(center=config.PASSAGEM_COVIL.center))

    def desenhar_caverna_liberada(self) -> None:
        'Brilho dourado na caverna que leva à arena do Rei Tritão.'
        # Tempo em segundos para animar os aneis.
        tempo = pygame.time.get_ticks() / 1000

        # Superficie transparente um pouco maior que a caverna.
        tamanho_camada = covil_tritao.CAVERNA_BOSS.inflate(60, 60).size
        camada = pygame.Surface(tamanho_camada, pygame.SRCALPHA)
        centro = (camada.get_width() // 2, camada.get_height() // 2)

        # Quatro aneis que sobem e desaparecem, como uma respiracao de luz.
        for anel in range(4):
            fase = (tempo * 0.8 + anel / 4) % 1.0
            raio = int(16 + fase * 44)
            alfa = int(200 * (1 - fase))
            pygame.draw.circle(camada, (255, 222, 110, alfa), centro, raio, 3)

        # Nucleo pulsante e Brilho fixo no centro.
        pygame.draw.circle(camada, (255, 246, 200, 220), centro, 12 + int(math.sin(tempo * 3) * 3))
        pygame.draw.circle(camada, (255, 210, 80, 90), centro, 34, 6)

        # Desenha a camada centralizada na caverna.
        self.tela.blit(camada, camada.get_rect(center=covil_tritao.CAVERNA_BOSS.center))

        # Aviso flutuante para deixar clara a nova passagem.
        aviso = self.fonte_auxiliar.render('[Avançar] Entrar na caverna', True, (255, 240, 180))
        caixa = aviso.get_rect(
            midbottom=(covil_tritao.CAVERNA_BOSS.centerx, covil_tritao.CAVERNA_BOSS.top - 8)
        )
        fundo = caixa.inflate(12, 6)
        pygame.draw.rect(self.tela, (20, 14, 6), fundo, border_radius=5)
        pygame.draw.rect(self.tela, (222, 181, 83), fundo, 2, border_radius=5)
        self.tela.blit(aviso, caixa)

    def desenhar_mapa(self) -> None:
        """Desenha o fundo, os objetos por profundidade e as sobreposicoes."""
        # No covil (e na arena do chefe), usa os quadros animados; no mapa
        # antigo, a imagem fixa.
        if self.cena in ("covil", "covil_boss") and self.mapa_animado is not None:
            self.tela.blit(self.mapa_animado.imagem, (0, 0))
        elif self.mapa_imagem is None:
            # Sem imagem carregada, desenha o cenario provisorio.
            desenhar_mapa_provisorio(self.tela)
        else:
            self.tela.blit(self.mapa_imagem, (0, 0))

        # Desenha o redemoinho da passagem quando ela esta aberta.
        if self.passagem_aberta and self.cena == "mapateste":
            self.desenhar_passagem()

        # No covil, a caverna brilha depois que os quatro guardas caem.
        if self.cena == "covil" and self.caverna_liberada:
            self.desenhar_caverna_liberada()

        # Quem tem os pes mais abaixo e desenhado por cima (fica "na frente").
        # No covil, as estatuas ("oclusores") entram nessa ordem pela base: quem
        # passa atras delas fica escondido.
        camadas = [
            (objeto.rect.top + altura_dos_pes(objeto), objeto)
            for objeto in self.grupo_objetos
        ]
        if self.cena == "covil" and self.mapa_animado is not None:
            camadas += [(oclusor.base, oclusor) for oclusor in self.oclusores]

        # Ordena pela coordenada vertical da base e desenha do fundo para a frente.
        for _, item in sorted(camadas, key=lambda camada: camada[0]):
            # Oclusor tem desenho proprio (recorta a parte do mapa que fica na frente).
            if isinstance(item, covil_tritao.Oclusor):
                item.desenhar(self.tela, self.mapa_animado.imagem)
                continue

            # Personagem/inimigo: usa a imagem atual do sprite.
            imagem = item.image

            # Se estiver atras de um oclusor, aplica transparencia.
            if personagem_atras_de_oclusor(item):
                imagem = item.image.copy()
                imagem.set_alpha(145)

            # Desenha o sprite na posicao do seu rect.
            self.tela.blit(imagem, item.rect)

        # Mostra o aviso do bau, se aplicavel.
        self.desenhar_aviso_bau()

        # Caixa com a mensagem de status no canto superior esquerdo.
        texto = self.fonte.render(self.mensagem, True, (240, 240, 245))
        caixa = pygame.Rect(7, 7, texto.get_width() + 16, 30)
        pygame.draw.rect(self.tela, (5, 17, 34), caixa, border_radius=5)
        self.tela.blit(texto, (14, 13))

        # Modo de depuracao: desenha chao, bloqueios, oclusores e pes.
        if self.mostrar_colisoes:
            if self.cena == "covil":
                extra = covil_tritao.CHAO_POSBOSS if self.rei_tritao_derrotado else []
                for poligono in covil_tritao.CHAO + extra:
                    pygame.draw.polygon(self.tela, (0, 255, 120), poligono, 2)
                for oclusor in self.oclusores:
                    pygame.draw.polygon(self.tela, (200, 110, 255), oclusor.poligono, 2)

            for obstaculo in config.CENA["bloqueios"]:
                pygame.draw.rect(self.tela, (255, 120, 0), obstaculo, 2)

            for objeto in self.grupo_objetos:
                pygame.draw.rect(self.tela, (255, 0, 255), retangulo_colisao(objeto), 1)

            # Legenda das cores.
            aviso = self.fonte_auxiliar.render(
                'Colisões: verde = chão; laranja = bloqueio; roxo = passar por trás; rosa = pés',
                True,
                (255, 225, 110),
            )
            self.tela.blit(aviso, (10, 43))

        # Fade de entrada ao chegar numa cena nova.
        if self.escurecimento > 0:
            veu = pygame.Surface(self.tela.get_size())
            veu.set_alpha(int(255 * self.escurecimento))
            self.tela.blit(veu, (0, 0))
