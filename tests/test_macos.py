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


@pytest.fixture
def not_homebrew(mocker: MockerFixture) -> None:
    """Patch sys.prefix to something that is not Homebrew so defaults are macOS standard."""
    py_version = sys.version_info
    builtin_py_prefix = (
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework"
        f"/Versions/{py_version.major}.{py_version.minor}"
    )
    mocker.patch("sys.prefix", builtin_py_prefix)


def test_user_data_dir_uses_xdg_data_home(mocker: MockerFixture, tmp_path: Path) -> None:
    xdg = tmp_path / "xdg-data"
    mocker.patch.dict(os.environ, {"XDG_DATA_HOME": str(xdg)}, clear=False)
    got = MacOS(appname="app", version="1").user_data_dir
    assert got == str(xdg / "app" / "1")


def test_user_cache_dir_uses_xdg_cache_home(mocker: MockerFixture, tmp_path: Path) -> None:
    xdg = tmp_path / "xdg-cache"
    mocker.patch.dict(os.environ, {"XDG_CACHE_HOME": str(xdg)}, clear=False)
    got = MacOS(appname="app", version="1").user_cache_dir
    assert got == str(xdg / "app" / "1")


def test_user_config_dir_uses_xdg_config_home_else_user_data(mocker: MockerFixture) -> None:
    # When set
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/cfg"}, clear=False)
    got = MacOS(appname="a", version="v").user_config_dir
    assert got == "/cfg/a/v"
    # When not set (or empty/whitespace) it should return user_data_dir
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": "   "}, clear=False)
    mac = MacOS(appname="a", version="v")
    assert mac.user_config_dir == mac.user_data_dir


def test_user_state_dir_uses_xdg_state_home_else_user_data(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"XDG_STATE_HOME": "/state"}, clear=False)
    got = MacOS(appname="a", version="v").user_state_dir
    assert got == "/state/a/v"
    # whitespace -> fallback to user_data_dir
    mocker.patch.dict(os.environ, {"XDG_STATE_HOME": "\t"}, clear=False)
    mac = MacOS(appname="a", version="v")
    assert mac.user_state_dir == mac.user_data_dir


@pytest.mark.parametrize(
    ("env_var", "func", "default"),
    [
        ("XDG_DOCUMENTS_DIR", "user_documents_dir", "~/Documents"),
        ("XDG_DOWNLOAD_DIR", "user_downloads_dir", "~/Downloads"),
        ("XDG_PICTURES_DIR", "user_pictures_dir", "~/Pictures"),
        ("XDG_VIDEOS_DIR", "user_videos_dir", "~/Movies"),
        ("XDG_MUSIC_DIR", "user_music_dir", "~/Music"),
        ("XDG_DESKTOP_DIR", "user_desktop_dir", "~/Desktop"),
    ],
)
def test_media_dirs_use_xdg_and_strip_whitespace(mocker: MockerFixture, env_var: str, func: str, default: str) -> None:
    # Uses provided value
    mocker.patch.dict(os.environ, {env_var: "/XDG/MEDIA"}, clear=False)
    assert getattr(MacOS(), func) == "/XDG/MEDIA"

    # Whitespace-only should fallback to default
    mocker.patch.dict(os.environ, {env_var: "   "}, clear=False)
    assert getattr(MacOS(), func) == str(Path(default).expanduser())


def test_user_runtime_dir_uses_xdg_runtime_when_set(mocker: MockerFixture, tmp_path: Path) -> None:
    run = tmp_path / "run"
    mocker.patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(run)}, clear=False)
    got = MacOS(appname="app", version="1").user_runtime_dir
    assert got == str(run / "app" / "1")


@pytest.mark.usefixtures("not_homebrew")
def test_site_runtime_dir_uses_xdg_runtime_when_set(mocker: MockerFixture, tmp_path: Path) -> None:
    run = tmp_path / "run"
    mocker.patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(run)}, clear=False)
    got = MacOS(appname="app", version="1").site_runtime_dir
    assert got == str(run / "app" / "1")


@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="single")])
@pytest.mark.usefixtures("not_homebrew")
def test_site_data_dir_honors_xdg_data_dirs(mocker: MockerFixture, multipath: bool) -> None:
    env = "/share/one:/share/two"
    mocker.patch.dict(os.environ, {"XDG_DATA_DIRS": env}, clear=False)
    mac = MacOS(appname="a", version="v", multipath=multipath)
    got = mac.site_data_dir
    if multipath:
        assert got == "/share/one/a/v:/share/two/a/v"
    else:
        assert got == "/share/one/a/v"


@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="single")])
@pytest.mark.usefixtures("not_homebrew")
def test_site_config_dir_honors_xdg_config_dirs(mocker: MockerFixture, multipath: bool) -> None:
    env = "/etc/one:/etc/two"
    mocker.patch.dict(os.environ, {"XDG_CONFIG_DIRS": env}, clear=False)
    mac = MacOS(appname="a", version="v", multipath=multipath)
    got = mac.site_config_dir
    if multipath:
        assert got == "/etc/one/a/v:/etc/two/a/v"
    else:
        assert got == "/etc/one/a/v"
