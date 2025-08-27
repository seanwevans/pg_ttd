import base64
import sys
from pathlib import Path
import sqlite3

from tools import generate_sprites as module

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_RED = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


def test_png_from_palette_stdlib_signature():
    data = module._png_from_palette_stdlib((1, 2, 3))
    assert data.startswith(PNG_SIGNATURE)


def test_generate_palette_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "PIL", None)
    palette = module.generate_palette()
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


def test_quote_sql_handles_various_types():
    assert module.quote_sql("O'Reilly") == "'O''Reilly'"
    assert module.quote_sql(42) == "'42'"
    assert module.quote_sql(Path("a'b")) == "'a''b'"


def test_main_writes_expected_file(tmp_path, monkeypatch, capsys):
    out = tmp_path / "out.sql"

    monkeypatch.setattr(module, "generate_palette", lambda: {"red": "data"})
    monkeypatch.setattr(sys, "argv", ["generate_sprites.py", "--output", str(out)])

    module.main()

    assert out.read_text() == module.insert_statement("red", "data") + "\n"
    assert f"Wrote 1 sprites to {out}" in capsys.readouterr().out
