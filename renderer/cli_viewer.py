#!/usr/bin/env python3
"""Minimal curses viewer for pg_ttd tiles.

The script connects to a PostgreSQL database and repeatedly fetches tile data
and the associated sprite information. Tiles are rendered in a curses window
using simple color pairs. After each render pass a `tick()` stored procedure is
called to advance the simulation.

Connection information is read from standard PostgreSQL environment variables
(`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) or from a JSON
configuration file referenced via the ``PGTTD_CONFIG`` environment variable.
Command line arguments can override these settings and also provide a DSN
connection string.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import logging
from dataclasses import dataclass
from typing import Iterable

import curses
import psycopg

import pgttd.db as db

logger = logging.getLogger(__name__)

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


def load_config() -> dict[str, str]:
    """Return connection parameters from environment or config file."""

    cfg_path = os.environ.get("PGTTD_CONFIG")
    if cfg_path and os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf8") as cfg:
            try:
                return json.load(cfg)
            except json.JSONDecodeError as exc:
                msg = f"Invalid JSON in config file '{cfg_path}': {exc.msg}"
                raise RuntimeError(msg) from exc

    pgport = os.environ.get("PGPORT", "5432")
    try:
        port = int(pgport)
    except ValueError as exc:
        raise RuntimeError(f"Invalid PGPORT value: {pgport}") from exc

    return {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": port,
        "dbname": os.environ.get("PGDATABASE", "pgttd"),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
    }


def fetch_tiles(conn) -> Iterable[Tile]:
    """Retrieve the current tile set from the database."""

    sql = (
        "SELECT t.x, t.y, s.glyph, s.color FROM tiles t "
        "JOIN sprites s ON t.sprite_id = s.id "
        "ORDER BY t.y, t.x"
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        for x, y, ch, color in cur:
            yield Tile(x, y, ch, color or "white")


def advance_tick(conn) -> None:
    """Advance the simulation by calling the `tick` stored procedure."""
    with conn.cursor() as cur:
        try:
            cur.execute("CALL tick()")
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Failed to advance simulation tick")
            raise


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


COLOUR_CACHE: dict[str, int] = {}


def colour_pair(colour: str, cache: dict[str, int] | None = None) -> int:
    """Return a curses color pair for a color name."""

    if cache is None:
        cache = COLOUR_CACHE
    colour = colour.lower()
    if colour not in cache:
        idx = len(cache) + 1
        base = COLOR_NAMES.get(colour, curses.COLOR_WHITE)
        curses.init_pair(idx, base, curses.COLOR_BLACK)
        cache[colour] = idx
    return curses.color_pair(cache[colour])


def render(stdscr, tiles: Iterable[Tile], colour_cache: dict[str, int] | None = None) -> None:
    """Render tiles onto the curses screen."""

    if colour_cache is None:
        colour_cache = COLOUR_CACHE
    stdscr.erase()
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


def main(stdscr, dsn: str | None, refresh: float, step: bool) -> None:
    """Render the simulation in a curses window."""

    curses.curs_set(0)
    stdscr.nodelay(True)
    if dsn:
        conn = db.connect(dsn)
    else:
        config = load_config()
        conn = psycopg.connect(**config)
    try:
        while True:
            tiles = fetch_tiles(conn)
            render(stdscr, tiles, COLOUR_CACHE)
            ch = stdscr.getch()
            if ch == ord("q"):
                break
            if not step or ch == ord("t"):
                try:
                    advance_tick(conn)
                except Exception:
                    logger.error("Tick advancement failed; exiting viewer")
                    break
            time.sleep(refresh)
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    db.add_dsn_argument(parser)
    parser.add_argument(
        "--refresh",
        type=float,
        default=0.5,
        help="delay between screen updates in seconds",
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="advance simulation only when 't' is pressed",
    )
    args = parser.parse_args()
    try:
        db.parse_dsn(args)
        dsn = args.dsn
    except RuntimeError:
        dsn = None
    curses.wrapper(main, dsn, args.refresh, args.step)
