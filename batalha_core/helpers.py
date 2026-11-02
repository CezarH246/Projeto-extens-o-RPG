"""Shared helpers for sprites, sizing, and event logging."""

import unicodedata
from pathlib import Path

import pygame
from PIL import Image

from .assets import *

LOG_BATALHA: list[str] = []

# Segoe UI e Calibri são mais nítidas que a Arial; a Arial é o reserva.
FAMILIAS_FONTE = "segoeui,calibri,arial"


def criar_fonte(tamanho: int, negrito: bool = False) -> pygame.font.Font:
    """Única porta de entrada das fontes da batalha: trocar a família aqui vale para tudo."""
    return pygame.font.SysFont(FAMILIAS_FONTE, tamanho, bold=negrito)


def texto_com_sombra(
    tela: pygame.Surface,
    fonte: pygame.font.Font,
    texto: str,
    cor: tuple[int, int, int],
    posicao: tuple[int, int],
    centralizado: bool = False,
) -> None:
    """Desenha o texto com uma sombra escura, para ler bem sobre qualquer fundo."""
    sombra = fonte.render(texto, True, (5, 8, 25))
    principal = fonte.render(texto, True, cor)
    retangulo = principal.get_rect(center=posicao) if centralizado else principal.get_rect(topleft=posicao)
    tela.blit(sombra, retangulo.move(2, 2))
    tela.blit(principal, retangulo)

def cor_barra_hp(valor: float, maximo: float) -> tuple[int, int, int]:
    proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
    if proporcao <= 0.30:
        return (220, 65, 65)
    if proporcao <= 0.60:
        return (245, 166, 35)
    return (75, 221, 115)


def registrar_evento(*args, sep=" ", **_kwargs) -> None:
    """Recebe as mensagens produzidas pelas regras e as mostra na tela."""
    texto = sep.join(str(item) for item in args)
    for linha in texto.splitlines():
        # A fonte do jogo não desenha emojis; as linhas de "=====" são só enfeite.
        linha = "".join(c for c in linha if ord(c) <= 0x24F or 0x2010 <= ord(c) <= 0x2027).strip()
        if any(c.isalnum() for c in linha):
            LOG_BATALHA.append(linha)
    del LOG_BATALHA[:-400]


def normalizar_nome(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    for caractere in (" ", "-", ".", ",", "'", '"'):
        texto = texto.replace(caractere, "_")
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto


def eh_rei_tritao(inimigo) -> bool:
    """Diz se o inimigo é o Rei Tritão, o boss do confronto especial."""
    return normalizar_nome(inimigo.nome.split(" Lv.")[0]) == "rei_tritao"


def resolver_sprite_inimigo(inimigo) -> Path | None:
    if eh_rei_tritao(inimigo):
        return REI_TRITAO_IDLE
    if inimigo.tipo == "Boss":
        return SPRITES_INIMIGOS["boss"]

    nome_sem_nivel = inimigo.nome.split(" Lv.")[0]
    return SPRITES_INIMIGOS.get(normalizar_nome(nome_sem_nivel))


def tamanho_com_escala(tamanho_base: tuple[int, int], personagem) -> tuple[int, int]:
    escala = max(0.01, float(getattr(personagem, "escala", 1.0)))
    return tuple(max(1, round(dimensao * escala)) for dimensao in tamanho_base)


def tamanho_corpo(personagem, tamanho_base: int = TAMANHO_CORPO_BASE) -> tuple[int, int]:
    """Tamanho do corpo do combatente, já contando a escala individual dele."""
    return tamanho_com_escala((tamanho_base, tamanho_base), personagem)


def tamanho_efeito_com_escala_alvo(
    tamanho_base: tuple[int, int],
    tamanho_alvo: tuple[int, int],
) -> tuple[int, int]:
    escala_alvo = min(
        tamanho_alvo[0] / TAMANHO_CORPO_BASE,
        tamanho_alvo[1] / TAMANHO_CORPO_BASE,
    )
    return tuple(max(1, round(dimensao * escala_alvo)) for dimensao in tamanho_base)


def mediana(valores: list[int]) -> int:
    ordenados = sorted(valores)
    return ordenados[len(ordenados) // 2]


def ajustar_quadros_ao_conteudo(
    quadros: list[pygame.Surface],
    tamanho: tuple[int, int],
    limitar_ao_tamanho: bool = False,
) -> list[pygame.Surface]:
    """Redimensiona os quadros para que o desenho visível ocupe a caixa `tamanho`.

    Cada arquivo de animação tem uma margem transparente maior ou menor, por isso
    a margem é descartada e a escala vem da altura do desenho visível: assim o
    personagem fica com o mesmo corpo em todas as animações dele, sem depender da
    largura da pose. O corte usa a união do conteúdo de todos os quadros, então
    nenhum frame é cortado e o movimento da animação é preservado. Quando
    `limitar_ao_tamanho` está ativo, essa união também fica contida na caixa pedida.
    """
    altura_alvo = tamanho[1]
    limites = [quadro.get_bounding_rect() for quadro in quadros]
    visiveis = [limite for limite in limites if limite.width > 0 and limite.height > 0]
    if not visiveis:
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    x0 = min(limite.left for limite in visiveis)
    y0 = min(limite.top for limite in visiveis)
    largura = max(limite.right for limite in visiveis) - x0
    altura = max(limite.bottom for limite in visiveis) - y0
    escala = altura_alvo / mediana([limite.height for limite in visiveis])
    if limitar_ao_tamanho:
        escala = min(escala, tamanho[0] / largura, tamanho[1] / altura)
    destino_tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))

    ajustados = []
    for quadro in quadros:
        destino = pygame.Surface(destino_tamanho, pygame.SRCALPHA)
        escalado = pygame.transform.smoothscale(
            quadro,
            (max(1, round(quadro.get_width() * escala)), max(1, round(quadro.get_height() * escala))),
        )
        recorte = pygame.Rect(round(x0 * escala), round(y0 * escala), *destino_tamanho).clip(escalado.get_rect())
        if recorte.width > 0 and recorte.height > 0:
            destino.blit(escalado.subsurface(recorte), (0, 0))
        ajustados.append(destino)
    return ajustados


def carregar_quadros_gif(caminho: Path) -> list[pygame.Surface]:
    """Lê todos os quadros de um gif, sem alterar o tamanho."""
    quadros = []
    with Image.open(caminho) as gif:
        for indice in range(getattr(gif, "n_frames", 1)):
            gif.seek(indice)
            dados = gif.convert("RGBA").tobytes()
            quadros.append(pygame.image.frombytes(dados, gif.size, "RGBA").convert_alpha())
    return quadros
