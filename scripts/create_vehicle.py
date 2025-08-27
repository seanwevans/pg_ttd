"""Insert a sample vehicle for testing.

The script connects to a PostgreSQL database using standard libpq
connection parameters. A JSON array of waypoints is inserted into the
`schedule` column. Each waypoint must be an object with `x` and `y` keys.
"""

import argparse
import json
import os

import psycopg2


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a vehicle")
    parser.add_argument("--x", type=int, default=0, help="Starting X coordinate")
    parser.add_argument("--y", type=int, default=0, help="Starting Y coordinate")
    parser.add_argument(
        "--schedule",
        type=str,
        default="[]",
        help="JSON array of waypoints, e.g. '[{\"x\":0,\"y\":0},{\"x\":5,\"y\":5}]'",
    )
    parser.add_argument("--company-id", type=int, default=None)
    parser.add_argument(
        "--cargo",
        type=str,
        default="[]",
        help="JSON description of cargo",
    )
    parser.add_argument(
        "--dsn",
        type=str,
        default=os.environ.get("PG_DSN", ""),
        help="PostgreSQL DSN string",
    )

    args = parser.parse_args()

    schedule = json.loads(args.schedule)
    cargo = json.loads(args.cargo)

    conn = psycopg2.connect(args.dsn)
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vehicles (x, y, schedule, cargo, company_id)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                """,
                (args.x, args.y, json.dumps(schedule), json.dumps(cargo), args.company_id),
            )
    print("Inserted vehicle at", args.x, args.y)


if __name__ == "__main__":
    main()
