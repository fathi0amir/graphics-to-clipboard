"""Copy graphics files to the clipboard with their real MIME type.

From the command line::

    $ copy-graphics example.svg

From Python, one call per file::

    from copy_graphics import copy

    copy("example.svg")                        # type read from the bytes, then the name
    copy("drawing.dat", mime="image/svg+xml")  # or state it yourself

Already have the bytes in memory (a render, an editor buffer, a notebook cell)?
Hand them over with the type they belong to::

    from copy_graphics import copy_bytes

    copy_bytes(png_bytes, "image/png")

Both return the MIME type that went on the clipboard. When the file is not a
graphic, or the platform has no usable clipboard, they raise a
``CopyGraphicsError`` subclass -- ``UnknownFileTypeError``, ``ClipboardError``
and ``ClipboardUnavailableError``, all importable from ``copy_graphics`` --
and ``copy`` raises ``OSError`` when the file cannot be read.

This is the same code path the CLI runs: ``get_backend()`` picks the Windows,
macOS or Linux backend for the current ``sys.platform``.
"""

from __future__ import annotations

from pathlib import Path

from .backends import get_backend
from .errors import (
    ClipboardError,
    ClipboardUnavailableError,
    CopyGraphicsError,
    UnknownFileTypeError,
)
from .flavors import Flavor
from .mimes import detect_mime

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "copy",
    "copy_bytes",
    "Flavor",
    "CopyGraphicsError",
    "ClipboardError",
    "ClipboardUnavailableError",
    "UnknownFileTypeError",
]


def copy(path: str | Path, mime: str | None = None) -> str:
    """Copy the graphics file at ``path`` to the clipboard.

    The type is detected from the file's leading bytes and then its name,
    unless ``mime`` is given, which also replaces the graphics-only check.
    Returns the MIME type published on the clipboard.
    """
    target = Path(path).expanduser()
    data = target.read_bytes()
    if not data:
        raise CopyGraphicsError(f"{target} is empty")
    if mime is None:
        mime = detect_mime(target, data)
    get_backend().copy([Flavor(mime, data)])
    return mime


def copy_bytes(data: bytes, mime: str) -> str:
    """Copy ``data`` to the clipboard as ``mime``.

    Use this when the image is already in memory and there is no file to sniff.
    Returns the MIME type published on the clipboard.
    """
    if not data:
        raise CopyGraphicsError("no bytes to copy: the payload is empty")
    get_backend().copy([Flavor(mime, data)])
    return mime
