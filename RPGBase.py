"""Compatibilidade com a versao antiga do modulo de regras.

Use Combate.py como entrada principal; ambos os imports compartilham agora
os mesmos modelos e regras, evitando duas implementacoes divergentes.
"""

from Combate import *
from Combate import __all__
