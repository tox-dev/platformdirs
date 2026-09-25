from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final
from unittest.mock import MagicMock

import pytest

import platformdirs
from platformdirs import android
from platformdirs.android import Android

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def _example_android_folder(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.android._android_folder", return_value="/data/data/com.example", autospec=True)
    mocker.patch("platformdirs.android.os.path.join", lambda *args: "/".join(args))


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"appname": "foo"},
        {"appname": "foo", "appauthor": "bar"},
        {"appname": "foo", "appauthor": "bar", "version": "v1.0"},
        {"appname": "foo", "appauthor": "bar", "version": "v1.0", "opinion": False},
    ],
    ids=[
        "no_args",
        "app_name",
        "app_name_with_app_author",
        "app_name_author_version",
        "app_name_author_version_false_opinion",
    ],
)
@pytest.mark.usefixtures("_example_android_folder")
def test_android(params: dict[str, Any], func: str) -> None:
    result = getattr(Android(**params), func)

    suffix_elements = []
    if "appname" in params:
        suffix_elements.append(params["appname"])
    if "version" in params:
        suffix_elements.append(params["version"])
    if suffix_elements:
        suffix_elements.insert(0, "")
    suffix = "/".join(suffix_elements)

    val = "/tmp"  # ruff:ignore[hardcoded-temp-file]
    expected_map = {
        "user_data_dir": f"/data/data/com.example/files{suffix}",
        "site_data_dir": f"/data/data/com.example/files{suffix}",
        "user_config_dir": f"/data/data/com.example/shared_prefs{suffix}",
        "site_config_dir": f"/data/data/com.example/shared_prefs{suffix}",
        "user_cache_dir": f"/data/data/com.example/cache{suffix}",
        "site_cache_dir": f"/data/data/com.example/cache{suffix}",
        "user_state_dir": f"/data/data/com.example/files{suffix}",
        "site_state_dir": f"/data/data/com.example/files{suffix}",
        "user_log_dir": f"/data/data/com.example/cache{suffix}{'' if params.get('opinion', True) is False else '/log'}",
        "site_log_dir": f"/data/data/com.example/cache{suffix}{'' if params.get('opinion', True) is False else '/log'}",
        "user_documents_dir": "/storage/emulated/0/Documents",
        "user_downloads_dir": "/storage/emulated/0/Download",
        "user_pictures_dir": "/storage/emulated/0/Pictures",
        "user_videos_dir": "/storage/emulated/0/Movies",
        "user_music_dir": "/storage/emulated/0/Music",
        "user_desktop_dir": "/storage/emulated/0/Documents/Desktop",
        "user_projects_dir": "/storage/emulated/0/Documents/Projects",
        "user_publicshare_dir": "/storage/emulated/0/Documents/Public",
        "user_templates_dir": "/storage/emulated/0/Documents/Templates",
        "user_fonts_dir": "/storage/emulated/0/Documents/fonts",
        "user_preference_dir": f"/data/data/com.example/shared_prefs{suffix}",
        "user_bin_dir": "/data/data/com.example/files/bin",
        "site_bin_dir": "/data/data/com.example/files/bin",
        "user_applications_dir": f"/data/data/com.example/files{suffix}",
        "site_applications_dir": f"/data/data/com.example/files{suffix}",
        "user_runtime_dir": f"/data/data/com.example/cache{suffix}{'' if not params.get('opinion', True) else val}",
        "site_runtime_dir": f"/data/data/com.example/cache{suffix}{'' if not params.get('opinion', True) else val}",
    }
    expected = expected_map[func]

    assert result == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        pytest.param("/data/user/1/a/files", "/data/user/1/a", id="user"),
        pytest.param("/data/data/a/files", "/data/data/a", id="data"),
        pytest.param(
            "/mnt/expand/8e06fc2f-a86a-44e8-81ce-109e0eedd5ed/user/1/a/files",
            "/mnt/expand/8e06fc2f-a86a-44e8-81ce-109e0eedd5ed/user/1/a",
            id="adopted",
        ),
        pytest.param("/data/data/filesync.app/files/app", "/data/data/filesync.app", id="data-files-prefix"),
        pytest.param(
            "/mnt/expand/8e06fc2f-a86a-44e8-81ce-109e0eedd5ed/user/0/filesync.app/files/app",
            "/mnt/expand/8e06fc2f-a86a-44e8-81ce-109e0eedd5ed/user/0/filesync.app",
            id="adopted-files-prefix",
        ),
        pytest.param("/data/data/a/files/app/lib/files", "/data/data/a", id="nested-files"),
    ],
)
def test_android_folder_from_sys_path(
    mocker: MockerFixture, path: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    mocker.patch.dict(sys.modules, {"jnius": MagicMock(side_effect=ModuleNotFoundError)})
    monkeypatch.delitem(__import__("sys").modules, "jnius")
    mocker.patch.dict(sys.modules, {"android": MagicMock(side_effect=ModuleNotFoundError)})
    monkeypatch.delitem(__import__("sys").modules, "android")

    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    _android_folder.cache_clear()
    monkeypatch.setattr(sys, "path", ["/A", "/B", path])

    assert Android().user_data_path == Path(expected, "files")


@pytest.fixture
def _clear_android_caches() -> None:
    for cached in vars(android).values():
        if hasattr(cached, "cache_clear"):
            cached.cache_clear()


@pytest.mark.usefixtures("_clear_android_caches", "_posix_path_join")
@pytest.mark.parametrize(
    ("app_folder", "storage"),
    [
        pytest.param("/data/data/org.example.app", "/storage/emulated/0", id="owner"),
        pytest.param("/data/user/10/org.example.app", "/storage/emulated/10", id="secondary-user"),
        pytest.param(
            "/mnt/expand/8e06fc2f-a86a-44e8-81ce-109e0eedd5ed/user/11/org.example.app",
            "/storage/emulated/11",
            id="adopted",
        ),
        pytest.param(None, "/storage/emulated/0", id="unknown"),
    ],
)
@pytest.mark.parametrize(
    ("prop", "folder"),
    [
        pytest.param("user_documents_dir", "Documents", id="documents"),
        pytest.param("user_downloads_dir", "Download", id="downloads"),
        pytest.param("user_pictures_dir", "Pictures", id="pictures"),
        pytest.param("user_videos_dir", "Movies", id="videos"),
        pytest.param("user_music_dir", "Music", id="music"),
        pytest.param("user_desktop_dir", "Documents/Desktop", id="desktop"),
        pytest.param("user_projects_dir", "Documents/Projects", id="projects"),
        pytest.param("user_publicshare_dir", "Documents/Public", id="publicshare"),
        pytest.param("user_templates_dir", "Documents/Templates", id="templates"),
        pytest.param("user_fonts_dir", "Documents/fonts", id="fonts"),
    ],
)
def test_android_shared_storage_follows_user(
    mocker: MockerFixture, app_folder: str | None, storage: str, prop: str, folder: str
) -> None:
    mocker.patch.dict(sys.modules, {"jnius": None})
    mocker.patch("platformdirs.android._android_folder", return_value=app_folder, autospec=True)
    assert getattr(Android(), prop) == f"{storage}/{folder}"


@pytest.fixture
def _posix_path_join(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.android.os.path.join", lambda *args: "/".join(args))


def _pyjnius(classes: dict[str, MagicMock]) -> MagicMock:
    # pyjnius raises JavaException for an unknown class and for an instance method called on a class object
    def autoclass(name: str) -> MagicMock:
        if name not in classes:
            msg = f"Class not found {name!r}"
            raise RuntimeError(msg)
        return classes[name]

    return MagicMock(autoclass=autoclass, JavaException=RuntimeError)


def _context(app_folder: str) -> MagicMock:
    app_dir = MagicMock(getAbsolutePath=MagicMock(return_value=app_folder))
    return MagicMock(getFilesDir=MagicMock(return_value=MagicMock(getParentFile=MagicMock(return_value=app_dir))))


def _environment() -> MagicMock:
    def public_directory(name: str) -> MagicMock:
        return MagicMock(getAbsolutePath=MagicMock(return_value=f"/storage/emulated/10/{name}"))

    return MagicMock(getExternalStoragePublicDirectory=MagicMock(side_effect=public_directory))


@pytest.mark.usefixtures("_clear_android_caches", "_posix_path_join")
@pytest.mark.parametrize(
    ("activity", "service"),
    [
        pytest.param(_context("/data/user/10/org.example.app"), None, id="activity"),
        pytest.param(None, _context("/data/user/10/org.example.app"), id="service"),
    ],
)
def test_android_folder_from_python_for_android(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, activity: MagicMock | None, service: MagicMock | None
) -> None:
    classes = {
        "org.kivy.android.PythonActivity": MagicMock(mActivity=activity),
        "org.kivy.android.PythonService": MagicMock(mService=service),
    }
    mocker.patch.dict(sys.modules, {"jnius": _pyjnius(classes), "android": None})
    monkeypatch.setattr(sys, "path", [])
    assert Android(appname="app").user_data_dir == "/data/user/10/org.example.app/files/app"


@pytest.mark.usefixtures("_clear_android_caches", "_posix_path_join")
def test_android_folder_without_python_for_android_uses_sys_path(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    mocker.patch.dict(sys.modules, {"jnius": _pyjnius({}), "android": None})
    monkeypatch.setattr(sys, "path", ["/data/user/10/org.example.app/files/app"])
    assert Android(appname="app").user_data_dir == "/data/user/10/org.example.app/files/app"


@pytest.mark.usefixtures("_clear_android_caches", "_posix_path_join")
@pytest.mark.parametrize(
    ("prop", "expected"),
    [
        pytest.param("user_documents_dir", "/storage/emulated/10/Documents", id="documents"),
        pytest.param("user_downloads_dir", "/storage/emulated/10/Download", id="downloads"),
        pytest.param("user_pictures_dir", "/storage/emulated/10/Pictures", id="pictures"),
        pytest.param("user_videos_dir", "/storage/emulated/10/Movies", id="videos"),
        pytest.param("user_music_dir", "/storage/emulated/10/Music", id="music"),
    ],
)
def test_android_media_dir_from_environment(mocker: MockerFixture, prop: str, expected: str) -> None:
    classes = {"android.os.Environment": _environment()}
    mocker.patch.dict(sys.modules, {"jnius": _pyjnius(classes)})
    assert getattr(Android(), prop) == expected


@pytest.mark.usefixtures("_clear_android_caches")
def test_android_media_dir_without_environment_falls_back(mocker: MockerFixture) -> None:
    mocker.patch.dict(sys.modules, {"jnius": _pyjnius({})})
    assert Android().user_downloads_dir == "/storage/emulated/0/Download"


def test_android_folder_not_found(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    mocker.patch.dict(sys.modules, {"jnius": None})

    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    _android_folder.cache_clear()
    monkeypatch.setattr(sys, "path", [])
    assert _android_folder() is None


@pytest.mark.parametrize("prop", ["user_data_dir", "user_config_dir", "user_cache_dir", "user_bin_dir"])
def test_android_folder_not_found_raises(mocker: MockerFixture, prop: str) -> None:
    mocker.patch("platformdirs.android._android_folder", return_value=None, autospec=True)
    with pytest.raises(RuntimeError, match=r"^cannot find the Android app folder"):
        getattr(Android(appname="foo"), prop)


@pytest.mark.parametrize(
    ("prop", "subdir"),
    [
        ("user_log_dir", "log"),
        ("user_runtime_dir", "tmp"),
    ],
)
def test_android_ensure_exists_creates_opinion_subdir(
    mocker: MockerFixture,
    tmp_path: Path,
    prop: str,
    subdir: str,
) -> None:
    mocker.patch("platformdirs.android._android_folder", return_value=str(tmp_path), autospec=True)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    dirs = Android(appname="myapp", ensure_exists=True)
    result = getattr(dirs, prop)

    expected = str(cache_dir / "myapp" / subdir)
    assert result == expected
    assert Path(result).is_dir()


@pytest.mark.parametrize(
    ("func", "expected"),
    [
        pytest.param("iter_config_dirs", "/data/data/com.example/shared_prefs/foo", id="config"),
        pytest.param("iter_data_dirs", "/data/data/com.example/files/foo", id="data"),
        pytest.param("iter_cache_dirs", "/data/data/com.example/cache/foo", id="cache"),
        pytest.param("iter_state_dirs", "/data/data/com.example/files/foo", id="state"),
        pytest.param("iter_log_dirs", "/data/data/com.example/cache/foo/log", id="log"),
        pytest.param("iter_runtime_dirs", "/data/data/com.example/cache/foo/tmp", id="runtime"),
    ],
)
@pytest.mark.usefixtures("_example_android_folder")
def test_android_iter_dirs_no_duplicates(func: str, expected: str) -> None:
    # Every site_*_dir on Android is defined as its user_*_dir.
    assert list(getattr(Android(appname="foo"), func)()) == [expected]


_SCOPED_APPLICATIONS_DIR: Final[str] = "/data/data/com.example/files/foo/1.0"


@pytest.mark.parametrize("func", ["user_applications_dir", "site_applications_dir"])
@pytest.mark.usefixtures("_example_android_folder")
def test_android_applications_dir_function_takes_app_arguments(mocker: MockerFixture, func: str) -> None:
    mocker.patch("platformdirs.PlatformDirs", Android)
    # Android scopes both applications directories to the app, so the function has to forward the name and version.
    assert getattr(platformdirs, func)(appname="foo", version="1.0") == _SCOPED_APPLICATIONS_DIR


@pytest.mark.parametrize("func", ["user_applications_path", "site_applications_path"])
@pytest.mark.usefixtures("_example_android_folder")
def test_android_applications_path_function_takes_app_arguments(mocker: MockerFixture, func: str) -> None:
    mocker.patch("platformdirs.PlatformDirs", Android)
    assert getattr(platformdirs, func)(appname="foo", version="1.0") == Path(_SCOPED_APPLICATIONS_DIR)
