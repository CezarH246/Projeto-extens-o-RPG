"""Draw the arena, panels, and battle messages."""

import pygame
import Combate as regras

from .animacoes import AnimacaoHabilidadeMago
from .assets import *
from .helpers import LOG_BATALHA, cor_barra_hp

class RenderizacaoBattleUI:
    """Renderiza a interface sem alterar as regras dos combatentes."""

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
