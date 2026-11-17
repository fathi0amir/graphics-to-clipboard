"""macOS clipboard backend using NSPasteboard through pyobjc.

An NSPasteboard holds one or more types per item. The raw MIME string is a
valid dynamic type and is what Inkscape, GIMP and browsers ask for, while
native apps ask for the ``public.*`` UTIs, so both are written for each item.
"""

from __future__ import annotations

from ..errors import ClipboardError, ClipboardUnavailableError
from ..flavors import Flavor

PASTEBOARD_TYPES = {
    "image/svg+xml": ("image/svg+xml", "public.svg-image"),
    "image/png": ("public.png", "image/png"),
    "image/jpeg": ("public.jpeg", "image/jpeg"),
    "image/gif": ("com.compuserve.gif", "image/gif"),
    "image/bmp": ("com.microsoft.bmp", "image/bmp"),
    "image/tiff": ("public.tiff", "image/tiff"),
    "image/webp": ("org.webmproject.webp", "image/webp"),
    "image/x-icon": ("com.microsoft.ico", "image/x-icon"),
    "image/heic": ("public.heic", "image/heic"),
    "application/pdf": ("com.adobe.pdf", "application/pdf"),
    "application/postscript": ("com.adobe.eps", "application/postscript"),
}


def copy(flavors: list[Flavor]) -> None:
    try:
        from AppKit import NSPasteboard
        from Foundation import NSData
    except ImportError as exc:  # pragma: no cover - only on a broken install
        raise ClipboardUnavailableError(
            "macOS clipboard support needs pyobjc-framework-Cocoa; reinstall with "
            "`uv tool install --force copy-graphics`"
        ) from exc

    pasteboard = NSPasteboard.generalPasteboard()
    pasteboard.clearContents()

    stored = 0
    for flavor in flavors:
        payload = NSData.dataWithBytes_length_(flavor.data, len(flavor.data))
        for name in PASTEBOARD_TYPES.get(flavor.mime, (flavor.mime,)):
            if pasteboard.setData_forType_(payload, name):
                stored += 1

    if not stored:
        raise ClipboardError("the macOS pasteboard rejected every clipboard type")
