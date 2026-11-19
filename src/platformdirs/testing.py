"""Test helpers that keep platformdirs away from the real user and system directories."""

from __future__ import annotations

__lazy_modules__ = [
    "pathlib",
    "threading",
    f"{__spec__.parent}.api",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

import platformdirs

from .api import PlatformDirsABC

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Final


@contextmanager
def isolated_dirs(root: str | os.PathLike[str]) -> Generator[Path, None, None]:
    """Resolve every directory of :data:`~platformdirs.PlatformDirs` under ``root`` while the context is active.

    Each kind maps to ``<root>/<kind>``, where ``kind`` is the property name without ``_dir``, such as ``user_config``.
    The data, config, cache, state, log, runtime and preference kinds append ``appname`` and ``version``, so
    ``PlatformDirs("app", version="1.0").user_config_path`` becomes ``<root>/user_config/app/1.0``. Every thread of the
    current process sees the change. A child process uses the original paths once it starts or returns from ``fork()``.
    When contexts overlap, the most recently entered active context determines the root.

    On Unix, ``use_site_for_root`` is ignored inside the context so user and site directories keep separate kinds. A
    relative ``root`` is made absolute on entry, so changing the working directory does not move the isolation root.

    :param root: directory that holds the redirected directories

    :yields: the absolute isolation root as a :class:`~pathlib.Path`

    """
    app_kinds: Final[frozenset[str]] = frozenset({
        "user_data",
        "site_data",
        "user_config",
        "site_config",
        "user_cache",
        "site_cache",
        "user_state",
        "site_state",
        "user_log",
        "site_log",
        "user_runtime",
        "site_runtime",
        "user_preference",
    })

    base = Path(root).absolute()
    patches = {
        name: _redirect(
            base / (kind := name.removesuffix("_dir")), app=kind in app_kinds, private=kind.startswith("user_")
        )
        for name in PlatformDirsABC.__abstractmethods__
    }
    # Base site lists follow the redirected dirs, and disabling root redirection keeps user and site kinds separate.
    patches |= {
        name: value
        for name, value in vars(PlatformDirsABC).items()
        if name == "_use_site" or (name.startswith("_site_") and name.endswith("_dirs"))
    }
    with _patch_class(platformdirs.PlatformDirs, patches):
        yield base


def _redirect(path: Path, *, app: bool, private: bool) -> property:
    def resolve(self: PlatformDirsABC) -> str:
        return self._append_app_name_and_version(str(path), private=private) if app else str(path)

    return property(resolve)


@contextmanager
def _patch_class(cls: type[PlatformDirsABC], patches: dict[str, property]) -> Generator[None, None, None]:
    key = id(patches)
    try:
        with _SCOPES.lock:
            if (state := _SCOPES.classes.get(cls)) is None:
                state = _Isolation(
                    original={name: vars(cls)[name] for name in patches if name in vars(cls)},
                    names=frozenset(patches),
                    active={},
                )
            try:
                _SCOPES.classes[cls] = state
                _set_attributes(cls, patches)
                state.active[key] = patches
            finally:
                if key not in state.active:
                    _restore_class(cls, state)
                    if not state.active:
                        _SCOPES.classes.pop(cls, None)
        yield
    finally:
        with _SCOPES.lock:
            if (state := _SCOPES.classes.get(cls)) is not None and key in state.active:
                _remove_patch(cls, state, key)


@dataclass(frozen=True, kw_only=True, slots=True)
class _Isolation:
    original: dict[str, property]
    names: frozenset[str]
    active: dict[int, dict[str, property]]


def _restore_class(cls: type[PlatformDirsABC], state: _Isolation) -> None:
    if state.active:
        _set_attributes(cls, state.active[next(reversed(state.active))])
    else:
        _restore_original(cls, state)


def _remove_patch(cls: type[PlatformDirsABC], state: _Isolation, key: int) -> None:
    was_latest = key == next(reversed(state.active))
    del state.active[key]
    if was_latest:
        _restore_class(cls, state)
    if not state.active:
        del _SCOPES.classes[cls]


def _set_attributes(cls: type[PlatformDirsABC], attributes: dict[str, property]) -> None:
    for name, value in attributes.items():
        setattr(cls, name, value)


def _restore_original(cls: type[PlatformDirsABC], state: _Isolation) -> None:
    _set_attributes(cls, state.original)
    for name in (state.names - state.original.keys()) & vars(cls).keys():
        delattr(cls, name)


class _Scopes:
    def __init__(self) -> None:
        self.classes: dict[type[PlatformDirsABC], _Isolation] = {}
        self.lock = Lock()

    def after_fork(self) -> None:
        self.lock = Lock()
        for cls, state in self.classes.items():
            _restore_original(cls, state)
        self.classes.clear()


_SCOPES: Final[_Scopes] = _Scopes()

if hasattr(os, "register_at_fork"):
    # Fork can copy a held lock and partially installed class attributes from another thread.
    os.register_at_fork(after_in_child=_SCOPES.after_fork)


__all__ = [
    "isolated_dirs",
]
