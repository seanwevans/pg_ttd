"""Wrapper module to advance the game tick."""

import argparse
import logging
import sys

import psycopg

from . import db


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    db.add_dsn_argument(parser)
    args, _ = parser.parse_known_args()
    db.parse_dsn(args)

    with db.connect(args.dsn) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("CALL tick()")
            conn.commit()
            logging.info("tick() executed successfully")
            return 0
        except psycopg.Error:  # pragma: no cover - simple CLI logging
            logging.exception("tick() execution failed")
            conn.rollback()
            return 1


if __name__ == "__main__":  # pragma: no cover - script execution
    sys.exit(main())
