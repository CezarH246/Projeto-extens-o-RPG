import pygame
#============================================
#IMPORTANDO PERSONAGENS E INIMIGOS
#============================================
from CezarPersonagem import Cezar
from LucasPersonagem import Lucas
from GuilhermePersonagem import Guilherme
from InimigoPersonagem import InimigoPeixe
from Combate import batalha, criar_herois

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
fonte = pygame.font.SysFont(None, 24)
fonte_alerta = pygame.font.SysFont(None, 32)

#==================================================
#CRIANDO UM GRUPO PARA ARMAZENAR TODAS AS SPRITS
#                      E
#                   IMPORTAR
#==================================================
# O grupo organiza o personagem e chama o método update() dele.
grupo_objetos = pygame.sprite.Group()
grupo_herois = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()

personagem_cezar = Cezar()
personagem_lucas = Lucas(personagem_cezar)
personagem_guilherme = Guilherme(personagem_lucas)

grupo_herois.add(personagem_guilherme, personagem_lucas, personagem_cezar)

inimigo_horizontal = InimigoPeixe(
    420, 80,
    eixo="horizontal",
    limites=pygame.Rect(280, 80, 480, 50),
)
inimigo_vertical = InimigoPeixe(
    620, 160,
    eixo="vertical",
    limites=pygame.Rect(620, 80, 50, 320),
)

grupo_inimigos.add(inimigo_horizontal, inimigo_vertical)
grupo_objetos.add(grupo_herois, grupo_inimigos)

# Heróis do Combate.py — o HP e o nível continuam entre as batalhas.
herois_combate = criar_herois()
mensagem_status = "WASD para mover. Enceste um inimigo para batalhar no terminal."


def retangulo_colisao(sprite):
    return sprite.rect.inflate(-18, -18)


def sprites_colidiram(sprite_a, sprite_b):
    return retangulo_colisao(sprite_a).colliderect(retangulo_colisao(sprite_b))


def inimigo_colidiu_com_grupo():
    for heroi in grupo_herois:
        for inimigo in grupo_inimigos:
            if sprites_colidiram(heroi, inimigo):
                return inimigo
    return None


def mostrar_aviso_batalha():
    tela.fill([4, 17, 36])
    grupo_objetos.draw(tela)
    aviso = fonte_alerta.render(
        "Batalha iniciada! Jogue no terminal.",
        True,
        (255, 220, 120),
    )
    tela.blit(aviso, (180, 220))
    pygame.display.update()
    pygame.event.pump()


def iniciar_combate(inimigo_mapa):
    global mensagem_status

    pygame.display.set_caption("RPG Saga dos Falidos — batalha no terminal")
    mostrar_aviso_batalha()

    vitoria = batalha(herois_combate)

    pygame.display.set_caption("RPG Saga dos Falidos")
    pygame.event.clear()

    if vitoria:
        inimigo_mapa.kill()
        mensagem_status = "Vitoria! O inimigo saiu do mapa. Continue explorando."
        return True

    mensagem_status = "Derrota. Todos os herois caíram."
    return False


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

    texto = fonte.render(mensagem_status, True, (220, 220, 230))
    tela.blit(texto, (12, 12))

    
   
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

        inimigo_em_colisao = inimigo_colidiu_com_grupo()
        if inimigo_em_colisao is not None:
            ainda_vivo = iniciar_combate(inimigo_em_colisao)
            if not ainda_vivo:
                loop_jogo = False

        # Mostra na janela o desenho preparado neste frame.
        pygame.display.update()
