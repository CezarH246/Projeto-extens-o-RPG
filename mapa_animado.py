"""Mapa animado: toca em loop os quadros convertidos de um vídeo.

Os quadros ficam em uma pasta (quadro_000.jpg, quadro_001.jpg, ...) junto de
um info.json com o FPS. Eles são guardados ainda comprimidos (108 quadros de
1280x720 abertos ocupariam ~400 MB de RAM; comprimidos, ~31 MB) e decodificados
numa thread separada, sempre um pouco à frente do quadro mostrado: assim o jogo
não engasga quando o mapa troca de quadro.

O mapa do Rei Tritão usa frame_001.jpg, frame_002.jpg, ... e não tem info.json;
nesse caso o FPS padrão é 12 e o tamanho vem do próprio primeiro quadro.
"""

from __future__ import annotations

import io
import json
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import pygame
from PIL import Image

QUADROS_ADIANTADOS = 2


class MapaAnimado:
    def __init__(self, pasta: Path, tamanho: tuple[int, int] | None = None):
        # Aceita os dois nomes usados no projeto: quadro_000.jpg (mapas antigos)
        # ou frame_001.jpg (mapa novo do Rei Tritão).
        arquivos = sorted(pasta.glob("quadro_*.jpg")) or sorted(pasta.glob("frame_*.jpg"))
        self._dados = [arquivo.read_bytes() for arquivo in arquivos]
        if not self._dados:
            raise FileNotFoundError(f"Nenhum quadro encontrado em {pasta}")

        # O info.json é opcional: sem ele, usa 12 FPS e o tamanho do primeiro quadro.
        arquivo_info = pasta / "info.json"
        info = (
            json.loads(arquivo_info.read_text(encoding="utf-8"))
            if arquivo_info.exists()
            else {}
        )
        self.fps = info.get("fps", 12)
        if tamanho is not None:
            self.tamanho = tamanho
        elif "largura" in info and "altura" in info:
            self.tamanho = (info["largura"], info["altura"])
        else:
            with Image.open(io.BytesIO(self._dados[0])) as primeiro_quadro:
                self.tamanho = primeiro_quadro.size
        self.tempo = 0.0
        self._indice = -1
        self._imagem: pygame.Surface | None = None
        self._decodificador = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mapa_animado")
        self._pedidos: dict[int, Future] = {}

    def _decodificar(self, indice: int) -> tuple[bytes, tuple[int, int]]:
        """Roda na thread: o Pillow libera o GIL enquanto descompacta o JPEG."""
        with Image.open(io.BytesIO(self._dados[indice])) as quadro:
            quadro = quadro.convert("RGB")
            if quadro.size != self.tamanho:
                quadro = quadro.resize(self.tamanho, Image.LANCZOS)
            return quadro.tobytes(), quadro.size

    def _pedir(self, indice: int) -> None:
        if indice not in self._pedidos:
            self._pedidos[indice] = self._decodificador.submit(self._decodificar, indice)

    def atualizar(self, tempo_frame: float) -> None:
        self.tempo += tempo_frame

    @property
    def imagem(self) -> pygame.Surface:
        """Quadro atual, já no tamanho pedido."""
        total = len(self._dados)
        indice = int(self.tempo * self.fps) % total
        if indice != self._indice:
            self._pedir(indice)
            dados, tamanho = self._pedidos.pop(indice).result()
            self._imagem = pygame.image.frombytes(dados, tamanho, "RGB").convert()
            self._indice = indice
            proximos = {(indice + passo) % total for passo in range(1, QUADROS_ADIANTADOS + 1)}
            for antigo in [chave for chave in self._pedidos if chave not in proximos]:
                self._pedidos.pop(antigo).cancel()
            for proximo in sorted(proximos):
                self._pedir(proximo)
        return self._imagem
