"""Recompensa do baú do covil: o bolo e, depois, a carta dos alunos.

Aparece por cima do mapa quando o jogador abre o baú (depois de derrotar o Rei
Tritão). E, Enter ou Espaço avançam: bolo -> carta -> fim. Na carta, a primeira
tecla mostra o texto inteiro se ele ainda estiver sendo escrito.

O bolo é desenhado em pixel art por código (num quadro pequeno, ampliado sem
suavizar), para combinar com os sprites do jogo sem precisar de imagem.
"""

from __future__ import annotations

import math
import random

import pygame

TEXTO_CARTA = (
    "Parabéns, aventureiro! Você derrotou o guardião das masmorras e provou seu "
    "valor. Como recompensa, leve este tesouro supremo... Só tome cuidado ao aceitar "
    "convites repentinos para salas adjacentes. Lembre-se: nem todo 'pedaço de bolo' "
    "oferecido nos corredores é apenas confeitaria. Há ofertas que exigem mais do que "
    "pontos de HP para digerir."
)
ASSINATURA_CARTA = "— Assinado: Os Falidos."

TECLAS_AVANCAR = (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
LETRAS_POR_SEGUNDO = 45
FONTES_CARTA = "georgia,palatinolinotype,bookantiqua,timesnewroman"

# Paleta do bolo (pixel art).
COR_PRATO = (214, 220, 230)
COR_PRATO_SOMBRA = (150, 158, 175)
COR_MASSA = (150, 88, 52)
COR_MASSA_SOMBRA = (112, 62, 36)
COR_RECHEIO = (240, 150, 170)
COR_COBERTURA = (252, 244, 236)
COR_COBERTURA_SOMBRA = (222, 206, 198)
COR_MORANGO = (220, 40, 60)
COR_FOLHA = (70, 160, 70)
COR_VELA = (120, 180, 240)
COR_VELA_LISTRA = (250, 250, 255)


def criar_bolo(escala: int = 6) -> pygame.Surface:
    """Bolo de dois andares com cobertura escorrendo, morangos e uma vela."""
    base = pygame.Surface((48, 48), pygame.SRCALPHA)
    desenhar = pygame.draw

    # Prato.
    desenhar.ellipse(base, COR_PRATO_SOMBRA, (3, 39, 42, 8))
    desenhar.ellipse(base, COR_PRATO, (3, 38, 42, 7))

    # Andar de baixo: massa, faixa de recheio e cobertura em cima.
    desenhar.rect(base, COR_MASSA, (7, 26, 34, 14))
    desenhar.rect(base, COR_MASSA_SOMBRA, (33, 26, 8, 14))
    desenhar.rect(base, COR_RECHEIO, (7, 32, 34, 2))
    desenhar.rect(base, COR_COBERTURA, (6, 24, 36, 4))
    for x, comprimento in ((8, 4), (13, 2), (18, 5), (24, 3), (29, 5), (35, 2), (39, 3)):
        desenhar.rect(base, COR_COBERTURA, (x, 28, 2, comprimento))

    # Andar de cima.
    desenhar.rect(base, COR_MASSA, (13, 14, 22, 11))
    desenhar.rect(base, COR_MASSA_SOMBRA, (29, 14, 6, 11))
    desenhar.rect(base, COR_RECHEIO, (13, 19, 22, 2))
    desenhar.rect(base, COR_COBERTURA, (12, 12, 24, 4))
    desenhar.rect(base, COR_COBERTURA_SOMBRA, (30, 12, 6, 4))
    for x, comprimento in ((14, 3), (19, 5), (24, 2), (28, 4), (33, 2)):
        desenhar.rect(base, COR_COBERTURA, (x, 16, 2, comprimento))

    # Morangos no andar de baixo e no topo.
    for x, y in ((9, 22), (20, 22), (31, 22), (16, 10), (29, 10)):
        desenhar.rect(base, COR_MORANGO, (x, y, 3, 3))
        desenhar.rect(base, COR_FOLHA, (x + 1, y - 1, 1, 1))

    # Vela (a chama é desenhada à parte, para tremular).
    desenhar.rect(base, COR_VELA, (23, 4, 2, 8))
    for y in (5, 8):
        desenhar.rect(base, COR_VELA_LISTRA, (23, y, 2, 1))

    return pygame.transform.scale(base, (base.get_width() * escala, base.get_height() * escala))


def quebrar_linhas(texto: str, fonte: pygame.font.Font, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if fonte.size(tentativa)[0] <= largura:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


class RecompensaBau:
    ESCALA_BOLO = 6

    def __init__(self, tamanho_tela: tuple[int, int]):
        self.tamanho = tamanho_tela
        self.etapa = "bolo"
        self.tempo = 0.0
        self.concluida = False
        self.letras_visiveis = 0.0
        self.bolo = criar_bolo(self.ESCALA_BOLO)
        self.faiscas: list[list[float]] = []  # [x, y, vel_y, vida]

        self.fonte_titulo = pygame.font.SysFont(FONTES_CARTA, 34, bold=True)
        self.fonte_carta = pygame.font.SysFont(FONTES_CARTA, 24, italic=True)
        self.fonte_assinatura = pygame.font.SysFont(FONTES_CARTA, 22, bold=True)
        self.fonte_dica = pygame.font.SysFont(None, 24)

        largura_carta = min(780, tamanho_tela[0] - 80)
        self.carta = pygame.Rect(0, 0, largura_carta, 0)
        self.margem_carta = 46
        self.linhas_carta = quebrar_linhas(TEXTO_CARTA, self.fonte_carta, largura_carta - 2 * self.margem_carta)
        altura_linha = self.fonte_carta.get_linesize() + 4
        self.altura_linha = altura_linha
        self.carta.height = 2 * self.margem_carta + 50 + altura_linha * len(self.linhas_carta) + 60
        self.carta.center = (tamanho_tela[0] // 2, tamanho_tela[1] // 2)

    @property
    def total_letras(self) -> int:
        return sum(len(linha) for linha in self.linhas_carta)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type != pygame.KEYDOWN or evento.key not in TECLAS_AVANCAR:
            return
        if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and evento.mod & pygame.KMOD_ALT:
            return  # Alt+Enter é a tela cheia.
        if self.etapa == "bolo":
            if self.tempo > 0.6:  # evita pular o bolo com a mesma tecla que abriu o baú
                self.etapa = "carta"
                self.tempo = 0.0
        elif self.letras_visiveis < self.total_letras:
            self.letras_visiveis = self.total_letras
        else:
            self.concluida = True

    def atualizar(self, tempo_frame: float) -> None:
        self.tempo += tempo_frame
        if self.etapa == "carta":
            self.letras_visiveis = min(self.total_letras, self.letras_visiveis + LETRAS_POR_SEGUNDO * tempo_frame)
        else:
            centro_x = self.tamanho[0] // 2
            if random.random() < 0.5:
                x = centro_x + random.uniform(-170, 170)
                y = self.tamanho[1] // 2 + random.uniform(-40, 140)
                self.faiscas.append([x, y, random.uniform(-60, -25), 1.0])
        for faisca in self.faiscas:
            faisca[1] += faisca[2] * tempo_frame
            faisca[3] -= tempo_frame / 1.4
        self.faiscas = [f for f in self.faiscas if f[3] > 0]

    def desenhar(self, tela: pygame.Surface) -> None:
        veu = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        veu.fill((0, 0, 0, 175))
        tela.blit(veu, (0, 0))
        if self.etapa == "bolo":
            self.desenhar_bolo(tela)
        else:
            self.desenhar_carta(tela)

    def desenhar_dica(self, tela: pygame.Surface, texto: str, y: int) -> None:
        alfa = int(150 + 105 * (math.sin(self.tempo * 4) + 1) / 2)
        dica = self.fonte_dica.render(texto, True, (255, 235, 170))
        dica.set_alpha(alfa)
        tela.blit(dica, dica.get_rect(center=(tela.get_width() // 2, y)))

    def desenhar_bolo(self, tela: pygame.Surface) -> None:
        largura, altura = tela.get_size()
        # Entra subindo e crescendo nos primeiros instantes.
        entrada = min(1.0, self.tempo / 0.7)
        suave = 1 - (1 - entrada) ** 3
        centro = (largura // 2, round(altura // 2 + 30 + (1 - suave) * 60))

        # Brilho dourado pulsando atrás do bolo.
        raio = int(190 + 12 * math.sin(self.tempo * 3))
        brilho = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for passo in range(8, 0, -1):
            pygame.draw.circle(brilho, (255, 210, 110, int(14 * suave)), (raio, raio), raio * passo // 8)
        tela.blit(brilho, brilho.get_rect(center=centro))

        bolo = self.bolo
        if suave < 1:
            lado = max(1, round(bolo.get_width() * (0.6 + 0.4 * suave)))
            bolo = pygame.transform.scale(bolo, (lado, lado))
        retangulo = bolo.get_rect(center=centro)
        tela.blit(bolo, retangulo)

        # Chama da vela tremulando (posição relativa ao desenho de 48 px).
        escala = retangulo.width / 48
        chama_x = retangulo.left + 24 * escala
        chama_y = retangulo.top + 2.5 * escala + math.sin(self.tempo * 18) * escala * 0.3
        pygame.draw.ellipse(tela, (255, 170, 40), (chama_x - 1.6 * escala, chama_y - 2.2 * escala, 3.2 * escala, 4 * escala))
        pygame.draw.ellipse(tela, (255, 245, 170), (chama_x - 0.8 * escala, chama_y - 1 * escala, 1.6 * escala, 2.4 * escala))

        for x, y, _, vida in self.faiscas:
            tamanho = 2 + int(vida * 3)
            cor = (255, 240, 160)
            pygame.draw.rect(tela, cor, (x, y, tamanho, tamanho))

        titulo = self.fonte_titulo.render("Você encontrou o TESOURO SUPREMO!", True, (255, 225, 120))
        sombra = self.fonte_titulo.render("Você encontrou o TESOURO SUPREMO!", True, (40, 20, 0))
        topo = retangulo.top - 70
        tela.blit(sombra, sombra.get_rect(center=(largura // 2 + 2, topo + 2)))
        tela.blit(titulo, titulo.get_rect(center=(largura // 2, topo)))
        if self.tempo > 0.6:
            self.desenhar_dica(tela, "E / Enter: ler a carta que veio junto", retangulo.bottom + 40)

    def desenhar_carta(self, tela: pygame.Surface) -> None:
        carta = self.carta
        # Pergaminho: papel envelhecido, borda escura e cantos enrolados.
        pygame.draw.rect(tela, (60, 40, 20), carta.move(6, 8), border_radius=14)
        pygame.draw.rect(tela, (236, 220, 180), carta, border_radius=14)
        pygame.draw.rect(tela, (214, 192, 145), carta.inflate(-18, -18), 2, border_radius=10)
        pygame.draw.rect(tela, (120, 84, 44), carta, 4, border_radius=14)
        for canto in (carta.topleft, carta.topright, carta.bottomleft, carta.bottomright):
            pygame.draw.circle(tela, (200, 176, 128), canto, 12)
            pygame.draw.circle(tela, (120, 84, 44), canto, 12, 3)

        x = carta.left + self.margem_carta
        y = carta.top + self.margem_carta
        titulo = self.fonte_titulo.render("Uma carta no fundo do baú", True, (90, 50, 20))
        tela.blit(titulo, titulo.get_rect(midtop=(carta.centerx, y - 10)))
        y += 50

        restantes = int(self.letras_visiveis)
        for linha in self.linhas_carta:
            if restantes <= 0:
                break
            trecho = linha[:restantes]
            restantes -= len(linha)
            tela.blit(self.fonte_carta.render(trecho, True, (55, 35, 20)), (x, y))
            y += self.altura_linha

        if self.letras_visiveis >= self.total_letras:
            assinatura = self.fonte_assinatura.render(ASSINATURA_CARTA, True, (90, 40, 20))
            tela.blit(assinatura, assinatura.get_rect(topright=(carta.right - self.margem_carta, y + 16)))
            self.desenhar_dica(tela, "E / Enter: fechar a carta", carta.bottom + 28)
