"""Interacao do editor: mouse, teclado e modo de teste de colisao.

Esta classe mixin nao desenha nada. Ela traduz cliques e teclas em alteracoes
no dicionario de dados (self.dados) e delega o desenho para o DesenhoMixin.
"""

from __future__ import annotations

# pygame fornece eventos, teclas e o estado do teclado.
import pygame

# covil_tritao fornece tamanho, entrada e dados do mapa do covil.
import covil_tritao

# Cezar e criado no modo de teste para simular o jogador andando.
from CezarPersonagem import Cezar

# config guarda a referencia compartilhada a mapa_teste e constantes.
import ferramentas.editor_config as config
from ferramentas.editor_config import (
    ALTURA,
    ALTURA_BARRA,
    ALTURA_EXPLICACAO,
    LARGURA,
    TECLAS_CAMADA,
    cantos,
)


class InteracaoMixin:
    """Eventos de mouse/teclado e o modo de teste."""

    def clicar_botao(self, botao) -> None:
        """Executa a acao de um botao da barra superior."""
        if isinstance(botao.acao, tuple):
            # Tupla ("camada", chave) troca a camada ativa.
            self.trocar_camada(botao.acao[1])
        elif botao.acao == "salvar":
            self.salvar()
        elif botao.acao == "desfazer":
            self.desfazer()
        elif botao.acao == "testar":
            self.alternar_teste(self.mouse())
        elif botao.acao == "sair":
            self.pedir_saida()

    def clique_contorno(self, pos, botao) -> None:
        """Trata um clique quando a camada ativa e de contornos (poligonos)."""
        # Botao direito: apaga o ponto sob o mouse.
        if botao == 3:
            alvo = self.ponto_proximo(pos)
            if alvo:
                self.guardar_para_desfazer()
                i, j = alvo
                del self.lista[i][j]
                self.selecionado = i
                self.aviso = f"Ponto apagado ({len(self.lista[i])} pontos restam)."
            return

        # Clicou em um ponto existente: comeca a arrastar esse ponto.
        alvo = self.ponto_proximo(pos)
        if alvo:
            self.guardar_para_desfazer()
            self.selecionado = alvo[0]
            self.arraste = ("ponto", *alvo)
            return

        # Clicou em uma linha: insere um ponto novo naquela aresta.
        linha = self.linha_proxima(pos)
        if linha:
            self.guardar_para_desfazer()
            i, j = linha
            self.lista[i].insert(j, list(pos))
            self.selecionado = i
            self.arraste = ("ponto", i, j)
            return

        # Clicou dentro de um poligono: apenas seleciona.
        dentro = self.poligono_em(pos)
        if dentro is not None:
            self.selecionado = dentro
            self.aviso = (
                "Contorno selecionado (amarelo): clique fora dele para acrescentar "
                "pontos; Delete apaga."
            )
            return

        # Sem selecao, o usuario precisa criar um contorno novo com N.
        if self.selecionado is None or self.selecionado >= len(self.lista):
            self.aviso = (
                'Para criar uma área nova, aperte N e clique em volta dela, ponto por ponto.'
            )
            return

        # Acrescenta um ponto ao contorno selecionado e ja comeca a arrastar.
        self.guardar_para_desfazer()
        self.lista[self.selecionado].append(list(pos))
        self.arraste = (
            "ponto",
            self.selecionado,
            len(self.lista[self.selecionado]) - 1,
        )

    def clique_bloqueio(self, pos, botao) -> None:
        """Trata um clique quando a camada ativa e de retangulos (bloqueios)."""
        # Botao direito: apaga o bloqueio sob o mouse.
        if botao == 3:
            alvo = self.retangulo_em(pos)
            if alvo is not None:
                self.guardar_para_desfazer()
                del self.lista[alvo]
                self.selecionado = None
                self.aviso = "Bloqueio apagado."
            return

        # Clicou em uma alca: comeca a redimensionar pelo canto oposto.
        canto = self.canto_em(pos)
        if canto:
            self.guardar_para_desfazer()
            i, indice = canto
            self.selecionado = i
            self.arraste = (
                "redimensionar",
                i,
                cantos(self.lista[i])[3 - indice],
            )
            return

        # Clicou dentro de um bloqueio: comeca a mover.
        alvo = self.retangulo_em(pos)
        if alvo is not None:
            self.guardar_para_desfazer()
            x, y, _, _ = self.lista[alvo]
            self.selecionado = alvo
            self.arraste = ("mover", alvo, (pos[0] - x, pos[1] - y))
            return

        # Clicou no vazio: cria um retangulo novo e redimensiona a partir dai.
        self.guardar_para_desfazer()
        self.lista.append([pos[0], pos[1], 0, 0])
        self.selecionado = len(self.lista) - 1
        self.arraste = ("redimensionar", self.selecionado, pos)

    def arrastar(self, pos) -> None:
        """Atualiza o item sendo arrastado, limitando a posicao ao mapa."""
        # Mantem o mouse dentro dos limites do mapa.
        x = max(0, min(LARGURA, pos[0]))
        y = max(0, min(ALTURA, pos[1]))

        # O primeiro item da tupla diz o tipo de arraste.
        tipo = self.arraste[0]

        if tipo == "ponto":
            # Move um ponto do poligono.
            _, i, j = self.arraste
            self.lista[i][j] = [x, y]
        elif tipo == "mover":
            # Move o retangulo inteiro, preservando o deslocamento do clique.
            _, i, (dx, dy) = self.arraste
            self.lista[i][0], self.lista[i][1] = x - dx, y - dy
        elif tipo == "redimensionar":
            # Redimensiona a partir do canto oposto (ox, oy).
            _, i, (ox, oy) = self.arraste
            self.lista[i] = [min(x, ox), min(y, oy), abs(x - ox), abs(y - oy)]

    def alternar_teste(self, pos) -> None:
        """Liga/desliga o modo de teste, no qual o Cezar anda com a colisao atual."""
        # Dentro do jogo o teste nao e necessario: F3 ja volta a jogar.
        if self.embutido:
            self.aviso = (
                'Dentro do jogo não precisa do teste: F3 volta a jogar com a colisão salva.'
            )
            return

        # Carrega o mapa_teste somente na primeira vez (evita import circular).
        if config.mapa_teste is None:
            import mapa_teste

            config.mapa_teste = mapa_teste
        mapa_teste = config.mapa_teste

        # Se ja estava testando, volta a editar.
        if self.testando:
            self.testando = False
            self.cezar = None
            mapa_teste.CENA["chao"] = None
            self.aviso = "Voltou a editar."
            return

        # Monta a mascara de chao a partir dos poligonos das camadas de chao.
        pos_boss = self.fundo == "posboss"
        chao = self.dados["chao"] + (
            self.dados["chao_posboss"] if pos_boss else []
        )
        superficie = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)
        for poligono in chao:
            if len(poligono) >= 3:
                pygame.draw.polygon(superficie, (255, 255, 255, 255), poligono)

        # Copia os dados editados para a CENA usada pelas funcoes do mapa.
        mapa_teste.CENA["tamanho"] = covil_tritao.TAMANHO
        mapa_teste.CENA["chao"] = pygame.mask.from_surface(superficie)
        mapa_teste.CENA["bloqueios"] = [
            pygame.Rect(r) for r in self.dados["bloqueios"] if r[2] > 2 and r[3] > 2
        ]
        self.oclusores_teste = [
            covil_tritao.Oclusor([tuple(p) for p in poligono])
            for poligono in self.dados["oclusores"]
            if len(poligono) >= 3
        ]

        # Cria o Cezar no tamanho do covil e aplica a velocidade do mapa.
        self.cezar = Cezar(tamanho=covil_tritao.TAMANHOS_SPRITES["Cezar"])
        self.cezar.velocidade *= covil_tritao.FATOR_VELOCIDADE
        self.cezar.quadro_animacao = 0
        self.cezar.tempo_animacao = 0.0

        # Comeca no mouse se ele estiver sobre o chao; senao, na entrada.
        if mapa_teste.CENA["chao"].get_at(
            (min(pos[0], LARGURA - 1), min(pos[1], ALTURA - 1))
        ):
            inicio = pos
        else:
            inicio = covil_tritao.ENTRADA
        mapa_teste.posicionar_pelos_pes(self.cezar, inicio)

        self.testando = True
        self.selecionado = None
        self.aviso = (
            'TESTE: ande com WASD/setas. A caixinha rosa são os pés. T volta a editar.'
        )

    def atualizar_teste(self, tempo_frame: float) -> None:
        """Move o Cezar de teste usando as mesmas regras do jogo."""
        # Le o teclado e monta o vetor de direcao.
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(
            (teclas[pygame.K_d] or teclas[pygame.K_RIGHT])
            - (teclas[pygame.K_a] or teclas[pygame.K_LEFT]),
            (teclas[pygame.K_s] or teclas[pygame.K_DOWN])
            - (teclas[pygame.K_w] or teclas[pygame.K_UP]),
        )

        # Com direcao, normaliza e move com colisao; senao, fica parado.
        if direcao.length_squared():
            direcao = direcao.normalize()
            passo = self.cezar.velocidade * tempo_frame
            andou = config.mapa_teste.mover_com_colisao(
                self.cezar,
                direcao.x * passo,
                direcao.y * passo,
            )
            config.mapa_teste.atualizar_animacao(
                self.cezar,
                direcao if andou else pygame.Vector2(),
                tempo_frame,
            )
        else:
            config.mapa_teste.atualizar_animacao(
                self.cezar, pygame.Vector2(), tempo_frame
            )

    def pedir_saida(self) -> None:
        'Sai do editor; com mudanças não salvas, só na segunda vez.'
        if self.alterado and not self.confirmar_saida:
            # Primeira tentativa: apenas avisa.
            self.confirmar_saida = True
            tecla = "F3/Esc" if self.embutido else "Esc"
            self.aviso = (
                f"Há mudanças NÃO SALVAS! {tecla} de novo sai sem salvar; Ctrl+S salva."
            )
        else:
            # Segunda tentativa (ou nada alterado): encerra.
            self.rodando = False

    def tecla(self, evento) -> None:
        """Trata uma tecla pressionada."""
        ctrl = evento.mod & pygame.KMOD_CTRL

        # Esc: sai do teste ou pede para sair do editor.
        if evento.key == pygame.K_ESCAPE:
            if self.testando:
                self.alternar_teste(self.mouse())
            else:
                self.pedir_saida()
        elif evento.key == pygame.K_F3 and self.embutido:
            # F3 dentro do jogo volta a jogar.
            self.pedir_saida()
        elif ctrl and evento.key == pygame.K_s:
            self.salvar()
        elif ctrl and evento.key == pygame.K_z:
            self.desfazer()
        elif evento.key == pygame.K_t:
            self.alternar_teste(self.mouse())
        elif self.testando:
            # No teste, as outras teclas sao para andar.
            return
        elif evento.key in TECLAS_CAMADA:
            self.trocar_camada(TECLAS_CAMADA[evento.key])
        elif evento.key == pygame.K_TAB:
            # Alterna o fundo inicial/pos-boss.
            self.fundo = "posboss" if self.fundo == "inicial" else "inicial"
            self.aviso = (
                f"Fundo: mapa {'pós-boss' if self.fundo == 'posboss' else 'inicial'}."
            )
        elif evento.key == pygame.K_f:
            self.preencher = not self.preencher
        elif evento.key == pygame.K_h:
            self.mostrar_ajuda = not self.mostrar_ajuda
        elif evento.key == pygame.K_n and self.camada_de_contorno:
            # Comeca um contorno vazio.
            self.guardar_para_desfazer()
            self.lista.append([])
            self.selecionado = len(self.lista) - 1
            self.aviso = (
                'Contorno novo: clique em volta da área, ponto por ponto (fecha sozinho).'
            )
        elif (
            evento.key in (pygame.K_DELETE, pygame.K_BACKSPACE)
            and self.selecionado is not None
        ):
            # Apaga o item selecionado.
            if self.selecionado < len(self.lista):
                self.guardar_para_desfazer()
                del self.lista[self.selecionado]
                self.selecionado = None
                self.aviso = "Apagado."

    def processar(self, evento) -> None:
        """Recebe um evento do pygame e o encaminha para a acao correta."""
        if evento.type == pygame.QUIT:
            # Fechar a janela tambem respeita mudancas nao salvas.
            if self.alterado and not self.confirmar_saida:
                self.confirmar_saida = True
                self.aviso = (
                    "Há mudanças NÃO SALVAS! Feche de novo para sair sem salvar; "
                    "Ctrl+S salva."
                )
            else:
                self.rodando = False
        elif evento.type == pygame.KEYDOWN:
            self.tecla(evento)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (1, 3):
            # Converte a posicao do mouse para a tela logica do jogo.
            pos = self.converter_mouse(evento.pos)
            botao = self.botao_em(pos)

            if botao and evento.button == 1:
                self.clicar_botao(botao)
            elif (
                botao
                or self.testando
                or pos[1] < ALTURA_BARRA + ALTURA_EXPLICACAO
            ):
                # Clique na barra, no modo de teste ou em botao: nao edita o mapa.
                return
            elif self.camada_de_contorno:
                self.clique_contorno(pos, evento.button)
            else:
                self.clique_bloqueio(pos, evento.button)
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            # Soltou o botao esquerdo: termina qualquer arraste.
            self.arraste = None
        elif evento.type == pygame.MOUSEMOTION and self.arraste:
            # Move o item que esta sendo arrastado.
            self.arrastar(self.converter_mouse(evento.pos))
