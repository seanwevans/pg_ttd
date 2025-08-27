"""Insert a sample vehicle for testing.

The script connects to a PostgreSQL database using standard libpq
connection parameters. A JSON array of waypoints is inserted into the
`schedule` column. Each waypoint must be an object with `x` and `y` keys.
"""

import argparse
import sys

import pgttd.db as db
from pgttd.create_vehicle import insert_vehicle


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a vehicle")
    parser.add_argument("--x", type=int, default=0, help="Starting X coordinate")
    parser.add_argument("--y", type=int, default=0, help="Starting Y coordinate")
    parser.add_argument(
        "--schedule",
        type=str,
        default="[]",
        help='JSON array of waypoints, e.g. [{"x":0,"y":0},{"x":5,"y":5}]',
    )
    parser.add_argument("--company-id", type=int, default=None)
    parser.add_argument(
        "--cargo",
        type=str,
        default="[]",
        help="JSON description of cargo",
    )
    args = db.parse_dsn(parser)

    try:
        insert_vehicle(
            dsn=args.dsn,
            x=args.x,
            y=args.y,
            schedule=args.schedule,
            cargo=args.cargo,
            company_id=args.company_id,
        )
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print("Inserted vehicle at", args.x, args.y)


if __name__ == "__main__":
    main()
