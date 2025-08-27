import sys
from pathlib import Path
import pytest
import contextlib
import importlib.util
from types import SimpleNamespace
from unittest import mock

# Ensure scripts directory is on the path
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))

import run_tick  # type: ignore
import db_util  # type: ignore
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
spec = importlib.util.spec_from_file_location(
    "run_tick", Path(__file__).resolve().parents[1] / "scripts" / "run_tick.py"
)
run_tick = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_tick)
DSN = "postgresql://example"

class DummyCursor:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.sql = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def execute(self, sql: str):
        if self.should_fail:
            raise Exception("boom")
        self.sql = sql


class DummyConnection:
    def __init__(self, cursor: DummyCursor):
        self.cursor_obj = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True

def test_main_success(monkeypatch):
    cursor = DummyCursor()
    conn = DummyConnection(cursor)

    def fake_connect(dsn: str):
        assert dsn == DSN
        return conn

    monkeypatch.setattr(db_util, "connect", fake_connect)
    monkeypatch.setattr(sys, "argv", ["run_tick.py", "--dsn", DSN])

    rc = run_tick.main()

    assert rc == 0
    assert cursor.sql == "CALL tick()"
    assert conn.committed
    assert conn.closed
    assert not conn.rolled_back

def test_main_failure(monkeypatch):
    cursor = DummyCursor(should_fail=True)
    conn = DummyConnection(cursor)

    monkeypatch.setattr(db_util, "connect", lambda dsn: conn)
    monkeypatch.setattr(sys, "argv", ["run_tick.py", "--dsn", DSN])

    rc = run_tick.main()

    assert rc == 1
    assert conn.rolled_back
    assert conn.closed
    assert not conn.committed

def test_main_rolls_back_on_failure(monkeypatch):
    conn = mock.MagicMock()
    cur = mock.MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    cur.execute.side_effect = RuntimeError

    monkeypatch.setattr(
        run_tick.db_util, "connect", lambda dsn: contextlib.closing(conn)
    )
    monkeypatch.setattr(
        run_tick.db_util, "parse_dsn", lambda parser: SimpleNamespace(dsn="dsn")
    )

    result = run_tick.main()

    assert result == 1
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()
