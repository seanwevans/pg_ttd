"""Wrapper script to advance the game tick."""

import argparse
import logging
import sys

import pgttd.db as db


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    db.add_dsn_argument(parser)
    args = parser.parse_args()
    db.parse_dsn(args)

    conn = None
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
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        return 1
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    import sys
    sys.exit(main())

