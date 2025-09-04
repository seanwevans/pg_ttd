import json
import sys
from unittest.mock import MagicMock

import pytest
from psycopg.types.json import Json

from pgttd import create_vehicle
from tests.helpers import DummyCursor, DummyConnection

# The original tests reference a ``cv_module`` variable but never assign it.
#
# Older versions of this test suite imported the module under that name, so the
# later assertions still expect a ``cv_module`` variable to exist.  Without this
# alias the tests crash with ``NameError`` before exercising the real
# functionality.  Provide the alias here so the tests can focus on validating
# the module's behaviour rather than failing due to a missing symbol.
cv_module = create_vehicle

DSN = "postgresql://example"


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
    assert params[0] == 1
    assert params[1] == 2
    assert isinstance(params[2], Json)
    assert params[2].obj == [{"x": 1, "y": 2}]
    assert isinstance(params[3], Json)
    assert params[3].obj == [{"resource": "wood", "amount": 3}]
    assert params[4] == 7
    assert conn.committed
    assert conn.closed
    assert f"Inserted vehicle at 1 2" in capsys.readouterr().out


def test_main_defaults(monkeypatch, capsys):
    cursor = DummyCursor()
    conn = DummyConnection(cursor)

    def fake_connect(dsn: str):
        assert dsn == DSN
        return conn

    monkeypatch.setattr(create_vehicle.db, "connect", fake_connect)
    monkeypatch.setattr(sys, "argv", ["create_vehicle.py", "--dsn", DSN])

    create_vehicle.main()

    sql, params = cursor.executed
    assert "INSERT INTO vehicles" in sql
    assert params[0] == 1
    assert params[1] == 1
    assert isinstance(params[2], Json)
    assert params[2].obj == []
    assert isinstance(params[3], Json)
    assert params[3].obj == []
    assert params[4] is None
    assert conn.committed
    assert conn.closed
    assert f"Inserted vehicle at 1 1" in capsys.readouterr().out


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


def test_validate_schedule_success():
    schedule = '[{"x":1,"y":2}]'
    assert cv_module.validate_schedule(schedule) == [{"x": 1, "y": 2}]


@pytest.mark.parametrize(
    "schedule, msg",
    [
        ("not json", "Invalid JSON for --schedule"),
        ("{}", "--schedule must be a JSON array"),
        ("[1]", "Schedule entry 0 must be an object"),
        ('[{"y":2}]', "Schedule entry 0 missing 'x'"),
        ('[{"x":2}]', "Schedule entry 0 missing 'y'"),
        ('[{"x":"1","y":2}]', "Schedule entry 0 key 'x' must be an integer"),
        ('[{"x":1,"y":"2"}]', "Schedule entry 0 key 'y' must be an integer"),
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
        (
            '[{"resource":"wood","amount":-1}]',
            "Cargo entry 0 key 'amount' must be non-negative",
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
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 1, 1, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_resource_wrong_type(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": 5, "amount": 3}])

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 1, 1, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_amount_non_integer(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": "wood", "amount": "three"}])

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 1, 1, "[]", cargo, None)

    connect_mock.assert_not_called()


def test_insert_vehicle_cargo_amount_negative(monkeypatch):
    connect_mock = MagicMock()
    monkeypatch.setattr(create_vehicle.db, "connect", connect_mock)
    cargo = json.dumps([{"resource": "wood", "amount": -1}])

    with pytest.raises(ValueError):
        create_vehicle.insert_vehicle(DSN, 0, 0, "[]", cargo, None)

    connect_mock.assert_not_called()
