"""Fluxo de turnos, entradas do jogador e resultado da batalha."""

import random

import pygame
import Combate as regras

from .assets import *
from .animacoes import *
from .helpers import LOG_BATALHA
from .temas import alternar_tema, nome_do_tema, tema_atual

class FluxoBattleUI:
    """Coordinate battle state and forward actions to the rules."""

    def inimigos_vivos(self) -> list:
        return [inimigo for inimigo in self.inimigos if inimigo.estar_vivo()]

    def herois_vivos(self) -> list:
        return [heroi for heroi in self.herois if heroi.estar_vivo()]

    def restaurar_grupo_apos_vitoria(self) -> None:
        # Ao vencer, o grupo é revivido e fica com PA cheio para o próximo
        # encontro. As barras ATB de heróis e inimigos também voltam a zero.
        for heroi in self.herois:
            heroi.hp = heroi.hpMax
            heroi.PA = heroi.PAMax

        for combatente in self.herois + self.inimigos:
            combatente.resetar_atb()

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
            self.restaurar_grupo_apos_vitoria()

        # Derrota ocorre quando não resta nenhum herói vivo.
        elif not self.herois_vivos():
            self.resultado = False
            self.mensagem = "Derrota. Pressione ENTER para retornar ao mapa."
            LOG_BATALHA.append("O grupo foi derrotado.")

    def animacoes_ativas(self) -> bool:
        return (
            self.animacao_dash is not None
            or self.animacao_ataque is not None
            or self.animacao_ultimate is not None
            or self.animacao_habilidade_mago is not None
            or self.animacao_ataque_inimigo is not None
        )

    def iniciar_impacto(self) -> tuple[dict, int]:
        """Guarda a vida de todos e o tamanho do log antes de uma ação das regras."""
        sprites = self.sprites_herois + self.sprites_inimigos
        return {sprite: sprite.personagem.hp for sprite in sprites}, len(LOG_BATALHA)

    def reter_impactos(self, estado: tuple[dict, int]) -> None:
        """Segura na tela o dano que as regras já aplicaram.

        As regras calculam o golpe na hora, mas a vida só cai, o número só
        aparece e a morte só é mostrada quando a animação termina."""
        vidas_antes, linhas_antes = estado
        for sprite, hp_antes in vidas_antes.items():
            if sprite.personagem.hp < hp_antes:
                sprite.hp_exibido = hp_antes
                self.impactos_pendentes.append((sprite, int(sprite.personagem._ultimo_dano_recebido)))
        if self.impactos_pendentes and self.log_retido_desde is None:
            self.log_retido_desde = linhas_antes

    def liberar_impactos(self) -> None:
        """A animação acabou: mostra o dano, a morte, o log e confere o resultado."""
        for sprite, dano in self.impactos_pendentes:
            sprite.hp_exibido = None
            sprite.adicionar_dano_flutuante(dano)
        self.impactos_pendentes.clear()
        self.log_retido_desde = None
        self.pausa_turno = PAUSA_ENTRE_ACOES
        self.verificar_resultado()

    def atualizar(self, tempo_frame: float) -> None:
        if self.fundo_animado is not None:
            self.fundo_animado.atualizar(tempo_frame)
        # Atualiza os danos flutuantes de heróis e inimigos.
        for sprite in self.sprites_herois + self.sprites_inimigos:
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
        
        # O golpe só "acerta" na tela quando a animação inteira termina.
        if self.impactos_pendentes and not self.animacoes_ativas():
            self.liberar_impactos()

        if self.resultado is not None or self.heroi_ativo is not None:
            return

        # Enquanto qualquer animação estiver em andamento, o ATB fica pausado
        # para que os inimigos não ataquem antes de a animação e o efeito terminarem.
        if self.animacoes_ativas():
            return

        # Respiro entre uma ação e a próxima, para dar tempo de ler o que houve.
        if self.pausa_turno > 0:
            self.pausa_turno -= tempo_frame
            return

        # Cada modelo Personagem avança sua própria ATB; Heroi e Inimigo
        # compartilham esse comportamento herdado da classe base.
        for combatente in self.herois + self.inimigos:
            ritmo = 1.0 if isinstance(combatente, regras.Heroi) else VELOCIDADE_ATB_INIMIGOS
            combatente.carregar_atb(tempo_frame * 3.0 * ritmo)

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
            self.cursor_acao = 0
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
        estado = self.iniciar_impacto()
        pronto.atacar(alvo)
        self.reter_impactos(estado)
        # Reinicia a ATB após a ação para começar o próximo ciclo do combatente.
        pronto.resetar_atb()
        self.pausa_turno = PAUSA_ENTRE_ACOES
        self.mensagem = f"{pronto.nome} atacou {alvo.nome}."

        # Com golpe em andamento, o resultado só é conferido quando ele termina.
        if not self.impactos_pendentes:
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
        self.cursor_acao = numero - 1

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

        estado = self.iniciar_impacto()
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
                    sprite_heroi = next((s for s in self.sprites_herois if s.personagem is self.heroi_ativo), None)
                    sprite_alvo = next((s for s in self.sprites_inimigos if s.personagem is alvo), None)

                    # Cezar conjura a habilidade especial parado. Lucas usa a
                    # corrida antes do ataque básico e da skill de dash.
                    usar_dash = (
                        acao in {"atacar", "habilidade_especial"}
                        if self.heroi_ativo.nome == "Lucas"
                        else acao != "habilidade_especial"
                    )
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
                            velocidade_animacao=DASH_TEMPO_POR_QUADRO.get(self.heroi_ativo.nome, 0.04),
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

        self.reter_impactos(estado)
        # Com golpe em andamento, o resultado só é conferido quando ele termina.
        if not self.impactos_pendentes:
            self.verificar_resultado()
        if self.resultado is None:
            # A ação válida consome o turno e reinicia a ATB desse herói.
            self.pausa_turno = PAUSA_ENTRE_ACOES
            self.heroi_ativo.resetar_atb()
            self.heroi_ativo = None
            self.acao_pendente = None
            self.mensagem = "Aguardando a próxima barra ATB ficar cheia."

    def processar_evento(self, evento: pygame.event.Event) -> None:
        # Apenas teclas pressionadas participam do menu de ações por turno.
        if evento.type != pygame.KEYDOWN:
            return

        # F2 troca o visual (Clássico / Moderno). Durante um golpe a troca é
        # ignorada, para nenhum personagem mudar de lugar no meio da animação.
        if evento.key == pygame.K_F2:
            if not self.animacoes_ativas():
                alternar_tema()
                self.aplicar_formacao()
                LOG_BATALHA.append(f"Visual: {nome_do_tema()}.")
            return

        if self.resultado is not None:
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
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
            if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_KP4):
                self.indice_alvo = (self.indice_alvo - 1) % total
            elif evento.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6):
                self.indice_alvo = (self.indice_alvo + 1) % total
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.executar_acao(self.acao_pendente)
            elif evento.key == pygame.K_ESCAPE:
                self.acao_pendente = None
                self.mensagem = "Seleção de alvo cancelada. Escolha uma ação."
            return

        # Tema Moderno: menu em lista, navegado com ↑/↓ (ou W/S) e ENTER.
        if tema_atual() == "moderno":
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.cursor_acao = (self.cursor_acao - 1) % 6
                return
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                self.cursor_acao = (self.cursor_acao + 1) % 6
                return
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.escolher_acao(self.cursor_acao + 1)
                return

        if pygame.K_1 <= evento.key <= pygame.K_6:
            self.escolher_acao(evento.key - pygame.K_0)
        elif pygame.K_KP1 <= evento.key <= pygame.K_KP6:
            # Teclado numérico: K_KP1 a K_KP6 equivalem às teclas 1 a 6.
            self.escolher_acao(evento.key - pygame.K_KP1 + 1)
