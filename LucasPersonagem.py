import pygame
from pathlib import Path

from PIL import Image

#========================================================
# Classe personagem Lucas — segue o Cezar pelo mapa
#=====================================================
class Lucas(pygame.sprite.Sprite):

    def __init__(self, alvo, *groups):
        super().__init__(*groups)

        self.alvo = alvo
        self.pasta_personagem = "personagens/Lucas_O_Barbaro"
        self.pasta_caminhadas = (
            Path(__file__).resolve().parent
            / "assets" / "personagens" / "Lucas_Protagonista" / "caminhadas"
        )

        self.imagens_parado = {
            "east": self.carregar_imagem("Idle/rotations/east.png"),
            "north": self.carregar_imagem("Idle/rotations/north.png"),
            "south": self.carregar_imagem("Idle/rotations/south.png"),
            "west": self.carregar_imagem("Idle/rotations/west.png"),
        }

        # A caminhada do Lucas é um gif por direção (diferente do Cezar, que
        # usa pastas de frames PNG).
        self.imagens_caminhada = {
            direcao: self.carregar_gif_caminhada(f"Idle_walk_{direcao}.gif")
            for direcao in ("east", "north", "south", "west")
        }

        self.direcao_atual = "south"
        self.image = self.imagens_parado[self.direcao_atual]

        self.rect = pygame.Rect(80, 150, 32, 32)
        self.posicao = pygame.Vector2(self.rect.topleft)

        # Histórico usado pelo Guilherme, que segue o Lucas.
        self.historico_posicoes = [pygame.Vector2(self.posicao)]

        self.velocidade = 55
        self.distancia_minima = 28
        self.atraso_seguimento = 24

        self.quadro_animacao = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 0.12

    def carregar_imagem(self, caminho):
        caminho_imagem = f"{self.pasta_personagem}/{caminho}"
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, [32, 32])

    def carregar_gif_caminhada(self, nome):
        """Carrega todos os quadros de um gif de caminhada, no tamanho do sprite."""
        quadros = []
        with Image.open(self.pasta_caminhadas / nome) as gif:
            for indice in range(getattr(gif, "n_frames", 1)):
                gif.seek(indice)
                dados = gif.convert("RGBA").tobytes()
                imagem = pygame.image.fromstring(dados, gif.size, "RGBA").convert_alpha()
                quadros.append(pygame.transform.scale(imagem, [32, 32]))
        return quadros

    def obter_destino(self):
        historico = self.alvo.historico_posicoes
        if len(historico) >= self.atraso_seguimento:
            return pygame.Vector2(historico[-self.atraso_seguimento])
        return pygame.Vector2(self.alvo.posicao)

    def update(self, tempo_frame):
        destino = self.obter_destino()
        diferenca = destino - self.posicao

        if diferenca.length_squared() > self.distancia_minima ** 2:
            if abs(diferenca.x) > abs(diferenca.y):
                self.direcao_atual = "east" if diferenca.x > 0 else "west"
            else:
                self.direcao_atual = "south" if diferenca.y > 0 else "north"

            direcao = diferenca.normalize()
            self.posicao += direcao * self.velocidade * tempo_frame
            self.rect.topleft = round(self.posicao.x), round(self.posicao.y)

            self.historico_posicoes.append(pygame.Vector2(self.posicao))
            if len(self.historico_posicoes) > 80:
                self.historico_posicoes.pop(0)

            self.tempo_animacao += tempo_frame
            if self.tempo_animacao >= self.velocidade_animacao:
                self.tempo_animacao -= self.velocidade_animacao
                total_quadros = len(self.imagens_caminhada[self.direcao_atual])
                self.quadro_animacao = (self.quadro_animacao + 1) % total_quadros
            self.image = self.imagens_caminhada[self.direcao_atual][self.quadro_animacao]
        else:
            self.direcao_atual = self.alvo.direcao_atual
            self.quadro_animacao = 0
            self.tempo_animacao = 0
            self.image = self.imagens_parado[self.direcao_atual]
