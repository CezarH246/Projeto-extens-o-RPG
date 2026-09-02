# Projeto Extensão RPG

## Como executar

1. Abra o terminal na pasta do projeto.
2. Instale o pygame, se necessário: `pip install pygame`.
3. Inicie o mapa com `python mapa_teste.py`.

## Fluxo do jogo

### Mapa e movimentação

1. `Jogo` cria a janela, carrega `assets/mapa_teste/mapateste.jpeg` e cria os três personagens.
2. `Cezar` recebe as teclas `WASD` e vira o líder do grupo.
3. `mover_com_colisao` tenta mover primeiro no eixo X e depois no eixo Y.
4. Se a nova posição tocar o fundo cinza ou uma parede, a posição anterior é restaurada.
5. Lucas e Guilherme seguem o histórico de posições do Cezar com atraso.
6. As escadas são exceções de colisão e podem ser atravessadas.
7. A sessão inicial não possui inimigos.
8. Ao alcançar o final do caminho, a sessão troca para `Scene Overview.png`, cria os inimigos e passa a permitir batalhas.

### Personagens

- `CezarPersonagem.py`: sprite, direções, caminhada e posição do líder.
- `LucasPersonagem.py`: sprite e seguimento do Cezar.
- `GuilhermePersonagem.py`: sprite e seguimento do Lucas.
- `InimigoPersonagem.py`: sprite, patrulha horizontal/vertical e inversão ao encontrar um bloqueio.

Cada personagem mantém `image`, `rect` e `posicao`. O `rect` participa da colisão; a imagem é apenas a representação visual.

### Regras de combate

1. `Combate.py` cria heróis, inimigos, atributos, HP, PA, ATB, XP e regras de dano.
2. `batalha_ui.py` cria os sprites de batalha e acompanha a barra ATB.
3. Quando um herói fica pronto, o jogador escolhe ataque, habilidade, ultimate, poção ou defesa.
4. A ação chama o método correspondente de `Combate.py`, que valida custo e condição e aplica dano.
5. O dano recebido é guardado em `_ultimo_dano_recebido` para a animação visual.
6. Quando todos os inimigos morrem, XP e drops são aplicados e o inimigo do mapa é removido.

### Ultimate do Cezar

O Cezar pode usar a ultimate desde o início para testes. `batalha_ui.py` carrega os 35 frames em `assets/ultimates/Cezar_Ultimate`, move o sprite até o alvo e reproduz o ataque durante o deslocamento.

### Transparência dos obstáculos

Durante o desenho do mapa, o código verifica se o corpo do herói está sobre pixels de árvore ou pilar. Nessa situação, ele é desenhado com alpha reduzido para indicar que está passando por trás do elemento.
