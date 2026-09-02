import pygame

#========================================================
# Inimigo no mapa — anda só no eixo horizontal ou vertical
#=====================================================
class InimigoPeixe(pygame.sprite.Sprite):

    def __init__(self, x, y, eixo="horizontal", limites=None, *groups):
        super().__init__(*groups)

        self.pasta_inimigo = "inimigos/Inimgo_Peixei"
        self.eixo = eixo
        self.sentido = 1

        self.imagens_parado = {
            "east": self.carregar_imagem("Idle/rotations/east.png"),
            "north": self.carregar_imagem("Idle/rotations/north.png"),
            "south": self.carregar_imagem("Idle/rotations/south.png"),
            "west": self.carregar_imagem("Idle/rotations/west.png"),
        }

        self.quadros_caminhada = 6
        self.imagens_caminhada = {
            direcao: [
                self.carregar_imagem(
                    f"Idle/animations/Walk/{direcao}/frame_{quadro:03d}.png"
                )
                for quadro in range(self.quadros_caminhada)
            ]
            for direcao in ("east", "north", "south", "west")
        }

        self.direcao_atual = "east" if eixo == "horizontal" else "south"
        self.image = self.imagens_caminhada[self.direcao_atual][0]

        self.rect = pygame.Rect(x, y, 32, 32)
        self.posicao = pygame.Vector2(self.rect.topleft)

        self.velocidade = 45
        self.limites = limites or pygame.Rect(0, 0, 720, 720)

        self.quadro_animacao = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 0.12

    def carregar_imagem(self, caminho):
        caminho_imagem = f"{self.pasta_inimigo}/{caminho}"
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, [32, 32])

    def retangulo_colisao(self):
        return self.rect.inflate(-18, -18)

    def update(self, tempo_frame):
        deslocamento = self.velocidade * tempo_frame * self.sentido

        if self.eixo == "horizontal":
            self.posicao.x += deslocamento
            if self.posicao.x < self.limites.left:
                self.posicao.x = self.limites.left
                self.sentido *= -1
            elif self.posicao.x > self.limites.right - self.rect.width:
                self.posicao.x = self.limites.right - self.rect.width
                self.sentido *= -1
            self.direcao_atual = "east" if self.sentido > 0 else "west"
        else:
            self.posicao.y += deslocamento
            if self.posicao.y < self.limites.top:
                self.posicao.y = self.limites.top
                self.sentido *= -1
            elif self.posicao.y > self.limites.bottom - self.rect.height:
                self.posicao.y = self.limites.bottom - self.rect.height
                self.sentido *= -1
            self.direcao_atual = "south" if self.sentido > 0 else "north"

        self.rect.topleft = round(self.posicao.x), round(self.posicao.y)

        self.tempo_animacao += tempo_frame
        if self.tempo_animacao >= self.velocidade_animacao:
            self.tempo_animacao -= self.velocidade_animacao
            self.quadro_animacao = (self.quadro_animacao + 1) % self.quadros_caminhada
        self.image = self.imagens_caminhada[self.direcao_atual][self.quadro_animacao]
