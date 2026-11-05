"""Desenho da interface do editor de colisao.

Esta classe mixin apenas le o estado (self.dados, self.camada, self.botoes...)
e pinta a tela. Separar o desenho da interacao evita que a classe Editor vire
um arquivo enorme e facilita achar cada responsabilidade.
"""

from __future__ import annotations

# pygame desenha superficies, poligonos, linhas, textos e botoes.
import pygame

# covil_tritao fornece tamanho e tipo Oclusor.
import covil_tritao

# config guarda a referencia ao mapa_teste usada no modo de teste.
import ferramentas.editor_config as config
from ferramentas.editor_config import (
    ALTURA,
    ALTURA_BARRA,
    ALTURA_EXPLICACAO,
    ALTURA_RODAPE,
    CAMADAS,
    COR_DESTAQUE,
    COR_PAINEL,
    COR_TEXTO,
    LARGURA,
    cantos,
)


class DesenhoMixin:
    """Todos os metodos que pintam o editor."""

    def desenhar_contornos(self, chave: str, ativa: bool) -> None:
        """Desenha os poligonos de uma camada de contorno."""
        # Cor da camada vem da configuracao.
        _, cor, _, _ = CAMADAS[chave]

        # Superficie transparente para o preenchimento semitransparente.
        preenchimento = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)

        for i, poligono in enumerate(self.dados[chave]):
            selecionado = ativa and i == self.selecionado

            # Preenchimento (mais forte na camada ativa).
            if len(poligono) >= 3 and self.preencher:
                pygame.draw.polygon(
                    preenchimento,
                    (*cor, 70 if ativa else 28),
                    poligono,
                )

            # Linhas do contorno: amarelo quando selecionado.
            if len(poligono) >= 2:
                pygame.draw.lines(
                    self.tela,
                    COR_DESTAQUE if selecionado else cor,
                    len(poligono) >= 3,
                    poligono,
                    3 if selecionado else 2,
                )

            # Oclusores mostram a linha de base (quem passa atras fica escondido).
            if chave == "oclusores" and len(poligono) >= 3:
                self.desenhar_base(poligono)

            # Pontos de edicao so aparecem na camada ativa.
            if ativa:
                for j, ponto in enumerate(poligono):
                    raio = 6 if selecionado and j == len(poligono) - 1 else 4
                    pygame.draw.circle(self.tela, (0, 0, 0), ponto, raio + 1)
                    pygame.draw.circle(
                        self.tela,
                        COR_DESTAQUE if selecionado else (255, 255, 255),
                        ponto,
                        raio,
                    )

        # Aplica o preenchimento por cima do fundo.
        self.tela.blit(preenchimento, (0, 0))

    def desenhar_base(self, poligono) -> None:
        'Linha tracejada da base: pés acima dela = atrás do objeto.'
        # Coordenadas X de todos os pontos e a maior coordenada Y (a base).
        xs = [x for x, _ in poligono]
        base = max(y for _, y in poligono)

        # Desenha tracejado em intervalos de 10 pixels.
        for x in range(min(xs), max(xs), 10):
            pygame.draw.line(
                self.tela,
                COR_DESTAQUE,
                (x, base),
                (min(x + 5, max(xs)), base),
                2,
            )

        # Rotulo "base" ao lado da linha.
        rotulo = self.fonte_dica.render("base", True, COR_DESTAQUE)
        self.tela.blit(
            rotulo,
            (max(xs) + 4, base - rotulo.get_height() // 2),
        )

    def desenhar_bloqueios(self, ativa: bool) -> None:
        """Desenha os retangulos da camada de bloqueios."""
        # Cor e preenchimento proprio dos bloqueios.
        _, cor, _, _ = CAMADAS["bloqueios"]
        preenchimento = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)

        for i, retangulo in enumerate(self.dados["bloqueios"]):
            r = pygame.Rect(retangulo)

            # Preenchimento semitransparente.
            if self.preencher:
                pygame.draw.rect(
                    preenchimento,
                    (*cor, 80 if ativa else 30),
                    r,
                )

            # Borda amarela se selecionado.
            selecionado = ativa and i == self.selecionado
            pygame.draw.rect(
                self.tela,
                COR_DESTAQUE if selecionado else cor,
                r,
                3 if selecionado else 2,
            )

            # Alcas de redimensionamento nos cantos.
            if ativa:
                for canto in cantos(retangulo):
                    alca = pygame.Rect(0, 0, 8, 8)
                    alca.center = canto
                    pygame.draw.rect(self.tela, (255, 255, 255), alca)
                    pygame.draw.rect(self.tela, (0, 0, 0), alca, 1)

        # Aplica o preenchimento por cima do fundo.
        self.tela.blit(preenchimento, (0, 0))

    def desenhar_teste(self) -> None:
        """Desenha o Cezar e os oclusores no modo de teste."""
        # O fundo do teste e o mesmo do editor.
        fundo = self.fundos[self.fundo]

        # Ordena heroi e oclusores pela base, igual ao jogo.
        pes = self.cezar.rect.top + config.mapa_teste.altura_dos_pes(self.cezar)
        camadas = [(pes, self.cezar)] + [
            (oclusor.base, oclusor) for oclusor in self.oclusores_teste
        ]

        for _, item in sorted(camadas, key=lambda camada: camada[0]):
            if isinstance(item, covil_tritao.Oclusor):
                item.desenhar(self.tela, fundo)
            else:
                self.tela.blit(item.image, item.rect)

        # Caixinha rosa mostrando o retangulo de colisao dos pes.
        pygame.draw.rect(
            self.tela,
            (255, 0, 200),
            config.mapa_teste.retangulo_colisao(self.cezar),
            2,
        )

    def desenhar_barra(self) -> None:
        """Desenha a barra superior de botoes e a explicacao da camada."""
        # Faixa semitransparente no topo.
        barra = pygame.Surface(
            (LARGURA, ALTURA_BARRA + ALTURA_EXPLICACAO),
            pygame.SRCALPHA,
        )
        barra.fill((*COR_PAINEL, 235))
        self.tela.blit(barra, (0, 0))

        # Posicao do mouse para destacar o botao sob o cursor.
        mouse = self.mouse()

        for botao in self.botoes:
            ativo = botao.acao == ("camada", self.camada) or (
                botao.acao == "testar" and self.testando
            )
            em_cima = botao.retangulo.collidepoint(mouse)

            # Fundo do botao muda quando o mouse esta em cima.
            fundo = (40, 52, 84) if em_cima else (24, 32, 56)
            pygame.draw.rect(self.tela, fundo, botao.retangulo, border_radius=6)
            pygame.draw.rect(
                self.tela,
                COR_DESTAQUE if ativo else (70, 84, 120),
                botao.retangulo,
                2,
                border_radius=6,
            )

            # Amostra de cor para os botoes de camada.
            x_texto = botao.retangulo.x + 10
            if isinstance(botao.acao, tuple):
                amostra = pygame.Rect(
                    botao.retangulo.x + 10,
                    botao.retangulo.centery - 6,
                    12,
                    12,
                )
                pygame.draw.rect(self.tela, botao.cor, amostra, border_radius=3)
                x_texto += 18

            # Texto do botao.
            texto = self.fonte_botao.render(
                botao.texto,
                True,
                COR_DESTAQUE if ativo else COR_TEXTO,
            )
            self.tela.blit(
                texto,
                (x_texto, botao.retangulo.centery - texto.get_height() // 2),
            )

        # Linha de explicacao logo abaixo dos botoes.
        nome, cor, _, explicacao = CAMADAS[self.camada]
        if self.testando:
            linha = (
                "MODO TESTE: ande com WASD ou as setas. A caixinha rosa são os pés. "
                "T ou Esc volta a editar."
            )
            cor = (255, 120, 220)
        else:
            linha = f"{nome}: {explicacao}"
        self.tela.blit(
            self.fonte.render(linha, True, cor),
            (10, ALTURA_BARRA + 2),
        )

    def desenhar_rodape(self) -> None:
        """Desenha a faixa inferior com aviso, fundo e coordenadas do mouse."""
        mouse = self.mouse()

        # Faixa semitransparente.
        rodape = pygame.Surface((LARGURA, ALTURA_RODAPE), pygame.SRCALPHA)
        rodape.fill((*COR_PAINEL, 235))
        self.tela.blit(rodape, (0, ALTURA - ALTURA_RODAPE))

        # Texto da direita: fundo e coordenadas.
        estado = (
            f"fundo: {'pós-boss' if self.fundo == 'posboss' else 'inicial'} (Tab)"
            f"   |   x {mouse[0]}, y {mouse[1]}"
        )
        if self.alterado:
            estado += '   |   NÃO SALVO'

        texto_estado = self.fonte.render(
            estado,
            True,
            (255, 150, 150) if self.alterado else (160, 175, 200),
        )
        self.tela.blit(
            texto_estado,
            (LARGURA - texto_estado.get_width() - 10, ALTURA - ALTURA_RODAPE + 4),
        )

        # Texto da esquerda: aviso atual.
        self.tela.blit(
            self.fonte.render(self.aviso, True, (255, 235, 160)),
            (10, ALTURA - ALTURA_RODAPE + 4),
        )

    def desenhar_dica_do_cursor(self) -> None:
        """Desenha a dica flutuante que explica o que o clique fara."""
        mouse = self.mouse()

        # Nao mostra dica sobre botoes, barra superior ou durante arraste.
        if (
            self.botao_em(mouse)
            or mouse[1] < ALTURA_BARRA + ALTURA_EXPLICACAO
            or self.arraste
        ):
            return

        dica = self.o_que_o_clique_faz(mouse)
        if not dica:
            return

        # Caixa amarela ao lado do cursor.
        texto = self.fonte_dica.render(dica, True, (20, 20, 20))
        caixa = texto.get_rect().inflate(12, 6)
        caixa.topleft = (mouse[0] + 16, mouse[1] + 14)

        # Evita que a caixa saia da tela.
        if caixa.right > LARGURA:
            caixa.right = mouse[0] - 8
        if caixa.bottom > ALTURA - ALTURA_RODAPE:
            caixa.bottom = mouse[1] - 8

        pygame.draw.rect(self.tela, (255, 236, 150), caixa, border_radius=5)
        pygame.draw.rect(self.tela, (60, 40, 0), caixa, 1, border_radius=5)
        self.tela.blit(texto, texto.get_rect(center=caixa.center))

    def desenhar_ajuda(self) -> None:
        """Desenha o painel de ajuda (tecla H esconde)."""
        if not self.mostrar_ajuda or self.testando:
            return

        # Texto muda conforme a camada ativa.
        if self.camada_de_contorno:
            linhas = [
                "COMO EDITAR UM CONTORNO",
                'N ............. começar um contorno novo',
                'clique ........ põe pontos em volta da área',
                "arrastar ponto  move o ponto",
                "clique na linha cria ponto no meio",
                "clique dentro . seleciona (fica amarelo)",
                'botão direito . apaga o ponto',
                "Delete ........ apaga o contorno inteiro",
            ]
        else:
            linhas = [
                "COMO EDITAR UM BLOQUEIO",
                "arrastar no vazio ... desenha um novo",
                "arrastar por dentro . move",
                "arrastar um canto ... muda o tamanho",
                'botão direito ....... apaga',
            ]

        # Dica extra para oclusores.
        if self.camada == "oclusores":
            linhas += [
                "",
                'Dica: contorne a estátua inteira e',
                'ponha um Bloqueio só na base dela.',
            ]

        # Rodape de atalhos, diferente quando embutido no jogo.
        linhas += [
            "",
            "F preenchimento   H esconder ajuda",
            "F3 / Esc: voltar ao jogo" if self.embutido else "Esc sair",
        ]

        # Caixa no canto superior direito.
        largura = max(self.fonte.size(linha)[0] for linha in linhas) + 24
        caixa = pygame.Rect(
            LARGURA - largura - 10,
            ALTURA_BARRA + ALTURA_EXPLICACAO + 8,
            largura,
            len(linhas) * 19 + 14,
        )

        fundo = pygame.Surface(caixa.size, pygame.SRCALPHA)
        fundo.fill((*COR_PAINEL, 220))
        self.tela.blit(fundo, caixa)
        pygame.draw.rect(self.tela, (70, 84, 120), caixa, 1, border_radius=4)

        # Cada linha, com a primeira em destaque.
        for n, linha in enumerate(linhas):
            cor = COR_DESTAQUE if n == 0 else COR_TEXTO
            self.tela.blit(
                self.fonte.render(linha, True, cor),
                (caixa.x + 12, caixa.y + 7 + n * 19),
            )

    def desenhar(self) -> None:
        """Desenha um quadro completo do editor."""
        # Fundo escolhido (inicial ou pos-boss).
        self.tela.blit(self.fundos[self.fundo], (0, 0))

        # No teste, mostra o Cezar; senao, todas as camadas.
        if self.testando:
            self.desenhar_teste()
        else:
            mostrar_posboss = (
                self.fundo == "posboss" or self.camada == "chao_posboss"
            )
            for chave in ("chao", "chao_posboss", "oclusores"):
                if chave == "chao_posboss" and not mostrar_posboss:
                    continue
                self.desenhar_contornos(chave, chave == self.camada)
            self.desenhar_bloqueios(self.camada == "bloqueios")

        # Interface por cima do mapa.
        self.desenhar_barra()
        self.desenhar_rodape()
        self.desenhar_ajuda()
        self.desenhar_dica_do_cursor()
