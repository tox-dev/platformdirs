"""Test helpers that keep platformdirs away from the real user and system directories."""

from __future__ import annotations

__lazy_modules__ = [
    "pathlib",
    f"{__spec__.parent}.api",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

import platformdirs

from .api import PlatformDirsABC

TYPE_CHECKING = False
if TYPE_CHECKING:
    import os
    from collections.abc import Generator
    from contextlib import AbstractContextManager
    from typing import Final


@contextmanager
def isolated_dirs(root: str | os.PathLike[str]) -> Generator[Path, None, None]:
    """Resolve every directory of :data:`~platformdirs.PlatformDirs` under ``root`` while the context is active.

    Each kind maps to ``<root>/<kind>``, where ``kind`` is the property name without ``_dir``, such as ``user_config``.
    The data, config, cache, state, log, runtime and preference kinds append ``appname`` and ``version``, so
    ``PlatformDirs("app", version="1.0").user_config_path`` becomes ``<root>/user_config/app/1.0``. Every thread of the
    current process sees the change, and subprocesses do not. When contexts overlap, the most recently entered
    active context determines the root.

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
    with _LOCK:
        if (state := _ISOLATED.get(cls)) is None:
            state = _Isolation(original={name: vars(cls)[name] for name in patches if name in vars(cls)})
            _ISOLATED[cls] = state
        state.active[key] = patches
        _set_attributes(cls, patches)
    try:
        yield
    finally:
        with _LOCK:
            was_latest = key == next(reversed(state.active))
            del state.active[key]
            if not state.active:
                _set_attributes(cls, state.original)
                for name in patches.keys() - state.original.keys():
                    delattr(cls, name)
                del _ISOLATED[cls]
            elif was_latest:
                _set_attributes(cls, state.active[next(reversed(state.active))])


@dataclass(frozen=True, kw_only=True, slots=True)
class _Isolation:
    original: dict[str, property]
    active: dict[int, dict[str, property]] = field(default_factory=dict)


def _set_attributes(cls: type[PlatformDirsABC], attributes: dict[str, property]) -> None:
    for name, value in attributes.items():
        setattr(cls, name, value)


_LOCK: Final[AbstractContextManager[bool]] = Lock()
_ISOLATED: Final[dict[type[PlatformDirsABC], _Isolation]] = {}


__all__ = [
    "isolated_dirs",
]
