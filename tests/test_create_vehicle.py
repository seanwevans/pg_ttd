import sys
from pathlib import Path
import json
from unittest.mock import MagicMock

import pytest

# Ensure scripts directory is on the path
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))

import create_vehicle  # type: ignore
import db_util  # type: ignore


class DummyCursor:
    def __init__(self):
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def execute(self, sql, params):
        self.executed = (sql, params)


class DummyConnection:
    def __init__(self, cursor: DummyCursor):
        self.cursor_obj = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


DSN = "postgresql://example"


def test_main_success(monkeypatch, capsys):
    cursor = DummyCursor()
    conn = DummyConnection(cursor)

    def fake_connect(dsn: str):
        assert dsn == DSN
        return conn

    monkeypatch.setattr(db_util, "connect", fake_connect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "create_vehicle.py",
            "--dsn",
            DSN,
            "--x",
            "1",
            "--y",
            "2",
            "--schedule",
            "[{\"x\":1,\"y\":2}]",
            "--cargo",
            "[{\"resource\":\"wood\",\"amount\":3}]",
            "--company-id",
            "7",
        ],
    )

    create_vehicle.main()

    sql, params = cursor.executed
    assert "INSERT INTO vehicles" in sql
    assert params == (
        1,
        2,
        json.dumps([{"x": 1, "y": 2}]),
        json.dumps([{"resource": "wood", "amount": 3}]),
        7,
    )
    assert conn.committed
    assert conn.closed
    assert f"Inserted vehicle at 1 2" in capsys.readouterr().out


def test_invalid_schedule_json(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(db_util, "connect", connect_mock)
    monkeypatch.setattr(
        sys,
        "argv",
        ["create_vehicle.py", "--dsn", DSN, "--schedule", "not json"],
    )

    with pytest.raises(ValueError, match="Invalid JSON for --schedule"):
        create_vehicle.main()

    connect_mock.assert_not_called()
