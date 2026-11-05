"""Troca de cenas, criacao de personagens e entrada/saida de batalha.

A classe Jogo herda estes metodos (padrao "mixin"): assim o loop principal fica
curto e cada grupo de responsabilidades mora em um arquivo pequeno. Os metodos
abaixo apenas orquestram objetos de outros modulos - as regras de combate
continuam em Combate.py e o desenho da batalha em batalha_ui.py.
"""

from __future__ import annotations

# pygame fornece Vector2, Group e a superficie da tela.
import pygame

# covil_tritao guarda os dados do mapa animado, colisoes e posicoes.
import covil_tritao

# Musicas controla a trilha sonora de cada situacao.
from Musicas import (
    tocar_musica_Boss,
    tocar_musica_batalha,
    tocar_musica_deepcave,
)

# config contem CENA e as constantes compartilhadas.
import mapa_config as config

# Transicoes centraliza os fades usados entre as cenas.
from Transicoes import executar_transicao

# Cutscene do kraken, antes da primeira luta contra o Rei Tritao.
from cutscene import CUTSCENE_KRAKEN, tocar_cutscene

# MapaAnimado desenha os quadros animados do covil (e do fundo da batalha).
from mapa_animado import MapaAnimado

# Modelos dos tres herois jogaveis.
from CezarPersonagem import Cezar
from LucasPersonagem import Lucas
from GuilhermePersonagem import Guilherme

# Modelos dos inimigos que aparecem no mapa.
from InimigoPersonagem import InimigoPeixe, ReiTritaoMapa

# Funcoes de colisao reaproveitadas do mapa.
from mapa_colisao import altura_dos_pes, desenhar_mapa_provisorio, posicionar_pelos_pes

# Colisao editavel (F3) de cada mapa, um arquivo por mapa.
import colisoes_mapas

# A fachada batalha_ui esconde os modulos de batalha_core.
from batalha_ui import (
    ALTURA as ALTURA_COMBATE,
    LARGURA as LARGURA_COMBATE,
    FUNDO_BATALHA_GUARDAS,
    FUNDO_BATALHA_REI_TRITAO,
    criar_batalha,
    preparar_fundo_animado,
)


class CenasMixin:
    """Criacao do grupo, viagens entre mapas e transicoes de batalha."""

    def criar_personagens(self, tamanhos: dict[str, int] | None = None) -> None:
        'Cria o grupo. `tamanhos` define o lado de cada sprite (padrão: 32 px).'
        # Evita erro quando o chamador nao passa tamanhos.
        tamanhos = tamanhos or {}

        # Cria o lider e os dois seguidores; cada seguidor recebe o anterior.
        self.cezar = Cezar(tamanho=tamanhos.get("Cezar", 32))
        self.lucas = Lucas(self.cezar, tamanho=tamanhos.get("Lucas", 32))
        self.guilherme = Guilherme(self.lucas, tamanho=tamanhos.get("Guilherme", 32))

        # Posicoes iniciais lado a lado, cada um um pouco mais a direita.
        posicoes = [(250, 150), (285, 150), (320, 150)]
        for personagem, posicao in zip((self.cezar, self.lucas, self.guilherme), posicoes):
            # posicao guarda o movimento com decimais.
            personagem.posicao = pygame.Vector2(posicao)

            # rect e a caixa usada para desenhar e colidir.
            personagem.rect.topleft = posicao

            # O historico comeca com a posicao inicial.
            personagem.historico_posicoes = [pygame.Vector2(posicao)]

        # So o lider anda pelo mapa; a equipe completa aparece na batalha.
        self.grupo_herois.add(self.cezar)

        # O grupo de objetos inclui herois e inimigos para desenhar por camadas.
        self.grupo_objetos.add(self.grupo_herois, self.grupo_inimigos)

    def criar_inimigos_casa(self) -> None:
        """Cria os inimigos do mapa provisorio de interior (nao usado na cena inicial)."""
        # Dois peixes patrulhando em eixos diferentes.
        inimigos = [
            InimigoPeixe(420, 155, eixo="horizontal"),
            InimigoPeixe(670, 180, eixo="vertical"),
        ]

        # quantidade_combate define quantos inimigos surgem na batalha.
        for inimigo in inimigos:
            inimigo.quantidade_combate = 3
            self.grupo_inimigos.add(inimigo)

    def criar_inimigos_mapa_teste(self) -> None:
        """Cria os quatro inimigos iniciais do mapa antigo."""
        # Cada inimigo patrulha em um eixo (horizontal ou vertical).
        inimigos = [
            InimigoPeixe(375, 100, eixo="horizontal"),
            InimigoPeixe(120, 250, eixo="vertical"),
            InimigoPeixe(550, 300, eixo="horizontal"),
            InimigoPeixe(550, 400, eixo="vertical"),
        ]

        # Todos geram uma batalha com tres inimigos.
        for inimigo in inimigos:
            inimigo.quantidade_combate = 3
            self.grupo_inimigos.add(inimigo)

        # Atualiza o grupo de desenho com os inimigos recem-criados.
        self.grupo_objetos.add(self.grupo_inimigos)

    def abrir_batalha(self, inimigo: InimigoPeixe) -> None:
        """Troca a janela do mapa pela tela definida em batalha_ui.py."""
        # A trilha da batalha comeca junto com a transicao para fora do mapa.
        pygame.mixer.music.stop()
        eh_rei = getattr(inimigo, "eh_rei_tritao", False)

        # Primeira vez contra o Rei: cutscene do kraken emergindo do mar (ela
        # comeca na arena e termina no cenario da batalha). Da para pular.
        tocou_cutscene = False
        if eh_rei and not getattr(self, "cutscene_kraken_vista", False):
            self.cutscene_kraken_vista = True
            tocou_cutscene = True
            # Quem esta no mapa (o lider e o Rei) continua aparecendo na cutscene,
            # na mesma ordem de desenho do mapa (pes mais abaixo ficam na frente).
            no_mapa = sorted(self.grupo_objetos, key=lambda item: item.rect.top + altura_dos_pes(item))
            personagens = [(item.image, item.rect.copy()) for item in no_mapa]
            if not tocar_cutscene(
                CUTSCENE_KRAKEN, self.tela, self.apresentar, self.relogio,
                fps=config.FPS, personagens=personagens,
            ):
                self.rodando = False
                return

        if eh_rei:
            tocar_musica_Boss()
        else:
            tocar_musica_batalha()

        # A cutscene ja termina escurecendo a tela: nada de mosaico por cima.
        if not tocou_cutscene and not executar_transicao(
            self.tela,
            self.desenhar_mapa,
            self.apresentar,
            self.relogio,
            fps=config.FPS,
            direcao="fechar",
        ):
            self.rodando = False
            return

        # Guarda o inimigo para remove-lo do mapa se o grupo vencer.
        self.inimigo_em_batalha = inimigo

        # A batalha usa resolucao logica 1280x720.
        self.tela = self.criar_janela((LARGURA_COMBATE, ALTURA_COMBATE))
        pygame.display.set_caption("RPG Saga dos Falidos - Batalha")

        # Fundo animado: guardas do covil e Rei Tritao tem cenario proprio.
        if getattr(inimigo, "eh_rei_tritao", False):
            fundo = FUNDO_BATALHA_REI_TRITAO
        elif getattr(inimigo, "eh_guarda_covil", False):
            fundo = FUNDO_BATALHA_GUARDAS
        else:
            fundo = None

        # criar_batalha pertence a batalha_ui: aqui so passamos os modelos e o fundo.
        self.batalha = criar_batalha(
            self.tela,
            self.herois_combate,
            inimigo.quantidade_combate,
            rei_tritao=getattr(inimigo, "eh_rei_tritao", False),
            fundo_animado=fundo,
        )

        # Permite tocar a musica de vitoria apenas uma vez por luta.
        self.musica_vitoria_tocada = False

        # O loop principal passa a atualizar a batalha em vez do mapa.
        self.modo = "combate"
        if not executar_transicao(
            self.tela,
            self.batalha.desenhar,
            self.apresentar,
            self.relogio,
            fps=config.FPS,
            direcao="abrir",
        ):
            self.rodando = False

    def fechar_batalha(self) -> None:
        'Volta ao mapa após o fim do combate. Em vitória, remove o inimigo tocado.'
        # Fecha a cena de combate antes de restaurar a resolução do mapa.
        if not executar_transicao(
            self.tela,
            self.batalha.desenhar,
            self.apresentar,
            self.relogio,
            fps=config.FPS,
            direcao="fechar",
        ):
            self.rodando = False
            return

        # Vitoria com um inimigo do mapa: remove o sprite derrotado.
        if self.batalha.resultado is True and self.inimigo_em_batalha is not None:
            era_rei_tritao = getattr(self.inimigo_em_batalha, "eh_rei_tritao", False)
            self.inimigo_em_batalha.kill()

            # Derrotar o rei muda o mapa para a versao pos-boss (com o bau).
            if era_rei_tritao:
                self.rei_tritao_derrotado = True
                self.mostrar_covil_pos_boss()
            else:
                self.mensagem = 'Vitória! O inimigo foi removido e as recompensas foram aplicadas.'
        else:
            # Derrota ou fuga: o grupo volta ao mapa e nao reabre a luta no mesmo lugar.
            self.mensagem = 'O grupo retornou ao mapa após a batalha.'
            self.inimigo_ignorado = self.inimigo_em_batalha

        # Restaura a resolucao logica da cena atual.
        self.tela = self.criar_janela(config.CENA["tamanho"])
        pygame.display.set_caption("RPG Saga dos Falidos - Mapa")

        # Limpa as referencias da batalha e volta ao modo mapa.
        self.batalha = None
        self.inimigo_em_batalha = None
        self.modo = "mapa"
        tocar_musica_deepcave()

        # Revela o mapa já atualizado após a vitória, derrota ou fuga.
        if not executar_transicao(
            self.tela,
            self.desenhar_mapa,
            self.apresentar,
            self.relogio,
            fps=config.FPS,
            direcao="abrir",
        ):
            self.rodando = False

    def foto_do_mapa(self) -> pygame.Surface:
        """So o fundo do mapa atual (sem personagens), para o editor desenhar por cima."""
        if self.mapa_animado is not None:
            return self.mapa_animado.imagem.copy()
        if self.mapa_imagem is not None:
            return self.mapa_imagem.copy()
        foto = pygame.Surface(self.tela.get_size())
        desenhar_mapa_provisorio(foto)
        return foto

    def abrir_editor_colisao(self) -> None:
        'F3 em qualquer mapa: o editor de colisão abre por cima do jogo, que fica pausado.'
        # Import adiado: evita carregar o editor quando o jogador nao o usa.
        from ferramentas.editor_colisao import Editor

        # No covil o editor carrega os dois fundos (inicial e pos-boss); nos
        # outros mapas usa o fundo que esta na tela agora.
        if self.cena == "covil":
            fundos, fundo = None, ("posboss" if self.rei_tritao_derrotado else "inicial")
        else:
            nome = "arena" if self.cena == "covil_boss" else "mapa"
            fundos, fundo = {nome: self.foto_do_mapa()}, nome

        # O editor recebe a tela logica, a conversao do mouse e um callback de salvamento.
        self.editor = Editor(
            tela=self.tela,
            converter_mouse=self.mouse_na_tela,
            ao_salvar=self.aplicar_colisao_salva,
            fundo=fundo,
            cena=self.cena,
            fundos=fundos,
        )
        self.modo = "editor"

    def aplicar_colisao_salva(self) -> None:
        'Lê a colisão salva do mapa atual e passa a usá-la sem reiniciar o jogo.'
        if self.cena == "covil":
            # Covil: chao (mais o caminho pos-boss, se o Rei ja caiu), bloqueios e estatuas.
            covil_tritao.recarregar_colisao()
            config.CENA["bloqueios"] = covil_tritao.BLOQUEIOS
            config.CENA["chao"] = covil_tritao.criar_mascara_chao(pos_boss=self.rei_tritao_derrotado)
            self.oclusores = [covil_tritao.Oclusor(poligono) for poligono in covil_tritao.OCLUSORES]
            return

        # Arena do Rei e mapa de teste: cada um com o seu arquivo (colisoes_mapas).
        dados = colisoes_mapas.carregar(self.cena)
        config.CENA["bloqueios"] = colisoes_mapas.bloqueios(dados)
        self.oclusores = colisoes_mapas.oclusores(dados)
        self.poligonos_chao = [p for p in dados["chao"] if len(p) >= 3]
        if self.cena == "covil_boss":
            # Sem contorno de chao, a arena inteira continua livre.
            config.CENA["chao"] = covil_tritao.criar_mascara_chao_boss()
        else:
            # Mapa de teste: sem contorno de chao, vale a regra antiga (tudo livre).
            config.CENA["chao"] = colisoes_mapas.mascara_chao(dados["chao"], config.CENA["tamanho"])

    def fechar_editor_colisao(self) -> None:
        """Volta do editor para o mapa."""
        self.editor = None
        self.modo = "mapa"

    def entrar_no_covil(self) -> None:
        'Leva o grupo ao Covil do Rei Tritão (também é onde o jogo começa).'
        # A cena passa a ser o covil e a colisao usa os dados do mapa animado.
        self.cena = "covil"
        self.caverna_liberada = False
        self.rei_tritao_spawnado = False
        config.CENA["tamanho"] = covil_tritao.TAMANHO
        config.CENA["bloqueios"] = covil_tritao.BLOQUEIOS
        config.CENA["chao"] = covil_tritao.criar_mascara_chao()

        # Ajusta a tela logica ao tamanho do covil, se necessario.
        if self.tela.get_size() != covil_tritao.TAMANHO:
            self.tela = self.criar_janela(covil_tritao.TAMANHO)

        # Cria a animacao do mapa a partir da pasta de quadros.
        self.mapa_animado = MapaAnimado(covil_tritao.PASTA_QUADROS)

        # O fundo da batalha dos guardas e pesado: ja vai sendo lido em segundo
        # plano enquanto o grupo anda, para a primeira luta nao demorar a abrir.
        preparar_fundo_animado(FUNDO_BATALHA_GUARDAS)
        preparar_fundo_animado(FUNDO_BATALHA_REI_TRITAO)

        # Tamanhos dos sprites especificos do covil.
        tamanhos = covil_tritao.TAMANHOS_SPRITES

        # Vindo do mapa antigo (sprites de 32 px), o grupo e recriado no tamanho do covil.
        if self.cezar.tamanho != tamanhos["Cezar"]:
            for heroi in (self.cezar, self.lucas, self.guilherme):
                heroi.kill()
            self.criar_personagens(tamanhos)

        # O grupo chega pela entrada da caverna, no alto da ponte.
        for heroi in (self.cezar, self.lucas, self.guilherme):
            # Guarda a velocidade original e aplica o fator do covil.
            heroi.velocidade_base = getattr(heroi, "velocidade_base", heroi.velocidade)
            heroi.velocidade = heroi.velocidade_base * covil_tritao.FATOR_VELOCIDADE

            # Posiciona os pes na entrada e reinicia o historico de seguimento.
            posicionar_pelos_pes(heroi, covil_tritao.ENTRADA)
            heroi.historico_posicoes = [pygame.Vector2(heroi.posicao)]

            # Todos olham para oeste (para dentro da caverna).
            heroi.direcao_atual = "west"
            heroi.image = heroi.imagens_parado["west"]

        # Os guardas do rei patrulham a ponte e a plataforma do trono.
        for x, y, eixo in covil_tritao.PATRULHAS:
            guarda = InimigoPeixe(0, 0, eixo=eixo, tamanho=tamanhos["guarda"])
            guarda.velocidade *= covil_tritao.FATOR_VELOCIDADE
            posicionar_pelos_pes(guarda, (x, y))
            guarda.quantidade_combate = 3
            guarda.eh_guarda_covil = True  # ativa o fundo animado da batalha
            self.grupo_inimigos.add(guarda)
            self.grupo_objetos.add(guarda)

        # Escurece a tela no primeiro frame para um fade de entrada.
        self.escurecimento = 1.0
        self.mensagem = (
            "Covil do Rei Tritão: derrote os guardas | "
            "WASD/setas: mover | M: música | F3: editar colisão | F11: tela cheia"
        )

    def liberar_caverna_boss(self) -> None:
        """Acende a caverna do alto da ponte quando o ultimo guarda cai."""
        self.caverna_liberada = True
        self.mensagem = (
            'Todos os guardas caíram! A caverna no alto da ponte começou a brilhar...'
        )

    def entrar_no_covil_boss(self) -> None:
        'Leva o grupo à arena exclusiva do Rei Tritão.'
        # A colisao da arena vem do arquivo dela (editavel com F3); sem arquivo,
        # a arena ocupa a tela toda e nao tem obstaculos.
        self.cena = "covil_boss"
        config.CENA["tamanho"] = covil_tritao.TAMANHO

        # Carrega o video do novo mapa; chao, bloqueios e estatuas sao os da arena.
        self.mapa_animado = MapaAnimado(covil_tritao.PASTA_QUADROS_BOSS)
        self.aplicar_colisao_salva()

        # Garante que a tela lógica já está no tamanho da arena.
        if self.tela.get_size() != covil_tritao.TAMANHO:
            self.tela = self.criar_janela(covil_tritao.TAMANHO)

        # O grupo chega por baixo, de frente para o trono do rei.
        for heroi in (self.cezar, self.lucas, self.guilherme):
            posicionar_pelos_pes(heroi, covil_tritao.ENTRADA_BOSS)
            heroi.historico_posicoes = [pygame.Vector2(heroi.posicao)]
            heroi.direcao_atual = "north"
            heroi.image = heroi.imagens_parado["north"]

        # Fade de entrada e cria o chefe no centro da arena.
        self.escurecimento = 1.0
        self.mensagem = 'Arena do Rei Tritão: não há escapatória!'
        self.surgir_rei_tritao()

    def surgir_rei_tritao(self) -> None:
        """Cria o chefe na arena exclusiva dele."""
        # O rei usa o sprite maior definido em covil_tritao.
        rei = ReiTritaoMapa(0, 0, tamanho=covil_tritao.TAMANHOS_SPRITES["rei"])
        posicionar_pelos_pes(rei, covil_tritao.POSICAO_REI_BOSS)

        # Entra nos grupos de combate e de desenho.
        self.grupo_inimigos.add(rei)
        self.grupo_objetos.add(rei)
        self.rei_tritao_spawnado = True

        # Avisa o jogador da nova ameaca.
        self.mensagem = 'A água estremece... O REI TRITÃO surgiu diante do trono!'

    def mostrar_covil_pos_boss(self) -> None:
        'Volta ao covil pós-chefe, com a ponte até o baú liberada.'
        # A arena do chefe some e o covil antigo volta na versão pos-boss.
        self.cena = "covil"
        config.CENA["tamanho"] = covil_tritao.TAMANHO
        config.CENA["bloqueios"] = covil_tritao.BLOQUEIOS
        self.mapa_animado = MapaAnimado(covil_tritao.PASTA_QUADROS_POSBOSS)

        # O chao agora inclui a passagem que leva ao bau.
        config.CENA["chao"] = covil_tritao.criar_mascara_chao(pos_boss=True)

        # Restaura as estatuas e a caverna deixa de brilhar.
        self.oclusores = [
            covil_tritao.Oclusor(poligono) for poligono in covil_tritao.OCLUSORES
        ]
        self.caverna_liberada = False

        # O grupo reaparece onde o rei estava, já perto do caminho do baú.
        for heroi in (self.cezar, self.lucas, self.guilherme):
            posicionar_pelos_pes(heroi, covil_tritao.POSICAO_REI)
            heroi.historico_posicoes = [pygame.Vector2(heroi.posicao)]
            heroi.direcao_atual = "east"
            heroi.image = heroi.imagens_parado["east"]

        # Fade e mensagem de vitoria.
        self.escurecimento = 1.0
        self.mensagem = 'O REI TRITÃO FOI DERROTADO! Um caminho de pedra agora leva até o baú!'

    def pode_abrir_bau(self) -> bool:
        'O baú só abre depois do chefe, uma vez, com o líder perto dele.'
        # Tres condicoes: estar no covil, ter vencido o rei e ainda nao ter aberto.
        if self.cena != "covil" or not self.rei_tritao_derrotado or self.bau_aberto:
            return False

        # Mede a distancia entre os pes do lider e a posicao do bau.
        pes = pygame.Vector2(
            self.cezar.rect.centerx,
            self.cezar.rect.top + altura_dos_pes(self.cezar),
        )
        return pes.distance_to(covil_tritao.POSICAO_BAU) <= covil_tritao.ALCANCE_BAU

    def fechar_recompensa(self) -> None:
        """Fecha a tela do bau e volta ao mapa."""
        self.bau_aberto = True
        self.recompensa = None
        self.modo = "mapa"
        self.mensagem = 'Baú aberto! O tesouro supremo era um bolo... e um aviso.'
