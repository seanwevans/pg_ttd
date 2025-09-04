import types
import tracemalloc

import pytest

from renderer.cli_viewer import render, Tile

class DummyScreen:
    def erase(self):
        pass
    def addch(self, y, x, ch, color):
        pass
    def refresh(self):
        pass


@pytest.mark.parametrize("N", [10_000])
def test_render_uses_less_memory_with_generator(monkeypatch, N):
    dummy_curses = types.SimpleNamespace(
        COLOR_BLACK=0,
        COLOR_RED=1,
        COLOR_GREEN=2,
        COLOR_YELLOW=3,
        COLOR_BLUE=4,
        COLOR_MAGENTA=5,
        COLOR_CYAN=6,
        COLOR_WHITE=7,
        init_pair=lambda idx, fg, bg: None,
        color_pair=lambda idx: idx,
    )
    monkeypatch.setattr("renderer.cli_viewer.curses", dummy_curses, raising=False)

    screen = DummyScreen()

    def generate_tiles(n):
        for i in range(n):
            yield Tile(x=i, y=0, ch="@", color="white")

    def run_list():
        tiles = list(generate_tiles(N))
        render(screen, tiles, color_cache={})

    def run_gen():
        tiles = generate_tiles(N)
        render(screen, tiles, color_cache={})

    tracemalloc.start()
    run_list()
    _, peak_list = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    run_gen()
    _, peak_gen = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert peak_gen < peak_list


def test_render_reuses_color_cache(monkeypatch):
    calls = []
    dummy_curses = types.SimpleNamespace(
        COLOR_BLACK=0,
        COLOR_RED=1,
        COLOR_GREEN=2,
        COLOR_YELLOW=3,
        COLOR_BLUE=4,
        COLOR_MAGENTA=5,
        COLOR_CYAN=6,
        COLOR_WHITE=7,
        init_pair=lambda idx, fg, bg: calls.append((idx, fg, bg)),
        color_pair=lambda idx: idx,
    )
    monkeypatch.setattr("renderer.cli_viewer.curses", dummy_curses, raising=False)

    screen = DummyScreen()
    tiles = [Tile(x=0, y=0, ch="@", color="white")]
    cache: dict[str, int] = {}

    render(screen, tiles, color_cache=cache)
    render(screen, tiles, color_cache=cache)

    assert len(calls) == 1
