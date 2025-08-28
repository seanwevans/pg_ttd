"""Command-line wrapper for :mod:`pgttd.run_tick`."""

from pgttd.run_tick import main


if __name__ == "__main__":  # pragma: no cover - script execution
    import sys

    sys.exit(main())

