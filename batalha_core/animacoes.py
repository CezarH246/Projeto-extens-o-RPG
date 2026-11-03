"""Reusable attack, skill, and damage animations."""

import pygame

from .assets import DISTANCIA_NASCIMENTO_BOLA


class FloatingDamage:
    """Animação de número de dano flutuante acima do sprite do inimigo."""
    def __init__(self, x: float, y: float, dano: int, duracao: float = 1.5):
        self.x = x
        self.y = y
        self.dano = dano
        self.tempo_decorrido = 0.0
        self.duracao = duracao
        self.cor_inicial = (255, 100, 100)  # Vermelho
        self.cor_final = (255, 200, 100)    # Laranja
    
    def atualizar(self, tempo_frame: float) -> bool:
        """Retorna False quando a animação termina."""
        self.tempo_decorrido += tempo_frame
        return self.tempo_decorrido < self.duracao
    
    def desenhar(self, tela: pygame.Surface, fonte: pygame.font.Font) -> None:
        """Desenha o número com transparência decrescente."""
        progresso = self.tempo_decorrido / self.duracao
        alpha = 255 * (1 - progresso)  # Desaparece gradualmente
        y_flutuante = self.y - (progresso * 40)  # Sobe 40 pixels
        
        # Interpola entre as cores
        r = int(self.cor_inicial[0] + (self.cor_final[0] - self.cor_inicial[0]) * progresso)
        g = int(self.cor_inicial[1] + (self.cor_final[1] - self.cor_inicial[1]) * progresso)
        b = int(self.cor_inicial[2] + (self.cor_final[2] - self.cor_inicial[2]) * progresso)
        cor = (r, g, b)
        
        texto = fonte.render(f"-{self.dano}", True, cor)
        sombra = fonte.render(f"-{self.dano}", True, (20, 8, 8))
        texto.set_alpha(int(alpha))
        sombra.set_alpha(int(alpha))
        rect = texto.get_rect(center=(int(self.x), int(y_flutuante)))
        # Contorno escuro nos quatro lados, para o número aparecer sobre qualquer cenário.
        for deslocamento in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            tela.blit(sombra, rect.move(deslocamento))
        tela.blit(texto, rect)


class AnimacaoUltimate:
    def __init__(self, frames: list[pygame.Surface], personagem, origem: tuple[int, int], alvo: tuple[int, int], velocidade_animacao: float = 0.08):
        self.frames = frames
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.indice = 0
        self.tempo = 0.0
        self.fim_ataque = 22
        self.velocidade_animacao = velocidade_animacao

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        if self.tempo >= self.velocidade_animacao:
            self.tempo = 0.0
            self.indice += 1
        return self.indice < len(self.frames)

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice <= self.fim_ataque:
            progresso = self.indice / self.fim_ataque
            centro = self.origem.lerp(self.alvo, progresso)
        else:
            centro = self.alvo
        imagem = self.frames[self.indice].copy()
        rect = imagem.get_rect(center=(round(centro.x), round(centro.y)))
        tela.blit(imagem, rect)


class AnimacaoAtaque(AnimacaoUltimate):
    """Mesma lógica da animação de ultimate, mas para o ataque básico."""
    pass


class AnimacaoDash(AnimacaoUltimate):
    """Animação curta de deslocamento do personagem antes do ataque."""
    def __init__(self, frames: list[pygame.Surface], personagem, origem: tuple[int, int], alvo: tuple[int, int], velocidade_animacao: float = 0.04):
        super().__init__(frames, personagem, origem, alvo, velocidade_animacao=velocidade_animacao)
        # O deslocamento ocupa a corrida inteira: o herói chega ao destino no
        # último quadro, sem parar no meio do caminho e dar um salto.
        self.fim_ataque = max(1, len(frames) - 1)

    def atualizar(self, tempo_frame: float) -> bool:
        # Guarda a sobra de tempo entre quadros, para a velocidade não depender do FPS.
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao and self.indice < len(self.frames):
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < len(self.frames)


class AnimacaoHabilidadeMago:
    """Mostra o Mago conjurando e lança a bola de fogo até o alvo."""
    def __init__(self, frames_mago, frames_bola, personagem, origem, alvo):
        self.frames_mago = frames_mago
        self.frames_bola = frames_bola
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.indice = 0
        self.tempo = 0.0
        self.velocidade_animacao = 0.07

    @property
    def duracao_mago(self) -> int:
        return len(self.frames_mago)

    @property
    def personagem_oculto(self) -> bool:
        return self.indice < self.duracao_mago

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < self.duracao_mago + len(self.frames_bola)

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice < self.duracao_mago:
            imagem = self.frames_mago[self.indice]
            centro = self.origem
        else:
            indice_bola = min(self.indice - self.duracao_mago, len(self.frames_bola) - 1)
            imagem = self.frames_bola[indice_bola]
            progresso = indice_bola / max(1, len(self.frames_bola) - 1)
            centro = self.origem.lerp(self.alvo, progresso)

        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoUltimateMago(AnimacaoHabilidadeMago):
    """Mostra a conjuração do Mago e o buraco negro diretamente no alvo."""

    # Frame da conjuração do Mago em que o buraco negro já começa a
    # aparecer sobre o inimigo (ainda enquanto ele conjura).
    frame_inicio_efeito = 38

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        # O efeito termina junto com o buraco negro, a partir do frame de início.
        return self.indice < self.frame_inicio_efeito + len(self.frames_bola)

    def desenhar(self, tela: pygame.Surface) -> None:
        indice_efeito = self.indice - self.frame_inicio_efeito

        if self.indice < self.duracao_mago:
            # Ainda conjurando: o Mago continua, mas o buraco negro já pode
            # estar aparecendo sobre o inimigo em paralelo.
            imagem = self.frames_mago[self.indice]
            centro = self.origem
            if self.frames_bola and indice_efeito >= 0:
                efeito = self.frames_bola[min(indice_efeito, len(self.frames_bola) - 1)]
                tela.blit(efeito, efeito.get_rect(center=(round(self.alvo.x), round(self.alvo.y))))
        else:
            # Conjuração terminou: segue somente o buraco negro no alvo.
            imagem = self.frames_bola[min(indice_efeito, len(self.frames_bola) - 1)]
            centro = self.alvo

        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoUltimateCezar:
    """Ultimate do Cezar: o personagem avança até perto do inimigo enquanto
    toca o gif completo. Sem efeito sobreposto no alvo."""

    def __init__(self, frames, personagem, origem, alvo, velocidade_animacao: float = 0.06):
        self.frames = frames
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.velocidade_animacao = velocidade_animacao
        self.indice = 0
        self.tempo = 0.0

        # O personagem NÃO atravessa o inimigo: ele para alguns pixels antes
        # do alvo (ponto de contato).
        distancia_parada = 55
        vetor = self.alvo - self.origem
        if vetor.length_squared() > 0 and vetor.length() > distancia_parada:
            self.ponto_contato = self.origem + vetor.normalize() * (vetor.length() - distancia_parada)
        else:
            self.ponto_contato = self.origem

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < len(self.frames)

    def desenhar(self, tela: pygame.Surface) -> None:
        progresso = self.indice / max(1, len(self.frames) - 1)
        # O personagem avança até o ponto de contato (perto do inimigo).
        centro = self.origem.lerp(self.ponto_contato, progresso)
        imagem = self.frames[min(self.indice, len(self.frames) - 1)]
        tela.blit(imagem, imagem.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoPersonagemProjetil(AnimacaoHabilidadeMago):
    """Toca o personagem parado enquanto o projétil viaja e explode no alvo."""

    frame_inicio_impacto = 27

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < max(len(self.frames_mago), len(self.frames_bola))

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.indice < len(self.frames_mago):
            personagem = self.frames_mago[self.indice]
            tela.blit(
                personagem,
                personagem.get_rect(center=(round(self.origem.x), round(self.origem.y))),
            )

        if self.indice < len(self.frames_bola):
            projetil = self.frames_bola[self.indice]
            if self.indice >= self.frame_inicio_impacto:
                centro = self.alvo
            else:
                progresso = self.indice / max(1, self.frame_inicio_impacto - 1)
                centro = self.origem.lerp(self.alvo, progresso)
            tela.blit(projetil, projetil.get_rect(center=(round(centro.x), round(centro.y))))


class AnimacaoEspecialSequencial(AnimacaoHabilidadeMago):
    """Especial em sequência (especial do Guilherme), quatro estágios:

    1. O mago toca a animação dele, parado no lugar;
    2. só depois de terminar, a magia se forma na posição dele;
    3. em seguida a bola de fogo viaja da origem até o alvo;
    4. por fim o efeito de impacto aparece centrado dentro do inimigo."""

    def __init__(self, frames_mago, frames_formacao, frames_bola, frames_efeito, personagem, origem, alvo):
        super().__init__(frames_mago, frames_bola, personagem, origem, alvo)
        self.frames_formacao = frames_formacao
        self.frames_efeito = frames_efeito

    @property
    def duracao_formacao(self) -> int:
        return len(self.frames_formacao)

    @property
    def duracao_efeito(self) -> int:
        return len(self.frames_efeito)

    @property
    def duracao_total(self) -> int:
        return (
            self.duracao_mago
            + self.duracao_formacao
            + len(self.frames_bola)
            + self.duracao_efeito
        )

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < self.duracao_total

    def _origem_bola(self) -> pygame.Vector2:
        # A bola nasce um pouco à frente do mago (no sentido do inimigo).
        vetor = self.alvo - self.origem
        if vetor.length_squared() > 0:
            return self.origem + vetor.normalize() * DISTANCIA_NASCIMENTO_BOLA
        return self.origem.copy()

    def desenhar(self, tela: pygame.Surface) -> None:
        indice = self.indice
        if indice < self.duracao_mago:
            # Estágio 1: animação do mago, com ele parado na posição dele.
            imagem = self.frames_mago[min(indice, len(self.frames_mago) - 1)]
            tela.blit(imagem, imagem.get_rect(center=(round(self.origem.x), round(self.origem.y))))
        elif indice < self.duracao_mago + self.duracao_formacao:
            # Estágio 2: a magia se forma na posição do mago.
            indice_formacao = indice - self.duracao_mago
            imagem = self.frames_formacao[min(indice_formacao, self.duracao_formacao - 1)]
            tela.blit(imagem, imagem.get_rect(center=(round(self.origem.x), round(self.origem.y))))
        elif indice < self.duracao_mago + self.duracao_formacao + len(self.frames_bola):
            # Estágio 3: a bola de fogo viaja da origem um pouco à frente até o inimigo.
            indice_bola = indice - self.duracao_mago - self.duracao_formacao
            progresso = indice_bola / max(1, len(self.frames_bola) - 1)
            bola = self.frames_bola[min(indice_bola, len(self.frames_bola) - 1)]
            origem_bola = self._origem_bola()
            centro = origem_bola.lerp(self.alvo, progresso)
            tela.blit(bola, bola.get_rect(center=(round(centro.x), round(centro.y))))
        elif self.frames_efeito:
            # Estágio 4: efeito de impacto dentro do inimigo.
            indice_efeito = min(
                indice - self.duracao_mago - self.duracao_formacao - len(self.frames_bola),
                self.duracao_efeito - 1,
            )
            efeito = self.frames_efeito[indice_efeito]
            tela.blit(efeito, efeito.get_rect(center=(round(self.alvo.x), round(self.alvo.y))))


class AnimacaoUltimateComEfeito:
    """Ultimate do Lucas: mostra o impacto no alvo quando o martelo atinge o chão."""

    frame_impacto_martelo = 38

    def __init__(self, frames, frames_efeito, personagem, origem, alvo, velocidade_animacao: float = 0.06):
        self.frames = frames
        self.frames_efeito = frames_efeito
        self.personagem = personagem
        self.origem = pygame.Vector2(origem)
        self.alvo = pygame.Vector2(alvo)
        self.velocidade_animacao = velocidade_animacao
        self.indice = 0
        self.tempo = 0.0

    def atualizar(self, tempo_frame: float) -> bool:
        self.tempo += tempo_frame
        while self.tempo >= self.velocidade_animacao:
            self.tempo -= self.velocidade_animacao
            self.indice += 1
        return self.indice < max(len(self.frames), self.frame_impacto_martelo + len(self.frames_efeito))

    def desenhar(self, tela: pygame.Surface) -> None:
        if self.frames_efeito and self.indice >= self.frame_impacto_martelo:
            indice_efeito = min(
                self.indice - self.frame_impacto_martelo,
                len(self.frames_efeito) - 1,
            )
            efeito = self.frames_efeito[indice_efeito]
            tela.blit(efeito, efeito.get_rect(center=(round(self.alvo.x), round(self.alvo.y))))
        imagem = self.frames[min(self.indice, len(self.frames) - 1)]
        tela.blit(imagem, imagem.get_rect(center=(round(self.origem.x), round(self.origem.y))))
