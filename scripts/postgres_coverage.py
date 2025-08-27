#!/usr/bin/env python3
"""Generate PL/pgSQL coverage report using the plpgsql_check extension.

This utility connects to a PostgreSQL database, retrieves coverage metrics for
all user-defined PL/pgSQL functions and writes them to a CSV file.
The plpgsql_check extension must be installed and the profiler enabled during
execution of tests. Run your SQL tests prior to invoking this script.
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import List, Tuple

import psycopg


def collect_coverage(dsn: str) -> List[Tuple[str, float, float]]:
    """Return coverage metrics for all PL/pgSQL functions."""
    query = """
        SELECT
            n.nspname || '.' || p.proname AS function,
            plpgsql_coverage_statements(p.oid::regprocedure) AS stmt_cov,
            plpgsql_coverage_branches(p.oid::regprocedure) AS branch_cov
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        JOIN pg_language l ON l.oid = p.prolang
        WHERE l.lanname = 'plpgsql'
          AND n.nspname NOT LIKE 'pg%'
          AND n.nspname <> 'information_schema'
        ORDER BY 1
    """
    # Allow authentication via either PGPASSWORD or POSTGRES_PASSWORD
    password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
    connect_kwargs = {"password": password} if password else {}

    with psycopg.connect(dsn, **connect_kwargs) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS plpgsql_check")
            cur.execute(query)
            rows = cur.fetchall()
    return [(func, float(stmt), float(branch)) for func, stmt, branch in rows]


def write_csv(rows: List[Tuple[str, float, float]], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["function", "statement_coverage", "branch_coverage"])
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Postgres coverage report")
    parser.add_argument("--dsn", required=True, help="PostgreSQL connection string")
    parser.add_argument(
        "--output",
        default="postgres-coverage.csv",
        help="Path to write CSV report",
    )
    args = parser.parse_args()

    rows = collect_coverage(args.dsn)
    write_csv(rows, args.output)

    for func, stmt_cov, branch_cov in rows:
        print(f"{func}: statements {stmt_cov:.0%} branches {branch_cov:.0%}")


if __name__ == "__main__":
    main()
