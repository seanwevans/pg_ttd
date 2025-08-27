#!/usr/bin/env python3
"""Generate simple colored square sprites and output SQL inserts.

This script generates a few colored square PNG images, encodes them as
Base64 strings, and writes SQL ``INSERT`` statements for a ``sprites``
table.  If Pillow is available it is used to produce 16x16 images.  If
not, the script falls back to generating 1x1 PNGs using only the Python
standard library.
"""

from __future__ import annotations

import argparse
import base64
import io
import struct
import zlib
from pathlib import Path
from typing import Any, Dict, Tuple


def quote_sql(value: Any) -> str:
    """Return a safely quoted SQL string literal.

    The original implementation assumed ``value`` was always a string and
    called :py:meth:`str.replace` directly.  During packaging/build steps some
    callers may provide values such as integers or ``Path`` objects which do
    not implement ``replace``.  Converting to ``str`` first avoids ``AttributeError``
    and ensures we can safely escape any single quotes.
    """

    text = str(value)
    return "'" + text.replace("'", "''") + "'"


def insert_statement(name: str, b64: str) -> str:
    """Return an INSERT statement for the sprites table."""
    return (
        "INSERT INTO sprites(name, image_base64) VALUES ({name}, {b64});".format(
            name=quote_sql(name), b64=quote_sql(b64)
        )
    )

# Basic palette of sprite colors.
PALETTE: Dict[str, Tuple[int, int, int]] = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}


def _png_from_palette_pillow(color: Tuple[int, int, int]) -> bytes:
    """Generate a PNG image using Pillow."""
    from PIL import Image

    img = Image.new("RGB", (16, 16), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _png_from_palette_stdlib(color: Tuple[int, int, int]) -> bytes:
    """Generate a minimal 1x1 PNG using only the standard library."""

    r, g, b = color
    width = height = 1
    # PNG file header
    png_signature = b"\x89PNG\r\n\x1a\n"

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw_data = bytes([0, r, g, b])  # no filter + RGB pixel
    idat = zlib.compress(raw_data)
    return png_signature + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def generate_palette() -> Dict[str, str]:
    """Return a mapping of sprite name to Base64-encoded PNG."""
    try:
        # Attempt to use Pillow if available
        import PIL  # noqa: F401

        generator = _png_from_palette_pillow
    except Exception:  # pragma: no cover - Pillow not available
        generator = _png_from_palette_stdlib

    sprites: Dict[str, str] = {}
    for name, rgb in PALETTE.items():
        png_bytes = generator(rgb)
        sprites[name] = base64.b64encode(png_bytes).decode("ascii")
    return sprites


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "sql" / "seed_sprites.sql",
        help="Path to write SQL insert statements",
    )
    args = parser.parse_args()

    sprites = generate_palette()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for name, b64 in sprites.items():
            f.write(insert_statement(name, b64) + "\n")
    print(f"Wrote {len(sprites)} sprites to {args.output}")


if __name__ == "__main__":
    main()
