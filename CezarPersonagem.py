import pygame

#========================================================
#Classe personagem Cezar vai herdar as sprites de Cezar
#=====================================================
class Cezar(pygame.sprite.Sprite):

    def __init__(self, *groups):
        # Registra o personagem nos grupos de sprites recebidos.
        super().__init__(*groups)   

        # Carrega as imagens usadas quando o personagem está parado.
        # A chave (east, north, south ou west) identifica a direção da imagem.
        self.imagens_parado = {
            "east": self.carregar_imagem("Idle/rotations/east.png"),
            "north": self.carregar_imagem("Idle/rotations/north.png"),
            "south": self.carregar_imagem("Idle/rotations/south.png"),
            "west": self.carregar_imagem("Idle/rotations/west.png"),
        }

        # Carrega os quatro frames de caminhada de cada direção.
        # Por exemplo, a direção east recebe frame_000.png até frame_003.png.
        self.imagens_caminhada = {
            direcao: [
                self.carregar_imagem(
                    # :3d completa o número com zeros: 0 vira "000".
                    f"Idle/animations/Walking/{direcao}/frame_{quadro:03d}.png"
                )
                for quadro in range(4)
            ]
            for direcao in ("east", "north", "south", "west")
        }

        # Começa olhando para o sul, usando a imagem parada correspondente.
        self.direcao_atual = "south"
        self.image = self.imagens_parado[self.direcao_atual]

        # O rect guarda a posição e o tamanho usados pelo Pygame para desenhar.
        self.rect = pygame.Rect(50, 50, 50, 50)

        # Vector2 permite guardar posições com casas decimais durante o movimento.
        self.posicao = pygame.Vector2(self.rect.topleft)

        # Velocidade em pixels por segundo. Diminua este valor para andar mais devagar.
        self.velocidade = 60

        # Controlam qual frame da caminhada está visível e quando trocar para o próximo.
        self.quadro_animacao = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 0.12

    def carregar_imagem(self, caminho):
        # Centraliza o carregamento e o redimensionamento de todas as imagens.
        caminho_imagem = f"personagens/Cezar_O_Ladino/{caminho}"
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, [50, 50])

    def update(self, tempo_frame):
        # Este método é chamado uma vez por frame pelo grupo de sprites.
        # Verifica quais teclas estão pressionadas neste momento.
        teclas = pygame.key.get_pressed()

        # Começa sem movimento; as teclas abaixo alteram x e y da direção.
        direcao = pygame.Vector2(0, 0)
        if teclas[pygame.K_d]:
            direcao.x += 1
        if teclas[pygame.K_a]:
            direcao.x -= 1
        if teclas[pygame.K_s]:
            direcao.y += 1
        if teclas[pygame.K_w]:
            direcao.y -= 1

        if direcao.length_squared() > 0:
            # Só troca a imagem e a posição quando alguma tecla é pressionada.
            # Como só existem animações cardeais, escolhe o eixo dominante.
            if abs(direcao.x) > abs(direcao.y):
                self.direcao_atual = "east" if direcao.x > 0 else "west"
            else:
                self.direcao_atual = "south" if direcao.y > 0 else "north"

            # Impede que o movimento diagonal seja mais rápido que o reto.
            direcao = direcao.normalize()

            # O tempo do frame torna a velocidade estável mesmo se o FPS variar.
            self.posicao += direcao * self.velocidade * tempo_frame

            # O rect precisa acompanhar a posição para o sprite aparecer no lugar certo.
            self.rect.topleft = round(self.posicao.x), round(self.posicao.y)

            # Troca o frame da caminhada conforme o tempo passa.
            self.tempo_animacao += tempo_frame
            if self.tempo_animacao >= self.velocidade_animacao:
                self.tempo_animacao -= self.velocidade_animacao
                # O operador % faz a animação voltar ao frame 0 após o frame 3.
                self.quadro_animacao = (self.quadro_animacao + 1) % 4
            self.image = self.imagens_caminhada[self.direcao_atual][self.quadro_animacao]
        else:
            # Parado, o personagem mostra a imagem da última direção usada.
            self.quadro_animacao = 0
            self.tempo_animacao = 0
            self.image = self.imagens_parado[self.direcao_atual]
