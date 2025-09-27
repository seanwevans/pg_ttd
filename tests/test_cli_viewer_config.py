import json

import pytest
from renderer.cli_viewer import load_config


def test_load_config_invalid_json(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text("{invalid json", encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        load_config()


def test_load_config_missing_config_file(monkeypatch):
    monkeypatch.setenv("PGTTD_CONFIG", "/nonexistent/config.json")
    with pytest.raises(RuntimeError, match="does not exist"):
        load_config()


def test_load_config_invalid_pgport(monkeypatch):
    monkeypatch.setenv("PGPORT", "not-a-number")
    with pytest.raises(RuntimeError, match="Invalid PGPORT"):
        load_config()


def test_load_config_requires_mapping(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps(["host", "localhost"]), encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="JSON object"):
        load_config()


def test_load_config_rejects_unsupported_field(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"dsn": "postgresql://"}), encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="unsupported connection field"):
        load_config()


def test_load_config_requires_string_values(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"host": 123}), encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="must be a string value"):
        load_config()


def test_load_config_validates_port(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"port": "invalid"}), encoding="utf8")
    monkeypatch.setenv("PGTTD_CONFIG", str(cfg))
    with pytest.raises(RuntimeError, match="field 'port' must be an integer"):
        load_config()
