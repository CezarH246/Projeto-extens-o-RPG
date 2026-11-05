"""Leitura, gravacao, desfazer e busca de elementos do editor de colisao.

Esta classe mixin cuida apenas dos DADOS: o dicionario carregado do JSON, a
camada ativa e as operacoes de procurar pontos/retangulos sob o mouse. Nenhum
metodo aqui desenha ou le teclado; isso fica nos outros mixins.
"""

from __future__ import annotations

# copy permite guardar uma copia profunda do estado antes de alterar.
import copy

# math calcula a distancia entre o mouse e os pontos/linhas.
import math

# pygame fornece Rect para testar cliques em retangulos.
import pygame

# covil_tritao indica onde o JSON deve ser salvo.
import covil_tritao

# Constantes e funcoes de geometria compartilhadas.
from ferramentas.editor_config import (
    CAMADAS,
    LADO_ALCA,
    MAXIMO_DESFAZER,
    RAIO_LINHA,
    RAIO_PONTO,
    cantos,
    distancia_ate_segmento,
    ponto_dentro,
)


class DadosMixin:
    """Operacoes sobre self.dados (carregado pelo Editor)."""

    @property
    def lista(self) -> list:
        """Lista de elementos da camada ativa."""
        return self.dados[self.camada]

    @property
    def camada_de_contorno(self) -> bool:
        """Verdadeiro quando a camada ativa usa poligonos em vez de retangulos."""
        return CAMADAS[self.camada][2]

    def guardar_para_desfazer(self) -> None:
        """Tira uma fotografia do estado atual antes de qualquer alteracao."""
        # deepcopy evita que listas internas sejam modificadas por engano.
        self.historico.append(copy.deepcopy(self.dados))

        # Mantem apenas as ultimas MAXIMO_DESFAZER fotografias.
        del self.historico[:-MAXIMO_DESFAZER]

        # Marca que existem mudancas nao salvas e cancela uma saida pendente.
        self.alterado = True
        self.confirmar_saida = False

    def desfazer(self) -> None:
        """Volta ao estado anterior guardado no historico."""
        if not self.historico:
            self.aviso = "Nada para desfazer."
            return

        # Recupera a ultima fotografia e limpa a selecao.
        self.dados = self.historico.pop()
        self.selecionado = None
        self.alterado = True
        self.aviso = "Desfeito."

    def salvar(self) -> None:
        """Limpa dados invalidos e grava o JSON de colisao."""
        # Contornos com menos de 3 pontos e retangulos sem area nao servem para nada.
        for chave, (_, _, contorno, _) in CAMADAS.items():
            if contorno:
                self.dados[chave] = [p for p in self.dados[chave] if len(p) >= 3]
        self.dados["bloqueios"] = [
            r for r in self.dados["bloqueios"] if r[2] > 2 and r[3] > 2
        ]

        def poligono(p):
            """Formata uma lista de pontos como [[x, y], ...]."""
            return "[" + ", ".join(f"[{round(x)}, {round(y)}]" for x, y in p) + "]"

        # Monta o texto do JSON manualmente para ficar legivel no Git.
        blocos = []
        for chave, (_, _, contorno, _) in CAMADAS.items():
            if contorno:
                itens = [poligono(p) for p in self.dados[chave]]
            else:
                itens = [
                    "[" + ", ".join(str(round(v)) for v in r) + "]"
                    for r in self.dados[chave]
                ]

            corpo = ",\n".join("    " + item for item in itens)
            blocos.append(
                f'  "{chave}": [\n{corpo}\n  ]' if itens else f'  "{chave}": []'
            )

        # Grava o arquivo lido pelo jogo.
        covil_tritao.ARQUIVO_COLISAO.write_text(
            "{\n" + ",\n".join(blocos) + "\n}\n",
            encoding="utf-8",
        )

        # A limpeza acima pode ter mudado os indices; limpa a selecao.
        self.alterado = False
        self.selecionado = None

        # Se o editor foi aberto dentro do jogo, aplica a colisao imediatamente.
        if self.ao_salvar:
            self.ao_salvar()
            self.aviso = 'Salvo! A colisão nova já vale no jogo (F3 volta a jogar).'
        else:
            self.aviso = (
                f"Salvo em {covil_tritao.ARQUIVO_COLISAO.name}. "
                "Abra o jogo de novo para ver."
            )

    def trocar_camada(self, chave: str) -> None:
        """Muda a camada ativa e, se necessario, o fundo exibido."""
        self.camada = chave

        # A camada pos-boss so faz sentido sobre o fundo pos-boss.
        if chave == "chao_posboss":
            self.fundo = "posboss"

        self.selecionado = None

        # Mostra a explicacao da camada no rodape.
        self.aviso = f"{CAMADAS[chave][0]}: {CAMADAS[chave][3]}"

    def ponto_proximo(self, pos):
        """Procura um ponto da camada ativa perto da posicao do mouse."""
        melhor, melhor_distancia = None, RAIO_PONTO

        # O item selecionado tem prioridade na busca.
        ordem = list(range(len(self.lista)))
        if self.selecionado is not None and self.selecionado < len(self.lista):
            ordem.insert(0, ordem.pop(self.selecionado))

        for i in ordem:
            for j, ponto in enumerate(self.lista[i]):
                distancia = math.dist(pos, ponto)
                if distancia <= melhor_distancia:
                    melhor, melhor_distancia = (i, j), distancia
        return melhor

    def linha_proxima(self, pos):
        """Procura uma aresta de poligono perto do mouse."""
        melhor, melhor_distancia = None, RAIO_LINHA

        for i, poligono in enumerate(self.lista):
            if len(poligono) < 2:
                continue

            # Cada aresta vai do ponto j ao proximo (o ultimo fecha no primeiro).
            for j in range(len(poligono)):
                a, b = poligono[j], poligono[(j + 1) % len(poligono)]
                distancia = distancia_ate_segmento(pos, a, b)
                if distancia <= melhor_distancia:
                    melhor, melhor_distancia = (i, j + 1), distancia
        return melhor

    def poligono_em(self, pos):
        """Devolve o indice do poligono que contem o ponto (do mais novo ao mais antigo)."""
        for i in reversed(range(len(self.lista))):
            if len(self.lista[i]) >= 3 and ponto_dentro(pos, self.lista[i]):
                return i
        return None

    def retangulo_em(self, pos):
        """Devolve o indice do retangulo que contem o ponto."""
        for i in reversed(range(len(self.lista))):
            if pygame.Rect(self.lista[i]).collidepoint(pos):
                return i
        return None

    def canto_em(self, pos):
        """Devolve (indice, canto) quando o mouse esta sobre uma alca de redimensionar."""
        for i in reversed(range(len(self.lista))):
            for indice, canto in enumerate(cantos(self.lista[i])):
                if (
                    abs(pos[0] - canto[0]) <= LADO_ALCA
                    and abs(pos[1] - canto[1]) <= LADO_ALCA
                ):
                    return i, indice
        return None

    def botao_em(self, pos) -> object | None:
        """Devolve o botao sob o mouse, se houver."""
        return next(
            (botao for botao in self.botoes if botao.retangulo.collidepoint(pos)),
            None,
        )

    def o_que_o_clique_faz(self, pos) -> str:
        """Texto da dica ao lado do cursor."""
        # No modo de teste o mouse nao edita nada.
        if self.testando:
            return ""

        # Camadas de contorno: ponto, linha, poligono ou inicio de contorno.
        if self.camada_de_contorno:
            if self.ponto_proximo(pos):
                return 'arraste: mover ponto  |  botão direito: apagar ponto'
            if self.linha_proxima(pos):
                return "clique: novo ponto nesta linha"
            if self.poligono_em(pos) is not None:
                return "clique: selecionar este contorno"
            if self.selecionado is not None and self.selecionado < len(self.lista):
                return "clique: acrescentar ponto ao contorno amarelo"
            return 'aperte N para começar um contorno novo'

        # Camadas de retangulo: alca, corpo ou desenho novo.
        if self.canto_em(pos):
            return "arraste: mudar o tamanho"
        if self.retangulo_em(pos) is not None:
            return 'arraste: mover  |  botão direito: apagar'
        return "arraste: desenhar um bloqueio novo"
