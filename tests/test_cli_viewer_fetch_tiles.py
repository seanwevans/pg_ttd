from renderer.cli_viewer import fetch_tiles


def test_fetch_tiles_sorted_by_y_then_x():
    rows = [
        (1, 1, "c", "green"),
        (0, 0, "a", "red"),
        (2, 1, "d", "blue"),
        (1, 0, "b", "yellow"),
    ]

    class DummyCursor:
        def __init__(self, rows):
            self.rows = rows
            self.sql = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def execute(self, sql):
            self.sql = sql
            if "order by" in sql.lower():
                self.rows = sorted(self.rows, key=lambda r: (r[1], r[0]))

        def __iter__(self):
            return iter(self.rows)

    class DummyConn:
        def __init__(self, rows):
            self.cur = DummyCursor(rows)

        def cursor(self):
            return self.cur

    conn = DummyConn(list(rows))

    tiles = list(fetch_tiles(conn))
    coords = [(t.x, t.y) for t in tiles]
    expected = sorted([(x, y) for x, y, _, _ in rows], key=lambda p: (p[1], p[0]))
    assert coords == expected
    assert "order by t.y, t.x" in conn.cur.sql.lower()
