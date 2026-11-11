"""Regras de colisao, movimento e animacao usadas pelo mapa.

COMO ENTENDER AS COLISOES SEM MEXER EM SPRITES
    Sprite e a imagem do personagem. Rect e uma caixa invisivel que o Pygame
    usa para posicionar essa imagem; hitbox e outra caixa invisivel, usada
    apenas para decidir se algo encostou. Elas sao retangulos simples: nao e
    preciso desenhar ou recortar a imagem pixel por pixel.

    Este modulo tem duas hitboxes com finalidades diferentes:
    - retangulo_colisao(): impede atravessar paredes, sair do mapa ou pisar fora
      do chao permitido;
    - retangulo_encontro(): detecta quando heroi e inimigo se encostam para
      iniciar uma batalha.

    As medidas dessas caixas usam as coordenadas logicas do mapa em pixels
      (x, y, largura, altura), nao exigem conhecimento de arte. No covil, a
    colisao acompanha os pes para dar a impressao de que o personagem anda
    atras ou na frente de objetos. No mapa antigo, ela ocupa quase todo o
    personagem.

    Os bloqueios e areas de chao podem ser ajustados no editor de colisao (F3).
    Seus dados ficam nos arquivos JSON carregados por colisoes_mapas.py; este
    modulo transforma esses dados em regras que o movimento usa.

Separar estas funcoes deixa mapa_jogo.py menor e permite que o jogo e o editor
compartilhem a mesma verificacao de colisao.
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
    """Distancia do topo da imagem ate o ponto mais baixo que nao e transparente.

    Isso ajuda a alinhar a hitbox aos pes mesmo que a imagem tenha espaco
    transparente ao redor. Nao precisamos contar pixels manualmente: o Pygame
    encontra automaticamente o retangulo da parte visivel da imagem.
    """
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
    """Posiciona o personagem usando os pes como referencia.

    ``pes`` e o ponto do mapa (x, y) onde a sola deve ficar. Assim, imagens de
    tamanhos diferentes podem ficar apoiadas no mesmo ponto do chao.
    """
    # O rect e posicionado de forma que o centro horizontal fique em pes[0] e
    # a altura dos pes fique em pes[1].
    sprite.rect.topleft = (
        round(pes[0] - sprite.rect.width / 2),
        round(pes[1] - altura_dos_pes(sprite)),
    )

    # "posicao" e o vetor usado pelos calculos de movimento (pode ter decimais).
    sprite.posicao = pygame.Vector2(sprite.rect.topleft)


def retangulo_colisao(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """Devolve a hitbox usada para impedir o personagem de atravessar o terreno.

    Pense nela como uma caixa invisivel em volta da parte do personagem que
    precisa respeitar paredes e bordas. Ela nao precisa acompanhar o contorno
    da arte: e um retangulo simples, calculado a partir do ``rect`` do sprite.
    """
    # Mapa antigo: usa quase toda a caixa do sprite. O -8 reduz a largura e a
    # altura totais em 8 pixels (4 de cada lado), para nao prender facilmente
    # em quinas. Esta margem e uma regra geral, nao algo medido na arte.
    if config.CENA["chao"] is None:
        return sprite.rect.inflate(-8, -8)

    # Covil: usa uma caixa pequena junto aos pes. Os percentuais sao uma
    # proporcao do tamanho atual do sprite, entao a regra continua funcionando
    # se o personagem for desenhado maior ou menor. Os valores minimos evitam
    # uma caixa de largura/altura zero em sprites muito pequenos.
    caixa = pygame.Rect(
        0,
        0,
        max(8, sprite.rect.width * 45 // 100),
        max(6, sprite.rect.height // 7),
    )

    # Centraliza a caixa sob o personagem e coloca a base dela na altura dos
    # pes. Assim, e a posicao dos pes - e nao a cabeca ou o corpo da imagem -
    # que determina se o personagem encosta no chao ou num obstaculo.
    caixa.midbottom = (sprite.rect.centerx, sprite.rect.top + altura_dos_pes(sprite))
    return caixa


def retangulo_encontro(sprite: pygame.sprite.Sprite) -> pygame.Rect:
    """Devolve a hitbox usada somente para detectar encontro com um inimigo.

    Esta caixa nao bloqueia o movimento. Ela responde a outra pergunta:
    "as areas do heroi e do inimigo se sobrepoem?". Quando sim, mapa_jogo.py
    pode iniciar a batalha.
    """
    # Mapa antigo: reaproveita a caixa de colisao para que os encontros
    # correspondam ao contato usado nessa cena.
    if config.CENA["chao"] is None:
        return retangulo_colisao(sprite)

    # Covil: usa uma versao menor do retangulo do sprite. Isso evita comecar uma
    # batalha quando as imagens parecem proximas, mas os personagens ainda
    # estao separados. inflate com valores negativos diminui a caixa.
    return sprite.rect.inflate(-sprite.rect.width * 2 // 5, -sprite.rect.height // 3)


def colide_com_terreno(rect: pygame.Rect) -> bool:
    """Responde se a hitbox toca uma area onde nao e permitido andar.

    A ordem das verificacoes e: dentro dos limites da tela, sobre o chao
    permitido (quando existe mascara) e sem sobrepor os retangulos bloqueados.
    """
    # Retangulo que representa o tamanho jogavel da cena atual. As coordenadas
    # do jogo comecam no canto superior esquerdo: (0, 0).
    limites_mapa = pygame.Rect((0, 0), config.CENA["tamanho"])

    # Se qualquer parte da hitbox passar do limite, o movimento e proibido.
    if not limites_mapa.contains(rect):
        return True

    # A mascara e um desenho preto/branco invisivel que indica onde existe chao.
    # None significa que esta cena nao usa uma mascara para limitar o caminho.
    chao = config.CENA["chao"]
    if chao is not None:
        # Testamos tres pontos na base da hitbox: esquerda, centro e direita.
        # Se algum deles estiver fora da mascara branca de chao, bloqueamos o
        # passo. Sao apenas tres consultas por movimento, nao uma analise da
        # imagem do personagem pixel por pixel.
        y = rect.bottom - 1
        if not all(chao.get_at((x, y)) for x in (rect.left, rect.centerx, rect.right - 1)):
            return True

    # Bloqueios sao retangulos invisiveis colocados sobre objetos solidos. O
    # metodo colliderect() diz se a hitbox do personagem se sobrepoe a algum.
    return any(rect.colliderect(obstaculo) for obstaculo in config.CENA["bloqueios"])


def mover_com_colisao(sprite: pygame.sprite.Sprite, dx: float, dy: float) -> bool:
    """Tenta mover o sprite e desfaz apenas os passos que causarem colisao.

    ``dx`` e ``dy`` sao quanto queremos andar horizontal e verticalmente neste
    quadro. Cada valor pode ser decimal; ``posicao`` guarda essa precisao e
    ``rect`` usa coordenadas inteiras para desenhar e testar as hitboxes.

    Os eixos sao testados separadamente. Se o personagem bater numa parede ao
    andar para frente, ainda pode mover-se de lado junto a ela (deslizar), em
    vez de ter todo o movimento diagonal cancelado.
    """
    # O retorno informa ao loop do mapa se pelo menos um eixo conseguiu mover.
    movimentou = False

    # Eixo X (horizontal): guarda a posicao segura, tenta o passo e atualiza o
    # retangulo usado pelas hitboxes. Se houver colisao, volta a posicao salva.
    if dx:
        x_anterior = sprite.posicao.x
        sprite.posicao.x += dx
        sprite.rect.x = round(sprite.posicao.x)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.x = x_anterior
            sprite.rect.x = round(sprite.posicao.x)
        else:
            movimentou = True

    # Eixo Y (vertical): repete o teste usando a posicao horizontal que ficou
    # apos o primeiro passo. Separar X e Y permite contornar quinas e deslizar.
    if dy:
        y_anterior = sprite.posicao.y
        sprite.posicao.y += dy
        sprite.rect.y = round(sprite.posicao.y)
        if colide_com_terreno(retangulo_colisao(sprite)):
            sprite.posicao.y = y_anterior
            sprite.rect.y = round(sprite.posicao.y)
        else:
            movimentou = True

    # mapa_jogo.py usa este resultado para registrar o caminho e escolher
    # animacao de caminhada ou parado.
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
