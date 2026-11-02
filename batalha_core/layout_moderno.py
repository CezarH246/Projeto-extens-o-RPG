"""Tema Moderno da batalha (inspirado em RPGs de console/mobile).

- Linha do tempo de turnos no topo, com o retrato de quem age e a fila seguinte.
- Menu de comandos em lista no canto superior esquerdo, com cursor e descrição.
- Cartões do grupo (HP, PA e ATB) e registro compacto no rodapé.
- Barras finas embaixo dos inimigos, com etiqueta de letra (A, B, C).
"""

import math

import pygame
import Combate as regras

from .assets import *
from .helpers import LOG_BATALHA, cor_barra_hp, criar_fonte, texto_com_sombra

CIANO = (64, 214, 255)
CIANO_ESCURO = (20, 70, 120)
VERMELHO = (255, 96, 96)
TEXTO = (236, 240, 248)
TEXTO_SUAVE = (150, 162, 186)
TEXTO_APAGADO = (92, 100, 122)
COR_ROTULO_HP = (110, 225, 160)
COR_ROTULO_PA = (120, 180, 255)
COR_BARRA_PA = (90, 160, 255)
COR_BARRA_HP_INIMIGO = (214, 78, 140)
COR_BARRA_ATB_INIMIGO = (232, 190, 90)
ULTIMATE_PRONTA = (255, 206, 90)

# Descrição mostrada no rodapé do menu para a ação sob o cursor.
DESCRICOES_ACOES = [
    "Golpe básico com a arma. Não gasta PA.",
    "Técnica da classe do herói. Custa 20 PA.",
    "Golpe poderoso. Custa 40 PA e exige nível 5.",
    "Ataque supremo, liberado quando a carga da ultimate enche.",
    "Usa uma poção para recuperar PA.",
    "Assume postura de defesa: +5 de defesa.",
]

LETRAS_INIMIGOS = "ABCDEF"

# Retângulos fixos do tema (resolução lógica 1280x720).
MENU = pygame.Rect(34, 106, 271, 344)
Y_RODAPE = 612
ALTURA_RODAPE = 96
LARGURA_CARTAO = 204
ESPACO_CARTAO = 8


class HudModerno:
    """Desenha a interface do tema Moderno sobre a arena já desenhada."""

    # ------------------------------------------------------------------
    # Recursos
    # ------------------------------------------------------------------

    def _fontes_modernas(self) -> None:
        if not hasattr(self, "fm_nome"):
            self.fm_nome = criar_fonte(18, negrito=True)
            self.fm_item = criar_fonte(19, negrito=True)
            self.fm_numero = criar_fonte(22, negrito=True)
            self.fm_pequena = criar_fonte(14, negrito=True)
            self.fm_texto = criar_fonte(16)
            self.fm_letra = criar_fonte(12, negrito=True)

    def _cache_moderno(self) -> dict:
        return self.__dict__.setdefault("_cache_hud_moderno", {})

    def _vidro(self, tamanho: tuple[int, int], raio: int, topo: tuple, base: tuple, alfa: int = 225) -> pygame.Surface:
        """Painel com degradê vertical e cantos arredondados (montado uma vez só)."""
        chave = ("vidro", tamanho, raio, topo, base, alfa)
        cache = self._cache_moderno()
        if chave not in cache:
            largura, altura = tamanho
            painel = pygame.Surface(tamanho, pygame.SRCALPHA)
            for y in range(altura):
                t = y / max(1, altura - 1)
                cor = tuple(round(topo[i] + (base[i] - topo[i]) * t) for i in range(3))
                pygame.draw.line(painel, (*cor, alfa), (0, y), (largura - 1, y))
            mascara = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=raio)
            painel.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            cache[chave] = painel
        return cache[chave]

    def _degrade_horizontal(self, tamanho: tuple[int, int], esquerda: tuple, direita: tuple, raio: int = 6) -> pygame.Surface:
        chave = ("horizontal", tamanho, esquerda, direita, raio)
        cache = self._cache_moderno()
        if chave not in cache:
            largura, altura = tamanho
            faixa = pygame.Surface(tamanho, pygame.SRCALPHA)
            for x in range(largura):
                t = x / max(1, largura - 1)
                cor = tuple(round(esquerda[i] + (direita[i] - esquerda[i]) * t) for i in range(4))
                pygame.draw.line(faixa, cor, (x, 0), (x, altura - 1))
            mascara = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=raio)
            faixa.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            cache[chave] = faixa
        return cache[chave]

    def _losango(self, sprite, tamanho: int, cor_borda: tuple) -> pygame.Surface:
        """Retrato do personagem recortado em losango, com borda colorida."""
        chave = ("losango", id(sprite), tamanho, cor_borda)
        cache = self._cache_moderno()
        if chave not in cache:
            meio = tamanho // 2
            pontas = [(meio, 0), (tamanho - 1, meio), (meio, tamanho - 1), (0, meio)]
            icone = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
            pygame.draw.polygon(icone, (18, 26, 44, 255), pontas)
            rosto = sprite.retrato(int(tamanho * 0.86))
            icone.blit(rosto, rosto.get_rect(center=(meio, meio)))
            mascara = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
            pygame.draw.polygon(mascara, (255, 255, 255, 255), pontas)
            icone.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            pygame.draw.polygon(icone, cor_borda, pontas, 2)
            cache[chave] = icone
        return cache[chave]

    def _etiqueta_letra(self, letra: str, centro: tuple[int, int]) -> None:
        """Pequeno losango vermelho com a letra do inimigo (A, B, C)."""
        x, y = centro
        pontas = [(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)]
        pygame.draw.polygon(self.tela, (150, 30, 40), pontas)
        pygame.draw.polygon(self.tela, (255, 210, 210), pontas, 1)
        rotulo = self.fm_letra.render(letra, True, (255, 255, 255))
        self.tela.blit(rotulo, rotulo.get_rect(center=(x, y)))

    def _barra_fina(self, x: int, y: int, largura: int, altura: int, proporcao: float, cor: tuple) -> None:
        pygame.draw.rect(self.tela, (34, 40, 56), (x, y, largura, altura), border_radius=altura // 2)
        preenchido = int(largura * max(0.0, min(1.0, proporcao)))
        if preenchido > 0:
            pygame.draw.rect(self.tela, cor, (x, y, preenchido, altura), border_radius=altura // 2)

    def _letra_do_inimigo(self, sprite) -> str:
        return LETRAS_INIMIGOS[self.sprites_inimigos.index(sprite) % len(LETRAS_INIMIGOS)]

    @staticmethod
    def _limites_do_corpo(sprite) -> pygame.Rect:
        """Retângulo do desenho visível do idle, na posição de repouso (não balança)."""
        base = sprite.frames_standard[0] if sprite.frames_standard else sprite.imagem
        corpo = base.get_bounding_rect()
        corpo.move_ip(sprite.centro_inicial[0] - base.get_width() // 2, sprite.centro_inicial[1] - base.get_height() // 2)
        return corpo

    # ------------------------------------------------------------------
    # Linha do tempo de turnos
    # ------------------------------------------------------------------

    def ordem_de_turnos(self) -> list:
        """Sprites vivos na ordem em que vão agir (pelo tempo até a ATB encher)."""
        fila = []
        for sprite in self.sprites_herois + self.sprites_inimigos:
            personagem = sprite.personagem
            if sprite.hp_visivel() <= 0:
                continue
            if personagem is self.heroi_ativo:
                tempo = -1.0
            else:
                ritmo = 1.0 if isinstance(personagem, regras.Heroi) else VELOCIDADE_ATB_INIMIGOS
                taxa = personagem.velocidade * 3.0 * ritmo
                tempo = (personagem.atb_max - personagem.atb_barra) / taxa if taxa > 0 else float("inf")
            fila.append((tempo, sprite))
        fila.sort(key=lambda item: item[0])
        return [sprite for _, sprite in fila]

    def _desenhar_linha_do_tempo(self) -> None:
        fila = self.ordem_de_turnos()
        if not fila:
            return
        y = 42
        trilho = self._degrade_horizontal((LARGURA - 110, 4), (*CIANO, 230), (*CIANO, 0), raio=2)
        self.tela.blit(trilho, (90, y - 2))

        primeiro = fila[0]
        cor = CIANO if primeiro in self.sprites_herois else VERMELHO
        grande = self._losango(primeiro, 70, cor)
        self.tela.blit(grande, grande.get_rect(center=(52, y + 4)))
        rotulo = "AGORA" if primeiro.personagem is self.heroi_ativo else "PRÓXIMO"
        texto_com_sombra(self.tela, self.fm_letra, rotulo, cor, (52, y + 48), centralizado=True)
        if primeiro in self.sprites_inimigos:
            self._etiqueta_letra(self._letra_do_inimigo(primeiro), (52 + 26, y + 26))

        for indice, sprite in enumerate(fila[1:]):
            x = 132 + indice * 74
            heroi = sprite in self.sprites_herois
            icone = self._losango(sprite, 44, CIANO if heroi else VERMELHO)
            # Heróis acima do trilho e inimigos abaixo, como numa linha do tempo.
            centro_y = y - 8 if heroi else y + 14
            self.tela.blit(icone, icone.get_rect(center=(x, centro_y)))
            if not heroi:
                self._etiqueta_letra(self._letra_do_inimigo(sprite), (x + 16, centro_y + 16))

    # ------------------------------------------------------------------
    # Menu de comandos
    # ------------------------------------------------------------------

    def _indice_cursor(self) -> int:
        if self.acao_pendente is not None:
            for numero, acao in self.ACOES_POR_NUMERO.items():
                if acao == self.acao_pendente:
                    return numero - 1
        return getattr(self, "cursor_acao", 0) % 6

    def _desenhar_menu_comandos(self) -> None:
        heroi = self.heroi_ativo
        if heroi is None or self.resultado is not None:
            return
        self.tela.blit(self._vidro(MENU.size, 10, (20, 40, 70), (10, 16, 30)), MENU.topleft)
        pygame.draw.rect(self.tela, (70, 120, 170), MENU, 1, border_radius=10)

        # Cabeçalho: retrato, nome e PA do herói da vez.
        cabecalho = self._degrade_horizontal((MENU.width - 2, 52), (*CIANO, 120), (*CIANO, 0), raio=9)
        self.tela.blit(cabecalho, (MENU.x + 1, MENU.y + 1))
        sprite = next((s for s in self.sprites_herois if s.personagem is heroi), None)
        if sprite is not None:
            retrato = self._losango(sprite, 46, CIANO)
            self.tela.blit(retrato, retrato.get_rect(center=(MENU.x + 30, MENU.y + 27)))
        texto_com_sombra(self.tela, self.fm_nome, f"{heroi.nome}  Nv.{heroi.level}", TEXTO, (MENU.x + 60, MENU.y + 6))
        texto_com_sombra(self.tela, self.fm_pequena, f"PA {heroi.PA}/{heroi.PAMax}", COR_ROTULO_PA, (MENU.x + 60, MENU.y + 29))

        cursor = self._indice_cursor()
        selecionando = self.acao_pendente is not None and bool(self.inimigos_vivos())
        for indice, (nome, detalhe, livre) in enumerate(self.acoes_disponiveis()):
            linha = pygame.Rect(MENU.x + 8, MENU.y + 58 + indice * 34, MENU.width - 16, 30)
            if indice == cursor:
                faixa = self._degrade_horizontal(linha.size, (40, 150, 210, 240), (20, 70, 120, 200))
                self.tela.blit(faixa, linha.topleft)
                pygame.draw.rect(self.tela, (150, 220, 255), linha, 1, border_radius=6)
            else:
                pygame.draw.rect(self.tela, (24, 34, 54), linha, border_radius=6)
                pygame.draw.rect(self.tela, (44, 60, 88), linha, 1, border_radius=6)

            cor_numero = CIANO if livre else TEXTO_APAGADO
            pygame.draw.circle(self.tela, cor_numero, (linha.x + 16, linha.centery), 10, 2)
            numero = self.fm_letra.render(str(indice + 1), True, cor_numero)
            self.tela.blit(numero, numero.get_rect(center=(linha.x + 16, linha.centery)))

            cor_nome = TEXTO if livre else TEXTO_APAGADO
            texto_com_sombra(self.tela, self.fm_item, nome, cor_nome, (linha.x + 34, linha.y + 3))
            if detalhe:
                if not livre:
                    cor_detalhe = (240, 120, 110)
                elif detalhe == "pronta!":
                    cor_detalhe = ULTIMATE_PRONTA
                else:
                    cor_detalhe = (180, 205, 235)
                rotulo = self.fm_letra.render(detalhe, True, cor_detalhe)
                self.tela.blit(rotulo, rotulo.get_rect(midright=(linha.right - 8, linha.centery)))

        # Cursor em losango, balançando para o lado, à esquerda da opção atual.
        y_cursor = MENU.y + 58 + cursor * 34 + 15
        x_cursor = MENU.x - 12 + round(math.sin(pygame.time.get_ticks() / 140) * 3)
        for deslocamento in (0, 9):
            x = x_cursor - deslocamento
            pontas = [(x, y_cursor - 6), (x + 6, y_cursor), (x, y_cursor + 6), (x - 6, y_cursor)]
            pygame.draw.polygon(self.tela, (220, 245, 255) if deslocamento == 0 else (120, 190, 230), pontas, 2)

        # Rodapé do menu: descrição da ação ou o alvo escolhido, e as teclas.
        y_rodape = MENU.y + 58 + 6 * 34 + 4
        pygame.draw.line(self.tela, (60, 90, 130), (MENU.x + 10, y_rodape), (MENU.right - 10, y_rodape))
        largura_texto = MENU.width - 24
        if selecionando:
            vivos = self.inimigos_vivos()
            alvo = vivos[self.indice_alvo % len(vivos)]
            sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)
            letra = f"[{self._letra_do_inimigo(sprite_alvo)}] " if sprite_alvo else ""
            linhas = [(f"Alvo: {letra}{alvo.nome}", CIANO), (f"HP {alvo.hp}/{alvo.hpMax}", TEXTO_SUAVE)]
            dica = "←/→ alvo  •  ENTER confirma  •  ESC volta"
        else:
            linhas = [(parte, TEXTO_SUAVE) for parte in self._quebrar(DESCRICOES_ACOES[cursor], self.fm_texto, largura_texto)[:2]]
            dica = "↑/↓ ou 1–6 escolhe  •  ENTER confirma"
        for indice, (texto, cor) in enumerate(linhas[:2]):
            texto = self._cortar_texto(self.fm_texto, texto, largura_texto)
            self.tela.blit(self.fm_texto.render(texto, True, cor), (MENU.x + 12, y_rodape + 6 + indice * 21))
        self.tela.blit(self.fm_letra.render(dica, True, (120, 170, 210)), (MENU.x + 12, y_rodape + 50))

    @staticmethod
    def _quebrar(texto: str, fonte: pygame.font.Font, largura: int) -> list[str]:
        linhas, atual = [], ""
        for palavra in texto.split():
            teste = f"{atual} {palavra}".strip()
            if fonte.size(teste)[0] > largura and atual:
                linhas.append(atual)
                atual = palavra
            else:
                atual = teste
        if atual:
            linhas.append(atual)
        return linhas

    # ------------------------------------------------------------------
    # Cartões do grupo e registro (rodapé)
    # ------------------------------------------------------------------

    def _desenhar_cartoes_grupo(self) -> None:
        for indice, sprite in enumerate(self.sprites_herois):
            heroi = sprite.personagem
            cartao = pygame.Rect(15 + indice * (LARGURA_CARTAO + ESPACO_CARTAO), Y_RODAPE, LARGURA_CARTAO, ALTURA_RODAPE)
            ativo = heroi is self.heroi_ativo
            vivo = sprite.hp_visivel() > 0
            topo = (24, 60, 96) if ativo else (20, 30, 50)
            self.tela.blit(self._vidro(cartao.size, 8, topo, (10, 16, 30), 230 if vivo else 160), cartao.topleft)
            pygame.draw.rect(self.tela, CIANO if ativo else (60, 80, 110), cartao, 2 if ativo else 1, border_radius=8)

            cor_nome = TEXTO if vivo else TEXTO_APAGADO
            texto_com_sombra(self.tela, self.fm_nome, heroi.nome, cor_nome, (cartao.x + 10, cartao.y + 4))
            if regras.ultimate_disponivel(heroi) and vivo:
                ult = self.fm_letra.render("ULT", True, (30, 22, 6))
                selo = pygame.Rect(0, 0, ult.get_width() + 10, 16)
                selo.topright = (cartao.right - 8, cartao.y + 8)
                pygame.draw.rect(self.tela, ULTIMATE_PRONTA, selo, border_radius=4)
                self.tela.blit(ult, ult.get_rect(center=selo.center))

            # HP e PA: rótulo colorido à esquerda, número grande à direita e barra fina.
            linhas = [
                ("HP", COR_ROTULO_HP, sprite.hp_visivel(), heroi.hpMax, cor_barra_hp(sprite.hp_visivel(), heroi.hpMax), 28),
                ("PA", COR_ROTULO_PA, heroi.PA, heroi.PAMax, COR_BARRA_PA, 56),
            ]
            for rotulo, cor_rotulo, valor, maximo, cor_barra, deslocamento in linhas:
                y = cartao.y + deslocamento
                self.tela.blit(self.fm_pequena.render(rotulo, True, cor_rotulo), (cartao.x + 10, y + 4))
                numero = self.fm_numero.render(str(int(valor)), True, cor_nome)
                self.tela.blit(numero, numero.get_rect(topright=(cartao.right - 10, y - 4)))
                self._barra_fina(cartao.x + 10, y + 22, cartao.width - 20, 4, valor / maximo if maximo else 0, cor_barra)

            # ATB em dois segmentos, como uma barra de "carga" do turno.
            proporcao = heroi.atb_barra / heroi.atb_max if heroi.atb_max else 0
            largura_segmento = (cartao.width - 26) // 2
            for segmento in range(2):
                parte = max(0.0, min(1.0, proporcao * 2 - segmento))
                cor = CIANO if ativo else (200, 215, 235)
                self._barra_fina(cartao.x + 10 + segmento * (largura_segmento + 6), cartao.y + 86, largura_segmento, 4, parte, cor)

    def _desenhar_registro_compacto(self) -> None:
        inicio = 15 + 3 * (LARGURA_CARTAO + ESPACO_CARTAO)
        painel = pygame.Rect(inicio, Y_RODAPE, LARGURA - 15 - inicio, ALTURA_RODAPE)
        self.tela.blit(self._vidro(painel.size, 8, (20, 30, 50), (10, 16, 30), 215), painel.topleft)
        pygame.draw.rect(self.tela, (60, 80, 110), painel, 1, border_radius=8)

        visiveis = LOG_BATALHA if self.log_retido_desde is None else LOG_BATALHA[:self.log_retido_desde]
        linhas = []
        for texto_log in visiveis[-8:]:
            cor = self.cor_do_evento(texto_log)
            for parte in self._quebrar(texto_log, self.fm_texto, painel.width - 34):
                linhas.append((parte, cor))
        for indice, (texto, cor) in enumerate(linhas[-3:]):
            y = painel.y + 8 + indice * 28
            ultima = indice == len(linhas[-3:]) - 1
            pygame.draw.rect(self.tela, cor, (painel.x + 10, y + 3, 3, 18), border_radius=1)
            texto_com_sombra(self.tela, self.fm_texto, texto, TEXTO if ultima else TEXTO_SUAVE, (painel.x + 20, y))

    # ------------------------------------------------------------------
    # Barras dos inimigos e marcador do herói da vez
    # ------------------------------------------------------------------

    def _desenhar_barras_inimigos(self) -> None:
        for sprite in self.sprites_inimigos:
            inimigo = sprite.personagem
            corpo = self._limites_do_corpo(sprite)
            largura = 130
            x = sprite.centro_inicial[0] - largura // 2 + 8
            y = corpo.bottom + 6
            vivo = sprite.hp_visivel() > 0
            nome = self._cortar_texto(self.fm_letra, inimigo.nome, largura + 40)
            texto_com_sombra(self.tela, self.fm_letra, nome, TEXTO if vivo else TEXTO_APAGADO, (x, y))
            self._etiqueta_letra(self._letra_do_inimigo(sprite), (x - 14, y + 27))
            proporcao_hp = sprite.hp_visivel() / inimigo.hpMax if inimigo.hpMax else 0
            self._barra_fina(x, y + 19, largura, 6, proporcao_hp, COR_BARRA_HP_INIMIGO)
            proporcao_atb = inimigo.atb_barra / inimigo.atb_max if inimigo.atb_max else 0
            self._barra_fina(x, y + 29, largura, 4, proporcao_atb, COR_BARRA_ATB_INIMIGO)

    def _desenhar_marcador_heroi(self) -> None:
        if self.heroi_ativo is None or self.resultado is not None:
            return
        sprite = next((s for s in self.sprites_herois if s.personagem is self.heroi_ativo), None)
        if sprite is None:
            return
        corpo = self._limites_do_corpo(sprite)
        x = sprite.centro_inicial[0]
        y = corpo.top - 16 + round(math.sin(pygame.time.get_ticks() / 160) * 5)
        pontas = [(x, y - 9), (x + 8, y), (x, y + 9), (x - 8, y)]
        pygame.draw.polygon(self.tela, CIANO, pontas)
        pygame.draw.polygon(self.tela, (220, 245, 255), pontas, 2)

    def desenhar_hud_moderno(self) -> None:
        self._fontes_modernas()
        self._desenhar_barras_inimigos()
        self._desenhar_marcador_heroi()
        self._desenhar_linha_do_tempo()
        self._desenhar_menu_comandos()
        self._desenhar_cartoes_grupo()
        self._desenhar_registro_compacto()
