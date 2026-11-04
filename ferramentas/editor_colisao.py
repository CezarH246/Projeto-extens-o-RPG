"""Editor visual da colisao do Covil do Rei Tritao.

Uso (na pasta do projeto):
    python ferramentas/editor_colisao.py

Abre o mapa do covil com a colisao por cima. Tudo e feito com o mouse; os
botoes do topo trocam o tipo de area e uma dica ao lado do cursor diz o que o
clique vai fazer. Salva em assets/mapas_animados/colisao_covil.json, que o
jogo le ao abrir.

Tipos de area (botoes do topo ou teclas 1 a 4):
  1  Chao              onde da para andar (os pes precisam estar dentro)
  2  Chao pos-boss     chao que so vale depois de derrotar o Rei Tritao
  3  Bloqueio          retangulo que nao da para atravessar (base de estatua, bau)
  4  Passar por tras   contorno de um objeto alto (estatua): quem anda atras
                       dele fica escondido; a linha amarela e a base

Testar (T): coloca o Cezar onde o mouse esta para andar com WASD/setas usando a
mesma colisao do jogo. T de novo volta a editar.

Dentro do jogo: no covil, F3 abre este editor por cima do jogo (pausado);
Ctrl+S salva e a colisao nova ja vale; F3 ou Esc voltam a jogar.

Atalhos: Ctrl+S salva, Ctrl+Z desfaz, N comeca um contorno novo, Delete apaga o
selecionado, Tab troca o fundo (inicial/pos-boss), F liga/desliga o
preenchimento, H esconde a ajuda, Esc sai.

ORGANIZACAO (heranca por mixins)
-------------------------------
A classe Editor abaixo junta tres classes menores:
- DadosMixin      -> JSON, desfazer e busca de pontos/retangulos;
- InteracaoMixin  -> mouse, teclado e modo de teste;
- DesenhoMixin    -> desenho da interface.

Isso e HERANCA MULTIPLA: Editor recebe java os metodos dos tres mixins. Cada
mixin usa ENCAPSULAMENTO para guardar seu proprio estado em self e se comunicar
por metodos (self.lista, self.salvar, self.desenhar...). O resultado e um
arquivo pequeno, com cada responsabilidade em um lugar claro.
"""

from __future__ import annotations

# json le o arquivo de colisao no inicio.
import json

# sys acrescenta a raiz do projeto ao caminho de importacao.
import sys

# Path localiza a raiz do projeto a partir deste arquivo.
from pathlib import Path

# pygame cria a janela e mede o mouse.
import pygame

# PROJETO e a pasta que contem "ferramentas".
PROJETO = Path(__file__).resolve().parent.parent

# Garante que "ferramentas.xxx", "covil_tritao" e "CezarPersonagem" sejam vistos
# mesmo quando o arquivo e executado diretamente.
if str(PROJETO) not in sys.path:
    sys.path.insert(0, str(PROJETO))

# Dados do mapa do covil.
import covil_tritao  # noqa: E402

# Modelo usado na anotacao de tipo do modo de teste.
from CezarPersonagem import Cezar  # noqa: E402

# Constantes e classes compartilhadas.
from ferramentas.editor_config import (  # noqa: E402
    CAMADAS,
    LARGURA,
    ORDEM_CAMADAS,
    Botao,
)

# Os tres mixins que compoem o Editor.
from ferramentas.editor_dados import DadosMixin  # noqa: E402
from ferramentas.editor_desenho import DesenhoMixin  # noqa: E402
from ferramentas.editor_interacao import InteracaoMixin  # noqa: E402


class Editor(DadosMixin, InteracaoMixin, DesenhoMixin):
    """Editor completo: estado, interacao e desenho no mesmo objeto."""

    def __init__(
        self,
        tela: pygame.Surface | None = None,
        converter_mouse=None,
        ao_salvar=None,
        fundo: str = "inicial",
    ):
        """Sem `tela`, abre a propria janela. Com `tela`, roda dentro do jogo (F3):
        o jogo repassa os eventos, `converter_mouse` traduz a posicao do mouse na
        janela para a tela do jogo e `ao_salvar` aplica a colisao nova na hora."""
        # Garante que fontes/eventos do pygame estejam prontos.
        pygame.init()

        # "embutido" indica se o editor esta rodando dentro do jogo.
        self.embutido = tela is not None

        if self.embutido:
            # Usa a superficie logica do jogo.
            self.tela = tela
        else:
            # Modo autonono: cria a propria janela.
            self.tela = pygame.display.set_mode(
                covil_tritao.TAMANHO,
                pygame.SCALED | pygame.RESIZABLE,
            )
            pygame.display.set_caption('Editor de colisão - Covil do Rei Tritão')

        # Funcao que converte a posicao do mouse para a tela logica.
        self.converter_mouse = converter_mouse or (lambda posicao: posicao)

        # Callback opcional chamado depois de salvar.
        self.ao_salvar = ao_salvar

        # Relogio e fontes da interface.
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("segoeui,arial", 15)
        self.fonte_botao = pygame.font.SysFont("segoeui,arial", 15, bold=True)
        self.fonte_dica = pygame.font.SysFont("segoeui,arial", 14, bold=True)

        # Carrega os dois fundos possiveis (inicial e pos-boss).
        self.fundos = {
            "inicial": self.carregar_fundo(covil_tritao.PASTA_QUADROS),
            "posboss": self.carregar_fundo(covil_tritao.PASTA_QUADROS_POSBOSS),
        }

        # Le o JSON de colisao e garante que todas as chaves existam.
        self.dados = json.loads(
            covil_tritao.ARQUIVO_COLISAO.read_text(encoding="utf-8")
        )
        for chave in CAMADAS:
            self.dados.setdefault(chave, [])

        # Estado de edicao.
        self.historico: list[dict] = []
        self.alterado = False
        self.camada = "chao"
        self.fundo = fundo
        self.selecionado: int | None = None
        self.arraste = None
        self.preencher = True
        self.mostrar_ajuda = True
        self.aviso = (
            "Escolha um tipo de área nos botões acima. "
            "Passe o mouse no mapa para ver o que cada clique faz."
        )
        self.confirmar_saida = False
        self.rodando = True

        # Estado do modo de teste.
        self.testando = False
        self.cezar: Cezar | None = None
        self.oclusores_teste: list[covil_tritao.Oclusor] = []

        # Cria os botoes da barra superior.
        self.botoes = self.criar_botoes()

    def mouse(self) -> tuple[int, int]:
        """Posicao do mouse ja convertida para a tela logica do jogo."""
        x, y = self.converter_mouse(pygame.mouse.get_pos())
        return round(x), round(y)

    @staticmethod
    def carregar_fundo(pasta: Path) -> pygame.Surface:
        """Carrega um quadro do meio da animacao e o escala para o tamanho do covil."""
        # Ordena os quadros e escolhe o do meio (representa bem a cena).
        quadros = sorted(pasta.glob("quadro_*.jpg"))
        imagem = pygame.image.load(quadros[len(quadros) // 2]).convert()

        # Ajusta ao tamanho logico do covil.
        return pygame.transform.smoothscale(imagem, covil_tritao.TAMANHO)

    def criar_botoes(self) -> list[Botao]:
        """Monta a lista de botoes da barra superior."""
        botoes, x = [], 8

        # Botoes das camadas (1 a 4), comecando pela esquerda.
        for numero, chave in enumerate(ORDEM_CAMADAS, start=1):
            nome, cor, _, _ = CAMADAS[chave]
            texto = f"{numero}  {nome}"
            largura = self.fonte_botao.size(texto)[0] + 36
            botoes.append(
                Botao(
                    pygame.Rect(x, 6, largura, 28),
                    texto,
                    ("camada", chave),
                    cor,
                )
            )
            x += largura + 6

        # Botoes de acao, alinhados a direita.
        x_direita = LARGURA - 8
        ultimo = (
            ("Voltar ao jogo  F3", "sair")
            if self.embutido
            else ("Testar andando  T", "testar")
        )
        for texto, acao in (
            ("Salvar  Ctrl+S", "salvar"),
            ("Desfazer  Ctrl+Z", "desfazer"),
            ultimo,
        ):
            largura = self.fonte_botao.size(texto)[0] + 20
            x_direita -= largura
            botoes.append(
                Botao(pygame.Rect(x_direita, 6, largura, 28), texto, acao)
            )
            x_direita -= 6

        return botoes

    def executar(self) -> None:
        """Laco principal quando o editor roda sozinho."""
        while self.rodando:
            # Limita a 60 FPS e mede o tempo do quadro.
            tempo_frame = self.relogio.tick(60) / 1000

            # Processa todos os eventos pendentes.
            for evento in pygame.event.get():
                self.processar(evento)

            # No modo de teste, move o Cezar.
            if self.testando:
                self.atualizar_teste(tempo_frame)

            # Desenha e mostra o quadro.
            self.desenhar()
            pygame.display.flip()

        # Encerra o pygame ao sair.
        pygame.quit()


# Permite executar o editor isoladamente.
if __name__ == "__main__":
    Editor().executar()
