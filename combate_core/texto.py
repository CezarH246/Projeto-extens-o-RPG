"""Text output shared by terminal combat and the battle interface."""

import sys
import time

from .configuracao import velocidade_texto

_saida = None

def definir_saida(funcao):
    """Define o destino das mensagens (terminal ou log visual da batalha)."""
    global _saida
    _saida = funcao

def imprimir_lento(*args, sep=" ", end="\n"):
    """Display text gradually when no visual output destination is configured."""
    texto = sep.join(str(arg) for arg in args)
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(velocidade_texto())
    sys.stdout.write(end)
    sys.stdout.flush()

def print(*args, sep=" ", end="\n"):
    """Single output entry point used by all rule modules."""
    if _saida is not None:
        return _saida(*args, sep=sep, end=end)
    return imprimir_lento(*args, sep=sep, end=end)
