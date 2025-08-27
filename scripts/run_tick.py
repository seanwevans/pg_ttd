"""Wrapper script to advance the game tick."""
import os
import psycopg


def main() -> None:
    """Call the ``tick`` stored procedure."""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL environment variable must be set")

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL tick()")
        conn.commit()


if __name__ == "__main__":
    main()
