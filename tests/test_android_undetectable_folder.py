from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from platformdirs.android import Android

if TYPE_CHECKING:
    from collections.abc import Iterator

_PROP_FAMILY = [
    "user_data_dir",
    "site_data_dir",
    "user_config_dir",
    "site_config_dir",
    "user_cache_dir",
    "site_cache_dir",
    "user_state_dir",
    "site_state_dir",
    "user_log_dir",
    "site_log_dir",
    "user_runtime_dir",
    "site_runtime_dir",
    "user_bin_dir",
    "site_bin_dir",
    "user_preference_dir",
    "user_applications_dir",
    "site_applications_dir",
]


@pytest.fixture
def undetectable_android_folder(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make the real _android_folder detection return None, as documented, when the base folder cannot be found."""
    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    # A None entry in sys.modules makes ``import android``/``import jnius`` raise ImportError.
    monkeypatch.setitem(sys.modules, "android", None)
    monkeypatch.setitem(sys.modules, "jnius", None)
    # No recognizable /data/.../files entry on sys.path either.
    monkeypatch.setattr(sys, "path", [])

    _android_folder.cache_clear()
    yield
    _android_folder.cache_clear()  # do not leak the cached None into other tests


@pytest.mark.usefixtures("undetectable_android_folder")
def test_android_folder_is_none_when_undetectable() -> None:
    """Sanity check through the real detection code path."""
    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    assert _android_folder() is None  # documented: base folder not found


@pytest.mark.usefixtures("undetectable_android_folder")
@pytest.mark.parametrize("prop", _PROP_FAMILY)
def test_dirs_do_not_raise_when_android_folder_undetectable(prop: str) -> None:
    """The properties must raise a descriptive RuntimeError instead of an opaque TypeError when undetectable."""
    android = Android(appname="foo")

    # Before the fix this raised TypeError: expected str, bytes or os.PathLike object, not NoneType.
    with pytest.raises(RuntimeError, match="Cannot determine the base Android app folder"):
        getattr(android, prop)
