import argparse
import os

import psycopg


def add_dsn_argument(parser: argparse.ArgumentParser) -> None:
    """Add a standard DSN argument to *parser*."""
    parser.add_argument(
        "--dsn",
        type=str,
        default=os.environ.get("DATABASE_URL", ""),
        help="PostgreSQL DSN; defaults to DATABASE_URL env var",
    )


def parse_dsn(args: argparse.Namespace) -> argparse.Namespace:
    """Validate that *args* contains a DSN."""
    if not args.dsn:
        raise RuntimeError("Database DSN must be provided via --dsn or DATABASE_URL")
    return args


def connect(dsn: str, **kwargs) -> psycopg.Connection:
    """Return a psycopg connection using *dsn*."""
    return psycopg.connect(dsn, **kwargs)
