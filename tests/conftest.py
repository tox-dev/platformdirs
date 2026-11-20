from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType

    from pytest_mock import MockerFixture


@pytest.fixture
def root_owned_paths(tmp_path: Path, mocker: MockerFixture) -> set[Path]:
    original_lstat = os.lstat
    foreign: set[Path] = set()

    def lstat(path: str | os.PathLike[str]) -> os.stat_result:
        info = original_lstat(path)
        entry = Path(path)
        if entry in foreign:
            return os.stat_result((*info[:4], info.st_uid or 1, *info[5:]))
        if not (entry.is_relative_to(tmp_path) or tmp_path.is_relative_to(entry)):
            return info
        return os.stat_result((*info[:4], 0, *info[5:]))

    mocker.patch.object(os, "lstat", autospec=True, side_effect=lstat)
    return foreign


_PROPS: Final[tuple[str, ...]] = (
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


@pytest.fixture(params=_PROPS)
def func(request: pytest.FixtureRequest) -> str:
    return cast("str", request.param)


@pytest.fixture(params=_PROPS)
def func_path(request: pytest.FixtureRequest) -> str:
    return cast("str", request.param).replace("_dir", "_path")


@pytest.fixture
def props() -> tuple[str, ...]:
    return _PROPS


@pytest.fixture
def _clear_xdg_env(monkeypatch: pytest.MonkeyPatch) -> None:
    xdg_env_vars: tuple[str, ...] = (
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
    for var in xdg_env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def runtime_temp_dir(tmp_path: Path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, system_root: Path) -> Path:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    mocker.patch("tempfile.tempdir", str(tmp_path))
    # A host symlink such as /var must not redirect the walk outside the simulated system tree.
    parents = {
        Path("/run/user"),
        Path("/var/run/user"),
        Path("/tmp/run/user"),  # ruff:ignore[hardcoded-temp-file]  # OpenBSD runtime path
    }
    ancestors = set().union(*(path.parents for path in parents)) | parents
    real_lstat = os.lstat

    def lstat(path: str | Path) -> os.stat_result:
        entry = Path(path)
        if entry.parent in parents:
            return real_lstat(system_root / entry.relative_to(entry.anchor))
        if entry in ancestors and (mapped := system_root / entry.relative_to(entry.anchor)).is_dir():
            return real_lstat(mapped)
        return real_lstat(path)

    mocker.patch.object(os, "lstat", new=lstat)
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


@pytest.fixture(
    params=[
        pytest.param(None, id="home-unset"),
        pytest.param("", id="home-empty"),
        pytest.param("relhome", id="home-relative"),
        pytest.param(".", id="home-dot"),
    ]
)
def _unknown_home(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, pwd: ModuleType
) -> None:
    if request.param is None:
        monkeypatch.delenv("HOME", raising=False)
    else:
        monkeypatch.setenv("HOME", request.param)
    mocker.patch.object(pwd, "getpwuid", side_effect=KeyError("getpwuid(): uid not found"), autospec=True)


@pytest.fixture
def pwd() -> ModuleType:
    return pytest.importorskip("pwd")


@pytest.fixture(params=["file", "file-symlink"])
def media_file(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    (target := tmp_path / "file").touch()
    if request.param == "file":
        return target
    (link := tmp_path / "media").symlink_to(target)
    return link
