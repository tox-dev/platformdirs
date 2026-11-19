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


def directory_problem(path: Path, *, missing_ok: bool, require_owner: bool = False) -> str | None:
    if sys.platform == "win32":
        return None
    try:
        _verify_path(path.absolute(), require_owner=require_owner)
    except FileNotFoundError as error:
        return None if missing_ok else f"{error.filename} is missing"
    except PermissionError as error:
        return str(error)
    except OSError as error:
        return f"{error.filename} cannot be checked: {error.strerror}"
    return None


def _verify_path(path: Path, *, require_owner: bool) -> None:
    directory = Path(path.anchor)
    pending = deque(path.parts[1:])
    owners = {0, getattr(os, "geteuid", os.getuid)()}
    shared = False
    links = 0
    max_links = 40
    while pending:
        entry = directory / pending.popleft()
        info = entry.lstat()
        if (shared or require_owner) and info.st_uid not in owners:
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
                shared = False
            pending.extendleft(reversed(target.parts[bool(target.anchor) :]))
            continue
        shared = _check_directory(entry, info, owners)
        directory = entry


def _check_directory(path: Path, info: os.stat_result, owners: set[int]) -> bool:
    if not stat.S_ISDIR(info.st_mode):
        msg = f"{path}, which is not a directory"
        raise PermissionError(msg)
    shared = bool(info.st_mode & stat.S_IWOTH)
    if shared and (not info.st_mode & stat.S_ISVTX or info.st_uid not in owners):
        msg = f"{path}, writable by every user"
        raise PermissionError(msg)
    return shared


__all__ = [
    "directory_problem",
]
