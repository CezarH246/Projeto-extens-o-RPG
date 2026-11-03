"""Draw the arena, panels, and battle messages."""

import math

import pygame
import Combate as regras

from .animacoes import AnimacaoHabilidadeMago
from .assets import *
from .helpers import LOG_BATALHA, cor_barra_hp, criar_fonte, texto_com_sombra
from .layout_moderno import CIANO, HudModerno
from .temas import tema_atual

class RenderizacaoBattleUI(HudModerno):
    """Renderiza a interface sem alterar as regras dos combatentes."""

    def desenhar_barra(self, x: int, y: int, largura: int, valor: float, maximo: float, cor: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.tela, (25, 27, 39), (x, y, largura, 10), border_radius=4)
        proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
        preenchimento = int(largura * proporcao)
        if preenchimento:
            pygame.draw.rect(self.tela, cor, (x, y, preenchimento, 10), border_radius=4)
        pygame.draw.rect(self.tela, (238, 238, 242), (x, y, largura, 10), 1, border_radius=4)

    def desenhar_paineis_herois(self) -> None:
        """Nome, HP, PA e ATB de cada herói, acima da cabeça dele."""
        for sprite in self.sprites_herois:
            sprite.desenhar_painel_heroi(self.tela, ativo=sprite.personagem is self.heroi_ativo)

    def acoes_disponiveis(self) -> list[tuple[str, str, bool]]:
        """Lista (nome, detalhe, disponível) das 6 ações do herói do turno.

        Quando a ação está bloqueada, o detalhe explica o motivo."""
        heroi = self.heroi_ativo
        if heroi is None:
            return [(nome, detalhe, False) for nome, detalhe in self.ROTULOS_ACOES]
        ultimate = regras.ultimate_disponivel(heroi)
        if heroi.level < 5:
            detalhe_especial = "Nv. 5"
        else:
            detalhe_especial = "40 PA" if heroi.PA >= 40 else "PA insuficiente"
        return [
            ("Ataque", "", True),
            ("Habilidade", "20 PA" if heroi.PA >= 20 else "PA insuficiente", heroi.PA >= 20),
            ("Especial", detalhe_especial, heroi.level >= 5 and heroi.PA >= 40),
            ("Ultimate", "pronta!" if ultimate else "carregando", ultimate),
            ("Poção de PA", f"x{heroi.pocoesPA}" if heroi.pocoesPA else "sem poções", heroi.pocoesPA > 0),
            ("Defender", "+5 DEF", True),
        ]

    ROTULOS_ACOES = [
        ("Ataque", ""),
        ("Habilidade", "20 PA"),
        ("Especial", "40 PA"),
        ("Ultimate", ""),
        ("Poção de PA", ""),
        ("Defender", "+5 DEF"),
    ]

    ACOES_POR_NUMERO = {
        1: "atacar",
        2: "habilidade_especial",
        3: "segunda_habilidade",
        4: "ultimate",
    }

    # Paleta e medidas dos painéis do rodapé (ações e registro).
    COR_PAINEL = (14, 22, 58)
    COR_BORDA = (222, 181, 83)
    COR_DOURADO = (255, 214, 102)
    ALTURA_PAINEL_RODAPE = 190
    LARGURA_PAINEL_ACOES = 660

    def _fontes_hud(self) -> None:
        """Cria as fontes do rodapé uma única vez."""
        if not hasattr(self, "fonte_acoes"):
            self.fonte_acoes = criar_fonte(20, negrito=True)
            self.fonte_mensagem = criar_fonte(18, negrito=True)
            self.fonte_dica = criar_fonte(15)
            self.fonte_rotulo = criar_fonte(14, negrito=True)
            self.fonte_log = criar_fonte(17)

    def _desenhar_painel(self, painel: pygame.Rect, titulo: str) -> None:
        """Fundo translúcido, borda dourada e cabeçalho, iguais nos dois painéis."""
        fundo = pygame.Surface(painel.size, pygame.SRCALPHA)
        pygame.draw.rect(fundo, (*self.COR_PAINEL, 228), fundo.get_rect(), border_radius=12)
        self.tela.blit(fundo, painel.topleft)
        pygame.draw.rect(self.tela, self.COR_BORDA, painel, 2, border_radius=12)
        texto_com_sombra(self.tela, self.fonte_rotulo, titulo.upper(), self.COR_DOURADO, (painel.x + 16, painel.y + 8))
        pygame.draw.line(self.tela, (70, 82, 130), (painel.x + 14, painel.y + 32), (painel.right - 14, painel.y + 32), 1)

    def _largura_tecla(self, texto: str) -> int:
        return max(22, self.fonte_rotulo.size(texto)[0] + 12)

    def _desenhar_tecla(self, texto: str, x: int, y: int) -> int:
        """Desenha uma tecla (ex.: ENTER) e devolve o x logo depois dela."""
        caixa = pygame.Rect(x, y, self._largura_tecla(texto), 22)
        pygame.draw.rect(self.tela, (235, 228, 205), caixa, border_radius=5)
        pygame.draw.rect(self.tela, (120, 110, 80), caixa, 1, border_radius=5)
        rotulo = self.fonte_rotulo.render(texto, True, (20, 24, 40))
        self.tela.blit(rotulo, rotulo.get_rect(center=caixa.center))
        return caixa.right

    def _desenhar_ajuda(self, itens: list[tuple[list[str], str]], direita: int, y: int) -> None:
        """Dica de teclas alinhada à direita: as teclas e, ao lado, o que elas fazem."""
        total = sum(
            sum(self._largura_tecla(tecla) + 4 for tecla in teclas) + 2 + self.fonte_dica.size(descricao)[0] + 14
            for teclas, descricao in itens
        )
        x = direita - total + 14
        for teclas, descricao in itens:
            for tecla in teclas:
                x = self._desenhar_tecla(tecla, x, y) + 4
            x += 2
            self.tela.blit(self.fonte_dica.render(descricao, True, (215, 220, 235)), (x, y + 2))
            x += self.fonte_dica.size(descricao)[0] + 14

    def _cortar_texto(self, fonte: pygame.font.Font, texto: str, largura: int) -> str:
        """Encurta o texto com reticências até caber na largura."""
        if fonte.size(texto)[0] <= largura:
            return texto
        while texto and fonte.size(texto + "…")[0] > largura:
            texto = texto[:-1]
        return texto.rstrip() + "…"

    def desenhar_painel_acoes(self) -> None:
        self._fontes_hud()
        painel = pygame.Rect(
            LARGURA - 15 - self.LARGURA_PAINEL_ACOES, ALTURA - 15 - self.ALTURA_PAINEL_RODAPE,
            self.LARGURA_PAINEL_ACOES, self.ALTURA_PAINEL_RODAPE,
        )
        heroi = self.heroi_ativo
        titulo = f"Ações  ·  {heroi.nome}  ·  PA {heroi.PA}/{heroi.PAMax}" if heroi else "Ações"
        self._desenhar_painel(painel, titulo)

        selecionando = self.acao_pendente is not None and bool(self.inimigos_vivos())
        if selecionando:
            ajuda = [(["←", "→"], "alvo"), (["ENTER"], "confirmar"), (["ESC"], "voltar")]
        elif heroi is not None:
            ajuda = [(["1–6"], "escolher a ação")]
        else:
            ajuda = []
        self._desenhar_ajuda(ajuda, painel.right - 14, painel.y + 6)

        # Seis botões em 2 colunas: tecla, nome e, à direita, custo ou motivo do bloqueio.
        for indice, (nome, detalhe, livre) in enumerate(self.acoes_disponiveis()):
            coluna, linha = indice // 3, indice % 3
            botao = pygame.Rect(painel.x + 14, painel.y + 40, 310, 32).move(coluna * 322, linha * 37)
            escolhida = selecionando and self.ACOES_POR_NUMERO.get(indice + 1) == self.acao_pendente
            if escolhida:
                fundo_botao, borda = (58, 78, 158), self.COR_DOURADO
            elif livre:
                fundo_botao, borda = (30, 44, 100), (62, 78, 140)
            else:
                fundo_botao, borda = (22, 28, 56), (40, 48, 80)
            pygame.draw.rect(self.tela, fundo_botao, botao, border_radius=8)
            pygame.draw.rect(self.tela, borda, botao, 2 if escolhida else 1, border_radius=8)

            tecla = pygame.Rect(botao.x + 6, botao.y + 5, 22, 22)
            pygame.draw.rect(self.tela, self.COR_DOURADO if livre else (70, 76, 105), tecla, border_radius=5)
            numero = self.fonte_rotulo.render(str(indice + 1), True, (20, 24, 40))
            self.tela.blit(numero, numero.get_rect(center=tecla.center))

            cor_nome = self.COR_DOURADO if escolhida else ((255, 255, 255) if livre else (120, 126, 152))
            texto_com_sombra(self.tela, self.fonte_acoes, nome, cor_nome, (botao.x + 38, botao.y + 3))
            if detalhe:
                if not livre:
                    cor_detalhe = (235, 120, 110) if heroi else (120, 126, 152)
                elif "PA" in detalhe:
                    cor_detalhe = (240, 200, 90)
                elif detalhe == "pronta!":
                    cor_detalhe = (120, 230, 150)
                else:
                    cor_detalhe = (170, 200, 240)
                texto_detalhe = self.fonte_dica.render(detalhe, True, cor_detalhe)
                self.tela.blit(texto_detalhe, texto_detalhe.get_rect(midright=(botao.right - 10, botao.centery)))

        # Linha de baixo: o alvo escolhido (com a vida dele) ou a situação do turno.
        y_status = painel.y + 155
        if selecionando:
            vivos = self.inimigos_vivos()
            alvo = vivos[self.indice_alvo % len(vivos)]
            x = painel.x + 16
            texto_com_sombra(self.tela, self.fonte_mensagem, "Alvo:", (200, 205, 225), (x, y_status))
            x += self.fonte_mensagem.size("Alvo:")[0] + 8
            largura_barra = 110
            texto_hp = f"{alvo.hp}/{alvo.hpMax}"
            x_hp = painel.right - 16 - largura_barra - self.fonte_dica.size(texto_hp)[0] - 8
            nome_alvo = self._cortar_texto(self.fonte_mensagem, alvo.nome, x_hp - x - 12)
            texto_com_sombra(self.tela, self.fonte_mensagem, nome_alvo, self.COR_DOURADO, (x, y_status))
            self.tela.blit(self.fonte_dica.render(texto_hp, True, (225, 228, 240)), (x_hp, y_status + 2))
            self.desenhar_barra(
                painel.right - 16 - largura_barra, y_status + 7, largura_barra,
                alvo.hp, alvo.hpMax, cor_barra_hp(alvo.hp, alvo.hpMax),
            )
        else:
            cor = self.COR_DOURADO if heroi is not None else (200, 205, 225)
            mensagem = self._cortar_texto(self.fonte_mensagem, self.mensagem, painel.width - 32)
            texto_com_sombra(self.tela, self.fonte_mensagem, mensagem, cor, (painel.x + 16, y_status))

    def cor_do_evento(self, texto: str) -> tuple[int, int, int]:
        """Cor de cada linha do registro, conforme o tipo de acontecimento."""
        if texto.startswith("Turno de"):
            return self.COR_DOURADO
        if "Vitória" in texto:
            return (120, 230, 150)
        if "derrotado" in texto or "Derrota" in texto:
            return (240, 110, 100)
        if "dano" in texto:
            # Golpe de herói em azul; golpe recebido pelo grupo em vermelho.
            heroi_atacou = any(texto.startswith(heroi.nome) for heroi in self.herois)
            return (130, 200, 255) if heroi_atacou else (255, 140, 115)
        if "não possui" in texto or "indisponível" in texto:
            return (235, 170, 90)
        return (205, 210, 228)

    def desenhar_log(self) -> None:
        """Registro da batalha no canto inferior esquerdo, ao lado das ações."""
        self._fontes_hud()
        largura = LARGURA - 15 - self.LARGURA_PAINEL_ACOES - 15 - 15
        painel = pygame.Rect(15, ALTURA - 15 - self.ALTURA_PAINEL_RODAPE, largura, self.ALTURA_PAINEL_RODAPE)
        self._desenhar_painel(painel, "Registro de batalha")

        # Enquanto um golpe está sendo animado, o texto dele ainda não aparece.
        visiveis = LOG_BATALHA if self.log_retido_desde is None else LOG_BATALHA[:self.log_retido_desde]
        largura_texto = painel.width - 50
        linhas = []  # (texto, cor, é a primeira linha do evento)
        for texto_log in visiveis[-12:]:
            cor = self.cor_do_evento(texto_log)
            atual, primeira = "", True
            for palavra in texto_log.split():
                teste = f"{atual} {palavra}".strip()
                if self.fonte_log.size(teste)[0] > largura_texto and atual:
                    linhas.append((atual, cor, primeira))
                    atual, primeira = palavra, False
                else:
                    atual = teste
            if atual:
                linhas.append((atual, cor, primeira))
        linhas = linhas[-5:]

        for indice, (linha, cor, primeira) in enumerate(linhas):
            # Quanto mais antiga a linha, mais apagada; a última fica em destaque.
            idade = len(linhas) - 1 - indice
            fator = max(0.7, 1 - idade * 0.08)
            cor_final = tuple(int(canal * fator) for canal in cor)
            y = painel.y + 40 + indice * 29
            if primeira:
                pygame.draw.circle(self.tela, cor_final, (painel.x + 22, y + 11), 4)
            texto_com_sombra(self.tela, self.fonte_log, linha, cor_final, (painel.x + 34, y))

    def desenhar_turno(self) -> None:
        """Aviso de quem age e marca sobre o herói que está esperando comando."""
        if self.resultado is not None:
            return
        if self.heroi_ativo is not None:
            texto_com_sombra(
                self.tela, self.fonte, f"Turno de {self.heroi_ativo.nome}", (255, 226, 92),
                (LARGURA // 2, 38), centralizado=True,
            )
            sprite = next((s for s in self.sprites_herois if s.personagem is self.heroi_ativo), None)
            if sprite is not None:
                # A seta sobe e desce em onda (seno) e pulsa de cor para chamar atenção.
                tempo = pygame.time.get_ticks() / 1000
                flutuar = math.sin(tempo * 6) * 6
                brilho = (math.sin(tempo * 6) + 1) / 2
                cor = (255, 200 + int(55 * brilho), 60 + int(90 * brilho))
                x = sprite.centro_inicial[0]
                y = round(sprite.topo_painel_heroi() - 8 + flutuar)
                ponta = [(x - 12, y - 16), (x + 12, y - 16), (x, y)]
                pygame.draw.polygon(self.tela, cor, ponta)
                pygame.draw.polygon(self.tela, (20, 20, 25), ponta, 2)
        else:
            texto_com_sombra(
                self.tela, self.fonte_pequena, "Aguardando as barras ATB...", (230, 232, 245),
                (LARGURA // 2, 38), centralizado=True,
            )

    def desenhar(self) -> None:
        if self.fundo_animado is not None:
            # O vídeo muda a cada quadro: escurece por cima com a mesma camada.
            if getattr(self, "_escurecimento", None) is None:
                self._escurecimento = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                self._escurecimento.fill((0, 0, 0, 38))
            self.tela.blit(self.fundo_animado.imagem, (0, 0))
            self.tela.blit(self._escurecimento, (0, 0))
        else:
            # O fundo já escurecido é montado uma única vez, não a cada frame.
            if getattr(self, "_fundo_escurecido", None) is None:
                self._fundo_escurecido = self.fundo.copy()
                escurecimento = pygame.Surface(self.fundo.get_size(), pygame.SRCALPHA)
                escurecimento.fill((0, 0, 0, 38))
                self._fundo_escurecido.blit(escurecimento, (0, 0))
            self.tela.blit(self._fundo_escurecido, (0, 0))

        moderno = tema_atual() == "moderno"
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

        # As entidades (cósmica do Guilherme, serpente do Cezar e Rei Antigo
        # Caído do Lucas) ficam atrás dos heróis enquanto a Ultimate do dono
        # estiver pronta.
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
            sprite.desenhar(
                self.tela, selecionado, self.fonte_dano,
                # No Moderno as barras ficam embaixo do inimigo (desenhadas pelo HUD).
                mostrar_barra=not moderno,
                cor_selecao=CIANO if moderno else (255, 226, 92),
            )
            
            # Desenha danos flutuantes
            for dano in sprite.danos_flutuantes:
                dano.desenhar(self.tela, self.fonte_dano)

        for sprite in self.sprites_herois:
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

        if moderno:
            self.desenhar_hud_moderno()
        else:
            self.desenhar_log()
            self.desenhar_turno()
            self.desenhar_paineis_herois()
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
