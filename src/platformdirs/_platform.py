"""Select the directory class for the running platform."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import PlatformDirsABC

if sys.platform == "win32":
    from .windows import Windows as _Result
elif sys.platform == "darwin":
    from .macos import MacOS as _Result
elif sys.platform == "ios":
    from .ios import IOS as _Result  # ruff:ignore[constant-imported-as-non-constant]  # a class, PEP 8 acronym
else:
    from .unix import Unix as _Result


def _set_platform_dir_class() -> type[PlatformDirsABC]:
    # Every Android build of CPython has sys.getandroidapilevel, even in a process started with a cleared environment.
    if hasattr(sys, "getandroidapilevel") or (
        os.getenv("ANDROID_DATA") == "/data" and os.getenv("ANDROID_ROOT") == "/system"
    ):
        if os.getenv("SHELL") or os.getenv("PREFIX"):
            return _Result

        from .android import _android_folder  # ruff:ignore[import-outside-top-level]  # the module exists only on this platform

        if _android_folder() is not None:
            from .android import Android  # ruff:ignore[import-outside-top-level]  # the module exists only on this platform

            return Android  # return to avoid redefinition of a result

    return _Result


if TYPE_CHECKING:
    # Work around mypy issue: https://github.com/python/mypy/issues/10962
    #: Currently active platform
    PlatformDirs = _Result
else:
    PlatformDirs = _set_platform_dir_class()  #: Currently active platform
AppDirs = PlatformDirs  #: Backwards compatibility with appdirs


__all__ = [
    "AppDirs",
    "PlatformDirs",
]
