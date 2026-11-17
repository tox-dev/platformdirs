"""Unix runtime directory checks."""

from __future__ import annotations

import os
import stat
import sys
import warnings
from pathlib import Path
from typing import Final, NoReturn

from .api import RuntimeDirWarning

if sys.platform == "win32":

    def geteuid() -> NoReturn:
        msg = "should only be used on Unix"
        raise RuntimeError(msg)

else:
    try:
        from os import geteuid
    except ImportError:
        from os import getuid as geteuid


def runtime_dir_problem(path: str, *, missing_ok: bool, check_mode: bool = True) -> str | None:
    # A missing path passes under missing_ok. A caller that creates or reads below it must check again.
    try:
        # A trailing / or /. makes lstat follow a final symlink, while Path drops it.
        info = os.lstat(str(Path(path)))
    except FileNotFoundError:
        return None if missing_ok else f"{path} is missing"
    except OSError as error:
        return f"{path} cannot be checked: {error.strerror}"
    mode = info.st_mode & 0o777
    checks = (
        (stat.S_ISLNK(info.st_mode), "is a symlink"),
        (not stat.S_ISDIR(info.st_mode), "is not a directory"),
        (info.st_uid != (uid := geteuid()), f"is owned by uid {info.st_uid}, not {uid}"),
        (check_mode and mode != RUNTIME_DIR_MODE, f"has mode {mode:04o}, not {RUNTIME_DIR_MODE:04o}"),
    )
    return next((f"{path} {problem}" for failed, problem in checks if failed), None)


def warn_once(message: str) -> None:
    # Each read repeats the check, so a warning per read would flood long-running programs.
    if message not in _WARNED:
        _WARNED.add(message)
        warnings.warn(message, RuntimeDirWarning, stacklevel=3)


_WARNED: Final[set[str]] = set()
RUNTIME_DIR_MODE: Final[int] = 0o700


__all__ = [
    "RUNTIME_DIR_MODE",
    "geteuid",
    "runtime_dir_problem",
    "warn_once",
]
