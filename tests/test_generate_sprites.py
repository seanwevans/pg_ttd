import base64
import sys
from pathlib import Path
import importlib.util
import sqlite3


spec = importlib.util.spec_from_file_location(
    "generate_sprites", Path(__file__).resolve().parents[1] / "tools" / "generate_sprites.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

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

def test_insert_statement_is_escaped(tmp_path):
    malicious_name = "evil'); DROP TABLE sprites; --"
    payload = "data"
    sql = module.insert_statement(malicious_name, payload)

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE sprites(name TEXT, image_base64 TEXT)")
    conn.executescript(sql)

    rows = conn.execute("SELECT name, image_base64 FROM sprites").fetchall()
    assert rows == [(malicious_name, payload)]
