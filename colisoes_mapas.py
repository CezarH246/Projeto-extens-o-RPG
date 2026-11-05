"""Colisão de cada mapa (cena) do jogo, num arquivo JSON por mapa.

O editor (F3 no jogo, ou `python ferramentas/editor_colisao.py <cena>`) lê e
grava estes arquivos; o jogo aplica a colisão do mapa em que o grupo está.

Camadas (nem todo mapa usa todas):
- "chao": polígonos onde se pode andar (os pés precisam estar dentro de um).
  Lista vazia = o mapa inteiro é livre (só os bloqueios atrapalham);
- "chao_posboss": chão a mais depois do Rei Tritão (só no covil);
- "bloqueios": retângulos [x, y, largura, altura] que não dá para atravessar;
- "oclusores": contornos de objetos altos que dá para rodear por trás.

Se o arquivo de um mapa ainda não existe, ele começa com a colisão que o mapa
já tinha no código (veja `colisao_padrao`), então nada muda até alguém editar.
"""

from __future__ import annotations

import json
from pathlib import Path

import pygame

PASTA = Path(__file__).resolve().parent / "assets" / "mapas_animados"

# cena -> (nome mostrado no editor, arquivo, camadas que o mapa usa)
CENAS = {
    "covil": ("Covil do Rei Tritão", PASTA / "colisao_covil.json", ["chao", "chao_posboss", "bloqueios", "oclusores"]),
    "covil_boss": ("Arena do Rei Tritão", PASTA / "colisao_arena_boss.json", ["chao", "bloqueios", "oclusores"]),
    "mapateste": ("Mapa de teste", PASTA / "colisao_mapateste.json", ["chao", "bloqueios", "oclusores"]),
}
TODAS_AS_CAMADAS = ["chao", "chao_posboss", "bloqueios", "oclusores"]


def colisao_padrao(cena: str) -> dict:
    """Colisão de antes do editor, para mapas que ainda não têm arquivo."""
    # Na arena, nenhum contorno de chão = a arena inteira livre (como antes).
    dados = {camada: [] for camada in CENAS[cena][2]}
    if cena == "mapateste":
        import mapa_config

        dados["bloqueios"] = [[r.x, r.y, r.w, r.h] for r in mapa_config.COLISOES_MAPA]
    return dados


def carregar(cena: str) -> dict:
    arquivo = CENAS[cena][1]
    dados = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.is_file() else colisao_padrao(cena)
    for camada in CENAS[cena][2]:
        dados.setdefault(camada, [])
    return dados


def salvar(cena: str, dados: dict) -> Path:
    """Grava um polígono/retângulo por linha, para o arquivo ficar legível."""

    def poligono(p):
        return "[" + ", ".join(f"[{round(x)}, {round(y)}]" for x, y in p) + "]"

    blocos = []
    for camada in CENAS[cena][2]:
        if camada == "bloqueios":
            itens = ["[" + ", ".join(str(round(v)) for v in r) + "]" for r in dados[camada]]
        else:
            itens = [poligono(p) for p in dados[camada]]
        corpo = ",\n".join("    " + item for item in itens)
        blocos.append(f'  "{camada}": [\n{corpo}\n  ]' if itens else f'  "{camada}": []')
    arquivo = CENAS[cena][1]
    arquivo.write_text("{\n" + ",\n".join(blocos) + "\n}\n", encoding="utf-8")
    return arquivo


def mascara_chao(poligonos: list, tamanho: tuple[int, int]) -> pygame.mask.Mask | None:
    """Máscara do chão; None quando não há polígonos (mapa inteiro livre)."""
    poligonos = [p for p in poligonos if len(p) >= 3]
    if not poligonos:
        return None
    superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
    for poligono in poligonos:
        pygame.draw.polygon(superficie, (255, 255, 255, 255), poligono)
    return pygame.mask.from_surface(superficie)


def bloqueios(dados: dict) -> list[pygame.Rect]:
    return [pygame.Rect(r) for r in dados.get("bloqueios", []) if r[2] > 2 and r[3] > 2]


def oclusores(dados: dict) -> list:
    import covil_tritao

    return [covil_tritao.Oclusor([tuple(p) for p in poligono]) for poligono in dados.get("oclusores", []) if len(poligono) >= 3]
