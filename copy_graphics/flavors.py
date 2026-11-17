"""One clipboard representation: the raw file bytes plus their MIME type."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Flavor:
    mime: str
    data: bytes
