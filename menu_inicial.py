"""Menu inicial: "A Saga dos Falidos".

Primeira tela do jogo. O título e os botões são desenhados por código (para
serem clicáveis e o texto sair sempre certo); o fundo é uma arte:

- assets/menu/fundo_menu.png (ou .jpg): imagem parada; ou
- assets/mapas_animados/menu_inicial/: vídeo convertido com
  `python ferramentas/converter_video_mapa.py "video.mp4" menu_inicial`.

Sem nenhuma dos dois, usa o covil escurecido como fundo provisório.

Controles: setas (ou W/S) escolhem, Enter/Espaço confirmam, mouse também
funciona. Esc volta das telas de opções e créditos.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import pygame

from mapa_animado import MapaAnimado

PASTA_PROJETO = Path(__file__).resolve().parent
FUNDOS_IMAGEM = [PASTA_PROJETO / "assets" / "menu" / nome for nome in ("fundo_menu.png", "fundo_menu.jpg")]
FUNDO_VIDEO = PASTA_PROJETO / "assets" / "mapas_animados" / "menu_inicial"
FUNDO_PROVISORIO = PASTA_PROJETO / "assets" / "mapas_animados" / "mapa_tritao"

TITULO = "A Saga dos Falidos"
SUBTITULO = "Crônicas de Eldoria"

# Pontos mágicos do mapa de Eldoria (fundo_menu.jpg) que brilham no menu:
# (x, y em fração da imagem, cor, raio em px na imagem). Se trocar a imagem,
# ajuste ou esvazie esta lista.
BRILHOS_FUNDO = [
    (0.832, 0.125, (170, 70, 255), 70),   # portal da Dimensão do Esquecimento
    (0.173, 0.531, (190, 80, 255), 26),   # estrela das Terras Corrompidas
    (0.136, 0.836, (255, 210, 90), 20),   # estrela da Torre da Balança
    (0.618, 0.427, (255, 210, 90), 18),   # estrela da Vila dos Pinheiros
]
# Segundos de uma ida e volta da câmera percorrendo o mapa.
PERIODO_CAMERA = 50.0
CREDITOS = [
    ("Equipe", ["Antonio Cezar", "Guilherme Machado", "Diego", "Lucas Soares"]),
    ("Projeto", ["Projeto de Extensão — APS 2"]),
]

FONTES_TITULO = "georgia,palatinolinotype,bookantiqua,timesnewroman"
FONTES_BOTAO = "georgia,palatinolinotype,bookantiqua,timesnewroman"

COR_OURO = (232, 186, 92)
COR_OURO_CLARO = (255, 236, 170)
COR_OURO_ESCURO = (150, 96, 30)
COR_CONTORNO = (28, 14, 4)
COR_TEXTO = (236, 228, 206)
COR_DESATIVADO = (130, 126, 118)

TECLAS_CIMA = (pygame.K_UP, pygame.K_w)
TECLAS_BAIXO = (pygame.K_DOWN, pygame.K_s)
TECLAS_CONFIRMAR = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


def texto_dourado(fonte: pygame.font.Font, texto: str, espessura: int = 3) -> pygame.Surface:
    """Texto em ouro: degradê claro em cima e escuro embaixo, contorno e sombra."""
    base = fonte.render(texto, True, (255, 255, 255))
    degrade = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    altura = base.get_height()
    for y in range(altura):
        t = y / max(1, altura - 1)
        # Claro até o meio, com um reflexo, e escurecendo para baixo.
        if t < 0.5:
            cor = [round(COR_OURO_CLARO[i] + (COR_OURO[i] - COR_OURO_CLARO[i]) * t / 0.5) for i in range(3)]
        else:
            cor = [round(COR_OURO[i] + (COR_OURO_ESCURO[i] - COR_OURO[i]) * (t - 0.5) / 0.5) for i in range(3)]
        pygame.draw.line(degrade, (*cor, 255), (0, y), (base.get_width(), y))
    base.blit(degrade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    contorno = fonte.render(texto, True, COR_CONTORNO)
    sombra = fonte.render(texto, True, (0, 0, 0))
    folga = espessura + 6
    resultado = pygame.Surface((base.get_width() + 2 * folga, base.get_height() + 2 * folga), pygame.SRCALPHA)
    sombra.set_alpha(150)
    resultado.blit(sombra, (folga + 3, folga + 5))
    for dx in range(-espessura, espessura + 1):
        for dy in range(-espessura, espessura + 1):
            if dx * dx + dy * dy <= espessura * espessura:
                resultado.blit(contorno, (folga + dx, folga + dy))
    resultado.blit(base, (folga, folga))
    return resultado


def brilho_de(superficie: pygame.Surface, cor, reducao: int = 6) -> pygame.Surface:
    """Versão borrada e colorida do contorno de uma imagem (para o brilho em volta)."""
    pequena = pygame.transform.smoothscale(
        superficie, (max(1, superficie.get_width() // reducao), max(1, superficie.get_height() // reducao))
    )
    borrada = pygame.transform.smoothscale(pequena, superficie.get_size())
    colorida = pygame.Surface(superficie.get_size())
    colorida.fill(cor)
    mascara = pygame.Surface(superficie.get_size())
    mascara.blit(borrada, (0, 0))
    colorida.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return colorida


def desenhar_ornamento(tela: pygame.Surface, centro: tuple[int, int], largura: int, cor=COR_OURO) -> None:
    """Linha fina dourada que some nas pontas, com um losango e dois pontos no meio."""
    cx, cy = centro
    linha = pygame.Surface((largura, 3), pygame.SRCALPHA)
    metade = largura / 2
    for x in range(largura):
        distancia = abs(x - metade) / metade
        alfa = round(230 * max(0.0, 1 - distancia) ** 1.3)
        linha.set_at((x, 1), (*cor, alfa))
        linha.set_at((x, 0), (*COR_OURO_CLARO, alfa // 3))
    tela.blit(linha, (cx - largura // 2, cy - 1))
    losango = [(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)]
    pygame.draw.polygon(tela, COR_CONTORNO, [(x + (1 if x > cx else -1 if x < cx else 0), y + (1 if y > cy else -1 if y < cy else 0)) for x, y in losango])
    pygame.draw.polygon(tela, cor, losango)
    pygame.draw.polygon(tela, COR_OURO_CLARO, [(cx, cy - 5), (cx + 3, cy), (cx, cy + 1), (cx - 3, cy)])
    for lado in (-1, 1):
        pygame.draw.circle(tela, cor, (cx + lado * 20, cy), 2)
        pygame.draw.circle(tela, cor, (cx + lado * 30, cy), 1)


def texto_contornado(fonte: pygame.font.Font, texto: str, cor, cor_contorno, espessura: int = 2) -> pygame.Surface:
    base = fonte.render(texto, True, cor)
    contorno = fonte.render(texto, True, cor_contorno)
    resultado = pygame.Surface((base.get_width() + 2 * espessura, base.get_height() + 2 * espessura), pygame.SRCALPHA)
    for dx in range(-espessura, espessura + 1):
        for dy in range(-espessura, espessura + 1):
            if dx or dy:
                resultado.blit(contorno, (dx + espessura, dy + espessura))
    resultado.blit(base, (espessura, espessura))
    return resultado


class Botao:
    def __init__(self, texto: str, acao: str, ativo: bool = True, dica: str = ""):
        self.texto = texto
        self.acao = acao
        self.ativo = ativo
        self.dica = dica
        self.retangulo = pygame.Rect(0, 0, 0, 0)


class MenuInicial:
    def __init__(
        self, converter_mouse=None, alternar_tela_cheia=None, tela_cheia=lambda: False,
        pode_continuar: bool = False, pausa_sobre: pygame.Surface | None = None,
    ):
        """`converter_mouse` traduz o mouse da janela para a tela lógica do jogo;
        `alternar_tela_cheia`/`tela_cheia` ligam a opção de tela cheia ao jogo.

        `pode_continuar` libera o CONTINUAR (há uma partida em andamento).
        Com `pausa_sobre` (uma foto da tela do jogo), vira o menu de pausa (Esc).

        Ao escolher, `escolha` recebe: "novo_jogo", "continuar", "retomar",
        "menu_principal" ou "sair"."""
        self.converter_mouse = converter_mouse or (lambda posicao: posicao)
        self.alternar_tela_cheia = alternar_tela_cheia
        self.tela_cheia = tela_cheia
        self.pode_continuar = pode_continuar
        self.pausa_sobre = pausa_sobre
        self.escolha: str | None = None
        self.inicio = "pausa" if pausa_sobre is not None else "principal"
        self.tela_atual = self.inicio
        self.indice = 0
        self.tempo = 0.0
        self.brasas: list[list[float]] = []  # [x, y, velocidade, fase, tamanho]

        self.fonte_titulo = pygame.font.SysFont(FONTES_TITULO, 76, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont(FONTES_TITULO, 24, italic=True)
        self.fonte_botao = pygame.font.SysFont(FONTES_BOTAO, 30, bold=True)
        self.fonte_dica = pygame.font.SysFont(FONTES_BOTAO, 16, italic=True)
        self.fonte_texto = pygame.font.SysFont(FONTES_BOTAO, 24)
        self.fonte_rodape = pygame.font.SysFont(None, 20)

        self.fundo_imagem: pygame.Surface | None = None
        self.fundo_animado: MapaAnimado | None = None
        self.fundo_provisorio = False
        self.carregar_fundo()
        self._cache_fundo: tuple[tuple[int, int], pygame.Surface] | None = None
        self._nevoa: pygame.Surface | None = None
        self._vinheta: pygame.Surface | None = None
        self._brilhos: dict = {}
        self._titulo: tuple[pygame.Surface, pygame.Surface] | None = None
        self._faixa: pygame.Surface | None = None
        self._textos: dict[tuple[str, str], pygame.Surface] = {}
        self._sombras: dict = {}

    # ----------------------------------------------------------------- fundo
    def carregar_fundo(self) -> None:
        if self.pausa_sobre is not None:
            return  # na pausa, o fundo é a própria tela do jogo, congelada
        imagem = next((caminho for caminho in FUNDOS_IMAGEM if caminho.is_file()), None)
        if imagem is not None:
            self.fundo_imagem = pygame.image.load(imagem).convert()
        elif (FUNDO_VIDEO / "info.json").is_file():
            self.fundo_animado = MapaAnimado(FUNDO_VIDEO)
        elif (FUNDO_PROVISORIO / "info.json").is_file():
            self.fundo_animado = MapaAnimado(FUNDO_PROVISORIO)
            self.fundo_provisorio = True

    def desenhar_fundo(self, tela: pygame.Surface) -> None:
        tamanho = tela.get_size()
        if self.pausa_sobre is not None:
            # Pausa: o jogo congelado ao fundo, bem escurecido.
            fundo = self.pausa_sobre
            if fundo.get_size() != tamanho:
                fundo = pygame.transform.smoothscale(fundo, tamanho)
            tela.blit(fundo, (0, 0))
            veu = pygame.Surface(tamanho, pygame.SRCALPHA)
            veu.fill((6, 4, 16, 205))
            tela.blit(veu, (0, 0))
            return
        if self.fundo_imagem is not None:
            self.desenhar_mapa_do_mundo(tela)
            tela.blit(self.vinheta(tamanho), (0, 0))
            return
        if self.fundo_animado is not None:
            imagem = self.fundo_animado.imagem
            if imagem.get_size() != tamanho:
                imagem = pygame.transform.smoothscale(imagem, tamanho)
            tela.blit(imagem, (0, 0))
        else:
            tela.fill((12, 10, 24))
        # O fundo provisório (o covil) é escurecido para o título se destacar.
        veu = pygame.Surface(tamanho, pygame.SRCALPHA)
        veu.fill((6, 4, 16, 150 if self.fundo_provisorio else 60))
        tela.blit(veu, (0, 0))

    def desenhar_mapa_do_mundo(self, tela: pygame.Surface) -> None:
        """Imagem parada (o mapa de Eldoria) com a câmera passeando devagar por ela."""
        largura, altura = tela.get_size()
        if self._cache_fundo is None or self._cache_fundo[0] != (largura, altura):
            # Amplia até cobrir a tela inteira (com uma folga para a câmera andar).
            escala = max(largura / self.fundo_imagem.get_width(), altura / self.fundo_imagem.get_height()) * 1.04
            tamanho = (round(self.fundo_imagem.get_width() * escala), round(self.fundo_imagem.get_height() * escala))
            self._cache_fundo = ((largura, altura), pygame.transform.smoothscale(self.fundo_imagem, tamanho))
        imagem = self._cache_fundo[1]
        sobra_x, sobra_y = imagem.get_width() - largura, imagem.get_height() - altura
        # Vai e volta suave (cosseno): para devagar nas pontas, sem tranco.
        ida = (1 - math.cos(self.tempo * 2 * math.pi / PERIODO_CAMERA)) / 2
        deslocamento = (-sobra_x * (0.5 + 0.5 * (ida - 0.5)), -sobra_y * ida)
        tela.blit(imagem, deslocamento)
        self.desenhar_brilhos(tela, imagem, deslocamento)
        self.desenhar_nevoa(tela)

    def brilho_base(self, cor, raio: int) -> pygame.Surface:
        """Luz redonda: forte no centro e sumindo até o preto na borda (para somar)."""
        chave = (cor, raio)
        if chave not in self._brilhos:
            brilho = pygame.Surface((raio * 2, raio * 2))
            for r in range(raio, 0, -1):
                intensidade = (1 - r / raio) ** 2
                pygame.draw.circle(brilho, [round(c * intensidade) for c in cor], (raio, raio), r)
            self._brilhos[chave] = brilho
        return self._brilhos[chave]

    def desenhar_brilhos(self, tela: pygame.Surface, imagem: pygame.Surface, deslocamento) -> None:
        escala = imagem.get_width() / self.fundo_imagem.get_width()
        for n, (fx, fy, cor, raio) in enumerate(BRILHOS_FUNDO):
            centro = (fx * imagem.get_width() + deslocamento[0], fy * imagem.get_height() + deslocamento[1])
            pulso = (math.sin(self.tempo * (1.6 + 0.3 * n) + n) + 1) / 2
            r = max(4, round(raio * escala * 1.6))
            brilho = self.brilho_base(cor, r).copy()
            forca = round(150 + 105 * pulso)
            brilho.fill((forca, forca, forca), special_flags=pygame.BLEND_RGB_MULT)
            tela.blit(brilho, (centro[0] - r, centro[1] - r), special_flags=pygame.BLEND_RGB_ADD)

    def desenhar_nevoa(self, tela: pygame.Surface) -> None:
        """Faixas de névoa clara atravessando o mapa bem devagar."""
        largura, altura = tela.get_size()
        if self._nevoa is None or self._nevoa.get_height() != altura:
            self._nevoa = pygame.Surface((largura * 2, altura), pygame.SRCALPHA)
            aleatorio = random.Random(7)  # sempre a mesma névoa
            for _ in range(26):
                w = aleatorio.randint(220, 520)
                h = aleatorio.randint(40, 110)
                x = aleatorio.randint(0, largura * 2 - w)
                y = aleatorio.randint(0, altura - h)
                nuvem = pygame.Surface((w, h), pygame.SRCALPHA)
                for passo in range(6, 0, -1):
                    caixa = nuvem.get_rect().inflate(-w * (6 - passo) // 7, -h * (6 - passo) // 7)
                    pygame.draw.ellipse(nuvem, (225, 230, 245, 7), caixa)
                self._nevoa.blit(nuvem, (x, y))
        x = -((self.tempo * 12) % largura)
        tela.blit(self._nevoa, (x, 0))

    def vinheta(self, tamanho: tuple[int, int]) -> pygame.Surface:
        """Bordas e faixas do título/botões mais escuras, para o texto ler bem."""
        if self._vinheta is None or self._vinheta.get_size() != tamanho:
            largura, altura = tamanho
            self._vinheta = pygame.Surface(tamanho, pygame.SRCALPHA)
            for y in range(altura):
                t = y / altura
                # Escuro em cima (título) e embaixo (botões), mais claro no meio.
                alfa = 70 + 90 * max(0.0, 1 - t / 0.38) ** 2 + 150 * max(0.0, (t - 0.42) / 0.58) ** 1.6
                pygame.draw.line(self._vinheta, (6, 4, 16, min(235, round(alfa))), (0, y), (largura, y))
            bordas = pygame.Surface(tamanho, pygame.SRCALPHA)
            for passo in range(14):
                pygame.draw.rect(bordas, (0, 0, 0, 9), bordas.get_rect().inflate(-passo * 22, -passo * 14), 12)
            self._vinheta.blit(bordas, (0, 0))
        return self._vinheta

    def desenhar_brasas(self, tela: pygame.Surface) -> None:
        largura, altura = tela.get_size()
        for x, y, _, fase, tamanho in self.brasas:
            brilho = (math.sin(self.tempo * 3 + fase) + 1) / 2
            cor = (255, 120 + int(80 * brilho), 60, int(90 + 120 * brilho))
            ponto = pygame.Surface((tamanho * 4, tamanho * 4), pygame.SRCALPHA)
            pygame.draw.circle(ponto, (cor[0], cor[1], cor[2], cor[3] // 4), (tamanho * 2, tamanho * 2), tamanho * 2)
            pygame.draw.circle(ponto, cor, (tamanho * 2, tamanho * 2), max(1, tamanho // 2 + 1))
            tela.blit(ponto, (x * largura - tamanho * 2, y * altura - tamanho * 2))

    # ------------------------------------------------------------- botões
    def botoes(self) -> list[Botao]:
        if self.tela_atual == "principal":
            if self.pode_continuar:
                continuar = Botao("CONTINUAR", "continuar")
            else:
                continuar = Botao("CONTINUAR", "continuar", ativo=False, dica="nenhuma partida em andamento")
            return [
                Botao("NOVO JOGO", "novo_jogo"),
                continuar,
                Botao("OPÇÕES", "opcoes"),
                Botao("CRÉDITOS", "creditos"),
            ]
        if self.tela_atual == "pausa":
            return [
                Botao("CONTINUAR", "retomar"),
                Botao("CONFIGURAÇÕES", "opcoes"),
                Botao("MENU PRINCIPAL", "menu_principal"),
                Botao("SAIR DO JOGO", "sair"),
            ]
        if self.tela_atual == "opcoes":
            from batalha_core.temas import nome_do_tema

            from Musicas import musica_ligada

            cheia = "Sim" if self.tela_cheia() else "Não"
            musica = "Ligada" if musica_ligada() else "Desligada"
            return [
                Botao(f"Música: {musica}", "musica"),
                Botao(f"Tela cheia: {cheia}", "tela_cheia", ativo=self.alternar_tela_cheia is not None),
                Botao(f"Visual da batalha: {nome_do_tema()}", "tema"),
                Botao("VOLTAR", "voltar"),
            ]
        return [Botao("VOLTAR", "voltar")]

    def layout(self, tela: pygame.Surface) -> tuple[pygame.Rect, list[Botao]]:
        """Área do título e botões, posicionados pela proporção da tela."""
        largura, altura = tela.get_size()
        banner = pygame.Rect(0, 0, min(760, largura - 80), 150)
        banner.midtop = (largura // 2, round(altura * 0.11))
        botoes = self.botoes()
        largura_botao = min(400, largura - 120)
        altura_botao = 52
        espaco = 10
        if self.tela_atual == "creditos":
            topo = altura - 120
        else:
            total = len(botoes) * altura_botao + (len(botoes) - 1) * espaco
            topo = max(banner.bottom + 40, round(altura * 0.62 - total / 2))
        for n, botao in enumerate(botoes):
            botao.retangulo = pygame.Rect(0, 0, largura_botao, altura_botao)
            botao.retangulo.midtop = (largura // 2, topo + n * (altura_botao + espaco))
        return banner, botoes

    # ------------------------------------------------------------- eventos
    def mover_selecao(self, passo: int, botoes: list[Botao]) -> None:
        for _ in range(len(botoes)):
            self.indice = (self.indice + passo) % len(botoes)
            if botoes[self.indice].ativo:
                return

    def confirmar(self, botao: Botao) -> None:
        if not botao.ativo:
            return
        if botao.acao in ("novo_jogo", "continuar", "retomar", "menu_principal", "sair"):
            self.escolha = botao.acao  # quem decide o que fazer é o jogo
        elif botao.acao in ("opcoes", "creditos"):
            self.tela_atual = botao.acao
            self.indice = 0
        elif botao.acao == "voltar":
            # Volta para a tela de onde veio, com o cursor no botão que levou até aqui.
            if self.inicio == "pausa":
                self.indice = 1
            else:
                self.indice = {"opcoes": 2, "creditos": 3}.get(self.tela_atual, 0)
            self.tela_atual = self.inicio
        elif botao.acao == "musica":
            from Musicas import alternar_musica

            alternar_musica()
        elif botao.acao == "tela_cheia":
            self.alternar_tela_cheia()
        elif botao.acao == "tema":
            from batalha_core.temas import alternar_tema

            alternar_tema()

    def processar_evento(self, evento: pygame.event.Event, tela: pygame.Surface) -> None:
        _, botoes = self.layout(tela)
        if evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_CIMA:
                self.mover_selecao(-1, botoes)
            elif evento.key in TECLAS_BAIXO:
                self.mover_selecao(1, botoes)
            elif evento.key in TECLAS_CONFIRMAR and not (evento.mod & pygame.KMOD_ALT):
                self.confirmar(botoes[min(self.indice, len(botoes) - 1)])
            elif evento.key == pygame.K_ESCAPE:
                if self.tela_atual == "pausa":
                    self.escolha = "retomar"  # Esc de novo volta a jogar
                elif self.tela_atual != "principal":
                    self.confirmar(Botao("", "voltar"))
        elif evento.type == pygame.MOUSEMOTION:
            posicao = self.converter_mouse(evento.pos)
            for n, botao in enumerate(botoes):
                if botao.ativo and botao.retangulo.collidepoint(posicao):
                    self.indice = n
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            posicao = self.converter_mouse(evento.pos)
            for n, botao in enumerate(botoes):
                if botao.retangulo.collidepoint(posicao):
                    self.indice = n
                    self.confirmar(botao)
                    break

    def atualizar(self, tempo_frame: float) -> None:
        self.tempo += tempo_frame
        if self.fundo_animado is not None:
            self.fundo_animado.atualizar(tempo_frame)
        # Brasas subindo devagar (posições em fração da tela).
        if len(self.brasas) < 40 and random.random() < 0.35:
            self.brasas.append([random.random(), 1.05, random.uniform(0.02, 0.06), random.uniform(0, 6.3), random.randint(2, 4)])
        for brasa in self.brasas:
            brasa[1] -= brasa[2] * tempo_frame
            brasa[0] += math.sin(self.tempo + brasa[3]) * 0.0006
        self.brasas = [brasa for brasa in self.brasas if brasa[1] > -0.05]

    # -------------------------------------------------------------- desenho
    def titulo_pronto(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Título dourado e o brilho dele, montados uma vez só."""
        if self._titulo is None:
            titulo = texto_dourado(self.fonte_titulo, TITULO, espessura=3)
            self._titulo = (titulo, brilho_de(titulo, (255, 190, 90)))
        return self._titulo

    def sombra_suave(self, tamanho: tuple[int, int], forca: int = 215) -> pygame.Surface:
        """Mancha escura oval, sem borda, que some aos poucos: separa o texto do mapa."""
        chave = (*tamanho, forca)
        if chave not in self._sombras:
            pequena = pygame.Surface((64, 32), pygame.SRCALPHA)
            for y in range(32):
                for x in range(64):
                    d = math.hypot((x - 31.5) / 32, (y - 15.5) / 16)
                    # Quase uniforme no miolo e sumindo só perto da borda.
                    pequena.set_at((x, y), (4, 3, 12, round(forca * min(1.0, max(0.0, 1 - d) * 1.8) ** 1.2)))
            self._sombras[chave] = pygame.transform.smoothscale(pequena, tamanho)
        return self._sombras[chave]

    def desenhar_banner(self, tela: pygame.Surface, banner: pygame.Rect) -> None:
        """Título sem placa: ouro sobre o mapa, com brilho pulsando e ornamentos."""
        sombra = self.sombra_suave((banner.width + 260, banner.height + 150))
        tela.blit(sombra, sombra.get_rect(center=(banner.centerx, banner.centery + 4)))
        titulo, brilho = self.titulo_pronto()
        centro = (banner.centerx, banner.top + 58)
        pulso = (math.sin(self.tempo * 1.4) + 1) / 2
        luz = brilho.copy()
        forca = round(70 + 60 * pulso)
        luz.fill((forca, forca, forca), special_flags=pygame.BLEND_RGB_MULT)
        tela.blit(luz, luz.get_rect(center=centro), special_flags=pygame.BLEND_RGB_ADD)
        tela.blit(titulo, titulo.get_rect(center=centro))

        largura_ornamento = min(560, titulo.get_width() + 40)
        desenhar_ornamento(tela, (banner.centerx, banner.top - 4), largura_ornamento)
        texto_subtitulo = "Jogo pausado" if self.pausa_sobre is not None else SUBTITULO
        subtitulo = texto_contornado(self.fonte_subtitulo, texto_subtitulo, (226, 212, 176), COR_CONTORNO, 2)
        y_sub = centro[1] + titulo.get_height() // 2 + 4
        tela.blit(subtitulo, subtitulo.get_rect(center=(banner.centerx, y_sub)))
        desenhar_ornamento(tela, (banner.centerx, y_sub + 26), round(largura_ornamento * 0.7))

    def texto_do_botao(self, texto: str, estado: str) -> pygame.Surface:
        """Textos das opções já prontos (montar o dourado a cada quadro pesaria)."""
        chave = (texto, estado)
        if chave not in self._textos:
            if estado == "escolhido":
                pronto = texto_dourado(self.fonte_botao, texto, espessura=2)
            elif estado == "dica":
                pronto = texto_contornado(self.fonte_dica, texto, COR_DESATIVADO, COR_CONTORNO, 1)
            else:
                cor = COR_TEXTO if estado == "normal" else COR_DESATIVADO
                pronto = texto_contornado(self.fonte_botao, texto, cor, COR_CONTORNO, 2)
            self._textos[chave] = pronto
        return self._textos[chave]

    def faixa_de_luz(self, tamanho: tuple[int, int]) -> pygame.Surface:
        """Faixa dourada translúcida atrás da opção escolhida, sumindo nas pontas."""
        if self._faixa is None or self._faixa.get_size() != tamanho:
            largura, altura = tamanho
            self._faixa = pygame.Surface(tamanho, pygame.SRCALPHA)
            for x in range(largura):
                horizontal = max(0.0, 1 - abs(x - largura / 2) / (largura / 2)) ** 1.5
                for y in range(altura):
                    vertical = max(0.0, 1 - abs(y - altura / 2) / (altura / 2)) ** 1.2
                    self._faixa.set_at((x, y), (255, 196, 90, round(165 * horizontal * vertical)))
            for x in range(largura):  # filetes finos em cima e embaixo
                alfa = round(200 * max(0.0, 1 - abs(x - largura / 2) / (largura / 2)) ** 1.3)
                self._faixa.set_at((x, 2), (*COR_OURO_CLARO, alfa))
                self._faixa.set_at((x, altura - 3), (*COR_OURO_CLARO, alfa))
        return self._faixa

    def desenhar_botao(self, tela: pygame.Surface, botao: Botao, selecionado: bool) -> None:
        """Opção só em texto; a escolhida ganha faixa de luz, ouro e losangos."""
        r = botao.retangulo
        escolhido = selecionado and botao.ativo
        centro_y = r.centery - (8 if botao.dica else 0)
        if escolhido:
            faixa = self.faixa_de_luz((r.width + 80, r.height))
            faixa = faixa.copy()
            faixa.set_alpha(round(200 + 55 * (math.sin(self.tempo * 4) + 1) / 2))
            tela.blit(faixa, faixa.get_rect(center=r.center))
        estado = "escolhido" if escolhido else "normal" if botao.ativo else "desativado"
        texto = self.texto_do_botao(botao.texto, estado)
        tela.blit(texto, texto.get_rect(center=(r.centerx, centro_y)))
        if botao.dica:
            dica = self.texto_do_botao(botao.dica, "dica")
            tela.blit(dica, dica.get_rect(center=(r.centerx, r.bottom - 9)))
        if escolhido:
            # Losangos dos dois lados, balançando de leve.
            balanco = round(3 * math.sin(self.tempo * 5))
            meia = texto.get_width() // 2
            for lado in (-1, 1):
                x = r.centerx + lado * (meia + 18 + balanco)
                losango = [(x, centro_y - 7), (x + 7, centro_y), (x, centro_y + 7), (x - 7, centro_y)]
                pygame.draw.polygon(tela, COR_CONTORNO, [(px + (1 if px > x else -1 if px < x else 0), py + (1 if py > centro_y else -1 if py < centro_y else 0)) for px, py in losango])
                pygame.draw.polygon(tela, COR_OURO, losango)
                pygame.draw.polygon(tela, COR_OURO_CLARO, [(x, centro_y - 4), (x + 2, centro_y), (x, centro_y + 1), (x - 2, centro_y)])

    def desenhar_creditos(self, tela: pygame.Surface, banner: pygame.Rect) -> None:
        painel = pygame.Rect(0, 0, min(640, tela.get_width() - 100), 0)
        linhas = sum(1 + len(nomes) for _, nomes in CREDITOS) + len(CREDITOS) - 1
        painel.height = 60 + linhas * 34
        painel.midtop = (tela.get_width() // 2, banner.bottom + 30)
        # Mesmo estilo do resto do menu: sem caixa, só uma sombra suave por trás.
        sombra = self.sombra_suave((painel.width + 200, painel.height + 120))
        tela.blit(sombra, sombra.get_rect(center=painel.center))
        y = painel.top + 24
        for n, (secao, nomes) in enumerate(CREDITOS):
            if n:
                desenhar_ornamento(tela, (painel.centerx, y + 14), 260)
                y += 34
            titulo = self.texto_do_botao(secao, "escolhido")
            tela.blit(titulo, titulo.get_rect(midtop=(painel.centerx, y - 6)))
            y += 38
            for nome in nomes:
                texto = texto_contornado(self.fonte_texto, nome, COR_TEXTO, COR_CONTORNO, 2)
                tela.blit(texto, texto.get_rect(midtop=(painel.centerx, y)))
                y += 32

    def desenhar(self, tela: pygame.Surface) -> None:
        self.desenhar_fundo(tela)
        if self.pausa_sobre is None:
            self.desenhar_brasas(tela)
        banner, botoes = self.layout(tela)
        self.desenhar_banner(tela, banner)
        if self.tela_atual == "creditos":
            self.desenhar_creditos(tela, banner)
        self.indice = min(self.indice, len(botoes) - 1)
        if self.tela_atual != "creditos":
            coluna = botoes[0].retangulo.unionall([b.retangulo for b in botoes[1:]])
            sombra = self.sombra_suave((coluna.width + 260, coluna.height + 140))
            tela.blit(sombra, sombra.get_rect(center=coluna.center))
        for n, botao in enumerate(botoes):
            self.desenhar_botao(tela, botao, n == self.indice)
        if self.tela_atual == "pausa":
            rodape = "Setas: escolher   Enter: confirmar   Esc: voltar a jogar   M: música   F11: tela cheia"
        else:
            rodape = "Setas: escolher   Enter: confirmar   Esc: voltar   M: música   F11: tela cheia"
        texto = self.fonte_rodape.render(rodape, True, (190, 186, 200))
        tela.blit(texto, texto.get_rect(midbottom=(tela.get_width() // 2, tela.get_height() - 12)))


# Rodar este arquivo direto (botão ▶ do VS Code) abre o jogo pelo menu, igual a
# `python mapa_teste.py`.
if __name__ == "__main__":
    from mapa_jogo import Jogo

    Jogo().executar()
