from __future__ import annotations

import contextlib
import importlib
import inspect
import os
import re
import stat
import sys
import typing
import warnings
from pathlib import Path
from tempfile import gettempdir

import pytest

import platformdirs
from platformdirs import RuntimeDirWarning, unix
from platformdirs.macos import MacOS
from platformdirs.unix import Unix

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _reload_after_test() -> typing.Iterator[None]:
    # The warnings are emitted once per process, so start every test from a fresh module.
    yield
    importlib.reload(unix)


@pytest.fixture
def _as_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=0)


@pytest.fixture
def _as_non_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=1000)


@pytest.fixture
def _no_xdg_runtime_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)


@pytest.fixture
def _missing_xdg_runtime_dir(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    # A missing directory passes the owner check that the mocked uid would fail.
    monkeypatch.setenv("XDG_RUNTIME_DIR", f"{posix_tmp_path}/runtime")


@pytest.mark.parametrize(
    "prop",
    [
        "user_documents_dir",
        "user_downloads_dir",
        "user_pictures_dir",
        "user_videos_dir",
        "user_music_dir",
        "user_desktop_dir",
        "user_projects_dir",
        "user_publicshare_dir",
        "user_templates_dir",
    ],
)
def test_user_media_dir(mocker: MockerFixture, prop: str) -> None:
    example_path = "/home/example/ExampleMediaFolder"
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = example_path
    assert getattr(Unix(), prop) == example_path


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", id="user_desktop_dir"),
        pytest.param("XDG_PROJECTS_DIR", "user_projects_dir", id="user_projects_dir"),
        pytest.param("XDG_PUBLICSHARE_DIR", "user_publicshare_dir", id="user_publicshare_dir"),
        pytest.param("XDG_TEMPLATES_DIR", "user_templates_dir", id="user_templates_dir"),
    ],
)
def test_user_media_dir_env_var(mocker: MockerFixture, env_var: str, prop: str) -> None:
    # Mock media dir not being in user-dirs.dirs file
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = None

    example_path = "/home/example/ExampleMediaFolder"
    mocker.patch.dict(os.environ, {env_var: example_path})

    assert getattr(Unix(), prop) == example_path


@pytest.mark.parametrize(
    ("env_var", "prop", "default_abs_path"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", "/home/example/Documents", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", "/home/example/Downloads", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", "/home/example/Pictures", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", "/home/example/Videos", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", "/home/example/Music", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", "/home/example/Desktop", id="user_desktop_dir"),
        pytest.param("XDG_PROJECTS_DIR", "user_projects_dir", "/home/example/Projects", id="user_projects_dir"),
        pytest.param("XDG_PUBLICSHARE_DIR", "user_publicshare_dir", "/home/example/Public", id="user_publicshare_dir"),
        pytest.param("XDG_TEMPLATES_DIR", "user_templates_dir", "/home/example/Templates", id="user_templates_dir"),
    ],
)
def test_user_media_dir_default(mocker: MockerFixture, env_var: str, prop: str, default_abs_path: str) -> None:
    # Mock media dir not being in user-dirs.dirs file
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = None

    # Mock no XDG env variable being set
    mocker.patch.dict(os.environ, {env_var: ""})

    # Mock home directory
    mocker.patch.dict(os.environ, {"HOME": "/home/example"})
    # Mock home directory for running the test on Windows
    mocker.patch.dict(os.environ, {"USERPROFILE": "/home/example"})

    assert getattr(Unix(), prop) == default_abs_path


@pytest.mark.parametrize(
    ("env_var", "prop", "default_abs_path"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", "/home/example/Documents", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", "/home/example/Downloads", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", "/home/example/Pictures", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", "/home/example/Videos", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", "/home/example/Music", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", "/home/example/Desktop", id="user_desktop_dir"),
        pytest.param("XDG_PROJECTS_DIR", "user_projects_dir", "/home/example/Projects", id="user_projects_dir"),
        pytest.param("XDG_PUBLICSHARE_DIR", "user_publicshare_dir", "/home/example/Public", id="user_publicshare_dir"),
        pytest.param("XDG_TEMPLATES_DIR", "user_templates_dir", "/home/example/Templates", id="user_templates_dir"),
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param("relative/dir", id="relative"),
        pytest.param("~/dir", id="tilde"),
        pytest.param("$HOME/dir", id="unexpanded-home"),
        pytest.param("C:/dir", id="windows-drive"),
    ],
)
def test_user_media_dir_relative_env_var_falls_back(
    mocker: MockerFixture, env_var: str, prop: str, default_abs_path: str, value: str
) -> None:
    # Mock media dir not being in user-dirs.dirs file
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = None

    mocker.patch.dict(os.environ, {env_var: value, "HOME": "/home/example", "USERPROFILE": "/home/example"})

    assert getattr(Unix(), prop) == default_abs_path


def test_user_fonts_dir_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"XDG_DATA_HOME": "", "HOME": "/home/example", "USERPROFILE": "/home/example"})
    assert Unix().user_fonts_dir == "/home/example/.local/share/fonts"


@pytest.mark.parametrize(
    ("prop", "suffix"),
    [
        pytest.param("user_fonts_path", "fonts", id="fonts"),
        pytest.param("user_applications_path", "applications", id="applications"),
    ],
)
@pytest.mark.parametrize(
    ("value", "base"),
    [
        pytest.param("/custom/data", "/custom/data", id="absolute"),
        pytest.param("relative/data", "/home/example/.local/share", id="relative"),
    ],
)
def test_user_data_home_derived_path(
    monkeypatch: pytest.MonkeyPatch, prop: str, suffix: str, value: str, base: str
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", value)
    monkeypatch.setenv("HOME", "/home/example")
    monkeypatch.setenv("USERPROFILE", "/home/example")
    assert getattr(Unix(), prop) == Path(base) / suffix


def test_user_preference_dir_is_config_dir() -> None:
    dirs = Unix(appname="MyApp", version="1.0")
    assert dirs.user_preference_dir == dirs.user_config_dir


class XDGVariable(typing.NamedTuple):
    name: str
    default_value: str


def _func_to_path(func: str) -> XDGVariable | None:
    mapping = {
        "user_data_dir": XDGVariable("XDG_DATA_HOME", "~/.local/share"),
        "site_data_dir": XDGVariable("XDG_DATA_DIRS", f"/usr/local/share{os.pathsep}/usr/share"),
        "user_config_dir": XDGVariable("XDG_CONFIG_HOME", "~/.config"),
        "site_config_dir": XDGVariable("XDG_CONFIG_DIRS", "/etc/xdg"),
        "user_cache_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
        "user_state_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
        "user_log_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
        "user_runtime_dir": XDGVariable("XDG_RUNTIME_DIR", f"{gettempdir()}/runtime-1234"),
        "user_bin_dir": None,
        "site_bin_dir": None,
        "user_applications_dir": None,
        "site_applications_dir": None,
        "site_log_dir": None,
        "site_state_dir": None,
        "site_runtime_dir": XDGVariable(
            "XDG_RUNTIME_DIR", "/var/run" if sys.platform.startswith(("freebsd", "openbsd", "netbsd")) else "/run"
        ),
    }
    return mapping.get(func)


@pytest.fixture
def dirs_instance() -> Unix:
    return Unix(multipath=True, opinion=False)


@pytest.fixture
def _getuid(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=1234)


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_not_set(monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.delenv(xdg_variable.name, raising=False)
    with _fallback_warning(expected=func == "user_runtime_dir"):
        result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_empty_value(monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, "")
    with _fallback_warning(expected=func == "user_runtime_dir"):
        result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


def _fallback_warning(*, expected: bool) -> contextlib.AbstractContextManager[object]:
    if expected:
        return pytest.warns(RuntimeDirWarning, match="^XDG_RUNTIME_DIR is not set, falling back to ")
    return contextlib.nullcontext()


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_custom_value(monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, "/custom-dir")
    result = getattr(dirs_instance, func)
    assert result == "/custom-dir"


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_padded_value(monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, " /custom-dir ")
    result = getattr(dirs_instance, func)
    assert result == "/custom-dir"


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize(
    ("env_var", "prop", "default"),
    [
        pytest.param("XDG_DATA_HOME", "user_data_dir", "~/.local/share", id="data"),
        pytest.param("XDG_CONFIG_HOME", "user_config_dir", "~/.config", id="config"),
        pytest.param("XDG_CACHE_HOME", "user_cache_dir", "~/.cache", id="cache"),
        pytest.param("XDG_STATE_HOME", "user_state_dir", "~/.local/state", id="state"),
        pytest.param("XDG_STATE_HOME", "user_log_dir", "~/.local/state", id="log"),
        pytest.param("XDG_CONFIG_HOME", "user_preference_dir", "~/.config", id="preference"),
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param("relative/dir", id="relative"),
        pytest.param("~/dir", id="tilde"),
        pytest.param("$HOME/dir", id="unexpanded-home"),
        pytest.param("C:/dir", id="windows-drive"),
    ],
)
def test_xdg_variable_relative_value(
    monkeypatch: pytest.MonkeyPatch, env_var: str, prop: str, default: str, value: str
) -> None:
    monkeypatch.setenv(env_var, value)
    assert Path(getattr(Unix(opinion=False), prop)) == Path(default).expanduser()


@pytest.mark.parametrize("opinion", [True, False])
def test_site_log_dir_fixed_path(opinion: bool) -> None:
    result = Unix(appname="foo", opinion=opinion).site_log_dir
    assert result == os.path.join("/var/log", "foo")  # ruff:ignore[os-path-join]


def test_site_state_dir_fixed_path() -> None:
    result = Unix(appname="foo").site_state_dir
    assert result == os.path.join("/var/lib", "foo")  # ruff:ignore[os-path-join]


def test_site_cache_path_multipath_keeps_path_separator_in_app_arguments() -> None:
    # Debian epoch versions such as 1:2 contain os.pathsep
    dirs = Unix(appname=f"org{os.pathsep}app", version=f"1{os.pathsep}2", multipath=True)
    assert dirs.site_cache_path == Path("/var/cache", f"org{os.pathsep}app", f"1{os.pathsep}2")


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize("platform", [pytest.param("freebsd", id="freebsd"), pytest.param("netbsd", id="netbsd")])
def test_freebsd_netbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    assert Unix().site_runtime_dir == "/var/run"


@pytest.mark.usefixtures("_getuid")
def test_openbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "openbsd")
    assert Unix().site_runtime_dir == "/var/run"


def test_platform_on_win32(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "win32")
    prev_unix = unix
    importlib.reload(unix)
    try:
        with pytest.raises(RuntimeError, match="should only be used on Unix"):
            unix.Unix().user_runtime_dir  # ruff:ignore[useless-expression]
    finally:
        sys.modules["platformdirs.unix"] = prev_unix


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.parametrize(
    ("existing_mode", "ensure_exists", "expected_mode"),
    [
        pytest.param(None, True, 0o700, id="created-private"),
        pytest.param(0o755, True, 0o700, id="loose-mode-tightened"),
        pytest.param(0o755, False, 0o755, id="loose-mode-untouched-without-ensure-exists"),
    ],
)
def test_user_runtime_dir_temp_fallback_mode(
    mocker: MockerFixture, runtime_temp_dir: Path, existing_mode: int | None, ensure_exists: bool, expected_mode: int
) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=(uid := runtime_temp_dir.stat().st_uid))
    base: typing.Final = runtime_temp_dir / f"runtime-{uid}"
    if existing_mode is not None:
        base.mkdir()
        base.chmod(existing_mode)
    with pytest.warns(RuntimeDirWarning, match=f"^XDG_RUNTIME_DIR is not set, falling back to {re.escape(str(base))}$"):
        _ = Unix(appname="foo", ensure_exists=ensure_exists).user_runtime_dir
    assert stat.S_IMODE(base.stat().st_mode) == expected_mode


@pytest.mark.parametrize("ensure_exists", [pytest.param(True, id="ensure-exists"), pytest.param(False, id="lookup")])
def test_user_runtime_dir_temp_fallback_rejects_other_owner(
    mocker: MockerFixture, runtime_temp_dir: Path, ensure_exists: bool
) -> None:
    owner: typing.Final = runtime_temp_dir.stat().st_uid
    (runtime_temp_dir / f"runtime-{owner + 1}").mkdir()
    mocker.patch("platformdirs.unix.getuid", return_value=owner + 1)
    with pytest.raises(PermissionError, match=f"owned by uid {owner},"):
        Unix(appname="foo", ensure_exists=ensure_exists).user_runtime_dir  # ruff:ignore[useless-expression]


_POSIX_ONLY: typing.Final = pytest.mark.skipif(sys.platform == "win32", reason="Windows has no POSIX owners or modes")
_PROBLEMS: typing.Final = {
    "symlink": "is a symlink",
    "file": "is not a directory",
    "mode-755": "has mode 0755, not 0700",
    "mode-500": "has mode 0500, not 0700",
}
_DEFAULT_PREFIXES: typing.Final = {
    "linux": "run/user",
    "freebsd": "var/run/user",
    "netbsd": "var/run/user",
    "openbsd": "tmp/run/user",
}


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_uses_private_xdg_runtime_dir(session_dir: Path) -> None:
    _create(session_dir, "private")
    assert Unix(appname="app").user_runtime_dir == str(session_dir / "app")


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_returns_missing_xdg_runtime_dir(session_dir: Path) -> None:
    assert Unix(appname="app").user_runtime_dir == str(session_dir / "app")


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid", "_umask")
def test_runtime_dir_creates_xdg_runtime_dir_private(session_dir: Path) -> None:
    _ = Unix(appname="app", ensure_exists=True).user_runtime_dir
    assert stat.S_IMODE(session_dir.stat().st_mode) == 0o700


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize("kind", list(_PROBLEMS))
def test_runtime_dir_invalid_xdg_runtime_dir_falls_back(
    session_dir: Path, default_dir: Path, runtime_uid: int, kind: str
) -> None:
    _create(session_dir, kind)
    _create(default_dir, "private")
    assert Unix(appname="app").user_runtime_dir == f"/run/user/{runtime_uid}/app"


@_POSIX_ONLY
@pytest.mark.parametrize("kind", list(_PROBLEMS))
def test_runtime_dir_invalid_xdg_runtime_dir_warns(
    session_dir: Path, default_dir: Path, runtime_uid: int, kind: str
) -> None:
    _create(session_dir, kind)
    _create(default_dir, "private")
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    expected: typing.Final = f"XDG_RUNTIME_DIR {session_dir} {_PROBLEMS[kind]}, falling back to /run/user/{runtime_uid}"
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
def test_runtime_dir_xdg_runtime_dir_of_other_user_warns(
    session_dir: Path, runtime_temp_dir: Path, mocker: MockerFixture
) -> None:
    _create(session_dir, "private")
    owner: typing.Final = session_dir.stat().st_uid
    mocker.patch("platformdirs.unix.getuid", return_value=owner + 1)
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    fallback: typing.Final = runtime_temp_dir / f"runtime-{owner + 1}"
    expected: typing.Final = (
        f"XDG_RUNTIME_DIR {session_dir} is owned by uid {owner}, not {owner + 1}, falling back to {fallback}"
    )
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
def test_runtime_dir_unreachable_xdg_runtime_dir_warns(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (blocker := runtime_temp_dir / "blocker").touch()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(blocker / "session"))
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    expected: typing.Final = (
        f"XDG_RUNTIME_DIR {blocker / 'session'} cannot be checked: Not a directory, falling back to {temp_dir}"
    )
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_temp_dir")
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize("platform", list(_DEFAULT_PREFIXES))
def test_runtime_dir_uses_private_default_dir(default_dir: Path, runtime_uid: int, platform: str) -> None:
    _create(default_dir, "private")
    assert Unix(appname="app").user_runtime_dir == f"/{_DEFAULT_PREFIXES[platform]}/{runtime_uid}/app"


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_temp_dir")
def test_runtime_dir_unset_warns(default_dir: Path, runtime_uid: int) -> None:
    _create(default_dir, "private")
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    expected: typing.Final = f"XDG_RUNTIME_DIR is not set, falling back to /run/user/{runtime_uid}"
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize("platform", list(_DEFAULT_PREFIXES))
@pytest.mark.parametrize("kind", [*_PROBLEMS, "missing"])
def test_runtime_dir_invalid_default_dir_falls_back(default_dir: Path, temp_dir: Path, kind: str) -> None:
    _create(default_dir, kind)
    assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_runtime_dir_default_dir_of_other_user_falls_back(
    runtime_temp_dir: Path, system_root: Path, mocker: MockerFixture
) -> None:
    mocker.patch("sys.platform", "linux")
    owner: typing.Final = runtime_temp_dir.stat().st_uid
    _create(system_root / "run" / "user" / str(owner + 1), "private")
    mocker.patch("platformdirs.unix.getuid", return_value=owner + 1)
    assert Unix(appname="app").user_runtime_dir == str(runtime_temp_dir / f"runtime-{owner + 1}" / "app")


@_POSIX_ONLY
@pytest.mark.parametrize("ensure_exists", [pytest.param(True, id="ensure-exists"), pytest.param(False, id="lookup")])
@pytest.mark.parametrize("kind", ["symlink", "file"])
def test_runtime_dir_temp_fallback_rejects(temp_dir: Path, kind: str, ensure_exists: bool) -> None:
    _create(temp_dir, kind)
    with pytest.raises(PermissionError, match=f"^runtime directory {re.escape(str(temp_dir))} {_PROBLEMS[kind]}; set "):
        _ = Unix(appname="app", ensure_exists=ensure_exists).user_runtime_dir


@_POSIX_ONLY
def test_runtime_dir_warns_once(temp_dir: Path) -> None:
    dirs: typing.Final = Unix(appname="app")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(3):
            _ = dirs.user_runtime_dir
        _ = Unix(appname="other").user_runtime_dir
    expected: typing.Final = f"XDG_RUNTIME_DIR is not set, falling back to {temp_dir}"
    assert [str(warning.message) for warning in caught] == [expected]


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_temp_dir", "runtime_uid")
def test_runtime_dir_warning_points_at_caller() -> None:
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    assert [warning.filename for warning in record] == [__file__]


@_POSIX_ONLY
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_site_redirect_skips_checks(session_dir: Path, mocker: MockerFixture) -> None:
    _create(session_dir, "mode-755")
    mocker.patch("platformdirs.unix.getuid", return_value=0)
    mocker.patch("sys.platform", "linux")
    assert Unix(appname="app", use_site_for_root=True).user_runtime_dir == "/run/app"


@pytest.fixture
def session_dir(runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(path := runtime_temp_dir / "session"))
    return path


@pytest.fixture
def default_dir(system_root: Path, mocker: MockerFixture, runtime_uid: int, platform: str) -> Path:
    mocker.patch("sys.platform", platform)
    return system_root / _DEFAULT_PREFIXES[platform] / str(runtime_uid)


@pytest.fixture
def temp_dir(runtime_temp_dir: Path, runtime_uid: int) -> Path:
    return runtime_temp_dir / f"runtime-{runtime_uid}"


@pytest.fixture
def runtime_uid(tmp_path: Path, mocker: MockerFixture) -> int:
    mocker.patch("platformdirs.unix.getuid", return_value=(owner := tmp_path.stat().st_uid))
    return owner


@pytest.fixture
def platform() -> str:
    return "linux"


def _create(path: Path, kind: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    match kind:
        case "private" | "mode-755" | "mode-500":
            path.mkdir()
            path.chmod({"private": 0o700, "mode-755": 0o755, "mode-500": 0o500}[kind])
        case "symlink":
            _create(target := path.with_name(f"{path.name}-target"), "private")
            path.symlink_to(target)
        case "file":
            path.touch()


def test_ensure_exists_creates_folder(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=True).user_data_path == Path(posix_tmp_path) / "acme"
    assert (Path(posix_tmp_path) / "acme").is_dir()


def test_folder_not_created_without_ensure_exists(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=False).user_data_path == Path(posix_tmp_path) / "acme"
    assert not (Path(posix_tmp_path) / "acme").exists()


_CLASSES: typing.Final = [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")]


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
@pytest.mark.parametrize("dirs_class", _CLASSES)
@pytest.mark.parametrize(
    "prop",
    [
        pytest.param(prop, id=prop)
        for prop in (
            "user_data_dir",
            "user_config_dir",
            "user_cache_dir",
            "user_state_dir",
            "user_log_dir",
            "user_preference_dir",
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
            "user_bin_dir",
            "user_applications_dir",
            "user_data_path",
        )
    ],
)
def test_without_home_raises(dirs_class: type[Unix | MacOS], prop: str) -> None:
    with pytest.raises(RuntimeError, match=r"^could not determine the home directory for '~"):
        getattr(dirs_class(appname="app"), prop)


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
@pytest.mark.parametrize("dirs_class", _CLASSES)
def test_without_home_ensure_exists_creates_nothing(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError):
        _ = dirs_class(appname="app", ensure_exists=True).user_data_dir
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
def test_without_home_raises_for_home_relative_user_dirs_entry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/Documents"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with pytest.raises(RuntimeError, match=r"^could not determine the home directory for '~'"):
        _ = Unix().user_documents_dir


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
@pytest.mark.parametrize("dirs_class", _CLASSES)
@pytest.mark.parametrize(
    ("env_var", "prop", "suffix"),
    [
        pytest.param("XDG_DATA_HOME", "user_data_dir", "/app", id="user_data_dir"),
        pytest.param("XDG_CONFIG_HOME", "user_config_dir", "/app", id="user_config_dir"),
        pytest.param("XDG_CACHE_HOME", "user_cache_dir", "/app", id="user_cache_dir"),
        pytest.param("XDG_STATE_HOME", "user_state_dir", "/app", id="user_state_dir"),
        pytest.param("XDG_DATA_HOME", "user_fonts_dir", "/fonts", id="user_fonts_dir"),
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", "", id="user_documents_dir"),
    ],
)
def test_without_home_absolute_xdg_dir_applies(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], env_var: str, prop: str, suffix: str
) -> None:
    monkeypatch.setenv(env_var, "/xdg")
    assert getattr(dirs_class(appname="app"), prop) == f"/xdg{suffix}"


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
def test_without_home_absolute_user_dirs_entry_applies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="/srv/docs"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert Unix().user_documents_dir == "/srv/docs"


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
@pytest.mark.parametrize(
    ("dirs_class", "prop", "expected"),
    [
        pytest.param(Unix, "site_config_dir", "/etc/xdg/app", id="unix-site_config_dir"),
        pytest.param(Unix, "site_cache_dir", "/var/cache/app", id="unix-site_cache_dir"),
        pytest.param(Unix, "site_state_dir", "/var/lib/app", id="unix-site_state_dir"),
        pytest.param(Unix, "site_log_dir", "/var/log/app", id="unix-site_log_dir"),
        pytest.param(Unix, "site_bin_dir", "/usr/local/bin", id="unix-site_bin_dir"),
        pytest.param(MacOS, "site_log_dir", "/Library/Logs/app", id="macos-site_log_dir"),
        pytest.param(MacOS, "site_applications_dir", "/Applications", id="macos-site_applications_dir"),
    ],
)
def test_without_home_site_dir_applies(dirs_class: type[Unix | MacOS], prop: str, expected: str) -> None:
    assert getattr(dirs_class(appname="app"), prop) == expected


@pytest.mark.usefixtures("_clear_xdg_env")
@pytest.mark.parametrize(
    ("dirs_class", "expected"),
    [
        pytest.param(Unix, "/home/app-user/.config/app", id="unix"),
        pytest.param(MacOS, "/home/app-user/Library/Application Support/app", id="macos"),
    ],
)
def test_empty_home_uses_passwd_entry(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    pwd: ModuleType,
    dirs_class: type[Unix | MacOS],
    expected: str,
) -> None:
    monkeypatch.setenv("HOME", "")
    entry = pwd.struct_passwd(("app-user", "x", 12345, 12345, "", "/home/app-user", "/bin/sh"))
    mocker.patch.object(pwd, "getpwuid", return_value=entry)
    assert dirs_class(appname="app").user_config_dir == expected


@pytest.mark.usefixtures("_clear_xdg_env", "_unknown_home")
@pytest.mark.parametrize("dirs_class", _CLASSES)
def test_place_file_without_home_creates_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, dirs_class: type[Unix | MacOS]
) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match=r"^could not determine the home directory for '~/"):
        dirs_class(appname="app").place_config_file("app.toml")
    assert not (tmp_path / "~").exists()


def test_place_runtime_file_rejects_temp_fallback_of_other_owner(mocker: MockerFixture, runtime_temp_dir: Path) -> None:
    owner: typing.Final = runtime_temp_dir.stat().st_uid
    (runtime_temp_dir / f"runtime-{owner + 1}").mkdir()
    mocker.patch("platformdirs.unix.getuid", return_value=owner + 1)
    with pytest.raises(PermissionError, match=f"owned by uid {owner},"):
        Unix(appname="foo").place_runtime_file("app.sock")


@pytest.mark.parametrize(
    ("source", "ensure_exists", "created"),
    [
        pytest.param("env", True, True, id="env"),
        pytest.param("user-dirs", True, True, id="user-dirs"),
        pytest.param("default", True, False, id="default"),
        pytest.param("env", False, False, id="env-off"),
        pytest.param("user-dirs", False, False, id="user-dirs-off"),
    ],
)
@pytest.mark.parametrize(
    ("key", "prop", "default"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", "Documents", id="user_documents_dir"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", "Downloads", id="user_downloads_dir"),
        pytest.param("XDG_PICTURES_DIR", "user_pictures_dir", "Pictures", id="user_pictures_dir"),
        pytest.param("XDG_VIDEOS_DIR", "user_videos_dir", "Videos", id="user_videos_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", "Music", id="user_music_dir"),
        pytest.param("XDG_DESKTOP_DIR", "user_desktop_dir", "Desktop", id="user_desktop_dir"),
        pytest.param("XDG_PROJECTS_DIR", "user_projects_dir", "Projects", id="user_projects_dir"),
        pytest.param("XDG_PUBLICSHARE_DIR", "user_publicshare_dir", "Public", id="user_publicshare_dir"),
        pytest.param("XDG_TEMPLATES_DIR", "user_templates_dir", "Templates", id="user_templates_dir"),
    ],
)
def test_ensure_exists_creates_configured_media_dir_only(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch,
    user_dirs_file: Path,
    tmp_path: Path,
    posix_tmp_path: str,
    key: str,
    prop: str,
    default: str,
    source: str,
    ensure_exists: bool,
    created: bool,
) -> None:
    monkeypatch.delenv(key, raising=False)
    user_dirs_file.write_text(f'{key}="$HOME/parent/media"\n' if source == "user-dirs" else "", encoding="utf-8")
    if source == "env":
        monkeypatch.setenv(key, f"{posix_tmp_path}/parent/media")
    result = Path(getattr(Unix(ensure_exists=ensure_exists), prop)).absolute()
    assert result == tmp_path / ("parent/media" if source != "default" else default)
    made = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if ".config" not in path.parts)
    assert made == (["parent", "parent/media"] if created else [])


@pytest.mark.skipif(sys.platform == "win32", reason="creating symlinks needs elevated rights on Windows")
@pytest.mark.parametrize(
    ("key", "prop"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
    ],
)
@pytest.mark.parametrize("source", ["env", "user-dirs"])
def test_ensure_exists_returns_dangling_media_symlink(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch, user_dirs_file: Path, tmp_path: Path, key: str, prop: str, source: str
) -> None:
    (link := tmp_path / "media").symlink_to(tmp_path / "unmounted")
    monkeypatch.delenv(key, raising=False)
    user_dirs_file.write_text(f'{key}="$HOME/media"\n' if source == "user-dirs" else "", encoding="utf-8")
    if source == "env":
        monkeypatch.setenv(key, str(link))
    assert getattr(Unix(ensure_exists=True), prop) == str(link)
    assert not link.exists()


def test_iter_data_dirs_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", "/xdg/data")
    monkeypatch.setenv("XDG_DATA_DIRS", f"/xdg/share1{os.pathsep}/xdg/share2")
    dirs = list(Unix().iter_data_dirs())
    assert dirs == ["/xdg/data", "/xdg/share1", "/xdg/share2"]


def test_iter_config_dirs_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/xdg/config")
    monkeypatch.setenv("XDG_CONFIG_DIRS", f"/xdg/etc1{os.pathsep}/xdg/etc2")
    dirs = list(Unix().iter_config_dirs())
    assert dirs == ["/xdg/config", "/xdg/etc1", "/xdg/etc2"]


def test_iter_data_dirs_creates_only_the_consumed_dir(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", f"{posix_tmp_path}/user")
    monkeypatch.setenv("XDG_DATA_DIRS", f"{posix_tmp_path}/site")
    assert Path(next(Unix(ensure_exists=True).iter_data_dirs())) == Path(posix_tmp_path) / "user"
    assert {p.name for p in Path(posix_tmp_path).iterdir()} == {"user"}


@pytest.mark.parametrize(
    ("multipath", "created"),
    [pytest.param(False, {"first"}, id="single"), pytest.param(True, {"first", "second"}, id="multipath")],
)
@pytest.mark.parametrize(
    ("prop", "env_var"), [("site_data_dir", "XDG_DATA_DIRS"), ("site_config_dir", "XDG_CONFIG_DIRS")]
)
def test_site_dir_ensure_exists_creates_only_the_returned_entries(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str, prop: str, env_var: str, multipath: bool, created: set[str]
) -> None:
    monkeypatch.setenv(env_var, f"{posix_tmp_path}/first{os.pathsep}{posix_tmp_path}/second")
    getattr(Unix(appname="acme", multipath=multipath, ensure_exists=True), prop)
    assert {p.name for p in Path(posix_tmp_path).iterdir()} == created


@pytest.mark.parametrize(
    ("prop", "env_var"), [("site_data_path", "XDG_DATA_DIRS"), ("site_config_path", "XDG_CONFIG_DIRS")]
)
def test_site_path_ensure_exists_ignores_multipath(
    monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str, prop: str, env_var: str
) -> None:
    monkeypatch.setenv(env_var, f"{posix_tmp_path}/first{os.pathsep}{posix_tmp_path}/second")
    result = getattr(Unix(appname="acme", multipath=True, ensure_exists=True), prop)
    assert result == Path(posix_tmp_path) / "first" / "acme"
    assert {p.name for p in Path(posix_tmp_path).iterdir()} == {"first"}


@pytest.mark.parametrize(
    ("method", "home_var", "dirs_var"),
    [("iter_data_dirs", "XDG_DATA_HOME", "XDG_DATA_DIRS"), ("iter_config_dirs", "XDG_CONFIG_HOME", "XDG_CONFIG_DIRS")],
)
def test_iter_dirs_create_site_dirs_only_as_consumed(
    monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str, method: str, home_var: str, dirs_var: str
) -> None:
    monkeypatch.setenv(home_var, f"{posix_tmp_path}/user")
    monkeypatch.setenv(dirs_var, f"{posix_tmp_path}/first{os.pathsep}{posix_tmp_path}/second")
    dirs = getattr(Unix(ensure_exists=True), method)()
    assert [Path(next(dirs)), Path(next(dirs))] == [Path(posix_tmp_path) / "user", Path(posix_tmp_path) / "first"]
    assert {p.name for p in Path(posix_tmp_path).iterdir()} == {"user", "first"}


def test_site_data_dir_default_ensure_exists_creates_only_the_first_entry(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    monkeypatch.delenv("XDG_DATA_DIRS", raising=False)
    mkdir = mocker.patch.object(Path, "mkdir", autospec=True)
    result = Unix(appname="acme", ensure_exists=True).site_data_dir
    assert Path(result) == Path("/usr/local/share/acme")
    assert [c.args[0] for c in mkdir.call_args_list] == [Path("/usr/local/share/acme")]


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(os.pathsep, id="single"),
        pytest.param(os.pathsep * 2, id="double"),
        pytest.param(f" {os.pathsep} ", id="padded"),
        pytest.param(f"{os.pathsep} {os.pathsep}", id="spaced"),
        pytest.param("relative/dir", id="relative"),
        pytest.param(f"relative/dir{os.pathsep}another/dir", id="all-relative"),
    ],
)
@pytest.mark.parametrize("prop", ["site_data_dir", "site_config_dir", "site_applications_dir"])
def test_site_dirs_fall_back_when_xdg_var_has_no_absolute_paths(
    monkeypatch: pytest.MonkeyPatch, prop: str, value: str
) -> None:
    monkeypatch.setenv("XDG_CONFIG_DIRS" if prop == "site_config_dir" else "XDG_DATA_DIRS", value)
    expected = {
        "site_data_dir": os.path.join("/usr/local/share", "foo"),  # ruff:ignore[os-path-join]
        "site_config_dir": os.path.join("/etc/xdg", "foo"),  # ruff:ignore[os-path-join]
        "site_applications_dir": os.path.join("/usr/local/share", "applications"),  # ruff:ignore[os-path-join]
    }[prop]
    assert getattr(Unix(appname="foo"), prop) == expected


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize("prop", ["site_data_dir", "site_config_dir", "site_applications_dir"])
@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="singlepath")])
def test_site_dirs_filter_relative_entries(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], prop: str, multipath: bool
) -> None:
    value: typing.Final = os.pathsep.join(("relative", "/custom/first", "", "~/relative", " /custom/second "))
    monkeypatch.setenv("XDG_DATA_DIRS", value)
    monkeypatch.setenv("XDG_CONFIG_DIRS", value)
    suffix: typing.Final = "applications" if prop == "site_applications_dir" else "foo"
    expected: typing.Final = [f"/custom/{name}{os.sep}{suffix}" for name in ("first", "second")]
    assert getattr(dirs_class(appname="foo", multipath=multipath), prop) == (
        os.pathsep.join(expected) if multipath else expected[0]
    )


def test_site_data_dir_multipath_falls_back_when_xdg_var_is_all_separators(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", os.pathsep)
    dirs = [os.path.join("/usr/local/share", "foo"), os.path.join("/usr/share", "foo")]  # ruff:ignore[os-path-join]
    assert Unix(appname="foo", multipath=True).site_data_dir == os.pathsep.join(dirs)


@pytest.mark.usefixtures("_getuid", "runtime_temp_dir")
@pytest.mark.parametrize("prop", ["user_runtime_dir", "site_runtime_dir"])
def test_runtime_dir_rejects_relative_value(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, prop: str) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", "relative/runtime")
    mocker.patch("sys.platform", "linux")
    expected: typing.Final = Path(gettempdir()) / "runtime-1234" if prop == "user_runtime_dir" else Path("/run")
    with _fallback_warning(expected=prop == "user_runtime_dir"):
        assert Path(getattr(Unix(), prop)) == expected


def test_site_applications_path_multipath_returns_first_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", f"/custom/first{os.pathsep}/custom/second")
    assert Unix(multipath=True).site_applications_path == Path("/custom/first/applications")


def test_user_media_dir_from_user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    user_dirs_file = config_dir / "user-dirs.dirs"
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n')
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


def test_user_media_dir_missing_key_in_user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    user_dirs_file = config_dir / "user-dirs.dirs"
    user_dirs_file.write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


def test_user_media_dir_no_user_dirs_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("HOME", "/nonexistent/path")
    monkeypatch.setenv("USERPROFILE", "/nonexistent/path")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert Unix().user_documents_dir == "/nonexistent/path/Documents"


def test_user_dirs_respects_xdg_config_home(posix_tmp_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    custom_config: typing.Final = Path(posix_tmp_path) / "custom_config"
    custom_config.mkdir()
    user_dirs_file = custom_config / "user-dirs.dirs"
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/CustomDocs"\n')
    monkeypatch.setenv("HOME", posix_tmp_path)
    monkeypatch.setenv("USERPROFILE", posix_tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", custom_config.as_posix())
    assert Unix().user_documents_path == Path(posix_tmp_path) / "CustomDocs"


@pytest.fixture
def posix_tmp_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    # Unix paths in Windows tests need the temporary directory's drive as the current drive.
    monkeypatch.chdir(tmp_path)
    return tmp_path.as_posix().removeprefix(tmp_path.drive)


def test_user_dirs_ignores_relative_xdg_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    home_config = tmp_path / ".config"
    home_config.mkdir()
    (home_config / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/HomeDocs"\n')
    rel_config = tmp_path / "relative_config"
    rel_config.mkdir()
    (rel_config / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/RelativeDocs"\n')

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative_config")

    assert Unix().user_documents_dir == f"{tmp_path}/HomeDocs"


_SITE_REDIRECT_CASES: list[tuple[str, str]] = [
    ("user_data_dir", os.path.join("/usr/local/share", "foo")),  # ruff:ignore[os-path-join]
    ("user_config_dir", os.path.join("/etc/xdg", "foo")),  # ruff:ignore[os-path-join]
    ("user_cache_dir", os.path.join("/var/cache", "foo")),  # ruff:ignore[os-path-join]
    ("user_state_dir", os.path.join("/var/lib", "foo")),  # ruff:ignore[os-path-join]
    ("user_log_dir", os.path.join("/var/log", "foo")),  # ruff:ignore[os-path-join]
    (
        "user_runtime_dir",
        os.path.join(  # ruff:ignore[os-path-join]
            "/var/run" if sys.platform.startswith(("freebsd", "openbsd", "netbsd")) else "/run",
            "foo",
        ),
    ),
    ("user_bin_dir", "/usr/local/bin"),
    ("user_applications_dir", f"/usr/local/share{os.sep}applications"),
]
_SITE_RUNTIME_DIR: typing.Final = dict(_SITE_REDIRECT_CASES)["user_runtime_dir"]


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_as_root(prop: str, expected: str) -> None:
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result == expected


@pytest.mark.usefixtures("_as_non_root", "_missing_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_as_non_root(prop: str, expected: str) -> None:
    dirs = Unix(appname="foo", use_site_for_root=True)
    result = getattr(dirs, prop)
    assert result != expected


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize("suffix", ["dir", "path"])
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_reaches_the_module_function(
    mocker: MockerFixture, prop: str, expected: str, suffix: str
) -> None:
    # The module-level functions have to reach every property the site redirect touches.
    mocker.patch("platformdirs.PlatformDirs", Unix)
    function = getattr(platformdirs, prop.removesuffix("dir") + suffix)
    accepted = inspect.Signature.from_callable(function).parameters
    options = {"use_site_for_root": True, "appname": "foo"}
    assert Path(function(**{k: v for k, v in options.items() if k in accepted})) == Path(expected)


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("use_site_for_root", "base"),
    [
        pytest.param(True, "/usr/local/share", id="enable"),
        pytest.param(False, "/home/alice/.local/share", id="disable"),
    ],
)
def test_use_site_for_root_follows_attribute_change(
    monkeypatch: pytest.MonkeyPatch, use_site_for_root: bool, base: str
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", "/home/alice/.local/share")
    dirs: typing.Final = Unix(appname="foo", use_site_for_root=not use_site_for_root)
    dirs.user_data_dir  # ruff:ignore[useless-expression]
    dirs.use_site_for_root = use_site_for_root
    assert dirs.user_data_dir == os.path.join(base, "foo")  # ruff:ignore[os-path-join]


@pytest.mark.usefixtures("_as_root", "_missing_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_disabled_as_root(prop: str, expected: str) -> None:
    dirs = Unix(appname="foo", use_site_for_root=False)
    result = getattr(dirs, prop)
    assert result != expected


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(
    ("xdg_var", "prop", "expected_site"),
    [
        ("XDG_DATA_HOME", "user_data_dir", os.path.join("/usr/local/share", "foo")),  # ruff:ignore[os-path-join]
        ("XDG_CONFIG_HOME", "user_config_dir", os.path.join("/etc/xdg", "foo")),  # ruff:ignore[os-path-join]
        ("XDG_CACHE_HOME", "user_cache_dir", os.path.join("/var/cache", "foo")),  # ruff:ignore[os-path-join]
        ("XDG_STATE_HOME", "user_state_dir", os.path.join("/var/lib", "foo")),  # ruff:ignore[os-path-join]
        ("XDG_STATE_HOME", "user_log_dir", os.path.join("/var/log", "foo")),  # ruff:ignore[os-path-join]
        pytest.param("XDG_RUNTIME_DIR", "user_runtime_dir", _SITE_RUNTIME_DIR, id="XDG_RUNTIME_DIR-user_runtime_dir"),
    ],
)
def test_use_site_for_root_bypasses_xdg_user_vars(
    monkeypatch: pytest.MonkeyPatch, xdg_var: str, prop: str, expected_site: str
) -> None:
    monkeypatch.setenv(xdg_var, "/custom/xdg/path")
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result == expected_site


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("xdg_var", "func"),
    [
        ("XDG_DATA_DIRS", Unix.iter_data_dirs),
        ("XDG_CONFIG_DIRS", Unix.iter_config_dirs),
    ],
)
def test_use_site_iter_dirs_no_duplicates(
    monkeypatch: pytest.MonkeyPatch,
    xdg_var: str,
    func: Callable[[Unix], Iterator[str]],
) -> None:
    monkeypatch.setenv(xdg_var, "/custom/xdg/path")
    result = func(Unix(appname="foo", use_site_for_root=True))
    assert list(result) == [os.path.join("/custom/xdg/path", "foo")]  # ruff:ignore[os-path-join]


_SINGLE_SITE_ITER_CASES = [
    (Unix.iter_cache_dirs, os.path.join("/var/cache", "foo")),  # ruff:ignore[os-path-join]
    (Unix.iter_state_dirs, os.path.join("/var/lib", "foo")),  # ruff:ignore[os-path-join]
    (Unix.iter_log_dirs, os.path.join("/var/log", "foo")),  # ruff:ignore[os-path-join]
    (
        Unix.iter_runtime_dirs,
        os.path.join(  # ruff:ignore[os-path-join]
            "/var/run" if sys.platform.startswith(("freebsd", "openbsd", "netbsd")) else "/run",
            "foo",
        ),
    ),
]


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(("func", "expected"), _SINGLE_SITE_ITER_CASES)
def test_use_site_iter_dirs_no_duplicates_single_site_dir(func: Callable[[Unix], Iterator[str]], expected: str) -> None:
    result = func(Unix(appname="foo", use_site_for_root=True))
    assert list(result) == [expected]


@pytest.mark.usefixtures("_as_root", "_inherited_xdg_runtime_dir")
def test_use_site_iter_runtime_dirs_bypasses_xdg_runtime_dir() -> None:
    assert list(Unix(appname="foo", use_site_for_root=True).iter_runtime_dirs()) == [_SITE_RUNTIME_DIR]


@pytest.mark.usefixtures("_as_root", "_inherited_xdg_runtime_dir")
def test_use_site_keeps_xdg_runtime_dir_for_site_runtime_dir() -> None:
    expected: typing.Final = os.path.join("/run/user/1000", "foo")  # ruff:ignore[os-path-join]
    assert Unix(appname="foo", use_site_for_root=True).site_runtime_dir == expected


@pytest.fixture
def _inherited_xdg_runtime_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/run/user/1000")


@pytest.mark.usefixtures("_as_non_root", "_no_xdg_runtime_dir", "runtime_temp_dir")
@pytest.mark.parametrize(("func", "expected"), _SINGLE_SITE_ITER_CASES)
def test_iter_dirs_as_non_root_keeps_user_dir(func: Callable[[Unix], Iterator[str]], expected: str) -> None:
    # Only an unset XDG_RUNTIME_DIR keeps the user runtime directory apart from the site one, and it warns.
    with _fallback_warning(expected=func is Unix.iter_runtime_dirs):
        result = list(func(Unix(appname="foo", use_site_for_root=True)))
    assert len(result) == 2
    assert result[0] != expected
    assert result[1] == expected


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("xdg_var", "func"),
    [
        ("XDG_CONFIG_DIRS", Unix.iter_config_dirs),
        ("XDG_DATA_DIRS", Unix.iter_data_dirs),
    ],
)
def test_iter_dirs_as_root_with_multipath_skips_joined_user_dir(
    monkeypatch: pytest.MonkeyPatch,
    xdg_var: str,
    func: Callable[[Unix], Iterator[str]],
) -> None:
    monkeypatch.setenv(xdg_var, f"/xdg/a{os.pathsep}/xdg/b")
    # Under multipath the user dir is the joined string, which no single site entry matches.
    assert list(func(Unix(multipath=True, use_site_for_root=True))) == ["/xdg/a", "/xdg/b"]


@pytest.mark.parametrize("uid", [pytest.param(0, id="root"), pytest.param(1000, id="user")], indirect=True)
@pytest.mark.parametrize("use_site_for_root", [pytest.param(True, id="redirect"), pytest.param(False, id="user-dirs")])
@pytest.mark.parametrize("multipath", [pytest.param(True, id="multipath"), pytest.param(False, id="singlepath")])
@pytest.mark.parametrize(
    "prop", ["user_data_path", "user_config_path", "user_preference_path", "user_applications_path"]
)
def test_user_path_site_redirect(
    monkeypatch: pytest.MonkeyPatch,
    uid: int,
    use_site_for_root: bool,
    multipath: bool,
    prop: str,
) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", f"/xdg/a{os.pathsep}/xdg/b")
    monkeypatch.setenv("XDG_CONFIG_DIRS", f"/xdg/a{os.pathsep}/xdg/b")
    monkeypatch.setenv("XDG_DATA_HOME", f"/user/with{os.pathsep}separator")
    monkeypatch.setenv("XDG_CONFIG_HOME", f"/user/with{os.pathsep}separator")
    dirs: typing.Final = Unix(appname="foo", version="1.0", multipath=multipath, use_site_for_root=use_site_for_root)
    base: typing.Final = "/xdg/a" if uid == 0 and use_site_for_root else f"/user/with{os.pathsep}separator"
    assert getattr(dirs, prop) == Path(base) / ("applications" if prop == "user_applications_path" else "foo/1.0")


@pytest.fixture
def uid(request: pytest.FixtureRequest, mocker: MockerFixture) -> int:
    value: typing.Final = typing.cast("int", request.param)
    mocker.patch("platformdirs.unix.getuid", return_value=value)
    return value


def test_iter_runtime_dirs_no_duplicate_with_xdg_runtime_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    # A missing directory skips the ownership check, which a real /run/user/1000 of another user would fail.
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/custom/runtime")
    # $XDG_RUNTIME_DIR backs both the user and the site runtime directory.
    assert list(Unix(appname="foo").iter_runtime_dirs()) == [f"/custom/runtime{os.sep}foo"]


@pytest.mark.parametrize(
    "folder",
    [
        pytest.param("100% complete", id="percent"),
        pytest.param("%(XDG_DESKTOP_DIR)s", id="interpolation-key"),
        pytest.param("100%%", id="double-percent"),
    ],
)
@pytest.mark.parametrize("base", [pytest.param("$HOME", id="home"), pytest.param("/absolute", id="absolute")])
def test_user_dirs_preserves_percent_signs(folder: str, base: str, tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text(
        f'XDG_DOCUMENTS_DIR="{base}/{folder}"\nXDG_DESKTOP_DIR="$HOME/Desktop"\n', encoding="utf-8"
    )
    assert Unix().user_documents_path == Path(tmp_path if base == "$HOME" else base) / folder


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        pytest.param(
            'XDG_DOCUMENTS_DIR="$HOME/Old"\nXDG_DOCUMENTS_DIR="$HOME/New"\n', "~/New", id="last-assignment-wins"
        ),
        pytest.param(
            'XDG_DESKTOP_DIR="$HOME/A"\nXDG_DESKTOP_DIR="$HOME/B"\nXDG_DOCUMENTS_DIR="$HOME/Docs"\n',
            "~/Docs",
            id="other-key-assigned-twice",
        ),
        pytest.param('XDG_DOCUMENTS_DIR="$HOME/Docs"\nnot an assignment\n', "~/Docs", id="stray-line"),
        pytest.param('XDG_DESKTOP_DIR="$HOME/Desktop"\n  XDG_DOCUMENTS_DIR="$HOME/Docs"\n', "~/Docs", id="indented"),
        pytest.param('XDG_DOCUMENTS_DIR="$HOME/Docs" # was "$HOME/Old"\n', "~/Docs", id="trailing-comment"),
        pytest.param(
            'XDG_DOCUMENTS_DIR="$HOME/My \\"Docs\\" \\$1 \\`x\\` a\\\\b"\n',
            r'~/My "Docs" $1 `x` a\b',
            id="shell-escapes",
        ),
        pytest.param('XDG_DOCUMENTS_DIR="/data/$HOMEWORK"\n', "/data/$HOMEWORK", id="home-only-as-prefix"),
        pytest.param('XDG_DOCUMENTS_DIR="$HOMEWORK/Docs"\n', "~/Documents", id="home-prefix-needs-slash"),
        pytest.param('XDG_DOCUMENTS_DIR="$HOME"\n', "~", id="home-itself"),
        pytest.param('XDG_DOCUMENTS_DIR="Docs"\n', "~/Documents", id="relative-ignored"),
        pytest.param(
            'XDG_DOCUMENTS_DIR="$HOME/Docs"\nXDG_DOCUMENTS_DIR="Docs"\n', "~/Docs", id="relative-reassignment-ignored"
        ),
        pytest.param('XDG_DOCUMENTS_DIR="$HOME/Docs\n', "~/Documents", id="unterminated-ignored"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs\n", "~/Docs", id="unquoted"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs # moved\n", "~/Docs", id="unquoted-trailing-comment"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs\t#moved\n", "~/Docs", id="unquoted-tab-comment"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs#1\n", "~/Docs#1", id="unquoted-hash-inside-word"),
    ],
)
def test_user_dirs_read_like_xdg_user_dir(content: str, expected: str, tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text(content, encoding="utf-8")
    assert Unix().user_documents_dir == expected.replace("~", str(tmp_path), 1)


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        pytest.param(b'XDG_MUSIC_DIR="$HOME/M\xfasica"\nXDG_DOCUMENTS_DIR="$HOME/Docs"\n', "~/Docs", id="other-entry"),
        pytest.param(b'XDG_DOCUMENTS_DIR="$HOME/Dok\xfament"\n', "~/Dok\udcfament", id="requested-entry"),
    ],
)
def test_user_dirs_undecodable_bytes(content: bytes, expected: str, tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_bytes(content)
    assert Unix().user_documents_dir == expected.replace("~", str(tmp_path), 1)


@pytest.fixture
def user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (config := tmp_path / ".config").mkdir()
    return config / "user-dirs.dirs"


_APP_COMPONENTS: typing.Final = ["home", "home/base", "home/base/app", "home/base/app/1.0"]


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
@pytest.mark.parametrize(
    ("prop", "env_var"),
    [
        pytest.param("user_data_dir", "XDG_DATA_HOME", id="data"),
        pytest.param("user_config_dir", "XDG_CONFIG_HOME", id="config"),
        pytest.param("user_cache_dir", "XDG_CACHE_HOME", id="cache"),
        pytest.param("user_state_dir", "XDG_STATE_HOME", id="state"),
        pytest.param("user_runtime_dir", "XDG_RUNTIME_DIR", id="runtime"),
        pytest.param("user_preference_dir", "XDG_CONFIG_HOME", id="preference"),
    ],
)
def test_unix_user_dir_creates_missing_components_private(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, modes: Callable[[Path], dict[str, int]], prop: str, env_var: str
) -> None:
    monkeypatch.setenv(env_var, str(tmp_path / "home" / "base"))
    getattr(Unix(appname="app", version="1.0", ensure_exists=True), prop)
    assert modes(tmp_path) == dict.fromkeys(_APP_COMPONENTS, 0o700)


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
def test_unix_user_log_dir_creates_missing_components_private(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, modes: Callable[[Path], dict[str, int]]
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "home" / "base"))
    _ = Unix(appname="app", version="1.0", ensure_exists=True).user_log_dir
    assert modes(tmp_path) == dict.fromkeys([*_APP_COMPONENTS, "home/base/app/1.0/log"], 0o700)


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_clear_xdg_env", "_umask")
def test_unix_default_config_dir_creates_dot_config_private(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, modes: Callable[[Path], dict[str, int]]
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    _ = Unix(appname="app", ensure_exists=True).user_config_dir
    assert modes(tmp_path) == {".config": 0o700, ".config/app": 0o700}


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
@pytest.mark.parametrize(
    ("prop", "env_var"),
    [
        pytest.param("site_data_dir", "XDG_DATA_DIRS", id="site-data"),
        pytest.param("site_config_dir", "XDG_CONFIG_DIRS", id="site-config"),
        pytest.param("site_runtime_dir", "XDG_RUNTIME_DIR", id="site-runtime"),
        pytest.param("user_documents_dir", "XDG_DOCUMENTS_DIR", id="media"),
    ],
)
def test_unix_shared_dir_keeps_default_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, modes: Callable[[Path], dict[str, int]], prop: str, env_var: str
) -> None:
    monkeypatch.setenv(env_var, str(tmp_path / "shared"))
    getattr(Unix(ensure_exists=True), prop)
    assert modes(tmp_path) == {"shared": 0o755}


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
@pytest.mark.parametrize(
    ("existing", "expected"),
    [
        pytest.param(["base"], {"base": 0o751, "base/app": 0o700}, id="existing-base"),
        pytest.param(["base", "base/app"], {"base": 0o751, "base/app": 0o751}, id="existing-app-dir"),
    ],
)
def test_unix_user_dir_leaves_existing_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    modes: Callable[[Path], dict[str, int]],
    existing: list[str],
    expected: dict[str, int],
) -> None:
    for name in existing:
        (path := tmp_path / name).mkdir()
        path.chmod(0o751)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "base"))
    _ = Unix(appname="app", ensure_exists=True).user_data_dir
    assert modes(tmp_path) == expected
