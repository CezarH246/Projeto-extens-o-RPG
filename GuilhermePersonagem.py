import pygame

#========================================================
# Classe personagem Guilherme — segue o Lucas pelo mapa
#=====================================================
class Guilherme(pygame.sprite.Sprite):

    def __init__(self, alvo, *groups):
        super().__init__(*groups)

        self.alvo = alvo
        self.pasta_personagem = "personagens/Guilherme_O_Mago"

        self.imagens_parado = {
            "east": self.carregar_imagem("Idle/rotations/east.png"),
            "north": self.carregar_imagem("Idle/rotations/north.png"),
            "south": self.carregar_imagem("Idle/rotations/south.png"),
            "west": self.carregar_imagem("Idle/rotations/west.png"),
        }

        # Pastas com sufixo vêm do exportador das sprites.
        pastas_caminhada = {
            "east": "east-e39e0c32",
            "north": "north",
            "south": "south",
            "west": "west-cdc3a2ce",
        }
        self.quadros_caminhada = 6
        self.imagens_caminhada = {
            direcao: [
                self.carregar_imagem(
                    f"Idle/animations/Walk/{pastas_caminhada[direcao]}/frame_{quadro:03d}.png"
                )
                for quadro in range(self.quadros_caminhada)
            ]
            for direcao in pastas_caminhada
        }

        self.direcao_atual = "south"
        self.image = self.imagens_parado[self.direcao_atual]

        self.rect = pygame.Rect(80, 220, 32, 32)
        self.posicao = pygame.Vector2(self.rect.topleft)

        self.velocidade = 50
        self.distancia_minima = 28
        self.atraso_seguimento = 24

        self.quadro_animacao = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 0.12

    def carregar_imagem(self, caminho):
        caminho_imagem = f"{self.pasta_personagem}/{caminho}"
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, [32, 32])

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

            self.tempo_animacao += tempo_frame
            if self.tempo_animacao >= self.velocidade_animacao:
                self.tempo_animacao -= self.velocidade_animacao
                self.quadro_animacao = (self.quadro_animacao + 1) % self.quadros_caminhada
            self.image = self.imagens_caminhada[self.direcao_atual][self.quadro_animacao]
        else:
            self.direcao_atual = self.alvo.direcao_atual
            self.quadro_animacao = 0
            self.tempo_animacao = 0
            self.image = self.imagens_parado[self.direcao_atual]
