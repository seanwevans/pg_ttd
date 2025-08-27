import contextlib
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
spec = importlib.util.spec_from_file_location(
    "run_tick", Path(__file__).resolve().parents[1] / "scripts" / "run_tick.py"
)
run_tick = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_tick)


def test_main_rolls_back_on_failure(monkeypatch):
    conn = mock.MagicMock()
    cur = mock.MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    cur.execute.side_effect = RuntimeError

    monkeypatch.setattr(
        run_tick.db_util, "connect", lambda dsn: contextlib.nullcontext(conn)
    )
    monkeypatch.setattr(
        run_tick.db_util, "parse_dsn", lambda parser: SimpleNamespace(dsn="dsn")
    )

    result = run_tick.main()

    assert result == 1
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()
