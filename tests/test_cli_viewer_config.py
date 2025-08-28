import pytest
from renderer.cli_viewer import load_config


def test_load_config_invalid_json(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text("{invalid json", encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        load_config()


def test_load_config_invalid_pgport(monkeypatch):
    monkeypatch.setenv("PGPORT", "not-a-number")
    with pytest.raises(RuntimeError, match="Invalid PGPORT"):
        load_config()
