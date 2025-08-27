"""Wrapper script to advance the game tick."""

import argparse
import os

import psycopg


def main() -> None:
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

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL tick()")
        conn.commit()


if __name__ == "__main__":
    main()
