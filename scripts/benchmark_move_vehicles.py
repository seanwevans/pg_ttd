"""Benchmark the move_vehicles stored procedure.

The script inserts a configurable number of vehicles and measures the
execution time of ``CALL move_vehicles()``. It requires a running
PostgreSQL database.
"""

import argparse
import json
import time

import pgttd.db as db


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark move_vehicles")
    db.add_dsn_argument(parser)
    parser.add_argument(
        "--count",
        type=int,
        default=100000,
        help="Number of vehicles to insert",
    )
    args = parser.parse_args()
    db.parse_dsn(args)

    schedule = [{"x": 100, "y": 0}]

    with db.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE vehicles")
            cur.execute(
                "INSERT INTO vehicles (x, y, schedule) "
                "SELECT 0, 0, %s::jsonb FROM generate_series(1, %s)",
                (json.dumps(schedule), args.count),
            )
            conn.commit()

        start = time.perf_counter()
        with conn.cursor() as cur:
            cur.execute("CALL move_vehicles()")
        conn.commit()
        elapsed = time.perf_counter() - start

    print(f"Moved {args.count} vehicles in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
