"""Wrapper script to advance the game tick."""

import argparse
import logging
import sys

import db_util


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    args = db_util.parse_dsn(parser)

    conn = None
    try:
        conn = db_util.connect(args.dsn)
        with conn.cursor() as cur:
            cur.execute("CALL tick()")
        conn.commit()
        logging.info("tick() executed successfully")
        return 0
    except Exception:  # pragma: no cover - simple CLI logging
        logging.exception("tick() execution failed")
        if conn is not None:
            conn.rollback()
        return 1
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())

