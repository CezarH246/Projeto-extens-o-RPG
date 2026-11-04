"""Loop principal do mapa e classe Jogo.

A classe Jogo junta tres conjuntos de metodos por heranca multipla (mixins):
- JanelaMixin  -> criar/escalar/centralizar a janela;
- CenasMixin   -> criar personagens, trocar de mapa e abrir/fechar batalha;
- DesenhoMixin -> desenhar fundo, objetos, avisos e colisoes.

Aqui ficam apenas o estado do jogo, a leitura do teclado e o laco principal.
Isso e o pilar da HERANCA em acao: Jogo reutiliza comportamentos prontos em vez
de copiar o codigo para dentro de uma classe gigante.
"""

from __future__ import annotations

# pygame fornece janela, eventos, grupos de sprites e desenho.
import pygame

# covil_tritao guarda tamanhos, entrada e patrulhas do mapa animado.
import covil_tritao

# Funcoes de musica da exploracao e da vitoria.
from Musicas import tocar_musica_exploracao, tocar_musica_vitoria

# config concentra constantes e a cena atual.
import mapa_config as config

# Regras de combate: cria os objetos que a batalha visual vai usar.
from Combate import criar_herois

# RecompensaBau e a tela do bau (bolo e carta).
from recompensa_bau import RecompensaBau

# Funcoes de colisao/movimento reaproveitadas pelo loop.
from mapa_colisao import (
    atualizar_animacao,
    carregar_mapa_caminho,
    mover_com_colisao,
    registrar_posicao,
    retangulo_colisao,
    retangulo_encontro,
)

# Mixins que compoem a classe Jogo.
from mapa_cenas import CenasMixin
from mapa_desenho import DesenhoMixin
from mapa_janela import JanelaMixin


class Jogo(JanelaMixin, CenasMixin, DesenhoMixin):
    """Estado e loop principal do mapa."""

    def __init__(self):
        # Inicializa todos os subsistemas do pygame (video, audio, fontes...).
        pygame.init()

        # Comeca a tocar a musica de exploracao.
        tocar_musica_exploracao()

        # Flag de tela cheia (F11 alterna).
        self.tela_cheia = False

        # O jogo pode comecar no covil (720x480 como o mapa) ou no mapa antigo.
        tamanho_inicial = (
            covil_tritao.TAMANHO
            if config.CENA_INICIAL == "covil"
            else (config.LARGURA_MAPA, config.ALTURA_MAPA)
        )

        # Cria a janela e guarda a superficie logica onde tudo e desenhado.
        self.tela = self.criar_janela(tamanho_inicial)
        pygame.display.set_caption("RPG Saga dos Falidos - Mapa")

        # Clock controla os quadros por segundo; fontes desenham os textos.
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 23)
        self.fonte_auxiliar = pygame.font.SysFont(None, 18)

        # Tenta carregar a imagem do mapa inicial (mapateste.jpeg).
        self.mapa_imagem = carregar_mapa_caminho()

        # Estado geral do jogo.
        self.rodando = True
        self.modo = "mapa"  # mapa | combate | bau | editor
        self.mostrar_colisoes = False
        self.batalha = None
        self.inimigo_em_batalha = None
        self.musica_vitoria_tocada = False
        self.inimigo_ignorado = None
        self.rei_tritao_spawnado = False
        self.rei_tritao_derrotado = False
        self.caverna_liberada = False
        self.bau_aberto = False
        self.recompensa: RecompensaBau | None = None
        self.editor = None  # editor de colisao (F3 no covil)

        # Estatuas do covil (recortes que escondem quem passa atras).
        self.oclusores = [
            covil_tritao.Oclusor(poligono)
            for poligono in covil_tritao.OCLUSORES
        ]

        # Cena atual e controle da passagem secreta.
        self.cena = "mapateste"
        self.passagem_aberta = False
        self.mapa_animado = None

        # Escurecimento: 1 = tela preta; diminui ate 0 ao entrar numa cena.
        self.escurecimento = 0.0

        # Mensagem exibida na caixa do canto superior esquerdo.
        self.mensagem = (
            "WASD/setas: mover | Encoste no inimigo para lutar | "
            "F3: colisões | F11: tela cheia"
        )

        # Nome do mapa em uso (usado pelo desenho provisorio).
        self.mapa_atual = "mapateste"

        # Grupos de sprites: herois, inimigos e tudo o que e desenhado no mapa.
        self.grupo_herois = pygame.sprite.Group()
        self.grupo_inimigos = pygame.sprite.Group()
        self.grupo_objetos = pygame.sprite.Group()

        # Cria o grupo no tamanho certo da cena inicial.
        self.criar_personagens(
            covil_tritao.TAMANHOS_SPRITES if config.CENA_INICIAL == "covil" else None
        )

        # Entra no covil ou cria os inimigos do mapa antigo.
        if config.CENA_INICIAL == "covil":
            self.entrar_no_covil()
        else:
            self.criar_inimigos_mapa_teste()

        # Estes mesmos objetos sao enviados a batalha e preservam nivel, HP, PA, XP e pocoes.
        self.herois_combate = criar_herois()

    def atualizar_lider(self, tempo_frame: float) -> None:
        """Le o teclado e move o Cezar (o lider do grupo)."""
        # get_pressed devolve o estado atual de todas as teclas.
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(0, 0)

        # WASD e as setas do teclado movem o lider do grupo.
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            direcao.x += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            direcao.x -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            direcao.y += 1
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            direcao.y -= 1

        # Com alguma tecla pressionada, normaliza para a diagonal nao ser mais rapida.
        if direcao.length_squared() > 0:
            direcao = direcao.normalize()

            # Move o lider com a regra de colisao (deslizando em X e Y).
            movimentou = mover_com_colisao(
                self.cezar,
                direcao.x * self.cezar.velocidade * tempo_frame,
                direcao.y * self.cezar.velocidade * tempo_frame,
            )

            # So registra no historico se realmente andou (os seguidores copiam isso).
            if movimentou:
                registrar_posicao(self.cezar)

            # Anima a caminhada; se bateu na parede, usa direcao zero (parado).
            atualizar_animacao(
                self.cezar,
                direcao if movimentou else pygame.Vector2(),
                tempo_frame,
            )
        else:
            # Nenhuma tecla: mantem a imagem parada.
            atualizar_animacao(self.cezar, pygame.Vector2(), tempo_frame)

    def atualizar_seguidor(
        self,
        seguidor: pygame.sprite.Sprite,
        lider: pygame.sprite.Sprite,
        atraso: int,
        tempo_frame: float,
    ) -> None:
        """Faz Lucas e Guilherme seguirem o historico de posicoes do lider."""
        # Escolhe uma posicao antiga do lider; "atraso" maior = mais longe.
        indice = max(0, len(lider.historico_posicoes) - atraso)
        destino = lider.historico_posicoes[indice]

        # Vetor do seguidor ate o destino.
        diferenca = destino - seguidor.posicao

        # Se ja esta bem perto, nao precisa andar; so fica parado.
        if diferenca.length_squared() < 4:
            atualizar_animacao(seguidor, pygame.Vector2(), tempo_frame)
            return

        # Direcao normalizada e distancia limitada pela velocidade do seguidor.
        direcao = diferenca.normalize()
        deslocamento = min(diferenca.length(), seguidor.velocidade * tempo_frame)

        # Move com colisao e registra o proprio caminho.
        movimentou = mover_com_colisao(
            seguidor,
            direcao.x * deslocamento,
            direcao.y * deslocamento,
        )
        if movimentou:
            registrar_posicao(seguidor)

        # Atualiza a animacao conforme o movimento.
        atualizar_animacao(
            seguidor,
            direcao if movimentou else pygame.Vector2(),
            tempo_frame,
        )

    def atualizar_inimigo(self, inimigo, tempo_frame: float) -> None:
        """Move um inimigo de patrulha, invertendo o sentido ao bater."""
        # O rei fica parado no trono, apenas respirando (idle).
        if getattr(inimigo, "eh_rei_tritao", False):
            inimigo.atualizar_idle(tempo_frame)
            return

        # Vetor de movimento depende do eixo de patrulha.
        direcao = (
            pygame.Vector2(inimigo.sentido, 0)
            if inimigo.eixo == "horizontal"
            else pygame.Vector2(0, inimigo.sentido)
        )

        # Tenta mover usando a mesma colisao dos herois.
        movimentou = mover_com_colisao(
            inimigo,
            direcao.x * inimigo.velocidade * tempo_frame,
            direcao.y * inimigo.velocidade * tempo_frame,
        )

        # Ao tocar em uma parede ou em uma borda, o inimigo inverte sua patrulha.
        if not movimentou:
            inimigo.sentido *= -1
            direcao *= -1

        # Atualiza a animacao do inimigo.
        atualizar_animacao(inimigo, direcao, tempo_frame)

    def encontrar_colisao_com_inimigo(self):
        """Retorna o inimigo tocado pelo grupo, ignorando o da ultima batalha."""
        # Marca se o unico inimigo tocado e justamente o que deve ser ignorado.
        tocando_ignorado = False

        # Compara a area de encontro de cada heroi com a de cada inimigo.
        for heroi in self.grupo_herois:
            for inimigo in self.grupo_inimigos:
                if retangulo_encontro(heroi).colliderect(retangulo_encontro(inimigo)):
                    # O inimigo da ultima batalha nao reabre a luta enquanto o
                    # grupo ainda estiver encostado nele (o grupo volta ao mapa
                    # no mesmo lugar e entraria em batalha de novo no mesmo frame).
                    if inimigo is self.inimigo_ignorado:
                        tocando_ignorado = True
                        continue
                    return inimigo

        # Se o grupo se afastou do inimigo ignorado, libera novas batalhas com ele.
        if not tocando_ignorado:
            self.inimigo_ignorado = None
        return None

    def processar_eventos(self) -> None:
        """Distribui os eventos do pygame para o modo ativo (mapa, bau, editor...)."""
        for evento in pygame.event.get():
            # Fechar a janela encerra o jogo.
            if evento.type == pygame.QUIT:
                self.rodando = False
                continue

            # F11 ou Alt+Enter alternam a tela cheia no mapa e na batalha.
            if evento.type == pygame.KEYDOWN and (
                evento.key == pygame.K_F11
                or (
                    evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                    and evento.mod & pygame.KMOD_ALT
                )
            ):
                self.alternar_tela_cheia()
                continue

            # Cada modo tem um dono dos eventos.
            if self.modo == "combate":
                self.batalha.processar_evento(evento)
            elif self.modo == "bau":
                self.recompensa.processar_evento(evento)
            elif self.modo == "editor":
                self.editor.processar(evento)

                # Se o editor pediu para sair, volta ao mapa.
                if not self.editor.rodando:
                    self.fechar_editor_colisao()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F3:
                # No covil, F3 abre o editor; no mapa antigo, mostra colisoes.
                if self.cena == "covil":
                    self.abrir_editor_colisao()
                else:
                    self.mostrar_colisoes = not self.mostrar_colisoes
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F4:
                # F4 tambem liga/desliga a visualizacao de colisoes.
                self.mostrar_colisoes = not self.mostrar_colisoes
            elif (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_e
                and self.pode_abrir_bau()
            ):
                # E abre a tela de recompensa quando o lider esta perto do bau.
                self.recompensa = RecompensaBau(self.tela.get_size())
                self.modo = "bau"

    def atualizar_mapa(self, tempo_frame: float) -> None:
        """Atualiza movimento, animacoes, passagens e encontros do mapa."""
        # Move o lider (e, por consequencia, os seguidores no mesmo frame).
        self.atualizar_lider(tempo_frame)

        # Atualiza cada inimigo de patrulha.
        for inimigo in self.grupo_inimigos:
            self.atualizar_inimigo(inimigo, tempo_frame)

        # Avanca os quadros do mapa animado (covil).
        if self.mapa_animado is not None:
            self.mapa_animado.atualizar(tempo_frame)

        # Reduz o escurecimento ate a tela ficar totalmente visivel.
        self.escurecimento = max(0.0, self.escurecimento - tempo_frame / 0.8)

        # Depois de exterminar todos os inimigos comuns, abre-se a passagem
        # para o Covil do Rei Tritao.
        if (
            self.cena == "mapateste"
            and not self.grupo_inimigos
            and not self.passagem_aberta
        ):
            self.passagem_aberta = True
            self.mensagem = (
                'A água estremece... Uma passagem para o Covil do Rei Tritão se abriu!'
            )

        # No covil, quando o ultimo guarda cai, a caverna do chefe se acende.
        if (
            self.cena == "covil"
            and not self.grupo_inimigos
            and not self.caverna_liberada
            and not self.rei_tritao_derrotado
        ):
            self.liberar_caverna_boss()

        # Com a caverna acesa, pisar nela leva à arena exclusiva do Rei Tritão.
        if (
            self.cena == "covil"
            and self.caverna_liberada
            and not self.rei_tritao_derrotado
            and retangulo_colisao(self.cezar).colliderect(covil_tritao.CAVERNA_BOSS)
        ):
            self.entrar_no_covil_boss()
            return

        # Se a passagem esta aberta, basta o lider pisar nela para trocar de cena.
        if self.passagem_aberta and self.cena == "mapateste":
            if retangulo_colisao(self.cezar).colliderect(config.PASSAGEM_COVIL):
                self.entrar_no_covil()
                return

        # Por fim, verifica se o grupo encostou em algum inimigo.
        inimigo = self.encontrar_colisao_com_inimigo()
        if inimigo is not None:
            self.abrir_batalha(inimigo)

    def executar(self) -> None:
        """Laco principal: eventos, atualizacao do modo ativo e desenho."""
        while self.rodando:
            # tick limita a 60 FPS e devolve o tempo decorrido em segundos.
            tempo_frame = self.relogio.tick(config.FPS) / 1000

            # Le teclado/mouse/janela.
            self.processar_eventos()

            # Cada modo tem sua atualizacao e desenho.
            if self.modo == "mapa":
                self.atualizar_mapa(tempo_frame)
                self.desenhar_mapa()
            elif self.modo == "bau":
                # O mapa continua animado por tras do bolo e da carta.
                if self.mapa_animado is not None:
                    self.mapa_animado.atualizar(tempo_frame)
                self.desenhar_mapa()
                self.recompensa.atualizar(tempo_frame)
                self.recompensa.desenhar(self.tela)
                if self.recompensa.concluida:
                    self.fechar_recompensa()
            elif self.modo == "editor":
                # O editor desenha por cima da tela logica.
                self.editor.desenhar()
            else:
                # Modo combate: atualiza a batalha e toca a musica de vitoria.
                self.batalha.atualizar(tempo_frame)
                if self.batalha.resultado is True and not self.musica_vitoria_tocada:
                    tocar_musica_vitoria()
                    self.musica_vitoria_tocada = True
                self.batalha.desenhar()
                if self.batalha.concluida:
                    self.fechar_batalha()

            # Sempre escala a tela logica para a janela real e mostra o frame.
            self.apresentar()

        # Ao sair do laco, encerra o pygame.
        pygame.quit()
