from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

import platformdirs
from platformdirs.ios import IOS

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType

    from pytest_mock import MockerFixture


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # The iOS simulator sets HOME to the app's data container; USERPROFILE stands in for it when tests run on Windows.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return tmp_path


@pytest.fixture
def _ios_platform() -> Iterator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(sys, "platform", "ios")
        importlib.reload(platformdirs)
        yield
    importlib.reload(platformdirs)


@pytest.mark.usefixtures("_ios_platform")
def test_ios_platform_uses_the_app_container_library(container: Path) -> None:
    assert Path(platformdirs.user_data_dir("SuperApp")) == container / "Library" / "Application Support" / "SuperApp"


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
def test_ios(container: Path, params: dict[str, Any], func: str) -> None:
    app = [params[key] for key in ("appname", "version") if key in params]
    app_support = ("Library", "Application Support", *app)
    expected = {
        "user_data_dir": app_support,
        "site_data_dir": app_support,
        "user_config_dir": app_support,
        "site_config_dir": app_support,
        "user_cache_dir": ("Library", "Caches", *app),
        "site_cache_dir": ("Library", "Caches", *app),
        "user_state_dir": app_support,
        "site_state_dir": app_support,
        "user_log_dir": ("Library", "Logs", *app),
        "site_log_dir": ("Library", "Logs", *app),
        "user_documents_dir": ("Documents",),
        "user_downloads_dir": ("Documents", "Downloads"),
        "user_pictures_dir": ("Documents", "Pictures"),
        "user_videos_dir": ("Documents", "Movies"),
        "user_music_dir": ("Documents", "Music"),
        "user_desktop_dir": ("Documents", "Desktop"),
        "user_projects_dir": ("Documents", "Projects"),
        "user_publicshare_dir": ("Documents", "Public"),
        "user_templates_dir": ("Documents", "Templates"),
        "user_fonts_dir": ("Library", "Fonts"),
        "user_preference_dir": app_support,
        "user_bin_dir": (".local", "bin"),
        "site_bin_dir": (".local", "bin"),
        "user_applications_dir": ("Applications",),
        "site_applications_dir": ("Applications",),
        "user_runtime_dir": ("tmp", *app),
        "site_runtime_dir": ("tmp", *app),
    }[func]

    assert Path(getattr(IOS(**params), func)) == container.joinpath(*expected)


@pytest.mark.parametrize(
    ("func", "created"),
    [
        pytest.param("site_config_dir", True, id="site_config_dir"),
        pytest.param("user_preference_dir", True, id="user_preference_dir"),
        pytest.param("site_log_dir", True, id="site_log_dir"),
        pytest.param("site_runtime_dir", True, id="site_runtime_dir"),
        pytest.param("user_pictures_dir", False, id="user_pictures_dir"),
    ],
)
@pytest.mark.usefixtures("container")
def test_ios_ensure_exists(func: str, created: bool) -> None:
    assert Path(getattr(IOS("foo", ensure_exists=True), func)).is_dir() is created


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
@pytest.mark.parametrize(
    ("func", "created"),
    [
        pytest.param(
            "user_data_dir", ["Library", "Library/Application Support", "Library/Application Support/foo"], id="data"
        ),
        pytest.param("user_cache_dir", ["Library", "Library/Caches", "Library/Caches/foo"], id="cache"),
        pytest.param("user_log_dir", ["Library", "Library/Logs", "Library/Logs/foo"], id="log"),
        pytest.param("user_runtime_dir", ["tmp", "tmp/foo"], id="runtime"),
    ],
)
def test_ios_ensure_exists_creates_private(
    container: Path, modes: Callable[[Path], dict[str, int]], func: str, created: list[str]
) -> None:
    getattr(IOS("foo", ensure_exists=True), func)
    assert modes(container) == dict.fromkeys(created, 0o700)


def test_ios_ensure_exists_without_home_creates_nothing(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, pwd: ModuleType, tmp_path: Path
) -> None:
    monkeypatch.delenv("HOME", raising=False)
    mocker.patch.object(pwd, "getpwuid", side_effect=KeyError("getpwuid(): uid not found"))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match=r"^could not determine the home directory, refusing to create '~/"):
        _ = IOS(appname="app", ensure_exists=True).user_data_dir
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("env_var", "func"),
    [
        pytest.param("XDG_DATA_HOME", "user_data_dir", id="user_data_dir"),
        pytest.param("XDG_CONFIG_DIRS", "site_config_dir", id="site_config_dir"),
        pytest.param("XDG_RUNTIME_DIR", "user_runtime_dir", id="user_runtime_dir"),
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
    ],
)
def test_ios_ignores_xdg_variables(monkeypatch: pytest.MonkeyPatch, container: Path, env_var: str, func: str) -> None:
    monkeypatch.setenv(env_var, "/xdg")
    assert Path(getattr(IOS(), func)).is_relative_to(container)
