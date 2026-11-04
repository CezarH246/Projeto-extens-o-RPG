"""Regras de colisao, movimento e animacao usadas pelo mapa.

O mapa trabalha com duas ideias diferentes:
- o "rect" do sprite e a area que o pygame usa para desenhar e para calcular
  encontros;
- o "retangulo de colisao" e uma area menor (ou os pes) que decide se o
  personagem pode pisar ali.

Separar essas funcoes em um modulo proprio deixa o loop principal (mapa_jogo.py)
menor e permite que o editor de colisao reutilize exatamente as mesmas regras.
"""

from __future__ import annotations

# pygame fornece Rect, Vector2, Surface e as operacoes de desenho.
import pygame

# config guarda as constantes e o dicionario CENA compartilhado.
import mapa_config as config


def carregar_mapa() -> pygame.Surface | None:
    """Carrega o mapa novo que recebe o grupo ao fim do caminho."""
    # A lista de candidatos permite tentar mais de um arquivo no futuro.
    candidatos = [
        config.MAPA_INICIAL,
    ]

    # Percorre os caminhos na ordem e usa o primeiro que existir e abrir.
    for caminho in candidatos:
        if caminho.exists():
            try:
                # convert() deixa a imagem no formato de pixel da tela (mais rapido).
                imagem = pygame.image.load(caminho).convert()

                # A imagem original e maior; primeiro ela e redimensionada.
                imagem = pygame.transform.smoothscale(imagem, (900, 600))

                # Depois recortamos somente a area jogavel de 720x480.
                config.MAPA_COLISAO = imagem.subsurface(
                    pygame.Rect(90, 60, config.LARGURA_MAPA, config.ALTURA_MAPA)
                ).copy()
                return config.MAPA_COLISAO
            except pygame.error:
                # Se o arquivo estiver corrompido, tenta o proximo candidato.
                continue

    # Nenhum mapa pode ser carregado; o jogo usara o desenho provisorio.
    return None


def carregar_mapa_caminho() -> pygame.Surface | None:
    """Carrega o mapa inicial (mapateste.jpeg) e o ajusta ao tamanho logico."""
    # Registra qual mapa esta ativo (usado pelo desenho provisorio).
    config.MAPA_ATUAL = "mapateste"
    try:
        # Carrega a imagem do disco e converte para o formato da tela.
        imagem = pygame.image.load(config.MAPA_CAMINHO).convert()

        # Redimensiona exatamente para a resolucao logica do mapa.
        config.MAPA_COLISAO = pygame.transform.smoothscale(
            imagem, (config.LARGURA_MAPA, config.ALTURA_MAPA)
        )
        return config.MAPA_COLISAO
    except pygame.error:
        # Sem imagem, o chamador desenha o mapa provisorio.
        return None


def desenhar_mapa_provisorio(tela: pygame.Surface, mapa_atual: str = "Casa_teste") -> None:
    'Mantém o jogo funcional caso a imagem de mapa não seja encontrada.'
    # O valor padrao "Casa_teste" reproduz o comportamento historico do jogo:
    # quando a imagem falta, ele desenha a versao de interior (casa).
    if mapa_atual == "Casa_teste":
        # Fundo marrom e piso claro representando uma casa.
        tela.fill((92, 72, 56))
        pygame.draw.rect(tela, (184, 163, 125), (32, 32, 776, 416))
        pygame.draw.rect(tela, (117, 96, 73), (32, 32, 776, 416), 8)

        # Porta e janela.
        pygame.draw.rect(tela, (72, 55, 44), (646, 100, 96, 56))
        pygame.draw.rect(tela, (213, 177, 79), (650, 104, 88, 48), 4)

        # Linhas verticais e horizontais simulando as tabuas do piso.
        for x in range(90, 780, 64):
            pygame.draw.line(tela, (169, 145, 108), (x, 40), (x, 440), 1)
        for y in range(40, 440, 64):
            pygame.draw.line(tela, (169, 145, 108), (40, y), (800, y), 1)
        return

    # Versao ao ar livre: fundo verde e caminhos de pedra.
    tela.fill((96, 115, 38))

    # Caminhos de pedra aproximados do mapa de referencia.
    pedras = [
        (280, 0, 280, 75),
        (450, 75, 130, 170),
        (0, 210, 250, 38),
        (95, 248, 125, 135),
        (220, 175, 52, 86),
    ]
    for pedra in pedras:
        pygame.draw.rect(tela, (150, 150, 130), pedra)
        pygame.draw.rect(tela, (110, 110, 92), pedra, 1)

    # Desenha referencias visuais para os mesmos objetos que bloqueiam o movimento.
    for obstaculo in config.COLISOES_TERRENO:
        pygame.draw.rect(tela, (79, 70, 59), obstaculo)
        pygame.draw.rect(tela, (45, 40, 35), obstaculo, 2)


def altura_dos_pes(sprite: pygame.sprite.Sprite) -> int:
    'Distância do topo do sprite até a sola dos pés (parte visível mais baixa).'
    # O calculo e caro; guardamos o resultado no proprio sprite na primeira vez.
    if not hasattr(sprite, "altura_pes"):
        # Prefere a imagem parada voltada para baixo (south); se nao existir,
        # usa a imagem atual do sprite.
        imagens_parado = getattr(sprite, "imagens_parado", None)
        imagem = imagens_parado["south"] if imagens_parado else sprite.image

        # get_bounding_rect() ignora pixels transparentes e devolve a caixa
        # visivel; o "bottom" dessa caixa e a altura dos pes.
        sprite.altura_pes = imagem.get_bounding_rect().bottom
    return sprite.altura_pes


def posicionar_pelos_pes(sprite: pygame.sprite.Sprite, pes: tuple[int, int]) -> None:
    'Coloca o sprite de modo que a sola dos pés fique no ponto indicado.'
    # O rect e posicionado de forma que o centro horizontal fique em pes[0] e
    # a altura dos pes fique em pes[1].
    sprite.rect.topleft = (
        round(pes[0] - sprite.rect.width / 2),
        round(pes[1] - altura_dos_pes(sprite)),
    )

    # "posicao" e o vetor usado pelos calculos de movimento (pode ter decimais).
    sprite.posicao = pygame.Vector2(sprite.rect.topleft)


def retangulo_colisao(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """Area que bate no terreno.

    No mapa antigo e quase o sprite inteiro. No covil (visao de cima, com chao
    desenhado) e so a sola dos pes: o corpo pode passar na frente de paredes e
    estatuas, como em RPGs vistos de cima, mas os pes nao saem do chao."""
    # Sem mascara de chao (mapa antigo): usa o sprite inteiro com uma pequena
    # margem para nao prender nas quinas.
    if config.CENA["chao"] is None:
        return sprite.rect.inflate(-8, -8)

    # No covil, a caixa tem 45% da largura e 1/7 da altura do sprite.
    caixa = pygame.Rect(
        0,
        0,
        max(8, sprite.rect.width * 45 // 100),
        max(6, sprite.rect.height // 7),
    )

    # Alinha a caixa ao centro horizontal e a base dos pes do sprite.
    caixa.midbottom = (sprite.rect.centerx, sprite.rect.top + altura_dos_pes(sprite))
    return caixa


def retangulo_encontro(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    'Área do corpo que inicia a batalha quando herói e inimigo se encostam.'
    # No mapa antigo, a area de encontro e a mesma da colisao.
    if config.CENA["chao"] is None:
        return retangulo_colisao(sprite)

    # No covil, o corpo e reduzido para o encontro nao acontecer de longe.
    return sprite.rect.inflate(-sprite.rect.width * 2 // 5, -sprite.rect.height // 3)


def colide_com_terreno(rect: pygame.Rect) -> bool:
    """Diz se um retangulo esta fora do mapa, fora do chao ou sobre um bloqueio."""
    # Limites da cena atual (720x480 no mapa antigo; tamanho do covil depois).
    limites_mapa = pygame.Rect((0, 0), config.CENA["tamanho"])

    # Se o retangulo sair da tela, ja e colisao.
    if not limites_mapa.contains(rect):
        return True

    # Mascara de chao: existe apenas no covil.
    chao = config.CENA["chao"]
    if chao is not None:
        # Os pes (base do retangulo) precisam estar sobre o chao: assim ninguem
        # anda sobre o abismo, a agua ou as paredes do covil.
        y = rect.bottom - 1
        if not all(chao.get_at((x, y)) for x in (rect.left, rect.centerx, rect.right - 1)):
            return True

    # Por fim, verifica os retangulos de bloqueio desenhados no mapa.
    return any(rect.colliderect(obstaculo) for obstaculo in config.CENA["bloqueios"])


def mover_com_colisao(sprite: pygame.sprite.Sprite, dx: float, dy: float) -> bool:
    'Move separadamente em X e Y para permitir deslizar pelos obstáculos.'
    # Comeca assumindo que o sprite nao se moveu.
    movimentou = False

    # Eixo X: guarda a posicao antiga, tenta mover e desfaz se colidir.
    if dx:
        x_anterior = sprite.posicao.x
        sprite.posicao.x += dx
        sprite.rect.x = round(sprite.posicao.x)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.x = x_anterior
            sprite.rect.x = round(sprite.posicao.x)
        else:
            movimentou = True

    # Eixo Y: o mesmo processo, independente do X, permitindo deslizar na parede.
    if dy:
        y_anterior = sprite.posicao.y
        sprite.posicao.y += dy
        sprite.rect.y = round(sprite.posicao.y)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.y = y_anterior
            sprite.rect.y = round(sprite.posicao.y)
        else:
            movimentou = True

    # O chamador usa o retorno para saber se deve animar a caminhada.
    return movimentou


def personagem_atras_de_oclusor(sprite: pygame.sprite.Sprite) -> bool:
    """Ponto de extensao: hoje nenhum personagem fica transparente atras de oclusores."""
    # Mantido como funcao para o desenho nao precisar mudar caso essa regra
    # seja implementada no futuro.
    return False


def atualizar_animacao(sprite: pygame.sprite.Sprite, direcao: pygame.Vector2, tempo_frame: float) -> None:
    'Utiliza as animações de caminhada que já existem nos sprites do mapa.'
    # Direcao zero significa parado: volta ao primeiro quadro e a imagem parada.
    if direcao.length_squared() == 0:
        sprite.quadro_animacao = 0
        sprite.tempo_animacao = 0
        sprite.image = sprite.imagens_parado[sprite.direcao_atual]
        return

    # Escolhe a direcao visual comparando o eixo de maior movimento.
    if abs(direcao.x) > abs(direcao.y):
        sprite.direcao_atual = "east" if direcao.x > 0 else "west"
    else:
        sprite.direcao_atual = "south" if direcao.y > 0 else "north"

    # Acumula o tempo passado desde o ultimo quadro.
    sprite.tempo_animacao += tempo_frame

    # Quando o tempo atinge a velocidade da animacao, avanca um quadro.
    if sprite.tempo_animacao >= sprite.velocidade_animacao:
        sprite.tempo_animacao -= sprite.velocidade_animacao
        total = len(sprite.imagens_caminhada[sprite.direcao_atual])
        sprite.quadro_animacao = (sprite.quadro_animacao + 1) % total

    # Aplica a imagem do quadro atual da direcao escolhida.
    sprite.image = sprite.imagens_caminhada[sprite.direcao_atual][sprite.quadro_animacao]


def registrar_posicao(sprite: pygame.sprite.Sprite) -> None:
    'Mantém o caminho que será seguido pelos dois companheiros.'
    # Guarda uma copia da posicao atual no historico.
    sprite.historico_posicoes.append(pygame.Vector2(sprite.posicao))

    # Limita o historico a 100 posicoes para nao crescer indefinidamente.
    if len(sprite.historico_posicoes) > 100:
        sprite.historico_posicoes.pop(0)
