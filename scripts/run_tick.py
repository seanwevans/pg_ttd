"""Wrapper script to advance the game tick."""

import argparse
import logging
import sys

import psycopg

import pgttd.db as db


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    args = db.parse_dsn(parser)

    try:
        conn_ctx = db.connect(args.dsn)
        if hasattr(conn_ctx, "__enter__"):
            conn = conn_ctx.__enter__()
        else:
            conn = conn_ctx
        with conn.cursor() as cur:
            cur.execute("CALL tick()")
        conn.commit()
        logging.info("tick() executed successfully")
        return 0

    except Exception:  # pragma: no cover - simple CLI logging
        logging.exception("tick() execution failed")
        return 1
    logging.info("tick() executed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
