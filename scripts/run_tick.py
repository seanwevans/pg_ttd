"""Wrapper script to advance the game tick."""

import argparse
import logging
import os
import sys

import psycopg


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    parser.add_argument(
        "--dsn",
        type=str,
        default=os.environ.get("DATABASE_URL", ""),
        help="PostgreSQL DSN; defaults to DATABASE_URL env var",
    )
    args = parser.parse_args()

    if not args.dsn:
        raise RuntimeError("Database DSN must be provided via --dsn or DATABASE_URL")

    logging.basicConfig(level=logging.INFO)

    conn = None
    try:
        conn = psycopg.connect(args.dsn)
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
