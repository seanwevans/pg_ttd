#!/usr/bin/env python3
"""Generate sql/schema.sql from individual table definitions.

This script concatenates SQL files in ``sql/tables`` in dependency order to
produce ``sql/schema.sql``. Edit the per-table files and re-run this script to
update the combined schema.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = ROOT / "sql" / "tables"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

# Ordered list to satisfy foreign key dependencies
TABLE_ORDER = [
    "terrain",
    "tiles",
    "companies",
    "industries",
    "vehicles",
    "industry_outputs",
    "vehicle_operations",
    "game_state",
    "resources",
    "resource_rules",
    "resource_industries",
]


def main() -> None:
    with SCHEMA_PATH.open("w", encoding="utf-8") as schema:
        schema.write("-- Auto-generated; do not edit directly.\n\n")
        for name in TABLE_ORDER:
            path = TABLES_DIR / f"{name}.sql"
            text = path.read_text()
            schema.write(text)
            if not text.endswith("\n"):
                schema.write("\n")
            schema.write("\n")


if __name__ == "__main__":
    main()
