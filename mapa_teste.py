import pygame
#============================================
#IMPORTANDO PERSONAGEM CEZAR
#============================================
from CezarPersonagem import Cezar
from LucasPersonagem import Lucas

#============================================
#Funcao que ininicializa o pygame
#============================================
pygame.init()
# Controla o tempo entre os frames e limita o jogo a 60 FPS.
relogio = pygame.time.Clock()

#=============================================
#criação da janela
#=============================================
tela = pygame.display.set_mode([840, 480])
pygame.display.set_caption("RPG Saga dos Falidos")


#==================================================
#CRIANDO UM GRUPO PARA ARMAZENAR TODAS AS SPRITS
#                      E
#                   IMPORTAR
#==================================================
# O grupo organiza o personagem e chama o método update() dele.
grupo_objetos = pygame.sprite.Group()
personagem_cezar = Cezar()
personagem_lucas = Lucas(personagem_cezar)
grupo_objetos.add(personagem_lucas, personagem_cezar)



#================================================
# FUNÇAO DE DESENHAR NA TELA
# E ATUALIZAÇÃO
#===============================================
def desenhar():
    # Limpa o frame anterior com a cor de fundo.
    tela.fill([4, 17, 36])

    # Envia o tempo do frame para o personagem calcular o movimento.
    grupo_objetos.update(relogio.tick(60) / 1000)

    # Desenha todos os sprites do grupo na janela.
    grupo_objetos.draw(tela)

    
   
#==================================================
# Criação de um loop para atualizar a tela.
# Variaveis globais
#==================================================
loop_jogo = True
#Pressionando_W = False

if __name__ == "__main__":
    while loop_jogo:

        # Lê os eventos da janela, como o clique no botão Fechar.
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                loop_jogo = False

        # Atualiza a tela e o personagem a cada volta do loop.
        desenhar()

        # Mostra na janela o desenho preparado neste frame.
        pygame.display.update()