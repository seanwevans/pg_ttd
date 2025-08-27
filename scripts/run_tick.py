"""Wrapper script to advance the game tick."""

import argparse

import db_util


def main() -> None:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    args = db_util.parse_dsn(parser)

    with db_util.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL tick()")
        conn.commit()


if __name__ == "__main__":
    main()
