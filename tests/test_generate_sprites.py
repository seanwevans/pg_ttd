import importlib.util
import sqlite3
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "generate_sprites", Path(__file__).resolve().parents[1] / "tools" / "generate_sprites.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_insert_statement_is_escaped(tmp_path):
    malicious_name = "evil'); DROP TABLE sprites; --"
    payload = "data"
    sql = module.insert_statement(malicious_name, payload)

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE sprites(name TEXT, image_base64 TEXT)")
    conn.executescript(sql)

    rows = conn.execute("SELECT name, image_base64 FROM sprites").fetchall()
    assert rows == [(malicious_name, payload)]
