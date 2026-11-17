"""Linux clipboard backend.

On Linux the clipboard is owned by a process that keeps serving the selection
after the CLI exits, and both helper tools expose exactly one target per
invocation, so only the first (best) flavor is published:

* Wayland: ``wl-copy --type MIME`` (package ``wl-clipboard``)
* X11: ``xclip -selection clipboard -t MIME -i`` (package ``xclip``)
"""

from __future__ import annotations

import os
import shutil
import subprocess

from ..errors import ClipboardError, ClipboardUnavailableError
from ..flavors import Flavor


def copy(flavors: list[Flavor]) -> None:
    flavor = flavors[0]
    wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
    x11 = bool(os.environ.get("DISPLAY"))

    if wayland and shutil.which("wl-copy"):
        _serve(["wl-copy", "--type", flavor.mime], flavor)
        return

    if x11 and shutil.which("xclip"):
        _serve(["xclip", "-selection", "clipboard", "-t", flavor.mime, "-i"], flavor)
        return

    hints = []
    if wayland:
        hints.append("Wayland needs wl-copy (install `wl-clipboard`)")
    if x11:
        hints.append("X11 needs xclip (install `xclip`)")
    if not wayland and not x11:
        hints.append("neither WAYLAND_DISPLAY nor DISPLAY is set, so there is no session to paste into")
    raise ClipboardUnavailableError("; ".join(hints))


def _serve(argv: list[str], flavor: Flavor) -> None:
    try:
        completed = subprocess.run(
            argv,
            input=flavor.data,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise ClipboardUnavailableError(f"could not run {argv[0]}: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        message = f"{argv[0]} exited with status {completed.returncode}"
        raise ClipboardError(f"{message}: {detail}" if detail else message)
