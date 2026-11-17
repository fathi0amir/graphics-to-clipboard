"""Work out the MIME type of a graphics file from its bytes, not just its name.

The OS registries disagree about several graphics types (Windows reports
``image/svg+xml`` for ``.svg`` only on some installs, macOS can say
``application/postscript`` for ``.eps``), so known graphics extensions are
mapped here and the file's own leading bytes win over its name.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from .errors import UnknownFileTypeError

# Extensions of the formats people actually paste between design tools.
SUFFIXES = {
    ".svg": "image/svg+xml",
    ".svgz": "image/svg+xml",
    ".png": "image/png",
    ".apng": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".jpe": "image/jpeg",
    ".jfif": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".dib": "image/bmp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".avif": "image/avif",
    ".heic": "image/heic",
    ".pdf": "application/pdf",
    ".ps": "application/postscript",
    ".eps": "application/postscript",
    ".ai": "application/postscript",
}

_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"II*\x00", "image/tiff"),
    (b"MM\x00*", "image/tiff"),
    (b"%PDF-", "application/pdf"),
    (b"%!PS", "application/postscript"),
    (b"\x00\x00\x01\x00", "image/x-icon"),
)

# Non-image types design tools still paste as vector artwork.
_DOCUMENT_TYPES = {"application/pdf", "application/postscript"}


def detect_mime(path: Path, data: bytes) -> str:
    """Return the MIME type to publish on the clipboard for ``data``."""
    sniffed = _from_signature(data)
    if sniffed:
        return sniffed
    if _looks_like_svg(data):
        return "image/svg+xml"
    suffix = path.suffix.lower()
    mime = SUFFIXES.get(suffix)
    if mime is None:
        mime, _ = mimetypes.guess_type(path.name)

    # Refusing generic types keeps a renamed text file or archive off the
    # clipboard, where nothing could paste it anyway.
    if mime and _is_graphic(mime):
        return mime

    if mime:
        found = f"{path.name!r} looks like {mime}, not a graphics format"
    else:
        found = f"cannot tell what kind of graphics {path.name!r} contains"
    raise UnknownFileTypeError(f"{found}; pass --mime TYPE if it really is graphics")


def _is_graphic(mime: str) -> bool:
    return mime.startswith("image/") or mime in _DOCUMENT_TYPES


def _from_signature(data: bytes) -> str | None:
    head = data[:16]
    for prefix, mime in _SIGNATURES:
        if head.startswith(prefix):
            return mime
    if head[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[4:12] == b"ftypavif":
        return "image/avif"
    if data[4:12] == b"ftypheic":
        return "image/heic"
    # "BM" alone is too weak, but a bitmap file header keeps four zero bytes
    # in its reserved field, right after the 32-bit file size.
    if data[:2] == b"BM" and len(data) >= 18 and data[6:10] == b"\x00\x00\x00\x00":
        return "image/bmp"
    return None


def _looks_like_svg(data: bytes) -> bool:
    head = data[:4096]
    if not head.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
        return False
    return b"<svg" in head.lower()
