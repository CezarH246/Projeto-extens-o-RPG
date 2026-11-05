"""Editor visual da colisao dos mapas do jogo.

Uso (na pasta do projeto):
    python ferramentas/editor_colisao.py [cena]
    cena: covil (padrao), covil_boss (arena do Rei Tritao) ou mapateste

Abre o mapa com a colisao por cima. Tudo e feito com o mouse; os botoes do topo
trocam o tipo de area e uma dica ao lado do cursor diz o que o clique vai
fazer. Cada mapa tem seu proprio JSON em assets/mapas_animados/ (veja
colisoes_mapas.py), que o jogo le ao abrir.

Tipos de area (botoes do topo ou teclas 1, 2, 3...; nem todo mapa usa todos):
  Chao              onde da para andar (os pes precisam estar dentro).
                    Sem nenhum contorno de chao, o mapa inteiro e livre
  Chao pos-boss     chao que so vale depois de derrotar o Rei Tritao (covil)
  Bloqueio          retangulo que nao da para atravessar (base de estatua, bau)
  Passar por tras   contorno de um objeto alto (estatua): quem anda atras
                    dele fica escondido; a linha amarela e a base

Testar (T): coloca o Cezar onde o mouse esta para andar com WASD/setas usando a
mesma colisao do jogo. T de novo volta a editar.

Dentro do jogo: F3 abre este editor por cima do mapa atual (o jogo fica
pausado); Ctrl+S salva e a colisao nova ja vale; F3 ou Esc voltam a jogar.

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

# Arquivo e camadas da colisao de cada mapa.
import colisoes_mapas  # noqa: E402

# Constantes e classes compartilhadas.
from ferramentas.editor_config import (  # noqa: E402
    CAMADAS,
    TECLAS_NUMERO,
    Botao,
)

# Nomes curtos dos botoes, para mapas estreitos.
NOMES_CURTOS = {"chao": "Chão", "chao_posboss": "Pós-boss", "bloqueios": "Bloqueio", "oclusores": "Atrás"}


def tamanho_do_mapa(cena: str) -> tuple[int, int]:
    """Resolucao logica de cada mapa (o mapa de teste e menor que o covil)."""
    if cena == "mapateste":
        import mapa_config

        return (mapa_config.LARGURA_MAPA, mapa_config.ALTURA_MAPA)
    return covil_tritao.TAMANHO

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
        fundo: str | None = None,
        cena: str = "covil",
        fundos: dict[str, pygame.Surface] | None = None,
    ):
        """Sem `tela`, abre a propria janela. Com `tela`, roda dentro do jogo (F3):
        o jogo repassa os eventos, `converter_mouse` traduz a posicao do mouse na
        janela para a tela do jogo e `ao_salvar` aplica a colisao nova na hora.

        `cena` escolhe o mapa ("covil", "covil_boss" ou "mapateste"; veja
        colisoes_mapas.CENAS) e `fundos` as imagens do mapa (nome -> imagem);
        sem `fundos`, o editor carrega as imagens do mapa sozinho."""
        # Garante que fontes/eventos do pygame estejam prontos.
        pygame.init()

        # Mapa sendo editado: nome, camadas que ele usa e atalhos 1, 2, 3...
        self.cena = cena
        nome_mapa, _, self.camadas = colisoes_mapas.CENAS[cena]
        self.teclas_camada = dict(zip(TECLAS_NUMERO, self.camadas))

        # "embutido" indica se o editor esta rodando dentro do jogo.
        self.embutido = tela is not None

        if self.embutido:
            # Usa a superficie logica do jogo.
            self.tela = tela
        else:
            # Modo autonono: cria a propria janela, do tamanho do mapa.
            self.tela = pygame.display.set_mode(
                tamanho_do_mapa(cena),
                pygame.SCALED | pygame.RESIZABLE,
            )
            pygame.display.set_caption(f'Editor de colisão - {nome_mapa}')
        self.tamanho = self.tela.get_size()
        self.largura, self.altura = self.tamanho

        # Funcao que converte a posicao do mouse para a tela logica.
        self.converter_mouse = converter_mouse or (lambda posicao: posicao)

        # Callback opcional chamado depois de salvar.
        self.ao_salvar = ao_salvar

        # Relogio e fontes da interface.
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("segoeui,arial", 15)
        self.fonte_botao = pygame.font.SysFont("segoeui,arial", 15, bold=True)
        self.fonte_dica = pygame.font.SysFont("segoeui,arial", 14, bold=True)

        # Imagens de fundo do mapa (no covil: inicial e pos-boss).
        self.fundos = {
            nome: (imagem if imagem.get_size() == self.tamanho else pygame.transform.smoothscale(imagem, self.tamanho))
            for nome, imagem in (fundos or self.fundos_do_mapa(cena)).items()
        }

        # Le o JSON de colisao do mapa (com todas as camadas que ele usa).
        self.dados = colisoes_mapas.carregar(cena)

        # Estado de edicao.
        self.historico: list[dict] = []
        self.alterado = False
        self.camada = self.camadas[0]
        self.fundo = fundo if fundo in self.fundos else next(iter(self.fundos))
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
        """Carrega um quadro do meio da animacao (representa bem a cena)."""
        quadros = sorted(pasta.glob("quadro_*.jpg")) or sorted(pasta.glob("frame_*.jpg"))
        return pygame.image.load(quadros[len(quadros) // 2]).convert()

    @classmethod
    def fundos_do_mapa(cls, cena: str) -> dict[str, pygame.Surface]:
        """Imagens de fundo de cada mapa, para o editor aberto fora do jogo."""
        if cena == "covil":
            return {
                "inicial": cls.carregar_fundo(covil_tritao.PASTA_QUADROS),
                "posboss": cls.carregar_fundo(covil_tritao.PASTA_QUADROS_POSBOSS),
            }
        if cena == "covil_boss":
            return {"arena": cls.carregar_fundo(covil_tritao.PASTA_QUADROS_BOSS)}
        import mapa_config

        return {"mapa": pygame.image.load(mapa_config.MAPA_CAMINHO).convert()}

    def criar_botoes(self) -> list[Botao]:
        """Monta a lista de botoes da barra superior."""
        botoes, x = [], 8
        # Em mapas estreitos (o mapa de teste tem 720 px) os botoes ficam compactos.
        compacto = self.largura < 1100

        # Botoes das camadas que este mapa usa (1, 2, 3...), a partir da esquerda.
        for numero, chave in enumerate(self.camadas, start=1):
            nome, cor, _, _ = CAMADAS[chave]
            if compacto:
                nome = NOMES_CURTOS.get(chave, nome)
            texto = f"{numero}  {nome}"
            # +36: margem e o quadradinho com a cor da camada.
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
        x_direita = self.largura - 8
        if compacto:
            ultimo = ("Voltar F3", "sair") if self.embutido else ("Testar T", "testar")
            acoes = (("Salvar", "salvar"), ("Desfazer", "desfazer"), ultimo)
        else:
            ultimo = (
                ("Voltar ao jogo  F3", "sair")
                if self.embutido
                else ("Testar andando  T", "testar")
            )
            acoes = (("Salvar  Ctrl+S", "salvar"), ("Desfazer  Ctrl+Z", "desfazer"), ultimo)
        for texto, acao in acoes:
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


# Permite executar o editor isoladamente: python ferramentas/editor_colisao.py [cena]
if __name__ == "__main__":
    cena = sys.argv[1] if len(sys.argv) > 1 else "covil"
    if cena not in colisoes_mapas.CENAS:
        raise SystemExit(f"Mapa desconhecido: {cena}. Use um destes: {', '.join(colisoes_mapas.CENAS)}")
    Editor(cena=cena).executar()
