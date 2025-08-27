#!/usr/bin/env python3
"""Minimal curses viewer for pg_ttd tiles.

The script connects to a PostgreSQL database and repeatedly fetches tile data
and the associated sprite information. Tiles are rendered in a curses window
using simple color pairs. After each render pass a `tick()` stored procedure is
called to advance the simulation.

Connection information is read from standard PostgreSQL environment variables
(`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) or from a JSON
configuration file referenced via the ``PGTTD_CONFIG`` environment variable.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import curses
import psycopg

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


@dataclass
class Tile:
    """Simple representation of a tile returned from the database."""

    x: int
    y: int
    ch: str
    color: str


COLOR_NAMES = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE,
}


def load_config() -> Dict[str, str]:
    """Return connection parameters from environment or config file."""

    cfg_path = os.environ.get("PGTTD_CONFIG")
    if cfg_path and os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf8") as cfg:
            return json.load(cfg)

    return {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": int(os.environ.get("PGPORT", 5432)),
        "dbname": os.environ.get("PGDATABASE", "pgttd"),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
    }


def fetch_tiles(conn) -> Iterable[Tile]:
    """Retrieve the current tile set from the database."""

    sql = (
        "SELECT t.x, t.y, s.glyph, s.color FROM tiles t "
        "JOIN sprites s ON t.sprite_id = s.id"
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        for x, y, ch, color in cur.fetchall():
            yield Tile(x, y, ch, color or "white")


def advance_tick(conn) -> None:
    """Advance the simulation by calling the `tick` stored procedure."""
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT tick()");
            conn.commit()
        except Exception:
            conn.rollback()


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def colour_pair(colour: str, cache: Dict[str, int]) -> int:
    """Return a curses color pair for a color name."""

    colour = colour.lower()
    if colour not in cache:
        idx = len(cache) + 1
        base = COLOR_NAMES.get(colour, curses.COLOR_WHITE)
        curses.init_pair(idx, base, curses.COLOR_BLACK)
        cache[colour] = idx
    return curses.color_pair(cache[colour])


def render(stdscr, tiles: Iterable[Tile]) -> None:
    """Render tiles onto the curses screen."""

    stdscr.erase()
    colour_cache: Dict[str, int] = {}
    for tile in tiles:
        try:
            stdscr.addch(tile.y, tile.x, tile.ch, colour_pair(tile.color, colour_cache))
        except curses.error:
            # Ignore tiles outside the screen.
            pass
    stdscr.refresh()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    config = load_config()
    conn = psycopg.connect(**config)
    try:
        while True:
            tiles = list(fetch_tiles(conn))
            render(stdscr, tiles)
            advance_tick(conn)
            time.sleep(0.5)
            if stdscr.getch() == ord("q"):
                break
    finally:
        conn.close()


if __name__ == "__main__":
    curses.wrapper(main)
