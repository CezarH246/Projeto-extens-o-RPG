"""Create animations corresponding to combat actions."""

import pygame

from .assets import *
from .animacoes import *
from .helpers import *
from .sprites import SpriteCombatente

class AcoesBattleUI:
    """Select and start animations without implementing damage rules."""

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
            if heroi.nome == "Guilherme":
                frames_projetil = self.carregar_animacao_projetil_ataque_guilherme(heroi)
                if frames and frames_projetil:
                    self.animacao_habilidade_mago = AnimacaoPersonagemProjetil(
                        frames,
                        frames_projetil,
                        heroi,
                        origem,
                        sprite_alvo.centro,
                    )
                return
            if frames:
                self.animacao_ataque = AnimacaoAtaque(frames, heroi, origem, sprite_alvo.centro)
            return

        if acao == "habilidade_especial":
            if heroi.nome == "Lucas":
                # Tecla 2 do Lucas: skill1 — dash de fogo em direção ao inimigo.
                frames = self.carregar_frames_gif(
                    SKILL_LUCAS,
                    tamanho_com_escala(TAMANHO_ANIMACAO_PERSONAGEM, heroi),
                    ajustar_ao_conteudo=False,
                )
                if frames:
                    self.animacao_ataque = AnimacaoUltimateCezar(
                        frames, heroi, origem, sprite_alvo.centro, velocidade_animacao=0.06,
                    )
                return
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
            if heroi.nome == "Guilherme":
                # Tecla 3 (SPECIAL) do Guilherme: animação do mago parado e,
                # depois, a sequência de efeitos — magia se formando, bola de
                # fogo indo até o inimigo e impacto dentro dele.
                frames_personagem, frames_formacao, frames_bola, frames_efeito = (
                    self.carregar_animacao_especial_guilherme(
                        heroi, tamanho_corpo(sprite_alvo.personagem)
                    )
                )
                if frames_personagem and frames_bola:
                    self.animacao_habilidade_mago = AnimacaoEspecialSequencial(
                        frames_personagem,
                        frames_formacao,
                        frames_bola,
                        frames_efeito,
                        heroi,
                        origem,
                        sprite_alvo.centro,
                    )
                return
            if heroi.nome == "Lucas":
                # O rugido fica no Lucas; somente o efeito separado voa ao alvo.
                frames_rugido, frames_projetil = (
                    self.carregar_animacao_especial_lucas(
                        heroi, tamanho_corpo(sprite_alvo.personagem)
                    )
                )
                if frames_rugido and frames_projetil:
                    self.animacao_habilidade_mago = AnimacaoPersonagemProjetil(
                        frames_rugido,
                        frames_projetil,
                        heroi,
                        origem,
                        sprite_alvo.centro,
                    )
                return
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
            elif heroi.nome == "Lucas":
                frames_ultimate, frames_efeito = self.carregar_animacao_ultimate_lucas(
                    heroi, tamanho_corpo(sprite_alvo.personagem)
                )
                if frames_ultimate:
                    # 0.12 s por quadro (2× mais lento que o padrão 0.06):
                    # a animação do herói e o efeito no inimigo ficam mais lentos.
                    self.animacao_ultimate = AnimacaoUltimateComEfeito(
                        frames_ultimate,
                        frames_efeito,
                        heroi,
                        origem,
                        sprite_alvo.centro,
                        velocidade_animacao=0.12,
                    )
            else:
                frames = self.carregar_animacao_ultimate(heroi)
                if frames:
                    self.animacao_ultimate = AnimacaoUltimate(frames, heroi, origem, sprite_alvo.centro)
