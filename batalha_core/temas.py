"""Temas (templates) da interface de batalha.

- "classico": painéis de status acima dos heróis, ações e registro no rodapé.
- "moderno": linha do tempo de turnos no topo, menu de comandos em lista,
  cartões do grupo no rodapé e barras finas embaixo dos inimigos.

Cada tema tem a própria formação (assets.py), pois o lugar livre na tela muda.
Durante a batalha, a tecla F2 alterna entre os temas.
"""

TEMAS = {
    "classico": "Clássico",
    "moderno": "Moderno",
}

# Tema usado ao abrir o jogo.
TEMA_PADRAO = "classico"

_tema_atual = TEMA_PADRAO


def tema_atual() -> str:
    return _tema_atual


def nome_do_tema(chave: str | None = None) -> str:
    return TEMAS[chave or _tema_atual]


def definir_tema(chave: str) -> None:
    global _tema_atual
    if chave in TEMAS:
        _tema_atual = chave


def alternar_tema() -> str:
    """Passa para o próximo tema da lista e devolve a chave dele."""
    global _tema_atual
    chaves = list(TEMAS)
    _tema_atual = chaves[(chaves.index(_tema_atual) + 1) % len(chaves)]
    return _tema_atual
