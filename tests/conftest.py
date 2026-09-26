from __future__ import annotations

import os
import stat
from typing import TYPE_CHECKING, Final, cast

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path
    from types import ModuleType

    from _pytest.fixtures import SubRequest
    from pytest_mock import MockerFixture

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "user_documents_dir",
    "user_downloads_dir",
    "user_pictures_dir",
    "user_videos_dir",
    "user_music_dir",
    "user_desktop_dir",
    "user_projects_dir",
    "user_publicshare_dir",
    "user_templates_dir",
    "user_fonts_dir",
    "user_preference_dir",
    "user_bin_dir",
    "site_bin_dir",
    "user_applications_dir",
    "user_runtime_dir",
    "site_data_dir",
    "site_config_dir",
    "site_cache_dir",
    "site_state_dir",
    "site_log_dir",
    "site_applications_dir",
    "site_runtime_dir",
)


@pytest.fixture(params=PROPS)
def func(request: SubRequest) -> str:
    return cast("str", request.param)


@pytest.fixture(params=PROPS)
def func_path(request: SubRequest) -> str:
    prop = cast("str", request.param)
    return prop.replace("_dir", "_path")


@pytest.fixture
def props() -> tuple[str, ...]:
    return PROPS


_XDG_ENV_VARS: Final[tuple[str, ...]] = (
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
    "XDG_PROJECTS_DIR",
    "XDG_PUBLICSHARE_DIR",
    "XDG_TEMPLATES_DIR",
)


@pytest.fixture
def _clear_xdg_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _XDG_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def runtime_temp_dir(tmp_path: Path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, system_root: Path) -> Path:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("tempfile.tempdir", str(tmp_path))
    # user_runtime_dir checks fixed system paths such as /run/user/<uid> first, so serve those from system_root.
    real_lstat: Final = os.lstat
    mocker.patch(
        "os.lstat",
        side_effect=lambda path: real_lstat(
            system_root / path[1:]
            if isinstance(path, str) and "/run/user/" in path and not path.startswith(str(tmp_path))
            else path
        ),
    )
    return tmp_path


@pytest.fixture
def system_root(tmp_path: Path) -> Path:
    return tmp_path / "root"


@pytest.fixture
def _umask() -> Iterator[None]:
    previous = os.umask(0o022)
    yield
    os.umask(previous)


@pytest.fixture
def modes() -> Callable[[Path], dict[str, int]]:
    def collect(root: Path) -> dict[str, int]:
        return {path.relative_to(root).as_posix(): stat.S_IMODE(path.stat().st_mode) for path in root.rglob("*")}

    return collect


@pytest.fixture(params=[pytest.param(None, id="home-unset"), pytest.param("", id="home-empty")])
def _unknown_home(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, pwd: ModuleType
) -> None:
    if request.param is None:
        monkeypatch.delenv("HOME", raising=False)
    else:
        monkeypatch.setenv("HOME", request.param)
    mocker.patch.object(pwd, "getpwuid", side_effect=KeyError("getpwuid(): uid not found"))


@pytest.fixture
def pwd() -> ModuleType:
    return pytest.importorskip("pwd")
