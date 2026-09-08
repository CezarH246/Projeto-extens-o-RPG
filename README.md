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
# Documentação do Arquivo `batalha_ui.py`

O módulo `batalha_ui.py` é responsável por toda a interface gráfica e visual do sistema de combate do jogo, utilizando a biblioteca **Pygame**. Ele conecta as regras lógicas de batalha (vindas de `Combate.py`) com a renderização de sprites, barras de status, animações de habilidades e gerenciamento de turnos via sistema **ATB (Active Time Battle)**.

---

## 1. Importações e Configurações Gerais

* **`from __future__ import annotations`**: Permite o uso de anotações de tipos modernas sem falhas de importação circular.
* **`import random`, `import unicodedata`, `from pathlib import Path`**: Bibliotecas nativas do Python para sorteio de alvos, tratamento/normalização de nomes de arquivos e manipulação de caminhos do sistema.
* **`import pygame`**: Biblioteca principal de renderização de telas, gerenciamento de eventos e manipulação de imagens.
* **`import Combate as regras`**: Importa o motor de regras do jogo (dano, experiência, poções, pontos de ação e barra ATB).
* **`from PIL import Image`**: Utilizada para extração e conversão quadro a quadro de arquivos `.gif` animados.

### Constantes de Tela e Caminhos (`ASSETS`)
* **`LARGURA` (1280) e `ALTURA` (720)**: Dimensões fixas da resolução da tela do jogo.
* **`FPS` (60)**: Taxa de quadros por segundo alvo da interface.
* **`PROJECT_DIR` e `ASSETS`**: Mapeamento do diretório base do projeto e da pasta contendo imagens, origens de animações e fundos.
* **Dicionários de Assets (`ATAQUES_INIMIGOS`, `ATAQUES_BASICOS`, `DASHES`, `ULTIMATES`, `SPRITES_HEROIS`, `SPRITES_INIMIGOS`)**: Mapeiam os identificadores dos personagens e inimigos às suas respetivas pastas de quadros para animações.
* **`LOG_BATALHA`**: Lista global que armazena os últimos eventos ocorridos na batalha para exibição em tela.

---

## 2. Funções Utilitárias Globais

* **`cor_barra_hp(valor, maximo)`**: Recebe a vida atual e a vida máxima de um personagem e retorna uma cor em formato RGB conforme a porcentagem:
  * **Verde** `(75, 221, 115)` para HP acima de 60%.
  * **Amarelo** `(245, 166, 35)` para HP entre 30% e 60%.
  * **Vermelho** `(220, 65, 65)` para HP abaixo de 30%.

* **`registrar_evento(*args, sep=" ", **_kwargs)`**: Redireciona a função `print` padrão do módulo de regras para a lista `LOG_BATALHA`, mantendo apenas os 6 eventos mais recentes na tela.

* **`normalizar_nome(texto)`**: Converte strings com acentos e caracteres especiais para um formato limpo em caixa baixa separado por *underscores* (ex: "Trîtã das Névoas" vira `trita_das_nevoas`), garantindo compatibilidade no carregamento de arquivos.

* **`resolver_sprite_inimigo(inimigo)`**: Localiza a pasta de imagens correspondente ao tipo ou nome do inimigo carregado no combate.

* **`tamanho_com_escala(tamanho_base, personagem)`**: Aplica o multiplicador individual do personagem (`escala`) ao tamanho do sprite, retornando as novas dimensões em pixels.

* **`criar_batalha(tela, herois, quantidade_inimigos)`**: Função utilitária que consulta o maior nível do grupo de heróis, gera uma lista equilibrada de inimigos através do módulo `Combate` e instancia a interface visual da batalha.

* **`iniciar_janela_batalha()`**: Função de teste isolado que abre a janela de batalha diretamente, sem a necessidade de rodar o mapa principal do jogo.

---

## 3. Classes de Animações Visuais

### `FloatingDamage`
Responsável pelo efeito do número de dano flutuando sobre a cabeça do alvo atacado.
* **`__init__(x, y, dano, duracao)`**: Inicializa a posição do texto, o valor do dano e o tempo total de exibição (padrão de 1.5s).
* **`atualizar(tempo_frame)`**: Incrementa o tempo decorrido e retorna `False` quando a animação se encerra.
* **`desenhar(tela, fonte)`**: Renderiza o texto subindo gradualmente na tela, alterando a cor de vermelho para laranja e aplicando efeito de desbotamento (*fade-out* via transparência/alpha).

### `AnimacaoUltimate`
Gerencia animações visuais de habilidades supremas que envolvem deslocamento ou transição de imagens.
* **`__init__(frames, personagem, origem, alvo, velocidade_animacao)`**: Configura os quadros da animação, os pontos inicial e final no espaço 2D e o tempo por quadro.
* **`atualizar(tempo_frame)`**: Avança os quadros da animação.
* **`desenhar(tela)`**: Renderiza os quadros do sprite enquanto realiza a interpolação linear de movimento (`lerp`) entre a posição de origem e o alvo.

### `AnimacaoAtaque` e `AnimacaoDash`
Herdam as propriedades de `AnimacaoUltimate`. A classe `AnimacaoDash` aplica uma velocidade de movimentação significativamente mais rápida para simular a investida do personagem.

### `AnimacaoHabilidadeMago`
Trata animações compostas do personagem Mago (combina a conjuração e o lançamento do projétil).
* **`__init__(frames_mago, frames_bola, personagem, origem, alvo)`**: Carrega separadamente a animação do conjurador e a animação do projétil.
* **`atualizar(tempo_frame)`**: Controla a transição do estado de cast para o estado de voo do feitiço.
* **`desenhar(tela)`**: Exibe primeiramente o Mago executando a simpatia no local de origem e, em seguida, desenha a bola de fogo deslocando-se em direção ao inimigo.

### `AnimacaoUltimateMago`
Herda de `AnimacaoHabilidadeMago`. Renderiza a conjuração no ponto de origem e projeta o efeito visual (buraco negro) fixado diretamente sobre o alvo, sem projétil intermediário.

---

## 4. Classes da Interface de Combate

### `SpriteCombatente`
Abstração visual de um herói ou inimigo presente na arena.
* **`__init__(personagem, centro, caminho, tamanho)`**: Associa o objeto de regras do combate ao seu componente visual, tamanho e coordenadas na tela.
* **`carregar(caminho)`**: Lê os arquivos `.png` da pasta do personagem (até 16 quadros) para formar a animação de repouso (*idle*). Caso o arquivo não exista, gera uma caixa preenchida temporária (*placeholder*).
* **`atualizar()`**: Alterna o quadro da animação de repouso a cada 100 milissegundos.
* **`adicionar_dano_flutuante(dano)`**: Cria uma instância da classe `FloatingDamage` acima do sprite.
* **`desenhar_barra_hp(tela)`**: Desenha as barras flutuantes de HP (com cor dinâmica), a barra azul de ATB e o nome do inimigo acima do seu sprite.
* **`desenhar(tela, selecionado, fonte_dano)`**: Desenha o sprite na tela (com opacidade reduzida se estiver morto) e adiciona um contorno amarelo destacado se estiver selecionado como alvo.

---

### `BattleUI` (Gerenciador Principal do Combate)
A classe que controla todo o ciclo de vida da tela de batalha.

#### Inicialização e Carregamento
* **`__init__(tela, herois, inimigos)`**: Prepara as fontes do Pygame, carrega a imagem de fundo, posiciona os combatentes e redireciona os logs de texto.
* **`carregar_fundo()` / `carregar_frames_*()` / `carregar_frames_gif()`**: Métodos auxiliares para ler imagens do disco, redimensionar texturas e converter arquivos GIF em superfícies nativas do Pygame.
* **`criar_sprites()`**: Define as posições padrão dos heróis à esquerda `[(220, 280), (170, 455), (390, 430)]` e dos inimigos à direita `[(1060, 270), (970, 445), (835, 360)]`.

#### Lógica de Turno e Atualização
* **`herois_vivos()` / `inimigos_vivos()`**: Filtra e retorna apenas as entidades com HP acima de 0.
* **`verificar_resultado()`**: Avalia o fim da batalha. Se todos os inimigos morrerem, aplica as recompensas (XP e poções); se os heróis morrerem, determina a derrota.
* **`atualizar(tempo_frame)`**: Executa em cada quadro do jogo:
  * Atualiza os números de dano flutuante e as animações em curso (dashes, ataques, magias).
  * incrementa as barras de ATB de todos os personagens com base no tempo decorrido.
  * Define o próximo herói apto a agir ou sorteia uma ação para a inteligência artificial dos inimigos.

#### Processamento de Comandos do Jogador
* **`escolher_acao(numero)`**: Mapeia a tecla numérica (1 a 6) para a intenção de ação do herói ativo:
  * **1**: Ataque básico
  * **2**: Habilidade especial
  * **3**: Segunda habilidade
  * **4**: Ultimate
  * **5**: Usar poção
  * **6**: Defender (+5 DEF)
* **`executar_acao(acao)`**: Executa o comando escolhido sobre o alvo selecionado, calcula os efeitos lógicos em `Combate.py`, agenda o dano flutuante e engatilha as sequências de animações visuais.
* **`processar_evento(evento)`**: Captura os comandos do teclado:
  * **Setas (Esquerda/Direita)** ou **A/D**: Alterna a seleção entre os inimigos vivos.
  * **ENTER**: Confirma a ação no alvo selecionado ou fecha a tela ao término da luta.
  * **ESC**: Cancela a seleção do alvo atual.

#### Renderização Visual
* **`desenhar_barra(...)`**: Desenha componentes visuais de barras retangulares estilizadas para a interface (HP, PA, ATB).
* **`desenhar_painel_herois()`**: Renderiza o painel inferior esquerdo contendo os nomes, níveis e barras de status do grupo.
* **`desenhar_painel_acoes()`**: Renderiza o painel inferior direito mostrando o menu com as opções de comando (1 a 6) e mensagens de ajuda.
* **`desenhar()`**: Método principal de desenho do frame. Limpa a tela, aplica o fundo com escurecimento, renderiza o título, ordena e desenha os sprites, reproduz as animações ativas, exibe o log do combate, constrói os painéis e apresenta a overlay final de Vitória ou Derrota.
