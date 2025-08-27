import contextlib
import sys
from types import SimpleNamespace
from unittest import mock

import pytest

from pgttd import run_tick

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

    monkeypatch.setattr(run_tick.db, "connect", fake_connect)
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

    monkeypatch.setattr(run_tick.db, "connect", lambda dsn: conn)
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
        run_tick.db, "connect", lambda dsn: contextlib.nullcontext(conn)
    )
    monkeypatch.setattr(
        run_tick.db, "parse_dsn", lambda parser: SimpleNamespace(dsn="dsn")
    )

    result = run_tick.main()

    assert result == 1
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()
