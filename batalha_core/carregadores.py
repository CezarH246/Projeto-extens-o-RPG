"""Load assets and create arena sprites."""

from pathlib import Path

import pygame

from .assets import *
from .animacoes import *
from .helpers import *
from .sprites import SpriteCombatente
from .temas import tema_atual

class CarregadoresBattleUI:
    """Interface methods dedicated to loading visual resources."""

    def restaurar_posicao_inicial_heroi(self, heroi):
        sprite_heroi = next((s for s in self.sprites_herois if s.personagem is heroi), None)
        if sprite_heroi is not None:
            sprite_heroi.centro = sprite_heroi.centro_inicial

    def carregar_fundo(self) -> pygame.Surface:
        try:
            imagem = pygame.image.load(FUNDO_BATALHA).convert()
            return pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))
        except (FileNotFoundError, pygame.error):
            fundo = pygame.Surface((LARGURA, ALTURA))
            fundo.fill((39, 73, 90))
            return fundo

    def carregar_animacao_dash(self, personagem) -> list[pygame.Surface]:
        caminho = DASHES.get(personagem.nome)
        if caminho is None:
            return []

        tamanho = tamanho_corpo(personagem)
        if caminho.is_file() and caminho.suffix.lower() == ".gif":
            frames = self.carregar_frames_gif(
                caminho,
                tamanho,
                ajustar_ao_conteudo=True,
            )
            return frames[::3] if personagem.nome == "Lucas" else frames
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_animacao_ataque(self, personagem) -> list[pygame.Surface]:
        caminho = ATAQUES_BASICOS.get(personagem.nome)
        if caminho is None:
            return []

        if personagem.nome == "Guilherme":
            return self.carregar_frames_gif(
                ATAQUE_BASICO_GUILHERME_GIF,
                tamanho_corpo(personagem, TAMANHO_ATAQUE),
                ajustar_ao_conteudo=True,
                limitar_ao_tamanho=True,
            )

        tamanho = tamanho_corpo(personagem, TAMANHO_ATAQUE)
        return self.carregar_animacao_arquivo(caminho, tamanho)

    def carregar_animacao_projetil_ataque_guilherme(
        self,
        personagem,
    ) -> list[pygame.Surface]:
        tamanho_base = tamanho_corpo(personagem, TAMANHO_ATAQUE)
        tamanho_projetil = tuple(round(dimensao * 1.25) for dimensao in tamanho_base)
        return self.carregar_frames_gif(
            EFEITO_ATAQUE_BASICO_GUILHERME,
            tamanho_projetil,
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )

    def carregar_animacao_ataque_inimigo(self, personagem) -> list[pygame.Surface]:
        caminho = ATAQUES_INIMIGOS.get(normalizar_nome(personagem.nome.split(" Lv.")[0]))
        if caminho is None:
            return []

        # O efeito de ataque acompanha o tamanho do combatente, mas com um teto:
        # um boss muito grande não deve gerar um golpe cobrindo a tela inteira.
        escala_ataque = min(1.35, float(getattr(personagem, "escala", 1.0)))
        tamanho = (int(250 * escala_ataque), int(250 * escala_ataque))
        return self.carregar_frames_pasta(caminho, tamanho, ajustar_ao_conteudo=False)

    def carregar_animacao_ultimate(self, personagem) -> list[pygame.Surface]:
        caminho = ULTIMATES.get(personagem.nome)
        if caminho is None:
            return []

        tamanho = tamanho_corpo(personagem, TAMANHO_ULTIMATE)
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_frames_gif(
        self,
        caminho: Path,
        tamanho: tuple[int, int],
        ajustar_ao_conteudo: bool = False,
        limitar_ao_tamanho: bool = False,
    ) -> list[pygame.Surface]:
        try:
            quadros = carregar_quadros_gif(caminho)
        except (OSError, ValueError, pygame.error):
            return []
        if ajustar_ao_conteudo:
            return ajustar_quadros_ao_conteudo(quadros, tamanho, limitar_ao_tamanho)
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    def carregar_animacao_arquivo(self, caminho: Path, tamanho: tuple[int, int]) -> list[pygame.Surface]:
        """Carrega uma animação que pode ser uma pasta de frames PNG ou um gif."""
        if caminho.is_file() and caminho.suffix.lower() == ".gif":
            return self.carregar_frames_gif(caminho, tamanho, ajustar_ao_conteudo=True)
        return self.carregar_frames_pasta(caminho, tamanho)

    def carregar_animacao_habilidade_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        frames_mago = self.carregar_frames_gif(
            ANIMACAO_MAGO_HABILIDADE,
            tamanho_corpo(personagem),
            ajustar_ao_conteudo=True,
        )
        frames_bola = self.carregar_frames_gif(BOLA_FOGO_MAGO, (96, 96))
        return frames_mago, frames_bola

    def carregar_animacao_habilidade_especial(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        """Habilidade especial (tecla 2): conjuração + projétil de cada herói.

        O Cezar conjura a magia (Cezar_Magia) e o projétil sai dela
        (Cezar_Projetil). Para os demais, usa a conjuração do Mago."""
        caminho = HABILIDADES_ESPECIAIS.get(personagem.nome)
        if caminho is None:
            return self.carregar_animacao_habilidade_mago(personagem)

        pasta_conjuracao, gif_projetil = caminho
        frames_conjuracao = self.carregar_frames_pasta(pasta_conjuracao, tamanho_corpo(personagem))
        frames_projetil = self.carregar_frames_gif(
            gif_projetil,
            tamanho_com_escala((TAMANHO_PROJETIL, TAMANHO_PROJETIL), personagem),
        )
        return frames_conjuracao, frames_projetil

    def carregar_animacao_segunda_habilidade(self, personagem) -> list[pygame.Surface]:
        """Segunda habilidade (tecla 3): animação própria do personagem."""
        caminho = SEGUNDAS_HABILIDADES.get(personagem.nome)
        if caminho is None:
            return []
        return self.carregar_animacao_arquivo(caminho, tamanho_corpo(personagem, TAMANHO_ATAQUE))

    def carregar_animacao_ultimate_mago(self, personagem) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        tamanho_mago = tamanho_corpo(personagem, TAMANHO_ULTIMATE)
        frames_mago = self.carregar_frames_pasta(ULTIMATE_GUILHERME, tamanho_mago)
        frames_buraco_negro = self.carregar_frames_pasta(ULTIMATE_GUILHERME_ATAQUE, (300, 300), ajustar_ao_conteudo=False)
        return frames_mago, frames_buraco_negro

    def carregar_animacao_ultimate_cezar(self, personagem) -> list[pygame.Surface]:
        """Carrega a ultimate do Cezar com o personagem maior e o efeito menor.

        O gif mistura os dois no mesmo quadro: os frames do personagem são
        recortados na silhueta e ampliados, enquanto os frames do flash de
        efeito (conteúdo ocupando quase todo o quadro de 400x400) são
        renderizados menores."""
        tamanho_personagem = TAMANHO_ULTIMATE_CEZAR
        tamanho_efeito = TAMANHO_ULTIMATE_CEZAR_EFEITO
        largura_personagem, altura_personagem = tamanho_personagem
        frames = []
        try:
            with Image.open(ULTIMATE_CEZAR_GIF) as gif:
                for indice in range(getattr(gif, "n_frames", 1)):
                    gif.seek(indice)
                    quadro = gif.convert("RGBA")
                    bbox = quadro.getbbox()
                    if bbox is None:
                        continue
                    largura = bbox[2] - bbox[0]
                    altura = bbox[3] - bbox[1]
                    # Frame do flash de efeito: mantém o quadro inteiro menor.
                    if largura > 300 or altura > 300:
                        dados = quadro.tobytes()
                        imagem = pygame.image.frombytes(dados, quadro.size, "RGBA").convert_alpha()
                        frames.append(pygame.transform.smoothscale(imagem, tamanho_efeito))
                        continue
                    # Frame do personagem: corta o fundo ocioso e amplia.
                    recorte = quadro.crop(bbox)
                    dados = recorte.tobytes()
                    imagem = pygame.image.frombytes(dados, recorte.size, "RGBA").convert_alpha()
                    escala = min(
                        largura_personagem / max(1, largura),
                        altura_personagem / max(1, altura),
                    )
                    escalado = pygame.transform.smoothscale(
                        imagem,
                        (max(1, round(largura * escala)), max(1, round(altura * escala))),
                    )
                    quadro_final = pygame.Surface(tamanho_personagem, pygame.SRCALPHA)
                    quadro_final.blit(
                        escalado,
                        escalado.get_rect(center=(largura_personagem // 2, altura_personagem // 2)),
                    )
                    frames.append(quadro_final)
        except (OSError, ValueError, pygame.error):
            return []
        return frames

    def carregar_animacao_efeito_cezar(self) -> list[pygame.Surface]:
        """Concatena inicio/meio/meio2/fim.gif do efeito que aparece no inimigo."""
        frames = []
        for caminho in EFEITO_CEZAR:
            frames.extend(self.carregar_frames_gif(caminho, (300, 300)))
        return frames

    def carregar_animacao_especial_lucas(
        self,
        personagem,
        tamanho_alvo: tuple[int, int],
    ) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
        """Carrega o rugido do Lucas e o efeito de projétil em escalas distintas."""
        frames_rugido = self.carregar_frames_gif(
            ESPECIAL_LUCAS,
            tamanho_com_escala(TAMANHO_ANIMACAO_PERSONAGEM, personagem),
            ajustar_ao_conteudo=False,
        )
        frames_projetil = self.carregar_frames_gif(
            EFEITO_ESPECIAL_LUCAS,
            tamanho_efeito_com_escala_alvo(
                TAMANHO_ULTIMATE_CEZAR_EFEITO,
                tamanho_alvo,
            ),
            ajustar_ao_conteudo=False,
        )
        return frames_rugido, frames_projetil

    def carregar_animacao_ultimate_lucas(self, personagem, tamanho_alvo: tuple[int, int]) -> tuple[list, list]:
        """Ultimate do Lucas: mesma animação do especial, mas sem projétil.
        O efeito aparece no inimigo desde o começo da animação, no tamanho
        do próprio inimigo (padrão dos efeitos)."""
        frames_ultimate = self.carregar_frames_gif(
            ULTIMATE_LUCAS,
            tamanho_com_escala(TAMANHO_ANIMACAO_PERSONAGEM, personagem),
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )
        frames_efeito = self.carregar_frames_gif(
            EFEITO_ULTIMATE_LUCAS,
            tamanho_efeito_com_escala_alvo(
                TAMANHO_ULTIMATE_CEZAR_EFEITO,
                tamanho_alvo,
            ),
            ajustar_ao_conteudo=False,
        )
        return frames_ultimate, frames_efeito

    def carregar_animacao_especial_guilherme(self, personagem, tamanho_alvo: tuple[int, int]) -> tuple[list, list, list, list]:
        """Especial do Guilherme em quatro estágios: mago, formação, projétil
        e impacto. Os efeitos ficam limitados ao tamanho do inimigo alvo."""
        frames_personagem = self.carregar_frames_gif(
            ANIMACAO_GUILHERME_ESPECIAL,
            tamanho_corpo(personagem),
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )
        frames_formacao = self.carregar_frames_gif(
            MAGIA_GUILHERME,
            tamanho_alvo,
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )
        frames_bola = self.carregar_frames_gif(
            BOLA_GUILHERME,
            (
                max(1, round(tamanho_alvo[0] * PROPORCAO_BOLA_FOGO)),
                max(1, round(tamanho_alvo[1] * PROPORCAO_BOLA_FOGO)),
            ),
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )
        frames_efeito = self.carregar_frames_gif(
            EFEITO_GUILHERME,
            tamanho_alvo,
            ajustar_ao_conteudo=True,
            limitar_ao_tamanho=True,
        )
        return frames_personagem, frames_formacao, frames_bola, frames_efeito

    def carregar_frames_pasta(
        self,
        caminho: Path,
        tamanho: tuple[int, int],
        ajustar_ao_conteudo: bool = True,
        limitar_ao_tamanho: bool = False,
    ) -> list[pygame.Surface]:
        """Carrega `frame_*.png` de uma pasta, no tamanho pedido.

        Por padrão o desenho visível é que ocupa a caixa `tamanho`; efeitos que
        devem manter o enquadramento original passam `ajustar_ao_conteudo=False`.
        """
        quadros = []
        for arquivo in sorted(caminho.glob("frame_*.png")):
            try:
                quadros.append(pygame.image.load(arquivo).convert_alpha())
            except pygame.error:
                continue
        if ajustar_ao_conteudo:
            return ajustar_quadros_ao_conteudo(
                quadros,
                tamanho,
                limitar_ao_tamanho=limitar_ao_tamanho,
            )
        return [pygame.transform.smoothscale(quadro, tamanho) for quadro in quadros]

    def posicoes_da_formacao(self) -> tuple[list, list]:
        """Posições de heróis e inimigos para o tema atual."""
        if tema_atual() == "moderno":
            por_nome, reserva = POSICOES_HEROIS_MODERNO, POSICOES_HEROIS_MODERNO_RESERVA
            inimigos, boss = POSICOES_INIMIGOS_MODERNO, POSICAO_BOSS_MODERNO
        else:
            por_nome, reserva = POSICOES_HEROIS, POSICOES_HEROIS_RESERVA
            inimigos, boss = POSICOES_INIMIGOS, POSICAO_BOSS_CENTRAL
        if self.pasta_fundo_animado == FUNDO_BATALHA_GUARDAS:
            por_nome, reserva, inimigos = FORMACAO_GUARDAS[tema_atual()]
        elif self.pasta_fundo_animado == FUNDO_BATALHA_REI_TRITAO:
            por_nome, reserva, boss = FORMACAO_REI_NA_ARENA[tema_atual()]
        # A posição depende do papel do herói (tanque na frente), não da ordem da lista.
        posicoes_herois = [
            por_nome.get(heroi.nome, reserva[indice]) for indice, heroi in enumerate(self.herois[:3])
        ]
        # O Rei Tritão luta sozinho: ele ocupa o lugar de destaque do lado inimigo.
        posicoes_inimigos = [
            boss if eh_rei_tritao(inimigo) else inimigos[indice] for indice, inimigo in enumerate(self.inimigos[:3])
        ]
        return posicoes_herois, posicoes_inimigos

    def aplicar_formacao(self) -> None:
        """Reposiciona os sprites quando o tema muda no meio da batalha."""
        posicoes_herois, posicoes_inimigos = self.posicoes_da_formacao()
        for sprite, posicao in zip(self.sprites_herois, posicoes_herois):
            sprite.centro = sprite.centro_inicial = posicao
        for sprite, posicao in zip(self.sprites_inimigos, posicoes_inimigos):
            sprite.centro = sprite.centro_inicial = posicao
        for entidade in self.entidades_atras:
            dono = next(s for s in self.sprites_herois if s.personagem is entidade.personagem)
            deslocamento = entidade.deslocamento
            entidade.centro = entidade.centro_inicial = (
                dono.centro[0] + deslocamento[0], dono.centro[1] + deslocamento[1],
            )

    def criar_sprites(self) -> None:
        posicoes_herois, posicoes_inimigos = self.posicoes_da_formacao()

        for indice, heroi in enumerate(self.herois[:3]):
            caminho, caminho_ultimate = ANIMACOES_HEROIS.get(heroi.nome, (None, None))
            tamanho = tamanho_corpo(heroi)
            sprite = SpriteCombatente(heroi, posicoes_herois[indice], caminho, tamanho, caminho_ultimate)
            self.sprites_herois.append(sprite)

            # Efeito que fica atrás do herói (entidade cósmica do Guilherme,
            # serpente do Cezar e Rei Antigo Caído do Lucas) enquanto a
            # Ultimate dele estiver pronta. O tamanho é o base da constante,
            # SEM multiplicar pela escala do herói: assim a entidade do Lucas
            # fica exatamente no mesmo tamanho da serpente do Cezar.
            entidade = ENTIDADES_ATRAS.get(heroi.nome) if ENTIDADES_ATRAS_ATIVAS else None
            if entidade is not None:
                caminho_entidade, tamanho_entidade, deslocamento = entidade
                sprite_entidade = SpriteCombatente(
                    heroi,
                    (posicoes_herois[indice][0] + deslocamento[0], posicoes_herois[indice][1] + deslocamento[1]),
                    caminho_entidade,
                    (tamanho_entidade, tamanho_entidade),
                )
                sprite_entidade.deslocamento = deslocamento
                self.entidades_atras.append(sprite_entidade)

        for indice, inimigo in enumerate(self.inimigos[:3]):
            caminho = resolver_sprite_inimigo(inimigo)
            tamanho = tamanho_corpo(inimigo)
            self.sprites_inimigos.append(SpriteCombatente(inimigo, posicoes_inimigos[indice], caminho, tamanho))
