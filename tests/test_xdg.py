from __future__ import annotations

import os
from typing import Final

import pytest

from platformdirs.macos import MacOS
from platformdirs.unix import Unix


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize("prop", ["site_data_dir", "site_config_dir", "site_applications_dir"])
@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="singlepath")])
def test_site_dirs_filter_relative_entries(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], prop: str, multipath: bool
) -> None:
    value: Final = os.pathsep.join(("relative", "/custom/first", "", "~/relative", " /custom/second "))
    monkeypatch.setenv("XDG_DATA_DIRS", value)
    monkeypatch.setenv("XDG_CONFIG_DIRS", value)
    suffix: Final = "applications" if prop == "site_applications_dir" else "foo"
    expected: Final = [f"/custom/{name}{os.sep}{suffix}" for name in ("first", "second")]
    assert getattr(dirs_class(appname="foo", multipath=multipath), prop) == (
        os.pathsep.join(expected) if multipath else expected[0]
    )
