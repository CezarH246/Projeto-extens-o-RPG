"""Valores compartilhados pelas regras do combate."""

import sys

ESCALAS = {
    "Lucas": 1.1,
    "Guilherme": 1.0,
    "Cezar": 1.0,
}
VELOCIDADE_TEXTO = 0.01
TESTE_ULTIMATES_SEM_RESTRICAO = True


def ultimates_sem_restricao() -> bool:
    """Leia a chave publica da fachada para preservar o controle de testes."""
    modulo = sys.modules.get("Combate")
    if modulo is not None:
        return getattr(modulo, "TESTE_ULTIMATES_SEM_RESTRICAO", TESTE_ULTIMATES_SEM_RESTRICAO)
    return TESTE_ULTIMATES_SEM_RESTRICAO


def velocidade_texto() -> float:
    """Leia a velocidade publica para manter configuravel o texto gradual."""
    modulo = sys.modules.get("Combate")
    if modulo is not None:
        return getattr(modulo, "VELOCIDADE_TEXTO", VELOCIDADE_TEXTO)
    return VELOCIDADE_TEXTO
