"""Utilities for inserting sample vehicles for testing."""

import argparse
import json

from . import db


def validate_schedule(schedule: str) -> list[dict[str, int]]:
    """Parse and validate a schedule JSON string."""
    try:
        schedule_obj = json.loads(schedule)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for --schedule: {e.msg}") from e

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
    return schedule_obj


def validate_cargo(cargo: str) -> list[dict[str, object]]:
    """Parse and validate a cargo JSON string."""
    try:
        cargo_obj = json.loads(cargo)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for --cargo: {e.msg}") from e

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
        if item["amount"] < 0:
            raise ValueError(
                f"Cargo entry {idx} key 'amount' must be non-negative"
            )
    return cargo_obj


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
    schedule_obj = validate_schedule(schedule)
    cargo_obj = validate_cargo(cargo)

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


def build_arg_parser() -> argparse.ArgumentParser:
    """Return an argument parser configured for vehicle creation."""
    parser = argparse.ArgumentParser(description="Create a vehicle")
    db.add_dsn_argument(parser)
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
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    db.parse_dsn(args)

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
        raise SystemExit(str(e)) from e

    print("Inserted vehicle at", args.x, args.y)


if __name__ == "__main__":  # pragma: no cover - script execution
    main()
