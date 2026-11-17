"""Platform clipboard backends. Each module exposes ``copy(flavors)``."""

from __future__ import annotations

import sys
from types import ModuleType

from ..errors import ClipboardUnavailableError


def get_backend() -> ModuleType:
    if sys.platform == "win32":
        from . import windows

        return windows
    if sys.platform == "darwin":
        from . import macos

        return macos
    if sys.platform.startswith("linux"):
        from . import linux

        return linux
    raise ClipboardUnavailableError(f"no clipboard support for platform {sys.platform!r}")
