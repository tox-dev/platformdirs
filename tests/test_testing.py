from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

import platformdirs
from platformdirs.android import Android
from platformdirs.testing import isolated_dirs

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def _resolve_all() -> dict[str, list[str]]:
    dirs = platformdirs.PlatformDirs("app", "author", "1.0")
    multi = platformdirs.PlatformDirs("app", "author", "1.0", multipath=True)
    result: dict[str, list[str]] = {}
    for name in dir(platformdirs.PlatformDirs):
        if name.endswith(("_dir", "_path")) and not name.startswith("_"):
            result[name] = [str(getattr(dirs, name))]
            result[f"multipath.{name}"] = str(getattr(multi, name)).split(os.pathsep)
        elif name.startswith("iter_"):
            result[name] = [str(path) for path in getattr(dirs, name)()]
    for name in platformdirs.__all__:
        if name.endswith(("_dir", "_path")):
            result[f"platformdirs.{name}"] = [str(getattr(platformdirs, name)())]
    return result


# Taken at collection, before any test enters isolation, so a leaked patch cannot become the baseline.
_ORIGINAL: Final = _resolve_all()
_ANDROID_ORIGINAL: Final = dict(vars(Android))


def _outside(root: Path) -> dict[str, list[str]]:
    return {
        name: outside
        for name, values in _resolve_all().items()
        if (outside := [value for value in values if not Path(value).is_relative_to(root)])
    }


def test_isolated_dirs_yields_root_as_path(tmp_path: Path) -> None:
    with isolated_dirs(str(tmp_path)) as root:
        assert root == tmp_path


def test_isolated_dirs_redirects_every_accessor(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        assert _outside(tmp_path) == {}


def test_isolated_dirs_redirects_android(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.PlatformDirs", Android)
    with isolated_dirs(tmp_path):
        assert _outside(tmp_path) == {}


def test_isolated_dirs_restores_android(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.PlatformDirs", Android)
    with isolated_dirs(tmp_path):
        pass
    assert dict(vars(Android)) == _ANDROID_ORIGINAL


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        pytest.param("user_data", "user_data/app/1.0", id="user_data"),
        pytest.param("site_data", "site_data/app/1.0", id="site_data"),
        pytest.param("user_config", "user_config/app/1.0", id="user_config"),
        pytest.param("site_config", "site_config/app/1.0", id="site_config"),
        pytest.param("user_cache", "user_cache/app/1.0", id="user_cache"),
        pytest.param("site_cache", "site_cache/app/1.0", id="site_cache"),
        pytest.param("user_state", "user_state/app/1.0", id="user_state"),
        pytest.param("site_state", "site_state/app/1.0", id="site_state"),
        pytest.param("user_log", "user_log/app/1.0", id="user_log"),
        pytest.param("site_log", "site_log/app/1.0", id="site_log"),
        pytest.param("user_runtime", "user_runtime/app/1.0", id="user_runtime"),
        pytest.param("site_runtime", "site_runtime/app/1.0", id="site_runtime"),
        pytest.param("user_preference", "user_preference/app/1.0", id="user_preference"),
        pytest.param("user_documents", "user_documents", id="user_documents"),
        pytest.param("user_downloads", "user_downloads", id="user_downloads"),
        pytest.param("user_pictures", "user_pictures", id="user_pictures"),
        pytest.param("user_videos", "user_videos", id="user_videos"),
        pytest.param("user_music", "user_music", id="user_music"),
        pytest.param("user_desktop", "user_desktop", id="user_desktop"),
        pytest.param("user_projects", "user_projects", id="user_projects"),
        pytest.param("user_publicshare", "user_publicshare", id="user_publicshare"),
        pytest.param("user_templates", "user_templates", id="user_templates"),
        pytest.param("user_fonts", "user_fonts", id="user_fonts"),
        pytest.param("user_bin", "user_bin", id="user_bin"),
        pytest.param("site_bin", "site_bin", id="site_bin"),
        pytest.param("user_applications", "user_applications", id="user_applications"),
        pytest.param("site_applications", "site_applications", id="site_applications"),
    ],
)
def test_isolated_dirs_layout(tmp_path: Path, kind: str, expected: str) -> None:
    with isolated_dirs(tmp_path):
        assert getattr(platformdirs.PlatformDirs("app", "author", "1.0"), f"{kind}_path") == tmp_path / expected


def test_isolated_dirs_ensure_exists_creates_under_root(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        assert platformdirs.PlatformDirs("app", ensure_exists=True).user_cache_path.is_dir()


def test_isolated_dirs_restores_on_exit(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        pass
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_restores_after_exception(tmp_path: Path) -> None:
    with pytest.raises(LookupError), isolated_dirs(tmp_path):
        raise LookupError
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_nested_restores_outer(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path / "outer"):
        with isolated_dirs(tmp_path / "inner"):
            pass
        assert platformdirs.user_data_path("app") == tmp_path / "outer" / "user_data" / "app"
