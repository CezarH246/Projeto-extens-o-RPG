import pygame

#========================================================
# Classe personagem Lucas — segue o Cezar pelo mapa
#=====================================================
class Lucas(pygame.sprite.Sprite):

    def __init__(self, alvo, *groups):
        super().__init__(*groups)

        self.alvo = alvo
        self.pasta_personagem = "personagens/Lucas_O_Barbaro"

        self.imagens_parado = {
            "east": self.carregar_imagem("Idle/rotations/east.png"),
            "north": self.carregar_imagem("Idle/rotations/north.png"),
            "south": self.carregar_imagem("Idle/rotations/south.png"),
            "west": self.carregar_imagem("Idle/rotations/west.png"),
        }

        # A animação de caminhada para oeste usa pasta com sufixo do exportador.
        pastas_caminhada = {
            "east": "east",
            "north": "north",
            "south": "south",
            "west": "west-c61c6cb2",
        }
        self.imagens_caminhada = {
            direcao: [
                self.carregar_imagem(
                    f"Idle/animations/Walking/{pastas_caminhada[direcao]}/frame_{quadro:03d}.png"
                )
                for quadro in range(4)
            ]
            for direcao in pastas_caminhada
        }

        self.direcao_atual = "south"
        self.image = self.imagens_parado[self.direcao_atual]

        self.rect = pygame.Rect(50, 90, 50, 50)
        self.posicao = pygame.Vector2(self.rect.topleft)

        self.velocidade = 55
        self.distancia_minima = 6

        self.quadro_animacao = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 0.12

    def carregar_imagem(self, caminho):
        caminho_imagem = f"{self.pasta_personagem}/{caminho}"
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, [50, 50])

    def obter_destino(self):
        historico = self.alvo.historico_posicoes
        if len(historico) >= 10:
            return pygame.Vector2(historico[-10])
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
                self.quadro_animacao = (self.quadro_animacao + 1) % 4
            self.image = self.imagens_caminhada[self.direcao_atual][self.quadro_animacao]
        else:
            self.direcao_atual = self.alvo.direcao_atual
            self.quadro_animacao = 0
            self.tempo_animacao = 0
            self.image = self.imagens_parado[self.direcao_atual]
