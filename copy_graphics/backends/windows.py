"""Windows clipboard backend built on pywin32's win32clipboard.

The Windows clipboard is a list of formats, and a format is either one of the
predefined CF_* numbers or any name registered with RegisterClipboardFormat.
Design tools ask for a named format (Inkscape reads ``image/x-inkscape-svg``,
GIMP and browsers read ``PNG``), so every name a format is known by is set on
the same clipboard: the app that pastes picks the one it understands.
"""

from __future__ import annotations

import time

from ..errors import ClipboardError, ClipboardUnavailableError
from ..flavors import Flavor

# Windows format names per MIME type, most widely understood first.
FORMAT_NAMES = {
    "image/svg+xml": ("image/svg+xml", "image/x-inkscape-svg", "SVG"),
    "image/png": ("PNG", "image/png"),
    "image/jpeg": ("image/jpeg", "JFIF", "JPEG"),
    "image/gif": ("image/gif", "GIF"),
    "image/bmp": ("image/bmp", "BMP"),
    "image/tiff": ("image/tiff", "TIFF"),
    "image/webp": ("image/webp", "WEBP"),
    "image/x-icon": ("image/x-icon", "ICO"),
    "image/avif": ("image/avif", "AVIF"),
    "image/heic": ("image/heic", "HEIC"),
    "application/pdf": ("application/pdf", "PDF"),
    "application/postscript": ("application/postscript", "Encapsulated PostScript"),
}

CF_DIB = 8
_OPEN_ATTEMPTS = 20
_OPEN_DELAY = 0.05


def copy(flavors: list[Flavor]) -> None:
    try:
        import win32clipboard as wc
    except ImportError as exc:  # pragma: no cover - only on a broken install
        raise ClipboardUnavailableError(
            "Windows clipboard support needs pywin32; reinstall with "
            "`uv tool install --force copy-graphics`"
        ) from exc

    _open(wc)
    try:
        wc.EmptyClipboard()
        for flavor in flavors:
            for name in FORMAT_NAMES.get(flavor.mime, (flavor.mime,)):
                wc.SetClipboardData(wc.RegisterClipboardFormat(name), flavor.data)
            dib = _dib_from_bmp(flavor)
            if dib is not None:
                wc.SetClipboardData(CF_DIB, dib)
    except Exception as exc:
        raise ClipboardError(f"could not write to the Windows clipboard: {exc}") from exc
    finally:
        wc.CloseClipboard()


def _open(wc: object) -> None:
    """Another process can hold the clipboard open for a moment; retry briefly."""
    last_error: Exception | None = None
    for _ in range(_OPEN_ATTEMPTS):
        try:
            wc.OpenClipboard()  # type: ignore[attr-defined]
            return
        except Exception as exc:
            last_error = exc
            time.sleep(_OPEN_DELAY)
    raise ClipboardError(f"could not open the Windows clipboard: {last_error}")


def _dib_from_bmp(flavor: Flavor) -> bytes | None:
    """Turn a .bmp file into the CF_DIB payload Paint, Word and Office expect.

    A .bmp file is a 14-byte BITMAPFILEHEADER followed by the DIB itself, so
    dropping that header is all that is needed; no image decoding involved.
    """
    if flavor.mime != "image/bmp":
        return None
    data = flavor.data
    if len(data) < 18 or data[:2] != b"BM":
        return None
    header_size = int.from_bytes(data[14:18], "little")
    if header_size not in (12, 40, 52, 56, 64, 108, 124):
        return None
    return data[14:]
