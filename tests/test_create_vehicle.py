import json
import sys
from unittest.mock import MagicMock

import pytest

from pgttd import create_vehicle, db


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

    monkeypatch.setattr(db, "connect", fake_connect)
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
            '[{"x":1,"y":2}]',
            "--cargo",
            '[{"resource":"wood","amount":3}]',
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


def test_invalid_schedule_json(monkeypatch, capsys):
    connect_mock = MagicMock()
    monkeypatch.setattr(db, "connect", connect_mock)
    monkeypatch.setattr(
        sys,
        "argv",
        ["create_vehicle.py", "--dsn", DSN, "--schedule", "not json"],
    )

    with pytest.raises(SystemExit) as exc:
        create_vehicle.main()
    assert exc.value.code == 1
    assert "Invalid JSON for --schedule" in capsys.readouterr().err

    connect_mock.assert_not_called()
