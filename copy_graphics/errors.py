"""Errors that the CLI turns into a one-line message instead of a traceback."""


class CopyGraphicsError(Exception):
    """Base class for every expected failure."""


class UnknownFileTypeError(CopyGraphicsError):
    """The file's graphics type could not be detected."""


class ClipboardError(CopyGraphicsError):
    """The clipboard rejected or could not receive the data."""


class ClipboardUnavailableError(ClipboardError):
    """This machine has no usable clipboard mechanism."""
