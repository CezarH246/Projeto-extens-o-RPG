"""Editor visual da colisão do Covil do Rei Tritão.

Uso (na pasta do projeto):
    python ferramentas/editor_colisao.py

Abre o mapa do covil com a colisão por cima. Tudo é feito com o mouse; os
botões do topo trocam o tipo de área e uma dica ao lado do cursor diz o que o
clique vai fazer. Salva em assets/mapas_animados/colisao_covil.json, que o
jogo lê ao abrir.

Tipos de área (botões do topo ou teclas 1 a 4):
  1  Chão              onde dá para andar (os pés precisam estar dentro)
  2  Chão pós-boss     chão que só vale depois de derrotar o Rei Tritão
  3  Bloqueio          retângulo que não dá para atravessar (base de estátua, baú)
  4  Passar por trás   contorno de um objeto alto (estátua): quem anda atrás
                       dele fica escondido; a linha amarela é a base

Testar (T): coloca o Cezar onde o mouse está para andar com WASD/setas usando a
mesma colisão do jogo. T de novo volta a editar.

Dentro do jogo: no covil, F3 abre este editor por cima do jogo (pausado);
Ctrl+S salva e a colisão nova já vale; F3 ou Esc voltam a jogar.

Atalhos: Ctrl+S salva, Ctrl+Z desfaz, N começa um contorno novo, Delete apaga o
selecionado, Tab troca o fundo (inicial/pós-boss), F liga/desliga o
preenchimento, H esconde a ajuda, Esc sai.
"""

from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import pygame

PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO))

import covil_tritao  # noqa: E402
from CezarPersonagem import Cezar  # noqa: E402

# Regras de colisão do jogo (mapa_teste), carregadas só ao entrar no modo de
# teste: dentro do jogo o editor não usa o teste, e importar o jogo de novo
# por aqui criaria uma segunda cópia dele.
mapa_teste = None

LARGURA, ALTURA = covil_tritao.TAMANHO

# chave no JSON: (nome no botão, cor, é contorno? (senão retângulo), explicação)
CAMADAS = {
    "chao": (
        "Chão", (0, 255, 120), True,
        "Onde dá para andar. Os pés do personagem precisam ficar dentro de um contorno verde.",
    ),
    "chao_posboss": (
        "Chão pós-boss", (0, 200, 255), True,
        "Chão que só passa a valer depois do Rei Tritão (o caminho até o baú). Fundo: mapa pós-boss.",
    ),
    "bloqueios": (
        "Bloqueio", (255, 140, 0), False,
        "Não dá para atravessar, mesmo em cima do chão: base de estátua, trono, baú. Use na BASE do objeto.",
    ),
    "oclusores": (
        "Passar por trás", (200, 110, 255), True,
        "Contorne o DESENHO do objeto alto. Quem anda atrás dele fica escondido. A linha amarela é a base.",
    ),
}
ORDEM_CAMADAS = list(CAMADAS)
TECLAS_CAMADA = {pygame.K_1: "chao", pygame.K_2: "chao_posboss", pygame.K_3: "bloqueios", pygame.K_4: "oclusores"}

RAIO_PONTO = 8
RAIO_LINHA = 6
LADO_ALCA = 10
MAXIMO_DESFAZER = 100
ALTURA_BARRA = 40
ALTURA_EXPLICACAO = 24
ALTURA_RODAPE = 26
COR_PAINEL = (8, 14, 28)
COR_TEXTO = (232, 236, 245)
COR_DESTAQUE = (255, 226, 92)


def distancia_ate_segmento(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    comprimento = dx * dx + dy * dy
    if comprimento == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / comprimento))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def ponto_dentro(p, poligono) -> bool:
    """Teste do raio (par/ímpar)."""
    dentro = False
    x, y = p
    for (x1, y1), (x2, y2) in zip(poligono, poligono[1:] + poligono[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            dentro = not dentro
    return dentro


def cantos(retangulo):
    x, y, w, h = retangulo
    return [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]


class Botao:
    def __init__(self, retangulo: pygame.Rect, texto: str, acao, cor=(70, 90, 140)):
        self.retangulo = retangulo
        self.texto = texto
        self.acao = acao
        self.cor = cor


class Editor:
    def __init__(self, tela: pygame.Surface | None = None, converter_mouse=None, ao_salvar=None, fundo: str = "inicial"):
        """Sem `tela`, abre a própria janela. Com `tela`, roda dentro do jogo (F3):
        o jogo repassa os eventos, `converter_mouse` traduz a posição do mouse na
        janela para a tela do jogo e `ao_salvar` aplica a colisão nova na hora."""
        pygame.init()
        self.embutido = tela is not None
        if self.embutido:
            self.tela = tela
        else:
            self.tela = pygame.display.set_mode(covil_tritao.TAMANHO, pygame.SCALED | pygame.RESIZABLE)
            pygame.display.set_caption("Editor de colisão - Covil do Rei Tritão")
        self.converter_mouse = converter_mouse or (lambda posicao: posicao)
        self.ao_salvar = ao_salvar
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("segoeui,arial", 15)
        self.fonte_botao = pygame.font.SysFont("segoeui,arial", 15, bold=True)
        self.fonte_dica = pygame.font.SysFont("segoeui,arial", 14, bold=True)

        self.fundos = {
            "inicial": self.carregar_fundo(covil_tritao.PASTA_QUADROS),
            "posboss": self.carregar_fundo(covil_tritao.PASTA_QUADROS_POSBOSS),
        }
        self.dados = json.loads(covil_tritao.ARQUIVO_COLISAO.read_text(encoding="utf-8"))
        for chave in CAMADAS:
            self.dados.setdefault(chave, [])
        self.historico: list[dict] = []
        self.alterado = False
        self.camada = "chao"
        self.fundo = fundo
        self.selecionado: int | None = None
        self.arraste = None
        self.preencher = True
        self.mostrar_ajuda = True
        self.aviso = "Escolha um tipo de área nos botões acima. Passe o mouse no mapa para ver o que cada clique faz."
        self.confirmar_saida = False
        self.rodando = True

        self.testando = False
        self.cezar: Cezar | None = None
        self.oclusores_teste: list[covil_tritao.Oclusor] = []

        self.botoes = self.criar_botoes()

    def mouse(self) -> tuple[int, int]:
        x, y = self.converter_mouse(pygame.mouse.get_pos())
        return round(x), round(y)

    @staticmethod
    def carregar_fundo(pasta: Path) -> pygame.Surface:
        quadros = sorted(pasta.glob("quadro_*.jpg"))
        imagem = pygame.image.load(quadros[len(quadros) // 2]).convert()
        return pygame.transform.smoothscale(imagem, covil_tritao.TAMANHO)

    def criar_botoes(self) -> list[Botao]:
        botoes, x = [], 8
        for numero, chave in enumerate(ORDEM_CAMADAS, start=1):
            nome, cor, _, _ = CAMADAS[chave]
            texto = f"{numero}  {nome}"
            largura = self.fonte_botao.size(texto)[0] + 36
            botoes.append(Botao(pygame.Rect(x, 6, largura, 28), texto, ("camada", chave), cor))
            x += largura + 6
        x_direita = LARGURA - 8
        ultimo = ("Voltar ao jogo  F3", "sair") if self.embutido else ("Testar andando  T", "testar")
        for texto, acao in (("Salvar  Ctrl+S", "salvar"), ("Desfazer  Ctrl+Z", "desfazer"), ultimo):
            largura = self.fonte_botao.size(texto)[0] + 20
            x_direita -= largura
            botoes.append(Botao(pygame.Rect(x_direita, 6, largura, 28), texto, acao))
            x_direita -= 6
        return botoes

    # ------------------------------------------------------------------ dados
    @property
    def lista(self) -> list:
        return self.dados[self.camada]

    @property
    def camada_de_contorno(self) -> bool:
        return CAMADAS[self.camada][2]

    def guardar_para_desfazer(self) -> None:
        self.historico.append(copy.deepcopy(self.dados))
        del self.historico[:-MAXIMO_DESFAZER]
        self.alterado = True
        self.confirmar_saida = False

    def desfazer(self) -> None:
        if not self.historico:
            self.aviso = "Nada para desfazer."
            return
        self.dados = self.historico.pop()
        self.selecionado = None
        self.alterado = True
        self.aviso = "Desfeito."

    def salvar(self) -> None:
        # Contornos com menos de 3 pontos e retângulos sem área não servem para nada.
        for chave, (_, _, contorno, _) in CAMADAS.items():
            if contorno:
                self.dados[chave] = [p for p in self.dados[chave] if len(p) >= 3]
        self.dados["bloqueios"] = [r for r in self.dados["bloqueios"] if r[2] > 2 and r[3] > 2]

        def poligono(p):
            return "[" + ", ".join(f"[{round(x)}, {round(y)}]" for x, y in p) + "]"

        blocos = []
        for chave, (_, _, contorno, _) in CAMADAS.items():
            if contorno:
                itens = [poligono(p) for p in self.dados[chave]]
            else:
                itens = ["[" + ", ".join(str(round(v)) for v in r) + "]" for r in self.dados[chave]]
            corpo = ",\n".join("    " + item for item in itens)
            blocos.append(f'  "{chave}": [\n{corpo}\n  ]' if itens else f'  "{chave}": []')
        covil_tritao.ARQUIVO_COLISAO.write_text("{\n" + ",\n".join(blocos) + "\n}\n", encoding="utf-8")
        self.alterado = False
        self.selecionado = None  # a limpeza acima pode ter mudado os índices
        if self.ao_salvar:
            self.ao_salvar()
            self.aviso = "Salvo! A colisão nova já vale no jogo (F3 volta a jogar)."
        else:
            self.aviso = f"Salvo em {covil_tritao.ARQUIVO_COLISAO.name}. Abra o jogo de novo para ver."

    def trocar_camada(self, chave: str) -> None:
        self.camada = chave
        if chave == "chao_posboss":
            self.fundo = "posboss"
        self.selecionado = None
        self.aviso = f"{CAMADAS[chave][0]}: {CAMADAS[chave][3]}"

    # ------------------------------------------------------------ procurar
    def ponto_proximo(self, pos):
        melhor, melhor_distancia = None, RAIO_PONTO
        ordem = list(range(len(self.lista)))
        if self.selecionado is not None and self.selecionado < len(self.lista):
            ordem.insert(0, ordem.pop(self.selecionado))  # o selecionado tem preferência
        for i in ordem:
            for j, ponto in enumerate(self.lista[i]):
                distancia = math.dist(pos, ponto)
                if distancia <= melhor_distancia:
                    melhor, melhor_distancia = (i, j), distancia
        return melhor

    def linha_proxima(self, pos):
        melhor, melhor_distancia = None, RAIO_LINHA
        for i, poligono in enumerate(self.lista):
            if len(poligono) < 2:
                continue
            for j in range(len(poligono)):
                a, b = poligono[j], poligono[(j + 1) % len(poligono)]
                distancia = distancia_ate_segmento(pos, a, b)
                if distancia <= melhor_distancia:
                    melhor, melhor_distancia = (i, j + 1), distancia
        return melhor

    def poligono_em(self, pos):
        for i in reversed(range(len(self.lista))):
            if len(self.lista[i]) >= 3 and ponto_dentro(pos, self.lista[i]):
                return i
        return None

    def retangulo_em(self, pos):
        for i in reversed(range(len(self.lista))):
            if pygame.Rect(self.lista[i]).collidepoint(pos):
                return i
        return None

    def canto_em(self, pos):
        for i in reversed(range(len(self.lista))):
            for indice, canto in enumerate(cantos(self.lista[i])):
                if abs(pos[0] - canto[0]) <= LADO_ALCA and abs(pos[1] - canto[1]) <= LADO_ALCA:
                    return i, indice
        return None

    def botao_em(self, pos) -> Botao | None:
        return next((botao for botao in self.botoes if botao.retangulo.collidepoint(pos)), None)

    def o_que_o_clique_faz(self, pos) -> str:
        """Texto da dica ao lado do cursor."""
        if self.testando:
            return ""
        if self.camada_de_contorno:
            if self.ponto_proximo(pos):
                return "arraste: mover ponto  |  botão direito: apagar ponto"
            if self.linha_proxima(pos):
                return "clique: novo ponto nesta linha"
            if self.poligono_em(pos) is not None:
                return "clique: selecionar este contorno"
            if self.selecionado is not None and self.selecionado < len(self.lista):
                return "clique: acrescentar ponto ao contorno amarelo"
            return "aperte N para começar um contorno novo"
        if self.canto_em(pos):
            return "arraste: mudar o tamanho"
        if self.retangulo_em(pos) is not None:
            return "arraste: mover  |  botão direito: apagar"
        return "arraste: desenhar um bloqueio novo"

    # ---------------------------------------------------------------- mouse
    def clicar_botao(self, botao: Botao) -> None:
        if isinstance(botao.acao, tuple):
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
        if botao == 3:
            alvo = self.ponto_proximo(pos)
            if alvo:
                self.guardar_para_desfazer()
                i, j = alvo
                del self.lista[i][j]
                self.selecionado = i
                self.aviso = f"Ponto apagado ({len(self.lista[i])} pontos restam)."
            return

        alvo = self.ponto_proximo(pos)
        if alvo:
            self.guardar_para_desfazer()
            self.selecionado = alvo[0]
            self.arraste = ("ponto", *alvo)
            return
        linha = self.linha_proxima(pos)
        if linha:
            self.guardar_para_desfazer()
            i, j = linha
            self.lista[i].insert(j, list(pos))
            self.selecionado = i
            self.arraste = ("ponto", i, j)
            return
        dentro = self.poligono_em(pos)
        if dentro is not None:
            self.selecionado = dentro
            self.aviso = "Contorno selecionado (amarelo): clique fora dele para acrescentar pontos; Delete apaga."
            return
        if self.selecionado is None or self.selecionado >= len(self.lista):
            self.aviso = "Para criar uma área nova, aperte N e clique em volta dela, ponto por ponto."
            return
        self.guardar_para_desfazer()
        self.lista[self.selecionado].append(list(pos))
        self.arraste = ("ponto", self.selecionado, len(self.lista[self.selecionado]) - 1)

    def clique_bloqueio(self, pos, botao) -> None:
        if botao == 3:
            alvo = self.retangulo_em(pos)
            if alvo is not None:
                self.guardar_para_desfazer()
                del self.lista[alvo]
                self.selecionado = None
                self.aviso = "Bloqueio apagado."
            return

        canto = self.canto_em(pos)
        if canto:
            self.guardar_para_desfazer()
            i, indice = canto
            self.selecionado = i
            self.arraste = ("redimensionar", i, cantos(self.lista[i])[3 - indice])
            return
        alvo = self.retangulo_em(pos)
        if alvo is not None:
            self.guardar_para_desfazer()
            x, y, _, _ = self.lista[alvo]
            self.selecionado = alvo
            self.arraste = ("mover", alvo, (pos[0] - x, pos[1] - y))
            return
        self.guardar_para_desfazer()
        self.lista.append([pos[0], pos[1], 0, 0])
        self.selecionado = len(self.lista) - 1
        self.arraste = ("redimensionar", self.selecionado, pos)

    def arrastar(self, pos) -> None:
        x = max(0, min(LARGURA, pos[0]))
        y = max(0, min(ALTURA, pos[1]))
        tipo = self.arraste[0]
        if tipo == "ponto":
            _, i, j = self.arraste
            self.lista[i][j] = [x, y]
        elif tipo == "mover":
            _, i, (dx, dy) = self.arraste
            self.lista[i][0], self.lista[i][1] = x - dx, y - dy
        elif tipo == "redimensionar":
            _, i, (ox, oy) = self.arraste
            self.lista[i] = [min(x, ox), min(y, oy), abs(x - ox), abs(y - oy)]

    # ---------------------------------------------------------- modo teste
    def alternar_teste(self, pos) -> None:
        global mapa_teste
        if self.embutido:
            self.aviso = "Dentro do jogo não precisa do teste: F3 volta a jogar com a colisão salva."
            return
        if mapa_teste is None:
            import mapa_teste
        if self.testando:
            self.testando = False
            self.cezar = None
            mapa_teste.CENA["chao"] = None
            self.aviso = "Voltou a editar."
            return
        pos_boss = self.fundo == "posboss"
        chao = self.dados["chao"] + (self.dados["chao_posboss"] if pos_boss else [])
        superficie = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)
        for poligono in chao:
            if len(poligono) >= 3:
                pygame.draw.polygon(superficie, (255, 255, 255, 255), poligono)
        mapa_teste.CENA["tamanho"] = covil_tritao.TAMANHO
        mapa_teste.CENA["chao"] = pygame.mask.from_surface(superficie)
        mapa_teste.CENA["bloqueios"] = [pygame.Rect(r) for r in self.dados["bloqueios"] if r[2] > 2 and r[3] > 2]
        self.oclusores_teste = [covil_tritao.Oclusor([tuple(p) for p in poligono]) for poligono in self.dados["oclusores"] if len(poligono) >= 3]

        self.cezar = Cezar(tamanho=covil_tritao.TAMANHOS_SPRITES["Cezar"])
        self.cezar.velocidade *= covil_tritao.FATOR_VELOCIDADE
        self.cezar.quadro_animacao = 0
        self.cezar.tempo_animacao = 0.0
        if mapa_teste.CENA["chao"].get_at((min(pos[0], LARGURA - 1), min(pos[1], ALTURA - 1))):
            inicio = pos
        else:
            inicio = covil_tritao.ENTRADA
        mapa_teste.posicionar_pelos_pes(self.cezar, inicio)
        self.testando = True
        self.selecionado = None
        self.aviso = "TESTE: ande com WASD/setas. A caixinha rosa são os pés. T volta a editar."

    def atualizar_teste(self, tempo_frame: float) -> None:
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(
            (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT]),
            (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP]),
        )
        if direcao.length_squared():
            direcao = direcao.normalize()
            passo = self.cezar.velocidade * tempo_frame
            andou = mapa_teste.mover_com_colisao(self.cezar, direcao.x * passo, direcao.y * passo)
            mapa_teste.atualizar_animacao(self.cezar, direcao if andou else pygame.Vector2(), tempo_frame)
        else:
            mapa_teste.atualizar_animacao(self.cezar, pygame.Vector2(), tempo_frame)

    def pedir_saida(self) -> None:
        """Sai do editor; com mudanças não salvas, só na segunda vez."""
        if self.alterado and not self.confirmar_saida:
            self.confirmar_saida = True
            tecla = "F3/Esc" if self.embutido else "Esc"
            self.aviso = f"Há mudanças NÃO SALVAS! {tecla} de novo sai sem salvar; Ctrl+S salva."
        else:
            self.rodando = False

    # ------------------------------------------------------------- teclado
    def tecla(self, evento) -> None:
        ctrl = evento.mod & pygame.KMOD_CTRL
        if evento.key == pygame.K_ESCAPE:
            if self.testando:
                self.alternar_teste(self.mouse())
            else:
                self.pedir_saida()
        elif evento.key == pygame.K_F3 and self.embutido:
            self.pedir_saida()
        elif ctrl and evento.key == pygame.K_s:
            self.salvar()
        elif ctrl and evento.key == pygame.K_z:
            self.desfazer()
        elif evento.key == pygame.K_t:
            self.alternar_teste(self.mouse())
        elif self.testando:
            return  # no teste, as outras teclas são para andar
        elif evento.key in TECLAS_CAMADA:
            self.trocar_camada(TECLAS_CAMADA[evento.key])
        elif evento.key == pygame.K_TAB:
            self.fundo = "posboss" if self.fundo == "inicial" else "inicial"
            self.aviso = f"Fundo: mapa {'pós-boss' if self.fundo == 'posboss' else 'inicial'}."
        elif evento.key == pygame.K_f:
            self.preencher = not self.preencher
        elif evento.key == pygame.K_h:
            self.mostrar_ajuda = not self.mostrar_ajuda
        elif evento.key == pygame.K_n and self.camada_de_contorno:
            self.guardar_para_desfazer()
            self.lista.append([])
            self.selecionado = len(self.lista) - 1
            self.aviso = "Contorno novo: clique em volta da área, ponto por ponto (fecha sozinho)."
        elif evento.key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.selecionado is not None:
            if self.selecionado < len(self.lista):
                self.guardar_para_desfazer()
                del self.lista[self.selecionado]
                self.selecionado = None
                self.aviso = "Apagado."

    # -------------------------------------------------------------- desenho
    def desenhar_contornos(self, chave: str, ativa: bool) -> None:
        _, cor, _, _ = CAMADAS[chave]
        preenchimento = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)
        for i, poligono in enumerate(self.dados[chave]):
            selecionado = ativa and i == self.selecionado
            if len(poligono) >= 3 and self.preencher:
                pygame.draw.polygon(preenchimento, (*cor, 70 if ativa else 28), poligono)
            if len(poligono) >= 2:
                pygame.draw.lines(self.tela, COR_DESTAQUE if selecionado else cor, len(poligono) >= 3, poligono, 3 if selecionado else 2)
            if chave == "oclusores" and len(poligono) >= 3:
                self.desenhar_base(poligono)
            if ativa:
                for j, ponto in enumerate(poligono):
                    raio = 6 if selecionado and j == len(poligono) - 1 else 4
                    pygame.draw.circle(self.tela, (0, 0, 0), ponto, raio + 1)
                    pygame.draw.circle(self.tela, COR_DESTAQUE if selecionado else (255, 255, 255), ponto, raio)
        self.tela.blit(preenchimento, (0, 0))

    def desenhar_base(self, poligono) -> None:
        """Linha tracejada da base: pés acima dela = atrás do objeto."""
        xs = [x for x, _ in poligono]
        base = max(y for _, y in poligono)
        for x in range(min(xs), max(xs), 10):
            pygame.draw.line(self.tela, COR_DESTAQUE, (x, base), (min(x + 5, max(xs)), base), 2)
        rotulo = self.fonte_dica.render("base", True, COR_DESTAQUE)
        self.tela.blit(rotulo, (max(xs) + 4, base - rotulo.get_height() // 2))

    def desenhar_bloqueios(self, ativa: bool) -> None:
        _, cor, _, _ = CAMADAS["bloqueios"]
        preenchimento = pygame.Surface(covil_tritao.TAMANHO, pygame.SRCALPHA)
        for i, retangulo in enumerate(self.dados["bloqueios"]):
            r = pygame.Rect(retangulo)
            if self.preencher:
                pygame.draw.rect(preenchimento, (*cor, 80 if ativa else 30), r)
            selecionado = ativa and i == self.selecionado
            pygame.draw.rect(self.tela, COR_DESTAQUE if selecionado else cor, r, 3 if selecionado else 2)
            if ativa:
                for canto in cantos(retangulo):
                    alca = pygame.Rect(0, 0, 8, 8)
                    alca.center = canto
                    pygame.draw.rect(self.tela, (255, 255, 255), alca)
                    pygame.draw.rect(self.tela, (0, 0, 0), alca, 1)
        self.tela.blit(preenchimento, (0, 0))

    def desenhar_teste(self) -> None:
        fundo = self.fundos[self.fundo]
        pes = self.cezar.rect.top + mapa_teste.altura_dos_pes(self.cezar)
        camadas = [(pes, self.cezar)] + [(oclusor.base, oclusor) for oclusor in self.oclusores_teste]
        for _, item in sorted(camadas, key=lambda camada: camada[0]):
            if isinstance(item, covil_tritao.Oclusor):
                item.desenhar(self.tela, fundo)
            else:
                self.tela.blit(item.image, item.rect)
        pygame.draw.rect(self.tela, (255, 0, 200), mapa_teste.retangulo_colisao(self.cezar), 2)

    def desenhar_barra(self) -> None:
        barra = pygame.Surface((LARGURA, ALTURA_BARRA + ALTURA_EXPLICACAO), pygame.SRCALPHA)
        barra.fill((*COR_PAINEL, 235))
        self.tela.blit(barra, (0, 0))
        mouse = self.mouse()
        for botao in self.botoes:
            ativo = botao.acao == ("camada", self.camada) or (botao.acao == "testar" and self.testando)
            em_cima = botao.retangulo.collidepoint(mouse)
            fundo = (40, 52, 84) if em_cima else (24, 32, 56)
            pygame.draw.rect(self.tela, fundo, botao.retangulo, border_radius=6)
            pygame.draw.rect(self.tela, COR_DESTAQUE if ativo else (70, 84, 120), botao.retangulo, 2, border_radius=6)
            x_texto = botao.retangulo.x + 10
            if isinstance(botao.acao, tuple):
                amostra = pygame.Rect(botao.retangulo.x + 10, botao.retangulo.centery - 6, 12, 12)
                pygame.draw.rect(self.tela, botao.cor, amostra, border_radius=3)
                x_texto += 18
            texto = self.fonte_botao.render(botao.texto, True, COR_DESTAQUE if ativo else COR_TEXTO)
            self.tela.blit(texto, (x_texto, botao.retangulo.centery - texto.get_height() // 2))

        nome, cor, _, explicacao = CAMADAS[self.camada]
        if self.testando:
            linha = "MODO TESTE: ande com WASD ou as setas. A caixinha rosa são os pés. T ou Esc volta a editar."
            cor = (255, 120, 220)
        else:
            linha = f"{nome}: {explicacao}"
        self.tela.blit(self.fonte.render(linha, True, cor), (10, ALTURA_BARRA + 2))

    def desenhar_rodape(self) -> None:
        mouse = self.mouse()
        rodape = pygame.Surface((LARGURA, ALTURA_RODAPE), pygame.SRCALPHA)
        rodape.fill((*COR_PAINEL, 235))
        self.tela.blit(rodape, (0, ALTURA - ALTURA_RODAPE))
        estado = f"fundo: {'pós-boss' if self.fundo == 'posboss' else 'inicial'} (Tab)   |   x {mouse[0]}, y {mouse[1]}"
        if self.alterado:
            estado += "   |   NÃO SALVO"
        texto_estado = self.fonte.render(estado, True, (255, 150, 150) if self.alterado else (160, 175, 200))
        self.tela.blit(texto_estado, (LARGURA - texto_estado.get_width() - 10, ALTURA - ALTURA_RODAPE + 4))
        self.tela.blit(self.fonte.render(self.aviso, True, (255, 235, 160)), (10, ALTURA - ALTURA_RODAPE + 4))

    def desenhar_dica_do_cursor(self) -> None:
        mouse = self.mouse()
        if self.botao_em(mouse) or mouse[1] < ALTURA_BARRA + ALTURA_EXPLICACAO or self.arraste:
            return
        dica = self.o_que_o_clique_faz(mouse)
        if not dica:
            return
        texto = self.fonte_dica.render(dica, True, (20, 20, 20))
        caixa = texto.get_rect().inflate(12, 6)
        caixa.topleft = (mouse[0] + 16, mouse[1] + 14)
        if caixa.right > LARGURA:
            caixa.right = mouse[0] - 8
        if caixa.bottom > ALTURA - ALTURA_RODAPE:
            caixa.bottom = mouse[1] - 8
        pygame.draw.rect(self.tela, (255, 236, 150), caixa, border_radius=5)
        pygame.draw.rect(self.tela, (60, 40, 0), caixa, 1, border_radius=5)
        self.tela.blit(texto, texto.get_rect(center=caixa.center))

    def desenhar_ajuda(self) -> None:
        if not self.mostrar_ajuda or self.testando:
            return
        if self.camada_de_contorno:
            linhas = [
                "COMO EDITAR UM CONTORNO",
                "N ............. começar um contorno novo",
                "clique ........ põe pontos em volta da área",
                "arrastar ponto  move o ponto",
                "clique na linha cria ponto no meio",
                "clique dentro . seleciona (fica amarelo)",
                "botão direito . apaga o ponto",
                "Delete ........ apaga o contorno inteiro",
            ]
        else:
            linhas = [
                "COMO EDITAR UM BLOQUEIO",
                "arrastar no vazio ... desenha um novo",
                "arrastar por dentro . move",
                "arrastar um canto ... muda o tamanho",
                "botão direito ....... apaga",
            ]
        if self.camada == "oclusores":
            linhas += ["", "Dica: contorne a estátua inteira e", "ponha um Bloqueio só na base dela."]
        linhas += ["", "F preenchimento   H esconder ajuda", "F3 / Esc: voltar ao jogo" if self.embutido else "Esc sair"]
        largura = max(self.fonte.size(linha)[0] for linha in linhas) + 24
        caixa = pygame.Rect(LARGURA - largura - 10, ALTURA_BARRA + ALTURA_EXPLICACAO + 8, largura, len(linhas) * 19 + 14)
        fundo = pygame.Surface(caixa.size, pygame.SRCALPHA)
        fundo.fill((*COR_PAINEL, 220))
        self.tela.blit(fundo, caixa)
        pygame.draw.rect(self.tela, (70, 84, 120), caixa, 1, border_radius=4)
        for n, linha in enumerate(linhas):
            cor = COR_DESTAQUE if n == 0 else COR_TEXTO
            self.tela.blit(self.fonte.render(linha, True, cor), (caixa.x + 12, caixa.y + 7 + n * 19))

    def desenhar(self) -> None:
        self.tela.blit(self.fundos[self.fundo], (0, 0))
        if self.testando:
            self.desenhar_teste()
        else:
            mostrar_posboss = self.fundo == "posboss" or self.camada == "chao_posboss"
            for chave in ("chao", "chao_posboss", "oclusores"):
                if chave == "chao_posboss" and not mostrar_posboss:
                    continue
                self.desenhar_contornos(chave, chave == self.camada)
            self.desenhar_bloqueios(self.camada == "bloqueios")
        self.desenhar_barra()
        self.desenhar_rodape()
        self.desenhar_ajuda()
        self.desenhar_dica_do_cursor()

    # ---------------------------------------------------------------- laço
    def processar(self, evento) -> None:
        if evento.type == pygame.QUIT:
            if self.alterado and not self.confirmar_saida:
                self.confirmar_saida = True
                self.aviso = "Há mudanças NÃO SALVAS! Feche de novo para sair sem salvar; Ctrl+S salva."
            else:
                self.rodando = False
        elif evento.type == pygame.KEYDOWN:
            self.tecla(evento)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (1, 3):
            botao = self.botao_em(self.converter_mouse(evento.pos))
            if botao and evento.button == 1:
                self.clicar_botao(botao)
            elif botao or self.testando or self.converter_mouse(evento.pos)[1] < ALTURA_BARRA + ALTURA_EXPLICACAO:
                return
            elif self.camada_de_contorno:
                self.clique_contorno(self.converter_mouse(evento.pos), evento.button)
            else:
                self.clique_bloqueio(self.converter_mouse(evento.pos), evento.button)
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arraste = None
        elif evento.type == pygame.MOUSEMOTION and self.arraste:
            self.arrastar(self.converter_mouse(evento.pos))

    def executar(self) -> None:
        while self.rodando:
            tempo_frame = self.relogio.tick(60) / 1000
            for evento in pygame.event.get():
                self.processar(evento)
            if self.testando:
                self.atualizar_teste(tempo_frame)
            self.desenhar()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Editor().executar()
