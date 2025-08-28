import json
import sys
from unittest.mock import MagicMock

import pytest

from scripts import create_vehicle
from pgttd import create_vehicle as cv_module

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

    monkeypatch.setattr(cv_module.db, "connect", fake_connect)

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
    monkeypatch.setattr(cv_module.db, "connect", connect_mock)
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


def test_module_main_invalid_schedule_json(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(cv_module.db, "connect", connect_mock)
    monkeypatch.setattr(
        sys,
        "argv",
        ["create_vehicle.py", "--dsn", DSN, "--schedule", "not json"],
    )

    with pytest.raises(ValueError):
        cv_module.main()

    connect_mock.assert_not_called()


def test_validate_schedule_success():
    schedule = '[{"x":1,"y":2}]'
    assert cv_module.validate_schedule(schedule) == [{"x": 1, "y": 2}]


@pytest.mark.parametrize(
    "schedule, msg",
    [
        ("not json", "Invalid JSON for --schedule"),
        ("{}", "--schedule must be a JSON array"),
        ("[1]", "Schedule entry 0 must be an object"),
        ("[{\"y\":2}]", "Schedule entry 0 missing 'x'"),
        ("[{\"x\":2}]", "Schedule entry 0 missing 'y'"),
        ("[{\"x\":\"1\",\"y\":2}]", "Schedule entry 0 key 'x' must be an integer"),
        ("[{\"x\":1,\"y\":\"2\"}]", "Schedule entry 0 key 'y' must be an integer"),
    ],
)
def test_validate_schedule_errors(schedule, msg):
    with pytest.raises(ValueError, match=msg):
        cv_module.validate_schedule(schedule)


def test_validate_cargo_success():
    cargo = '[{"resource":"wood","amount":3}]'
    assert cv_module.validate_cargo(cargo) == [{"resource": "wood", "amount": 3}]


@pytest.mark.parametrize(
    "cargo, msg",
    [
        ("not json", "Invalid JSON for --cargo"),
        ("{}", "--cargo must be a JSON array"),
        ("[1]", "Cargo entry 0 must be an object"),
        (
            '[{"resource":"wood"}]',
            "Cargo entry 0 must contain 'resource' and 'amount' keys",
        ),
        (
            '[{"amount":3}]',
            "Cargo entry 0 must contain 'resource' and 'amount' keys",
        ),
        (
            '[{"resource":5,"amount":3}]',
            "Cargo entry 0 key 'resource' must be a string",
        ),
        (
            '[{"resource":"wood","amount":"3"}]',
            "Cargo entry 0 key 'amount' must be an integer",
        ),
    ],
)
def test_validate_cargo_errors(cargo, msg):
    with pytest.raises(ValueError, match=msg):
        cv_module.validate_cargo(cargo)


@pytest.mark.parametrize(
    "cargo",
    [
        json.dumps([{"resource": "wood"}]),  # missing amount
        json.dumps([{"amount": 3}]),  # missing resource
    ],
)
def test_insert_vehicle_cargo_missing_required_keys(monkeypatch, cargo):
    connect_mock = MagicMock()
    monkeypatch.setattr(cv_module.db, "connect", connect_mock)

    with pytest.raises(ValueError):
        cv_module.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_resource_wrong_type(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(cv_module.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": 5, "amount": 3}])

    with pytest.raises(ValueError):
        cv_module.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_amount_non_integer(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(cv_module.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": "wood", "amount": "three"}])

    with pytest.raises(ValueError):
        cv_module.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()
