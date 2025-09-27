import argparse

import pytest

import renderer.cli_viewer as cli_viewer


class DummyStdScr:
    def nodelay(self, flag: bool) -> None:
        self.nodelay_flag = flag


def test_positive_float_rejects_non_positive_values():
    for value in ["0", "0.0", "-1", "-0.5"]:
        with pytest.raises(argparse.ArgumentTypeError):
            cli_viewer.positive_float(value)


def test_positive_float_accepts_positive_value():
    assert cli_viewer.positive_float("0.1") == pytest.approx(0.1)


def test_main_rejects_invalid_refresh(monkeypatch):
    stdscr = DummyStdScr()

    with pytest.raises(ValueError, match="Refresh interval must be greater than zero"):
        cli_viewer.main(stdscr, dsn=None, refresh=0, step=False)
