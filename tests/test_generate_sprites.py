import base64
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from tools import generate_sprites

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_RED = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


def test_png_from_palette_stdlib_signature():
    data = generate_sprites._png_from_palette_stdlib((1, 2, 3))
    assert data.startswith(PNG_SIGNATURE)


def test_generate_palette_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "PIL", None)
    palette = generate_sprites.generate_palette()
    assert palette["red"] == EXPECTED_RED
    # ensure base64 decodes to a PNG file
    png = base64.b64decode(palette["red"])
    assert png.startswith(PNG_SIGNATURE)
