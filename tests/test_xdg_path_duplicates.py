from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from platformdirs.macos import MacOS
from platformdirs.unix import Unix

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skipif(sys.platform == "win32", reason="XDG paths use POSIX absolute paths")
@pytest.mark.parametrize("dirs_class", [Unix, MacOS])
@pytest.mark.parametrize("method", ["iter_config_paths", "iter_data_paths", "find_config_files", "find_data_files"])
@pytest.mark.parametrize("suffix", ["", "/", "/."])
def test_equivalent_xdg_paths_appear_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    dirs_class: type[Unix | MacOS],
    method: str,
    suffix: str,
) -> None:
    kind = method.split("_")[1]
    monkeypatch.setenv(f"XDG_{kind.upper()}_HOME", str(tmp_path))
    monkeypatch.setenv(f"XDG_{kind.upper()}_DIRS", f"{tmp_path}{suffix}")
    dirs = dirs_class()

    if method.startswith("find_"):
        expected = tmp_path / "app.toml"
        expected.touch()
        actual = getattr(dirs, method)("app.toml")
    else:
        expected = tmp_path
        actual = list(getattr(dirs, method)())

    assert actual == [expected]
