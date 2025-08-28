import json
import sys
from unittest.mock import MagicMock

import pytest

from pgttd import create_vehicle

DSN = "postgresql://example"


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


def test_main_success(monkeypatch, capsys):
    cursor = DummyCursor()
    conn = DummyConnection(cursor)

    def fake_connect(dsn: str):
        assert dsn == DSN
        return conn

    monkeypatch.setattr(create_vehicle.db, "connect", fake_connect)

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


def test_invalid_schedule_json(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    monkeypatch.setattr(
        sys,
        "argv",
        ["create_vehicle.py", "--dsn", DSN, "--schedule", "not json"],
    )

    with pytest.raises(SystemExit) as exc:
        create_vehicle.main()
    assert "Invalid JSON for --schedule" in str(exc.value)

    connect_mock.assert_not_called()


@pytest.mark.parametrize(
    "cargo",
    [
        json.dumps([{"resource": "wood"}]),  # missing amount
        json.dumps([{"amount": 3}]),  # missing resource
    ],
)
def test_insert_vehicle_cargo_missing_required_keys(monkeypatch, cargo):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_resource_wrong_type(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": 5, "amount": 3}])

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_amount_non_integer(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": "wood", "amount": "three"}])

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()
