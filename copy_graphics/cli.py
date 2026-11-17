"""Command line entry point for copy-graphics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, copy
from .errors import CopyGraphicsError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="copy-graphics",
        description=(
            "Copy a graphics file to the clipboard together with its real MIME type, "
            "so you can paste it into Inkscape, GIMP, Krita, Illustrator or Figma."
        ),
    )
    parser.add_argument("file", metavar="FILE", nargs="+", help="graphics file to copy")
    parser.add_argument(
        "-t",
        "--mime",
        metavar="TYPE",
        help="publish this MIME type instead of detecting one",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="print nothing on success")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    if len(args.file) > 1:
        parser.error(f"copy one file at a time (got {len(args.file)})")

    path = Path(args.file[0]).expanduser()
    try:
        mime = copy(path, args.mime)
        size = path.stat().st_size
    except OSError as exc:
        print(f"copy-graphics: error: cannot read {path}: {exc.strerror or exc}", file=sys.stderr)
        return 1
    except CopyGraphicsError as exc:
        print(f"copy-graphics: error: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Copied {path.name} as {mime} ({_human_size(size)}) to the clipboard.")
    return 0


def _human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    kib = size / 1024
    if kib < 1024:
        return f"{kib:.1f} KiB"
    return f"{kib / 1024:.1f} MiB"
