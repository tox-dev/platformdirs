"""Validate POSIX directory paths before using them."""

from __future__ import annotations

__lazy_modules__ = [
    "collections",
    "pathlib",
]

import os
import stat
import sys
from collections import deque
from pathlib import Path


def directory_problem(path: Path, *, missing_ok: bool = False, root_only: bool = False) -> str | None:
    if sys.platform == "win32":
        return None
    try:
        _verify_path(path.absolute(), root_only=root_only)
    except FileNotFoundError as error:
        return None if missing_ok else f"{error.filename} is missing"
    except PermissionError as error:
        return str(error)
    except OSError as error:
        return f"{error.filename} cannot be checked: {error.strerror}"
    return None


def _verify_path(path: Path, *, root_only: bool) -> None:
    directory = Path(path.anchor)
    pending = deque(path.parts[1:])
    owners = {0}
    if not root_only:
        owners.add(getattr(os, "geteuid")())  # ruff:ignore[get-attr-with-constant]  # absent from Windows stubs
    links = 0
    max_links = 40
    while pending:
        entry = directory / pending.popleft()
        info = os.lstat(entry)
        if info.st_uid not in owners:
            msg = f"{entry}, owned by uid {info.st_uid}"
            raise PermissionError(msg)
        if stat.S_ISLNK(info.st_mode):
            links += 1
            if links > max_links:
                msg = f"{entry}, which has too many symbolic links"
                raise PermissionError(msg)
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
    "directory_problem",
]
