"""Wrapper module to advance the game tick."""

import argparse
import logging
import sys

from . import db


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    args = db.parse_dsn(parser)

    conn = None
    conn_ctx = None
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
        if conn:
            conn.rollback()
        return 1
    finally:
        if conn:
            conn.close()
        if conn_ctx is not conn and hasattr(conn_ctx, "__exit__"):
            conn_ctx.__exit__(None, None, None)


if __name__ == "__main__":  # pragma: no cover - script execution
    sys.exit(main())
