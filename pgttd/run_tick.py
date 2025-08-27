"""Wrapper module to advance the game tick."""

import argparse
import logging
import sys
from contextlib import ExitStack

from . import db


def main() -> int:
    """Call the ``tick`` stored procedure."""
    parser = argparse.ArgumentParser(description="Advance the game tick")
    db.add_dsn_argument(parser)
    args, _ = parser.parse_known_args()
    db.parse_dsn(args)

    with ExitStack() as stack:
        conn_ctx = db.connect(args.dsn)
        conn = stack.enter_context(conn_ctx) if hasattr(conn_ctx, "__enter__") else conn_ctx
        stack.callback(getattr(conn, "close", lambda: None))
        try:
            with conn.cursor() as cur:
                cur.execute("CALL tick()")
            conn.commit()
            logging.info("tick() executed successfully")
            return 0
        except Exception:  # pragma: no cover - simple CLI logging
            logging.exception("tick() execution failed")
            conn.rollback()
            return 1


if __name__ == "__main__":  # pragma: no cover - script execution
    sys.exit(main())
