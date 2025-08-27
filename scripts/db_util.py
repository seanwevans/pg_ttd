import argparse
import os

import psycopg


def parse_dsn(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Add a standard DSN argument to ``parser`` and return parsed args.

    The ``--dsn`` option defaults to the ``DATABASE_URL`` environment
    variable. A ``RuntimeError`` is raised if no DSN can be determined.
    """
    parser.add_argument(
        "--dsn",
        type=str,
        default=os.environ.get("DATABASE_URL", ""),
        help="PostgreSQL DSN; defaults to DATABASE_URL env var",
    )
    args = parser.parse_args()
    if not args.dsn:
        raise RuntimeError("Database DSN must be provided via --dsn or DATABASE_URL")
    return args


def connect(dsn: str, **kwargs) -> psycopg.Connection:
    """Return a psycopg connection using *dsn*."""
    return psycopg.connect(dsn, **kwargs)
