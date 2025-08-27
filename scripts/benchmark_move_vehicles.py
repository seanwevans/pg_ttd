"""Benchmark the move_vehicles stored procedure.

The script inserts a configurable number of vehicles and measures the
execution time of ``CALL move_vehicles()``. It requires a running
PostgreSQL database.
"""

import argparse
import time

import db_util


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark move_vehicles")
    parser.add_argument(
        "--count",
        type=int,
        default=100000,
        help="Number of vehicles to insert",
    )
    args = db_util.parse_dsn(parser)

    with db_util.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE vehicles")
            cur.execute(
                "INSERT INTO vehicles (x, y, schedule) "
                'SELECT 0, 0, \'[{"x":100,"y":0}]\'::jsonb '
                "FROM generate_series(1,%s)",
                (args.count,),
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
