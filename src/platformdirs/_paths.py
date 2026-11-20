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


def create_checked_directories(path: Path, *, private: bool, root_only: bool = False, strict: bool = False) -> None:
    absolute = path.absolute()
    existing = absolute
    while not existing.is_dir():
        existing = existing.parent
    uid = os.geteuid() if hasattr(os, "geteuid") else os.getuid()
    allow_group_write = uid != 0 and not (root_only or strict)
    if problem := directory_problem(existing, root_only=root_only, allow_group_write=allow_group_write):
        raise PermissionError(problem)
    if existing == absolute:
        return
    if private and not root_only and not existing.stat().st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        make_directories(path, private=private)
        return
    owners = {0} if root_only else {0, uid}
    mode = 0o755 if root_only else 0o777
    writable = stat.S_IWOTH if allow_group_write else stat.S_IWGRP | stat.S_IWOTH
    for component in absolute.relative_to(existing).parts:
        existing /= component
        existing.mkdir(mode=0o700 if private else mode, exist_ok=True)
        info = os.lstat(existing)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid not in owners:
            msg = f"{existing} is not a trusted directory"
            raise PermissionError(msg)
        if info.st_mode & writable and not info.st_mode & stat.S_ISVTX:
            msg = f"{existing}, writable by another user"
            raise PermissionError(msg)


def directory_problem(
    path: Path, *, missing_ok: bool = False, root_only: bool = False, allow_group_write: bool = False
) -> str | None:
    if os.name == "nt":
        return None
    try:
        _verify_path(path.absolute(), root_only=root_only, allow_group_write=allow_group_write)
    except FileNotFoundError as error:
        return None if missing_ok else f"{error.filename} is missing"
    except PermissionError as error:
        return str(error)
    except OSError as error:
        return f"{error.filename} cannot be checked: {error.strerror}"
    return None


def _verify_path(path: Path, *, root_only: bool, allow_group_write: bool) -> None:
    directory = Path(path.anchor)
    pending = deque(path.parts[1:])
    owners = {0}
    if not root_only:
        owners.add(os.geteuid() if hasattr(os, "geteuid") else os.getuid())
    writable = stat.S_IWOTH if allow_group_write else stat.S_IWGRP | stat.S_IWOTH
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
        if info.st_mode & writable and not info.st_mode & stat.S_ISVTX:
            msg = f"{entry}, writable by another user"
            raise PermissionError(msg)
        directory = entry


def make_directories(path: Path, *, private: bool) -> None:
    # Private creation applies the XDG mode to every new directory, including intermediate parents.
    mode = 0o700 if private else 0o777
    missing = []
    while True:
        try:
            path.mkdir(mode=mode, exist_ok=True)
        except FileNotFoundError:
            parent = path.parent
            if parent == path:  # A missing drive or share has no parent to create.
                raise
            missing.append(path)
            path = parent
        else:
            break
    for directory in reversed(missing):
        directory.mkdir(mode=mode, exist_ok=True)


__all__ = [
    "create_checked_directories",
    "directory_problem",
    "make_directories",
]
