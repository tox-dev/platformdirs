"""Validate POSIX directory paths before using them."""

from __future__ import annotations

__lazy_modules__ = [
    "collections",
    "pathlib",
]

import os
import stat
from collections import deque
from pathlib import Path


def site_directory_problem(path: Path) -> str | None:
    try:
        _verify_path(path.absolute())
    except FileNotFoundError as error:
        return f"{error.filename} is missing"
    except PermissionError as error:
        return str(error)
    except OSError as error:
        return f"{error.filename} cannot be checked: {error.strerror}"
    return None


def _verify_path(path: Path) -> None:
    directory = Path(path.anchor)
    pending = deque(path.parts[1:])
    while pending:
        entry = directory / pending.popleft()
        info = os.lstat(entry)
        if info.st_uid != 0:
            msg = f"{entry}, owned by uid {info.st_uid}"
            raise PermissionError(msg)
        if stat.S_ISLNK(info.st_mode):
            target = entry.readlink()
            if target.is_absolute():
                directory = Path(target.anchor)
            pending.extendleft(reversed(target.parts[bool(target.anchor) :]))
            continue
        if not stat.S_ISDIR(info.st_mode):
            msg = f"{entry}, which is not a directory"
            raise PermissionError(msg)
        if info.st_mode & (stat.S_IWGRP | stat.S_IWOTH) and not info.st_mode & stat.S_ISVTX:
            msg = f"{entry}, writable by another user"
            raise PermissionError(msg)
        directory = entry


__all__ = [
    "site_directory_problem",
]
