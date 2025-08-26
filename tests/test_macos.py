from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from platformdirs.macos import MacOS

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _fix_os_pathsep(mocker: MockerFixture) -> None:
    """If we're not running on macOS, set `os.pathsep` to what it should be on macOS."""
    if sys.platform != "darwin":  # pragma: darwin no cover
        mocker.patch("os.pathsep", ":")
        mocker.patch("os.path.pathsep", ":")


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
def test_macos(mocker: MockerFixture, params: dict[str, Any], func: str) -> None:
    # Make sure we are not in Homebrew
    py_version = sys.version_info
    builtin_py_prefix = (
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework"
        f"/Versions/{py_version.major}.{py_version.minor}"
    )
    mocker.patch("sys.prefix", builtin_py_prefix)

    result = getattr(MacOS(**params), func)

    home = str(Path("~").expanduser())
    suffix_elements = tuple(params[i] for i in ("appname", "version") if i in params)
    suffix = os.sep.join(("", *suffix_elements)) if suffix_elements else ""  # noqa: PTH118

    expected_map = {
        "user_data_dir": f"{home}/Library/Application Support{suffix}",
        "site_data_dir": f"/Library/Application Support{suffix}",
        "user_config_dir": f"{home}/Library/Application Support{suffix}",
        "site_config_dir": f"/Library/Application Support{suffix}",
        "user_cache_dir": f"{home}/Library/Caches{suffix}",
        "site_cache_dir": f"/Library/Caches{suffix}",
        "user_state_dir": f"{home}/Library/Application Support{suffix}",
        "user_log_dir": f"{home}/Library/Logs{suffix}",
        "user_documents_dir": f"{home}/Documents",
        "user_downloads_dir": f"{home}/Downloads",
        "user_pictures_dir": f"{home}/Pictures",
        "user_videos_dir": f"{home}/Movies",
        "user_music_dir": f"{home}/Music",
        "user_desktop_dir": f"{home}/Desktop",
        "user_runtime_dir": f"{home}/Library/Caches/TemporaryItems{suffix}",
        "site_runtime_dir": f"{home}/Library/Caches/TemporaryItems{suffix}",
    }
    expected = expected_map[func]

    assert result == expected


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
@pytest.mark.parametrize(
    "site_func",
    [
        "site_data_dir",
        "site_config_dir",
        "site_cache_dir",
        "site_runtime_dir",
        "site_cache_path",
        "site_data_path",
    ],
)
@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="singlepath")])
def test_macos_homebrew(mocker: MockerFixture, params: dict[str, Any], multipath: bool, site_func: str) -> None:
    test_data = [
        {
            "sys_prefix": "/opt/homebrew/opt/python@3.13/Frameworks/Python.framework/Versions/3.13",
            "homebrew_prefix": "/opt/homebrew",
        },
        {
            "sys_prefix": "/usr/local/opt/python@3.13/Frameworks/Python.framework/Versions/3.13",
            "homebrew_prefix": "/usr/local",
        },
        {
            "sys_prefix": "/myown/arbitrary/prefix/opt/python@3.13/Frameworks/Python.framework/Versions/3.13",
            "homebrew_prefix": "/myown/arbitrary/prefix",
        },
    ]
    for prefix in test_data:
        mocker.patch("sys.prefix", prefix["sys_prefix"])

        result = getattr(MacOS(multipath=multipath, **params), site_func)

        home = str(Path("~").expanduser())
        suffix_elements = tuple(params[i] for i in ("appname", "version") if i in params)
        suffix = os.sep.join(("", *suffix_elements)) if suffix_elements else ""  # noqa: PTH118

        expected_path_map = {
            "site_cache_path": Path(f"{prefix['homebrew_prefix']}/var/cache{suffix}"),
            "site_data_path": Path(f"{prefix['homebrew_prefix']}/share{suffix}"),
        }
        expected_map = {
            "site_data_dir": f"{prefix['homebrew_prefix']}/share{suffix}",
            "site_config_dir": f"{prefix['homebrew_prefix']}/share{suffix}",
            "site_cache_dir": f"{prefix['homebrew_prefix']}/var/cache{suffix}",
            "site_runtime_dir": f"{home}/Library/Caches/TemporaryItems{suffix}",
        }
        if multipath:
            expected_map["site_data_dir"] += f":/Library/Application Support{suffix}"
            expected_map["site_config_dir"] += f":/Library/Application Support{suffix}"
            expected_map["site_cache_dir"] += f":/Library/Caches{suffix}"
        expected = expected_path_map[site_func] if site_func.endswith("_path") else expected_map[site_func]

        assert result == expected
