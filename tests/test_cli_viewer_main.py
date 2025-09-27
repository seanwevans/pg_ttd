import renderer.cli_viewer as cli_viewer


class DummyScreen:
    def __init__(self):
        self.nodelay_flag = None

    def nodelay(self, flag: bool) -> None:
        self.nodelay_flag = flag

    def erase(self) -> None:
        pass

    def addch(self, y: int, x: int, ch: str, color: int) -> None:
        pass

    def refresh(self) -> None:
        pass

    def getch(self) -> int:
        return ord("q")


class DummyConnection:
    def __init__(self):
        self.closed = False

    def close(self) -> None:
        self.closed = True


class DummyCurses:
    COLOR_BLACK = 0
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_YELLOW = 3
    COLOR_BLUE = 4
    COLOR_MAGENTA = 5
    COLOR_CYAN = 6
    COLOR_WHITE = 7
    error = Exception

    def __init__(self):
        self.started = False
        self.use_default_called = False
        self.init_calls: list[tuple[int, int, int]] = []

    def curs_set(self, value: int) -> None:
        pass

    def start_color(self) -> None:
        self.started = True

    def has_colors(self) -> bool:
        return True

    def use_default_colors(self) -> None:
        if not self.started:
            raise AssertionError("use_default_colors called before start_color")
        self.use_default_called = True

    def init_pair(self, idx: int, fg: int, bg: int) -> None:
        if not self.started:
            raise AssertionError("init_pair called before start_color")
        self.init_calls.append((idx, fg, bg))

    def color_pair(self, idx: int) -> int:
        return idx


def test_main_initializes_curses_colors(monkeypatch):
    dummy_curses = DummyCurses()
    monkeypatch.setattr(cli_viewer, "curses", dummy_curses, raising=False)

    dummy_conn = DummyConnection()
    monkeypatch.setattr(cli_viewer.db, "connect", lambda dsn: dummy_conn)
    monkeypatch.setattr(
        cli_viewer,
        "fetch_tiles",
        lambda conn: [cli_viewer.Tile(x=0, y=0, ch="@", color="white")],
    )
    monkeypatch.setattr(cli_viewer, "advance_tick", lambda conn: None)
    monkeypatch.setattr(cli_viewer.time, "sleep", lambda _: None)
    monkeypatch.setattr(cli_viewer, "COLOR_CACHE", {}, raising=False)

    screen = DummyScreen()
    cli_viewer.main(screen, "postgresql://", refresh=0.0, step=True)

    assert dummy_curses.started is True
    assert dummy_curses.use_default_called is True
    assert dummy_curses.init_calls, "expected init_pair to be invoked"
    assert dummy_conn.closed is True
