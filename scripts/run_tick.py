"""Wrapper script to advance the game tick."""

import argparse
import logging
import sys

import db_util


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    args = db_util.parse_dsn(parser)

    try:
        with db_util.connect(args.dsn) as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("CALL tick()")
                conn.commit()
            except Exception:  # pragma: no cover - simple CLI logging
                logging.exception("tick() execution failed")
                conn.rollback()
                return 1
    except Exception:  # pragma: no cover - simple CLI logging
        logging.exception("tick() execution failed")
        return 1
    logging.info("tick() executed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
