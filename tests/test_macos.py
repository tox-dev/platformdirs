from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from platformdirs.macos import MacOS

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_XDG_ENV_VARS = (
    "XDG_DATA_HOME",
    "XDG_DATA_DIRS",
    "XDG_CONFIG_HOME",
    "XDG_CONFIG_DIRS",
    "XDG_CACHE_HOME",
    "XDG_STATE_HOME",
    "XDG_RUNTIME_DIR",
    "XDG_DOCUMENTS_DIR",
    "XDG_DOWNLOAD_DIR",
    "XDG_PICTURES_DIR",
    "XDG_VIDEOS_DIR",
    "XDG_MUSIC_DIR",
    "XDG_DESKTOP_DIR",
)


@pytest.fixture(autouse=True)
def _fix_os_pathsep(mocker: MockerFixture) -> None:
    """If we're not running on macOS, set `os.pathsep` to what it should be on macOS."""
    if sys.platform != "darwin":  # pragma: darwin no cover
        mocker.patch("os.pathsep", ":")
        mocker.patch("os.path.pathsep", ":")


@pytest.fixture
def _clear_xdg_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _XDG_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
@pytest.mark.usefixtures("_clear_xdg_env")
def test_macos(mocker: MockerFixture, params: dict[str, Any], func: str) -> None:
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
        "site_state_dir": f"/Library/Application Support{suffix}",
        "user_log_dir": f"{home}/Library/Logs{suffix}",
        "site_log_dir": f"/Library/Logs{suffix}",
        "user_documents_dir": f"{home}/Documents",
        "user_downloads_dir": f"{home}/Downloads",
        "user_pictures_dir": f"{home}/Pictures",
        "user_videos_dir": f"{home}/Movies",
        "user_music_dir": f"{home}/Music",
        "user_desktop_dir": f"{home}/Desktop",
        "user_bin_dir": f"{home}/.local/bin",
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
@pytest.mark.usefixtures("_clear_xdg_env")
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


@pytest.mark.parametrize(
    ("env_var", "prop", "xdg_path"),
    [
        pytest.param("XDG_DATA_HOME", "user_data_dir", "/custom/data", id="user_data_dir"),
        pytest.param("XDG_CONFIG_HOME", "user_config_dir", "/custom/config", id="user_config_dir"),
        pytest.param("XDG_CACHE_HOME", "user_cache_dir", "/custom/cache", id="user_cache_dir"),
        pytest.param("XDG_STATE_HOME", "user_state_dir", "/custom/state", id="user_state_dir"),
        pytest.param("XDG_RUNTIME_DIR", "user_runtime_dir", "/custom/runtime", id="user_runtime_dir"),
        pytest.param("XDG_RUNTIME_DIR", "site_runtime_dir", "/custom/runtime", id="site_runtime_dir"),
    ],
)
@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
def test_macos_xdg_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    env_var: str,
    prop: str,
    xdg_path: str,
    params: dict[str, Any],
) -> None:
    monkeypatch.setenv(env_var, xdg_path)
    result = getattr(MacOS(**params), prop)
    suffix_elements = tuple(params[i] for i in ("appname", "version") if i in params)
    suffix = os.sep.join(("", *suffix_elements)) if suffix_elements else ""  # noqa: PTH118
    assert result == f"{xdg_path}{suffix}"


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        pytest.param("XDG_DATA_DIRS", "site_data_dir", id="site_data_dir"),
        pytest.param("XDG_CONFIG_DIRS", "site_config_dir", id="site_config_dir"),
    ],
)
@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="singlepath")])
def test_macos_xdg_site_dirs(
    monkeypatch: pytest.MonkeyPatch,
    env_var: str,
    prop: str,
    multipath: bool,
) -> None:
    monkeypatch.setenv(env_var, "/custom/first:/custom/second")
    result = getattr(MacOS(multipath=multipath), prop)
    if multipath:
        assert result == "/custom/first:/custom/second"
    else:
        assert result == "/custom/first"


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", id="user_desktop_dir"),
    ],
)
def test_macos_xdg_media_dirs(monkeypatch: pytest.MonkeyPatch, env_var: str, prop: str) -> None:
    monkeypatch.setenv(env_var, "/custom/media")
    assert getattr(MacOS(), prop) == "/custom/media"


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        pytest.param("XDG_DATA_HOME", "user_data_dir", id="user_data_dir"),
        pytest.param("XDG_CONFIG_HOME", "user_config_dir", id="user_config_dir"),
        pytest.param("XDG_CACHE_HOME", "user_cache_dir", id="user_cache_dir"),
        pytest.param("XDG_STATE_HOME", "user_state_dir", id="user_state_dir"),
        pytest.param("XDG_RUNTIME_DIR", "user_runtime_dir", id="user_runtime_dir"),
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", id="user_desktop_dir"),
    ],
)
@pytest.mark.usefixtures("_clear_xdg_env")
def test_macos_xdg_empty_falls_back(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, env_var: str, prop: str
) -> None:
    py_version = sys.version_info
    builtin_py_prefix = (
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework"
        f"/Versions/{py_version.major}.{py_version.minor}"
    )
    mocker.patch("sys.prefix", builtin_py_prefix)
    monkeypatch.setenv(env_var, "")
    home = str(Path("~").expanduser())
    expected_map = {
        "user_data_dir": f"{home}/Library/Application Support",
        "user_config_dir": f"{home}/Library/Application Support",
        "user_cache_dir": f"{home}/Library/Caches",
        "user_state_dir": f"{home}/Library/Application Support",
        "user_runtime_dir": f"{home}/Library/Caches/TemporaryItems",
        "user_documents_dir": f"{home}/Documents",
        "user_downloads_dir": f"{home}/Downloads",
        "user_pictures_dir": f"{home}/Pictures",
        "user_videos_dir": f"{home}/Movies",
        "user_music_dir": f"{home}/Music",
        "user_desktop_dir": f"{home}/Desktop",
        "user_bin_dir": f"{home}/.local/bin",
    }
    assert getattr(MacOS(), prop) == expected_map[prop]


def test_iter_data_dirs_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", "/xdg/data")
    monkeypatch.setenv("XDG_DATA_DIRS", "/xdg/share1:/xdg/share2")
    dirs = list(MacOS().iter_data_dirs())
    assert dirs == ["/xdg/data", "/xdg/share1", "/xdg/share2"]


def test_iter_config_dirs_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/xdg/config")
    monkeypatch.setenv("XDG_CONFIG_DIRS", "/xdg/etc1:/xdg/etc2")
    dirs = list(MacOS().iter_config_dirs())
    assert dirs == ["/xdg/config", "/xdg/etc1", "/xdg/etc2"]


@pytest.mark.usefixtures("_clear_xdg_env")
def test_iter_data_dirs_homebrew(mocker: MockerFixture) -> None:
    mocker.patch("sys.prefix", "/opt/homebrew/opt/python@3.13/Frameworks/Python.framework/Versions/3.13")
    dirs = list(MacOS().iter_data_dirs())
    home = str(Path("~").expanduser())
    assert dirs == [f"{home}/Library/Application Support", "/opt/homebrew/share", "/Library/Application Support"]


@pytest.mark.usefixtures("_clear_xdg_env")
def test_iter_config_dirs_homebrew(mocker: MockerFixture) -> None:
    mocker.patch("sys.prefix", "/opt/homebrew/opt/python@3.13/Frameworks/Python.framework/Versions/3.13")
    dirs = list(MacOS().iter_config_dirs())
    home = str(Path("~").expanduser())
    assert dirs == [f"{home}/Library/Application Support", "/opt/homebrew/share", "/Library/Application Support"]


@pytest.mark.usefixtures("_clear_xdg_env")
def test_iter_data_dirs_no_homebrew(mocker: MockerFixture) -> None:
    py_version = sys.version_info
    builtin_py_prefix = (
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework"
        f"/Versions/{py_version.major}.{py_version.minor}"
    )
    mocker.patch("sys.prefix", builtin_py_prefix)
    dirs = list(MacOS().iter_data_dirs())
    home = str(Path("~").expanduser())
    assert dirs == [f"{home}/Library/Application Support", "/Library/Application Support"]
