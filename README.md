# copy-graphics

Put a graphics file on the clipboard **as a graphic**, with its real MIME type,
so the paste target gets the original file bytes instead of a bitmap snapshot or
a file path. Pasting into Inkscape keeps the SVG editable, and PNG/JPEG/BMP
arrive at full resolution.

```console
$ copy-graphics logo.svg
Copied logo.svg as image/svg+xml (8.4 KiB) to the clipboard.
```

## Install

From GitHub:

```console
uv tool install --from git+https://github.com/<you>/copy-graphics copy-graphics
```

From a local checkout:

```console
uv tool install --from . copy-graphics      # or: uv tool install --editable .
```

Run it without installing: `uv run copy-graphics logo.svg`.

## Usage

```console
copy-graphics FILE            # detect the type from the bytes, then the extension
copy-graphics --mime image/svg+xml drawing.dat
copy-graphics --quiet FILE    # no output, useful in scripts
```

| File | MIME type published |
| --- | --- |
| `.svg`, `.svgz` | `image/svg+xml` |
| `.png` | `image/png` |
| `.jpg`, `.jpeg`, `.jfif` | `image/jpeg` |
| `.gif` | `image/gif` |
| `.bmp`, `.dib` | `image/bmp` |
| `.tif`, `.tiff` | `image/tiff` |
| `.webp` | `image/webp` |
| `.ico` | `image/x-icon` |
| `.avif`, `.heic` | `image/avif`, `image/heic` |
| `.pdf`, `.eps`, `.ps` | `application/pdf`, `application/postscript` |

Content sniffing comes first (PNG/JPEG/GIF/BMP/TIFF/WebP/AVIF/PDF/EPS magic
bytes and an `<svg` scan), then the extension, so a misnamed file still lands
on the clipboard with the right type. A file that detects as something other
than an `image/*` or PDF/postscript type is refused rather than copied, and
`--mime` overrides both the detection and that check.

## Use it from Python

The package is an ordinary importable library, so a script or notebook can call
`copy_graphics.copy` directly:

```python
from copy_graphics import copy

copy("logo.svg")                           # returns "image/svg+xml"
copy("drawing.dat", mime="image/svg+xml")  # state the type instead of detecting it
```

When the bytes are already in memory there is no file to sniff, so name the
type:

```python
from copy_graphics import copy_bytes

copy_bytes(png_bytes, "image/png")
```

Both functions return the MIME type that went on the clipboard and raise a
`CopyGraphicsError` subclass when the file is not a graphic
(`UnknownFileTypeError`) or the platform clipboard is unusable
(`ClipboardError`, `ClipboardUnavailableError`); all of those are re-exported
from `copy_graphics`. `copy` raises `OSError` if the file cannot be read.

Install it into the environment your script runs on: `uv tool install` only
exposes the `copy-graphics` command and keeps the package in its own
environment, which your interpreter cannot import.

```console
uv add git+https://github.com/<you>/copy-graphics      # or: %pip install git+<url>
```

## How each platform is served

* **Windows** – `win32clipboard`. The MIME type is registered as a clipboard
  format under every name design software looks for, e.g. `image/svg+xml`,
  `image/x-inkscape-svg` and `SVG`, or `PNG` for raster images. `.bmp` files
  also get `CF_DIB` (the file's 14-byte `BITMAPFILEHEADER` removed) so Office,
  Paint and similar apps can paste them.
* **macOS** – `NSPasteboard` via pyobjc, writing the raw MIME type and the
  matching Apple UTI (`public.svg-image`, `public.png`, ...) on the same item.
* **Linux** – `wl-copy --type MIME` on Wayland, `xclip -selection clipboard -t MIME`
  on X11. Both tools serve one clipboard target at a time, so only the detected
  type is published. Install `wl-clipboard` or `xclip` first; the CLI tells you
  which one is missing.

Linux needs a graphical session (`WAYLAND_DISPLAY` or `DISPLAY`) and puts the
data on the *clipboard* selection, not primary/middle-click.

## Requirements

Python 3.10+. `uv tool install` pulls `pywin32` on Windows and
`pyobjc-framework-Cocoa` on macOS automatically; Linux needs no Python packages
beyond the standard library.
