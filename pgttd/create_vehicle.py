"""Utilities for inserting sample vehicles for testing."""

import argparse
import json

from . import db

def insert_vehicle(
    dsn: str,
    x: int,
    y: int,
    schedule: str,
    cargo: str,
    company_id: int | None,
) -> None:
    """Validate arguments and insert a vehicle into the database.

    Raises:
        ValueError: If ``schedule`` or ``cargo`` are not valid JSON or fail
            validation checks.
    """
    try:
        schedule_obj = json.loads(schedule)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for --schedule: {e.msg}") from e

    try:
        cargo_obj = json.loads(cargo)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for --cargo: {e.msg}") from e

    if not isinstance(schedule_obj, list):
        raise ValueError("--schedule must be a JSON array")
    for idx, entry in enumerate(schedule_obj):
        if not isinstance(entry, dict):
            raise ValueError(f"Schedule entry {idx} must be an object")
        for coord in ("x", "y"):
            if coord not in entry:
                raise ValueError(f"Schedule entry {idx} missing '{coord}'")
            if not isinstance(entry[coord], int):
                raise ValueError(
                    f"Schedule entry {idx} key '{coord}' must be an integer"
                )

    if not isinstance(cargo_obj, list):
        raise ValueError("--cargo must be a JSON array")
    for idx, item in enumerate(cargo_obj):
        if not isinstance(item, dict):
            raise ValueError(f"Cargo entry {idx} must be an object")
        if "resource" not in item or "amount" not in item:
            raise ValueError(
                f"Cargo entry {idx} must contain 'resource' and 'amount' keys"
            )
        if not isinstance(item["resource"], str):
            raise ValueError(f"Cargo entry {idx} key 'resource' must be a string")
        if not isinstance(item["amount"], int):
            raise ValueError(f"Cargo entry {idx} key 'amount' must be an integer")

    with db.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vehicles (x, y, schedule, cargo, company_id)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                """,
                (
                    x,
                    y,
                    json.dumps(schedule_obj),
                    json.dumps(cargo_obj),
                    company_id,
                ),
            )
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a vehicle")
    parser.add_argument("--x", type=int, default=0, help="Starting X coordinate")
    parser.add_argument("--y", type=int, default=0, help="Starting Y coordinate")
    parser.add_argument(
        "--schedule",
        type=str,
        default="[]",
        help='JSON array of waypoints, e.g. "[{"x":0,"y":0},{"x":5,"y":5}]"',
    )
    parser.add_argument("--company-id", type=int, default=None)
    parser.add_argument(
        "--cargo",
        type=str,
        default="[]",
        help="JSON description of cargo",
    )
    args = db.parse_dsn(parser)

    insert_vehicle(
        dsn=args.dsn,
        x=args.x,
        y=args.y,
        schedule=args.schedule,
        cargo=args.cargo,
        company_id=args.company_id,
    )

    print("Inserted vehicle at", args.x, args.y)


if __name__ == "__main__":  # pragma: no cover - script execution
    main()

