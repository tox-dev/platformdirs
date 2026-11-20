from __future__ import annotations

import contextlib
import errno
import importlib
import inspect
import os
import re
import stat
import sys
import time
import typing
import warnings
from operator import attrgetter, methodcaller
from pathlib import Path
from tempfile import gettempdir
from types import MappingProxyType

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
    importlib.reload(sys.modules["platformdirs._runtime"])
    importlib.reload(unix)


@pytest.fixture
def _as_root(mocker: MockerFixture, _clear_xdg_env: None) -> None:
    mocker.patch("platformdirs.unix.geteuid", return_value=0, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=0, autospec=True)


@pytest.fixture
def _as_non_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.geteuid", return_value=1000, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=1000, autospec=True)


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
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder", autospec=True)
    example_path = "/home/example/ExampleMediaFolder"
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
    mocker.patch("platformdirs.unix._get_user_dirs_folder", autospec=True).return_value = None

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
    mocker.patch("platformdirs.unix._get_user_dirs_folder", autospec=True).return_value = None

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
    mocker.patch("platformdirs.unix._get_user_dirs_folder", autospec=True).return_value = None

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


@pytest.fixture
def dirs_instance() -> Unix:
    return Unix(multipath=True, opinion=False)


@pytest.fixture
def _geteuid(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.geteuid", return_value=1234, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=1234, autospec=True)


class XDGVariable(typing.NamedTuple):
    name: str
    default_value: str


_XDG_VARIABLES: typing.Final[MappingProxyType[str, XDGVariable]] = MappingProxyType({
    "user_data_dir": XDGVariable("XDG_DATA_HOME", "~/.local/share"),
    "site_data_dir": XDGVariable("XDG_DATA_DIRS", f"/usr/local/share{os.pathsep}/usr/share"),
    "user_config_dir": XDGVariable("XDG_CONFIG_HOME", "~/.config"),
    "site_config_dir": XDGVariable("XDG_CONFIG_DIRS", "/etc/xdg"),
    "user_cache_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
    "user_state_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
    "user_log_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
    "user_runtime_dir": XDGVariable("XDG_RUNTIME_DIR", f"{gettempdir()}/runtime-1234"),
    "site_runtime_dir": XDGVariable(
        "XDG_RUNTIME_DIR", "/var/run" if sys.platform.startswith(("freebsd", "openbsd", "netbsd")) else "/run"
    ),
})
_XDG_CASES: typing.Final[list[tuple[str, XDGVariable]]] = list(_XDG_VARIABLES.items())


@pytest.mark.usefixtures("_geteuid")
@pytest.mark.parametrize(("func", "xdg_variable"), _XDG_CASES, ids=list(_XDG_VARIABLES))
def test_xdg_variable_not_set(
    monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str, xdg_variable: XDGVariable
) -> None:
    monkeypatch.delenv(xdg_variable.name, raising=False)
    with _fallback_warning(expected=func == "user_runtime_dir"):
        result = getattr(dirs_instance, func)
    # match tested expansion
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


def _fallback_warning(*, expected: bool) -> contextlib.AbstractContextManager[pytest.WarningsRecorder | None]:
    if expected:
        return pytest.warns(RuntimeDirWarning, match="^XDG_RUNTIME_DIR is not set, falling back to ")
    return contextlib.nullcontext()


@pytest.mark.usefixtures("_geteuid")
@pytest.mark.parametrize(("func", "xdg_variable"), _XDG_CASES, ids=list(_XDG_VARIABLES))
def test_xdg_variable_empty_value(
    monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str, xdg_variable: XDGVariable
) -> None:
    monkeypatch.setenv(xdg_variable.name, "")
    with _fallback_warning(expected=func == "user_runtime_dir"):
        result = getattr(dirs_instance, func)
    # match tested expansion
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


@pytest.mark.usefixtures("_geteuid")
@pytest.mark.parametrize(("func", "xdg_variable"), _XDG_CASES, ids=list(_XDG_VARIABLES))
def test_xdg_variable_custom_value(
    monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str, xdg_variable: XDGVariable
) -> None:
    monkeypatch.setenv(xdg_variable.name, "/custom-dir")
    result = getattr(dirs_instance, func)
    assert result == "/custom-dir"


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize(
    "kind",
    [
        pytest.param("data", id="data"),
        pytest.param("config", id="config"),
        pytest.param("cache", id="cache"),
        pytest.param("state", id="state"),
    ],
)
@pytest.mark.parametrize("whitespace", [pytest.param(" ", id="space"), pytest.param("\t", id="tab")])
def test_xdg_home_preserves_trailing_whitespace(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], kind: str, whitespace: str
) -> None:
    home: typing.Final[str] = f"/xdg-fixture/home{whitespace}"
    monkeypatch.setenv(f"XDG_{kind.upper()}_HOME", home)
    assert getattr(dirs_class(appname="demo"), f"user_{kind}_dir") == f"{home}{os.sep}demo"


@pytest.mark.usefixtures("_clear_xdg_env")
@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize(
    "kind",
    [
        pytest.param("data", id="data"),
        pytest.param("config", id="config"),
        pytest.param("cache", id="cache"),
        pytest.param("state", id="state"),
    ],
)
def test_xdg_home_rejects_leading_whitespace(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], kind: str
) -> None:
    expected: typing.Final[str] = getattr(dirs_class(appname="demo"), f"user_{kind}_dir")
    monkeypatch.setenv(f"XDG_{kind.upper()}_HOME", " /xdg-fixture/home")
    assert getattr(dirs_class(appname="demo"), f"user_{kind}_dir") == expected


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
def test_xdg_media_preserves_trailing_whitespace(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS]
) -> None:
    monkeypatch.setenv("XDG_DOCUMENTS_DIR", "/xdg-fixture/documents ")
    assert dirs_class().user_documents_dir == "/xdg-fixture/documents "


@pytest.mark.usefixtures("_geteuid")
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
    assert result == os.path.join("/var/log", "foo")  # ruff:ignore[os-path-join]  # match host separators


def test_site_state_dir_fixed_path() -> None:
    result = Unix(appname="foo").site_state_dir
    assert result == os.path.join("/var/lib", "foo")  # ruff:ignore[os-path-join]  # match host separators


def test_site_cache_path_multipath_keeps_path_separator_in_app_arguments() -> None:
    # Debian epoch versions such as 1:2 contain os.pathsep
    dirs = Unix(appname=f"org{os.pathsep}app", version=f"1{os.pathsep}2", multipath=True)
    assert dirs.site_cache_path == Path("/var/cache", f"org{os.pathsep}app", f"1{os.pathsep}2")


@pytest.mark.parametrize("prop", ["site_data_dir", "site_config_dir"])
@pytest.mark.parametrize(
    ("appname", "version"),
    [
        pytest.param(f"x{os.pathsep}/etc/evil", None, id="appname"),
        pytest.param("foo", f"1{os.pathsep}/etc/evil", id="version"),
    ],
)
def test_site_dir_multipath_rejects_path_separator_in_app_arguments(
    prop: str, appname: str, version: str | None
) -> None:
    with pytest.raises(ValueError, match="multipath cannot join"):
        getattr(Unix(appname=appname, version=version, multipath=True), prop)


def test_site_dir_multipath_rejects_path_separator_before_creating(
    monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str
) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", f"{posix_tmp_path}/site")
    with pytest.raises(ValueError, match="multipath cannot join"):
        _ = Unix(appname=f"x{os.pathsep}y", multipath=True, ensure_exists=True).site_data_dir
    assert not Path(posix_tmp_path, "site").exists()


@pytest.mark.usefixtures("_geteuid")
@pytest.mark.parametrize("platform", [pytest.param("freebsd", id="freebsd"), pytest.param("netbsd", id="netbsd")])
def test_freebsd_netbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    assert Unix().site_runtime_dir == "/var/run"


@pytest.mark.usefixtures("_geteuid")
def test_openbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "openbsd")
    assert Unix().site_runtime_dir == "/var/run"


def test_platform_on_win32(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "win32")
    prev_unix = unix
    importlib.reload(sys.modules["platformdirs._runtime"])
    importlib.reload(unix)
    try:
        with pytest.raises(RuntimeError, match="should only be used on Unix"):
            unix.Unix().user_runtime_dir  # ruff:ignore[useless-expression]  # property access raises
    finally:
        sys.modules["platformdirs.unix"] = prev_unix


@pytest.mark.parametrize("uid", [0, 1234])
def test_platform_without_geteuid(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, runtime_temp_dir: Path, uid: int
) -> None:
    monkeypatch.setattr(sys, "platform", "emscripten")
    monkeypatch.delattr(os, "geteuid", raising=False)
    getuid = mocker.patch(  # simplint: ignore[mock-without-spec]  # getuid absent on Windows
        "os.getuid", return_value=uid, create=True
    )
    importlib.reload(sys.modules["platformdirs._runtime"])
    importlib.reload(unix)

    # Match the temporary tree's owner to the simulated platform credentials.
    original = os.lstat

    def owned(path: str | Path) -> os.stat_result:
        info = original(path)
        return os.stat_result((*info[:4], uid, *info[5:]))

    mocker.patch.object(os, "lstat", new=owned)
    assert unix.geteuid is getuid
    dirs = unix.Unix(appname="app")
    with _fallback_warning(expected=True):
        assert Path(dirs.user_runtime_dir) == runtime_temp_dir / f"runtime-{uid}" / "app"
    config_dir = unix.Unix(appname="app", use_site_for_root=True).user_config_dir
    assert Path(config_dir) == Path({0: "/etc/xdg/app"}.get(uid, dirs.user_config_dir))


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.parametrize(
    ("existing_mode", "ensure_exists", "expected_mode"),
    [
        pytest.param(None, True, 0o700, id="created-private"),
        pytest.param(0o775, True, 0o700, id="group-writable-tightened"),
        pytest.param(0o775, False, 0o775, id="group-writable-lookup"),
        pytest.param(0o755, True, 0o700, id="loose-mode-tightened"),
        pytest.param(0o755, False, 0o755, id="loose-mode-untouched-without-ensure-exists"),
    ],
)
def test_user_runtime_dir_temp_fallback_mode(
    mocker: MockerFixture, runtime_temp_dir: Path, existing_mode: int | None, ensure_exists: bool, expected_mode: int
) -> None:
    mocker.patch("platformdirs.unix.geteuid", return_value=(uid := runtime_temp_dir.stat().st_uid), autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=uid, autospec=True)
    base: typing.Final[Path] = runtime_temp_dir / f"runtime-{uid}"
    if existing_mode is not None:  # simplint: ignore[conditional-in-test]  # existing directory case
        base.mkdir()
        base.chmod(existing_mode)
    with pytest.warns(RuntimeDirWarning, match=f"^XDG_RUNTIME_DIR is not set, falling back to {re.escape(str(base))}$"):
        _ = Unix(appname="foo", ensure_exists=ensure_exists).user_runtime_dir
    assert stat.S_IMODE(base.stat().st_mode) == expected_mode


@pytest.mark.parametrize("ensure_exists", [pytest.param(True, id="ensure-exists"), pytest.param(False, id="lookup")])
def test_user_runtime_dir_temp_fallback_rejects_other_owner(
    mocker: MockerFixture, runtime_temp_dir: Path, ensure_exists: bool
) -> None:
    owner: typing.Final[int] = runtime_temp_dir.stat().st_uid
    (runtime_temp_dir / f"runtime-{owner + 1}").mkdir()
    mocker.patch("platformdirs.unix.geteuid", return_value=owner + 1, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=owner + 1, autospec=True)
    with pytest.raises(PermissionError, match=f"owned by uid {owner},"):
        # property access raises
        Unix(appname="foo", ensure_exists=ensure_exists).user_runtime_dir  # ruff:ignore[useless-expression]


@pytest.mark.usefixtures("_geteuid", "runtime_temp_dir")
@pytest.mark.parametrize(
    ("temp", "expected"),
    [
        pytest.param("/", "/runtime-1234", id="root"),
        pytest.param("{root}/", "{root}/runtime-1234", id="trailing-slash"),
    ],
)
def test_user_runtime_dir_temp_fallback_single_slash(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, runtime_temp_dir: Path, temp: str, expected: str
) -> None:
    temp = temp.format(root=runtime_temp_dir)
    expected = expected.format(root=runtime_temp_dir)
    monkeypatch.setenv("TMPDIR", temp)
    mocker.patch("tempfile.tempdir", temp)
    with pytest.warns(RuntimeDirWarning, match=f"^XDG_RUNTIME_DIR is not set, falling back to {re.escape(expected)}$"):
        assert Unix().user_runtime_dir == expected


_POSIX_ONLY: typing.Final[pytest.MarkDecorator] = pytest.mark.skipif(
    sys.platform == "win32", reason="Windows has no POSIX owners or modes"
)


@_POSIX_ONLY
@pytest.mark.parametrize("cwd", [pytest.param(".", id="current"), pytest.param("..", id="cached")])
def test_user_runtime_dir_rejects_cwd_temp_fallback(
    runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, cwd: str
) -> None:
    for name in ("TMPDIR", "TEMP", "TMP"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(runtime_temp_dir / cwd)
    mocker.patch("platformdirs.unix.TemporaryFile", autospec=True, side_effect=PermissionError)
    with pytest.raises(PermissionError, match="no safe temporary directory"):
        _ = Unix(appname="app").user_runtime_dir


@_POSIX_ONLY
def test_user_runtime_dir_rejects_relative_temp_setting(
    runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    monkeypatch.chdir(runtime_temp_dir)
    monkeypatch.setenv("TMPDIR", "relative")
    mocker.patch("tempfile.tempdir", "relative")
    mocker.patch("platformdirs.unix.TemporaryFile", autospec=True, side_effect=PermissionError)
    with pytest.raises(PermissionError, match="no safe temporary directory"):
        _ = Unix(appname="app").user_runtime_dir


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_user_runtime_dir_uses_new_absolute_temp_setting(
    runtime_temp_dir: Path, runtime_uid: int, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    (old := runtime_temp_dir / "old").mkdir()
    (new := runtime_temp_dir / "new").mkdir()
    mocker.patch("tempfile.tempdir", str(old))
    monkeypatch.setenv("TMPDIR", str(new))
    assert Unix(appname="app").user_runtime_dir == str(new / f"runtime-{runtime_uid}" / "app")


_PROBLEMS: typing.Final[MappingProxyType[str, str]] = MappingProxyType({
    "symlink": "is a symlink",
    "file": "is not a directory",
    "mode-755": "has mode 0755, not 0700",
    "mode-500": "has mode 0500, not 0700",
})
_UNREACHABLE: typing.Final[MappingProxyType[str, str]] = MappingProxyType({
    "file": os.strerror(errno.ENOTDIR),
    "symlink-loop": os.strerror(errno.ELOOP),
})
_DEFAULT_PREFIXES: typing.Final[MappingProxyType[str, str]] = MappingProxyType({
    "linux": "run/user",
    "freebsd": "var/run/user",
    "netbsd": "var/run/user",
    "openbsd": "tmp/run/user",
})


@_POSIX_ONLY
def test_user_runtime_dir_temp_fallback_named_after_effective_uid(
    mocker: MockerFixture, runtime_temp_dir: Path
) -> None:
    owner: typing.Final[int] = runtime_temp_dir.stat().st_uid
    mocker.patch("os.getuid", return_value=owner + 1, autospec=True)
    mocker.patch("os.geteuid", return_value=owner, autospec=True)
    importlib.reload(unix)
    with pytest.warns(RuntimeDirWarning):
        result = unix.Unix(appname="foo").user_runtime_dir
    assert result == f"{runtime_temp_dir}/runtime-{owner}/foo"


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_uses_private_xdg_runtime_dir(session_dir: Path) -> None:
    _create(session_dir, "private")
    assert Unix(appname="app").user_runtime_dir == str(session_dir / "app")


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
        case "symlink-loop":
            path.symlink_to(path)


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
    expected: typing.Final[str] = (
        f"XDG_RUNTIME_DIR {session_dir} {_PROBLEMS[kind]}, falling back to /run/user/{runtime_uid}"
    )
    assert [str(warning.message) for warning in record] == [expected]


_TRAILING_SEPARATORS: typing.Final[list[str]] = ["/", "//", "/.", "/./"]


@_POSIX_ONLY
@pytest.mark.parametrize("suffix", _TRAILING_SEPARATORS)
def test_runtime_dir_symlink_xdg_runtime_dir_with_trailing_separator_warns(
    session_dir: Path, default_dir: Path, runtime_uid: int, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    _create(session_dir, "symlink")
    _create(default_dir, "private")
    monkeypatch.setenv("XDG_RUNTIME_DIR", f"{session_dir}{suffix}")
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    expected: typing.Final[str] = (
        f"XDG_RUNTIME_DIR {session_dir}{suffix} is a symlink, falling back to /run/user/{runtime_uid}"
    )
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.usefixtures("default_dir")
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize("suffix", _TRAILING_SEPARATORS)
def test_runtime_dir_symlink_xdg_runtime_dir_with_trailing_separator_creates_nothing(
    session_dir: Path, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    _create(session_dir, "symlink")
    monkeypatch.setenv("XDG_RUNTIME_DIR", f"{session_dir}{suffix}")
    _ = Unix(appname="app", ensure_exists=True).user_runtime_dir
    assert list(session_dir.iterdir()) == []


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_private_xdg_runtime_dir_with_trailing_separator(
    session_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create(session_dir, "private")
    monkeypatch.setenv("XDG_RUNTIME_DIR", f"{session_dir}/")
    assert Unix(appname="app").user_runtime_dir == str(session_dir / "app")


@_POSIX_ONLY
def test_runtime_dir_xdg_runtime_dir_of_other_user_warns(
    session_dir: Path, runtime_temp_dir: Path, mocker: MockerFixture
) -> None:
    _create(session_dir, "private")
    owner: typing.Final[int] = session_dir.stat().st_uid
    mocker.patch("platformdirs.unix.geteuid", return_value=owner + 1, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=owner + 1, autospec=True)
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app").user_runtime_dir
    fallback: typing.Final[Path] = runtime_temp_dir / f"runtime-{owner + 1}"
    expected: typing.Final[str] = (
        f"XDG_RUNTIME_DIR {session_dir} is owned by uid {owner}, not {owner + 1}, falling back to {fallback}"
    )
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.parametrize("kind", list(_UNREACHABLE))
@pytest.mark.parametrize("ensure_exists", [pytest.param(False, id="lazy"), pytest.param(True, id="ensure-exists")])
def test_runtime_dir_unreachable_xdg_runtime_dir_warns(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch, kind: str, ensure_exists: bool
) -> None:
    _create(blocker := runtime_temp_dir / "blocker", kind)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(blocker / "session"))
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app", ensure_exists=ensure_exists).user_runtime_dir == str(temp_dir / "app")
    expected: typing.Final[str] = (
        f"XDG_RUNTIME_DIR {blocker / 'session'} cannot be checked: {_UNREACHABLE[kind]}, falling back to {temp_dir}"
    )
    assert [str(warning.message) for warning in record] == [expected]
    assert (temp_dir / "app").is_dir() is ensure_exists


@_POSIX_ONLY
@pytest.mark.parametrize("kind", ["symlink", "private"])
def test_runtime_dir_parent_of_other_user_in_shared_dir_warns(
    shared_dir: Path, temp_dir: Path, runtime_uid: int, foreign: set[Path], kind: str
) -> None:
    _create(planted := shared_dir / "run", kind)
    foreign.add(planted)
    with pytest.warns(RuntimeDirWarning) as record:
        _ = Unix(appname="app", ensure_exists=True).user_runtime_dir
    expected: typing.Final[str] = (
        f"XDG_RUNTIME_DIR {planted / 'user'} is below {planted}, owned by uid {runtime_uid + 1}, "
        f"falling back to {temp_dir}"
    )
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
def test_runtime_dir_parent_owned_by_other_user_warns(
    runtime_temp_dir: Path, temp_dir: Path, runtime_uid: int, foreign: set[Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    (other := runtime_temp_dir / "other").mkdir(mode=0o755)
    foreign.add(other)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(session := other / "session"))
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")
    assert [str(warning.message) for warning in record] == [
        f"XDG_RUNTIME_DIR {session} is below {other}, owned by uid {runtime_uid + 1}, falling back to {temp_dir}"
    ]


@_POSIX_ONLY
def test_runtime_dir_unreadable_parent_warns(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    (blocked := runtime_temp_dir / "blocked").mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(session := blocked / "session"))
    original_lstat = os.lstat

    def unreadable(path: str | os.PathLike[str]) -> os.stat_result:
        if Path(path) == blocked:
            raise OSError(errno.EIO, os.strerror(errno.EIO), str(path))
        return original_lstat(path)

    mocker.patch(  # simplint: ignore[mock-without-spec]  # runtime_temp_dir already wraps os.lstat
        "os.lstat", side_effect=unreadable
    )
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")
    assert [str(warning.message) for warning in record] == [
        (
            f"XDG_RUNTIME_DIR {session} is below {blocked} cannot be checked: {os.strerror(errno.EIO)}, "
            f"falling back to {temp_dir}"
        )
    ]


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize(
    ("ensure_exists", "access"),
    [
        pytest.param(True, attrgetter("user_runtime_dir"), id="ensure-exists"),
        pytest.param(False, methodcaller("place_runtime_file", "app.sock"), id="place-runtime-file"),
    ],
)
def test_runtime_dir_parent_of_other_user_in_shared_dir_creates_nothing(
    shared_dir: Path, foreign: set[Path], ensure_exists: bool, access: Callable[[Unix], str | Path]
) -> None:
    _create(planted := shared_dir / "run", "symlink")
    foreign.add(planted)
    access(Unix(appname="app", ensure_exists=ensure_exists))
    assert not list((shared_dir / "run-target").iterdir())


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid")
@pytest.mark.filterwarnings("error::platformdirs.RuntimeDirWarning")
def test_runtime_dir_own_parent_in_shared_dir_is_used(shared_dir: Path) -> None:
    _create(shared_dir / "run", "private")
    assert Unix(appname="app", ensure_exists=True).user_runtime_dir == str(shared_dir / "run" / "user" / "app")


@_POSIX_ONLY
def test_runtime_rechecks_parent_after_creation(
    shared_dir: Path, temp_dir: Path, foreign: set[Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    mkdir = Path.mkdir

    def changed(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)
        if path == shared_dir / "run/user":
            foreign.add(path.parent)

    monkeypatch.setattr(Path, "mkdir", changed)
    with pytest.warns(RuntimeDirWarning, match=re.escape(f"is below {shared_dir / 'run'}, owned by")):
        assert Unix("app", ensure_exists=True).user_runtime_path == temp_dir / "app"


@_POSIX_ONLY
def test_runtime_checks_parents_of_symlink_target(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = runtime_temp_dir / "shared"
    (target := parent / "private").mkdir(parents=True)
    parent.chmod(0o777)
    (link := runtime_temp_dir / "linked").symlink_to(target)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(link / "runtime"))
    with pytest.warns(RuntimeDirWarning, match=re.escape(f"is below {parent}, writable")):
        assert Unix("app").user_runtime_path == temp_dir / "app"


@_POSIX_ONLY
def test_runtime_dir_sticky_parent_of_other_user_warns(
    shared_dir: Path, temp_dir: Path, runtime_uid: int, mocker: MockerFixture
) -> None:
    info = shared_dir.stat()
    original_lstat = os.lstat
    other_owner = os.stat_result((*info[:4], runtime_uid + 1, *info[5:]))
    mocker.patch(  # simplint: ignore[mock-without-spec]  # runtime_temp_dir already wraps os.lstat
        "os.lstat",
        side_effect=lambda path, **kwargs: other_owner if Path(path) == shared_dir else original_lstat(path, **kwargs),
    )
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")
    assert [str(warning.message) for warning in record] == [
        (
            f"XDG_RUNTIME_DIR {shared_dir / 'run' / 'user'} is below {shared_dir}, "
            f"owned by uid {runtime_uid + 1}, falling back to {temp_dir}"
        )
    ]


@_POSIX_ONLY
def test_runtime_dir_parent_writable_by_everyone_warns(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (open_dir := runtime_temp_dir / "open").mkdir()
    open_dir.chmod(0o777)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(session := open_dir / "session"))
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")
    assert [str(warning.message) for warning in record] == [
        f"XDG_RUNTIME_DIR {session} is below {open_dir}, writable by another user, falling back to {temp_dir}"
    ]


@_POSIX_ONLY
def test_runtime_dir_parent_writable_by_group_warns(
    runtime_temp_dir: Path, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (shared := runtime_temp_dir / "shared").mkdir()
    shared.chmod(0o770)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(session := shared / "session"))
    with pytest.warns(RuntimeDirWarning) as record:
        assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")
    assert [str(warning.message) for warning in record] == [
        f"XDG_RUNTIME_DIR {session} is below {shared}, writable by another user, falling back to {temp_dir}"
    ]


@pytest.fixture
def shared_dir(runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # Sticky and writable by every user, like /tmp, with XDG_RUNTIME_DIR two levels below it.
    (path := runtime_temp_dir / "shared").mkdir()
    path.chmod(0o1777)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(path / "run" / "user"))
    return path


@pytest.fixture
def foreign(runtime_uid: int, mocker: MockerFixture, tmp_path: Path) -> set[Path]:
    # Creating a file as another user needs root, so report the paths added here as owned by another uid.
    paths: set[Path] = set()
    lstat: typing.Final[Callable[[str | Path], os.stat_result]] = os.lstat
    mocker.patch(  # simplint: ignore[mock-without-spec]  # autospec cannot wrap a patched os.lstat
        "os.lstat",
        side_effect=lambda path: (
            os.stat_result((*(info := lstat(path))[:4], runtime_uid + 1, *info[5:]))
            if Path(path) in paths
            else lstat(path)
        ),
    )
    # fs.protected_symlinks refuses even root to follow another user's symlink in a sticky directory as the last
    # component, so following one fails here the way following a symlink loop does.
    (loop := tmp_path / "loop").symlink_to(loop)
    follow = os.stat
    mocker.patch(
        "os.stat",
        autospec=True,
        side_effect=lambda path, **kwargs: follow(
            loop if Path(path) in paths and stat.S_ISLNK(lstat(path).st_mode) else path, **kwargs
        ),
    )
    return paths


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
    expected: typing.Final[str] = f"XDG_RUNTIME_DIR is not set, falling back to /run/user/{runtime_uid}"
    assert [str(warning.message) for warning in record] == [expected]


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize("platform", list(_DEFAULT_PREFIXES))
@pytest.mark.parametrize(
    "kind",
    [*(pytest.param(kind, id=kind) for kind in _PROBLEMS), pytest.param("missing", id="missing")],
)
def test_runtime_dir_invalid_default_dir_falls_back(default_dir: Path, temp_dir: Path, kind: str) -> None:
    _create(default_dir, kind)
    assert Unix(appname="app").user_runtime_dir == str(temp_dir / "app")


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_runtime_dir_default_dir_of_other_user_falls_back(
    runtime_temp_dir: Path, system_root: Path, mocker: MockerFixture
) -> None:
    mocker.patch("sys.platform", "linux")
    owner: typing.Final[int] = runtime_temp_dir.stat().st_uid
    _create(system_root / "run" / "user" / str(owner + 1), "private")
    mocker.patch("platformdirs.unix.geteuid", return_value=owner + 1, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=owner + 1, autospec=True)
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
    dirs: typing.Final[Unix] = Unix(appname="app")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(3):
            _ = dirs.user_runtime_dir
        _ = Unix(appname="other").user_runtime_dir
    expected: typing.Final[str] = f"XDG_RUNTIME_DIR is not set, falling back to {temp_dir}"
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
    mocker.patch("platformdirs.unix.geteuid", return_value=0, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=0, autospec=True)
    mocker.patch("sys.platform", "linux")
    assert Unix(appname="app", use_site_for_root=True).user_runtime_dir == "/run/app"


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize(
    "create",
    [
        pytest.param(lambda: Unix(appname="app", ensure_exists=True).user_runtime_dir, id="ensure-exists"),
        pytest.param(lambda: Unix(appname="app").place_runtime_file("app.sock"), id="place"),
    ],
)
def test_runtime_dir_temp_fallback_rejects_dir_hidden_from_check(
    mocker: MockerFixture, temp_dir: Path, create: Callable[[], object]
) -> None:
    _hide_during_check(mocker, temp_dir)
    with pytest.raises(PermissionError, match=f"^runtime directory {re.escape(str(temp_dir))} is missing; set "):
        create()


def _hide_during_check(mocker: MockerFixture, base: Path) -> None:
    # Move ``base`` away for each lstat of it, as its owner can in a shared sticky directory.
    lstat: typing.Final[Callable[[str], os.stat_result]] = os.lstat
    _create(base, "private")

    def hide(path: str) -> os.stat_result:
        if path != str(base):
            return lstat(path)
        base.rename(hidden := base.with_name(f"{base.name}-hidden"))
        try:
            return lstat(path)
        finally:
            hidden.rename(base)

    mocker.patch(  # simplint: ignore[mock-without-spec]  # autospec cannot wrap a patched os.lstat
        "os.lstat", side_effect=hide
    )


@_POSIX_ONLY
@pytest.mark.usefixtures("temp_dir")
def test_runtime_dir_xdg_runtime_dir_hidden_from_check_warns(mocker: MockerFixture, session_dir: Path) -> None:
    _hide_during_check(mocker, session_dir)
    with pytest.warns(RuntimeDirWarning, match=f"^XDG_RUNTIME_DIR {re.escape(str(session_dir))} is missing, falling"):
        _ = Unix(appname="app", ensure_exists=True).user_runtime_dir


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_place_runtime_file_creates_runtime_dir_before_check(mocker: MockerFixture, runtime_base: Path) -> None:
    _plant_after_check(mocker, runtime_base)
    Unix(appname="app").place_runtime_file("app.sock")
    assert not runtime_base.is_symlink()


def _plant_after_check(mocker: MockerFixture, base: Path) -> None:
    # Link ``base`` to a directory with ``app/app.sock`` once an lstat finds it missing, as another user can.
    lstat: typing.Final[Callable[[str], os.stat_result]] = os.lstat

    def plant(path: str) -> os.stat_result:
        try:
            return lstat(path)
        except FileNotFoundError:
            if path == str(base):
                _create(base, "symlink")
                (base / "app").mkdir()
                (base / "app" / "app.sock").touch()
            raise

    mocker.patch(  # simplint: ignore[mock-without-spec]  # autospec cannot wrap a patched os.lstat
        "os.lstat", side_effect=plant
    )


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_find_runtime_file_returns_file_in_own_runtime_dir(runtime_base: Path) -> None:
    Unix(appname="app").place_runtime_file("app.sock").touch()
    assert Unix(appname="app").find_runtime_file("app.sock") == runtime_base / "app" / "app.sock"


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.usefixtures("runtime_uid")
def test_find_runtime_file_ignores_public_xdg(session_dir: Path) -> None:
    session_dir.mkdir()
    session_dir.chmod(0o755)
    (session_dir / "ready").touch()
    assert Unix().find_runtime_files("ready") == []


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.usefixtures("runtime_uid")
def test_find_runtime_file_below_rejected_xdg(runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime_temp_dir))
    runtime_temp_dir.chmod(0o755)
    dirs = Unix("app")
    placed = dirs.place_runtime_file("ready")
    placed.touch()
    assert dirs.find_runtime_files("ready") == [placed]


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_temp_dir")
def test_find_runtime_file_in_system_fallback_below_xdg(
    default_dir: Path, system_root: Path, runtime_uid: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create(default_dir, "private")
    (default_dir / "app").mkdir()
    (default_dir / "app/ready").touch()
    (system_root / "run").chmod(0o755)
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/run")
    is_file = os.path.isfile
    monkeypatch.setattr(os.path, "isfile", lambda path: is_file(system_root / Path(path).relative_to("/")))
    with pytest.warns(RuntimeDirWarning):
        assert Unix("app").find_runtime_files("ready") == [Path(f"/run/user/{runtime_uid}/app/ready")]


@_POSIX_ONLY
def test_search_skips_group_writable_temp_fallback(temp_dir: Path) -> None:
    temp_dir.mkdir()
    temp_dir.chmod(0o775)
    (temp_dir / "ready").touch()
    with pytest.warns(RuntimeDirWarning):
        assert Unix().find_runtime_files("ready") == []


@_POSIX_ONLY
@pytest.mark.parametrize(
    "lookup",
    [
        pytest.param(attrgetter("site_runtime_path"), id="site"),
        pytest.param(lambda dirs: tuple(dirs.iter_runtime_paths())[-1], id="iterator"),
    ],
)
@pytest.mark.parametrize("ensure_exists", [pytest.param(False, id="lookup"), pytest.param(True, id="create")])
def test_site_runtime_rejects_public_override(
    session_dir: Path, temp_dir: Path, lookup: Callable[[Unix], Path], ensure_exists: bool
) -> None:
    _create(session_dir, "mode-755")
    with pytest.warns(RuntimeDirWarning):
        assert lookup(Unix("app", ensure_exists=ensure_exists)) == temp_dir / "app"
    assert (temp_dir / "app").exists() is ensure_exists
    assert list(session_dir.iterdir()) == []


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
def test_root_site_runtime_creates_missing_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "sessions" / "root"
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(base))
    assert Unix("app", use_site_for_root=True).site_runtime_path == base / "app"
    assert not base.parent.exists()
    assert Unix("app", use_site_for_root=True, ensure_exists=True).site_runtime_path == base / "app"
    assert (base / "app").is_dir()
    assert stat.S_IMODE(base.stat().st_mode) == stat.S_IMODE(base.parent.stat().st_mode) == 0o700


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
def test_root_site_runtime_refuses_creation_in_public_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (base := tmp_path / "session").mkdir()
    base.chmod(0o755)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(base))
    assert Unix("app", use_site_for_root=True).site_runtime_path == base / "app"
    with pytest.raises(PermissionError, match="has mode 0755"):
        _ = Unix("app", use_site_for_root=True, ensure_exists=True).site_runtime_path
    assert list(base.iterdir()) == []


@_POSIX_ONLY
def test_runtime_temp_rejects_world_writable_leaf(temp_dir: Path) -> None:
    temp_dir.mkdir()
    temp_dir.chmod(0o777)
    with pytest.raises(PermissionError, match="has writable mode 0777"):
        _ = Unix().user_runtime_path


@_POSIX_ONLY
@pytest.mark.parametrize("ensure_exists", [True, False])
@pytest.mark.usefixtures("runtime_uid")
def test_runtime_temp_requires_trusted_parent(runtime_temp_dir: Path, ensure_exists: bool) -> None:
    runtime_temp_dir.chmod(0o777)
    with pytest.raises(PermissionError, match=r"is below .*writable by another user; set XDG_RUNTIME_DIR"):
        _ = Unix(ensure_exists=ensure_exists).user_runtime_dir


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root")
def test_use_site_find_runtime_file_bypasses_xdg_runtime_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    marker = tmp_path / "ready"
    marker.touch()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(marker))
    mocker.patch("platformdirs.unix._UnixDefaults.site_runtime_dir", str(tmp_path))
    assert unix.Unix(use_site_for_root=True).find_runtime_file("ready") == marker


@_POSIX_ONLY
@pytest.mark.usefixtures("runtime_uid", "session_dir")
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_find_runtime_file_returns_file_outside_runtime_dirs(mocker: MockerFixture, runtime_temp_dir: Path) -> None:
    mocker.patch.object(Unix, "site_runtime_dir", str(site := runtime_temp_dir / "site"))
    site.mkdir()
    (site / "app.sock").touch()
    assert Unix(appname="app").find_runtime_file("app.sock") == site / "app.sock"


_NOT_FOUND: typing.Final[list[pytest.ParameterSet]] = [
    pytest.param("file", None, id="file"),
    pytest.param("files", [], id="files"),
]


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize(("suffix", "expected"), _NOT_FOUND)
def test_find_runtime_file_skips_runtime_dir_planted_after_check(
    mocker: MockerFixture, runtime_base: Path, suffix: str, expected: list[Path] | None
) -> None:
    _plant_after_check(mocker, runtime_base)
    assert getattr(Unix(appname="app"), f"find_runtime_{suffix}")("app.sock") == expected


@_POSIX_ONLY
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
@pytest.mark.parametrize(("suffix", "expected"), _NOT_FOUND)
def test_find_runtime_file_skips_runtime_dir_hidden_from_check(
    mocker: MockerFixture, runtime_base: Path, suffix: str, expected: list[Path] | None
) -> None:
    _hide_during_check(mocker, runtime_base)
    (runtime_base / "app").mkdir()
    (runtime_base / "app" / "app.sock").touch()
    assert getattr(Unix(appname="app"), f"find_runtime_{suffix}")("app.sock") == expected


@pytest.mark.usefixtures("_geteuid", "runtime_temp_dir")
@pytest.mark.filterwarnings("ignore::platformdirs.RuntimeDirWarning")
def test_find_runtime_files_skips_missing_temp_fallback_at_root(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("TMPDIR", "/")
    mocker.patch("tempfile.tempdir", "/")
    # Only root can create /runtime-1234, so count every app.sock as found while the fallback stays missing.
    mocker.patch("os.path.isfile", autospec=True, side_effect=lambda path: Path(path).name == "app.sock")
    assert Unix(appname="app").find_runtime_files("app.sock") == [Path("/run/app/app.sock")]


@pytest.fixture(params=["temp_dir", "session_dir", "temp_dir_in_session_dir"])
def runtime_base(request: pytest.FixtureRequest) -> Path:
    return request.getfixturevalue(request.param)


@pytest.fixture
def temp_dir_in_session_dir(
    runtime_temp_dir: Path, runtime_uid: int, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> Path:
    # Like XDG_RUNTIME_DIR=/tmp, which fails the check while the fallback inside it passes.
    _create(session := runtime_temp_dir / "session", "symlink")
    monkeypatch.setenv("TMPDIR", str(session))
    mocker.patch("tempfile.tempdir", str(session))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(session))
    return session / f"runtime-{runtime_uid}"


@pytest.fixture
def session_dir(runtime_temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(path := runtime_temp_dir / "session"))
    return path


@_POSIX_ONLY
@pytest.mark.parametrize(
    ("target", "error"),
    [
        pytest.param("platformdirs.unix.TemporaryFile", PermissionError, id="no-safe-root"),
        pytest.param("platformdirs.unix.gettempdir", FileNotFoundError, id="no-temp-dir"),
    ],
)
def test_find_runtime_files_with_xdg_and_no_temp_root(
    session_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    target: str,
    error: type[OSError],
) -> None:
    _create(session_dir, "private")
    _create(session_dir / "app", "private")
    (file := session_dir / "app" / "app.sock").touch()
    for name in ("TMPDIR", "TEMP", "TMP"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(session_dir.parent)
    mocker.patch(target, autospec=True, side_effect=error)
    assert Unix(appname="app").find_runtime_files("app.sock") == [file]


@pytest.fixture
def default_dir(system_root: Path, mocker: MockerFixture, runtime_uid: int, platform: str) -> Path:
    mocker.patch("sys.platform", platform)
    return system_root / _DEFAULT_PREFIXES[platform] / str(runtime_uid)


@pytest.fixture
def temp_dir(runtime_temp_dir: Path, runtime_uid: int) -> Path:
    return runtime_temp_dir / f"runtime-{runtime_uid}"


@pytest.fixture
def runtime_uid(tmp_path: Path, mocker: MockerFixture) -> int:
    mocker.patch("platformdirs.unix.geteuid", return_value=(owner := tmp_path.stat().st_uid), autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=owner, autospec=True)
    return owner


@pytest.fixture
def platform() -> str:
    return "linux"


def test_ensure_exists_creates_folder(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=True).user_data_path == Path(posix_tmp_path) / "acme"
    assert (Path(posix_tmp_path) / "acme").is_dir()


def test_folder_not_created_without_ensure_exists(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=False).user_data_path == Path(posix_tmp_path) / "acme"
    assert not (Path(posix_tmp_path) / "acme").exists()


_CLASSES: typing.Final[list[pytest.ParameterSet]] = [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")]


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


@pytest.mark.usefixtures("_clear_xdg_env")
@pytest.mark.parametrize("dirs_class", _CLASSES)
@pytest.mark.parametrize(
    ("data_home", "expected"),
    [pytest.param("/", "/fonts", id="root"), pytest.param("/xdg/", "/xdg/fonts", id="trailing_slash")],
)
def test_user_fonts_dir_xdg_trailing_separator(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], data_home: str, expected: str
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", data_home)
    assert dirs_class().user_fonts_dir == expected


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
@pytest.mark.parametrize("home", [pytest.param("", id="empty"), pytest.param("relhome", id="relative")])
@pytest.mark.parametrize(
    ("dirs_class", "expected"),
    [
        pytest.param(Unix, "/home/app-user/.config/app", id="unix"),
        pytest.param(MacOS, "/home/app-user/Library/Application Support/app", id="macos"),
    ],
)
def test_unusable_home_uses_passwd_entry(  # ruff:ignore[too-many-arguments]  # parametrized case inputs
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    pwd: ModuleType,
    dirs_class: type[Unix | MacOS],
    expected: str,
    home: str,
) -> None:
    monkeypatch.setenv("HOME", home)
    entry = pwd.struct_passwd(("app-user", "x", 12345, 12345, "", "/home/app-user", "/bin/sh"))
    mocker.patch.object(pwd, "getpwuid", return_value=entry, autospec=True)
    assert dirs_class(appname="app").user_config_dir == expected


@pytest.mark.usefixtures("_clear_xdg_env")
@pytest.mark.parametrize("dirs_class", _CLASSES)
def test_relative_passwd_home_raises(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, pwd: ModuleType, dirs_class: type[Unix | MacOS]
) -> None:
    monkeypatch.delenv("HOME", raising=False)
    entry = pwd.struct_passwd(("app-user", "x", 12345, 12345, "", "relhome", "/bin/sh"))
    mocker.patch.object(pwd, "getpwuid", return_value=entry, autospec=True)
    with pytest.raises(RuntimeError, match=r"^could not determine the home directory for '~/"):
        _ = dirs_class(appname="app").user_config_dir


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
    owner: typing.Final[int] = runtime_temp_dir.stat().st_uid
    (runtime_temp_dir / f"runtime-{owner + 1}").mkdir()
    mocker.patch("platformdirs.unix.geteuid", return_value=owner + 1, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=owner + 1, autospec=True)
    with pytest.raises(PermissionError, match=f"owned by uid {owner},"):
        Unix(appname="foo").place_runtime_file("app.sock")


_MEDIA_DIR_CASES: typing.Final[tuple[tuple[str, str, str], ...]] = (
    ("XDG_DOCUMENTS_DIR", "user_documents_dir", "Documents"),
    ("XDG_DOWNLOAD_DIR", "user_downloads_dir", "Downloads"),
    ("XDG_PICTURES_DIR", "user_pictures_dir", "Pictures"),
    ("XDG_VIDEOS_DIR", "user_videos_dir", "Videos"),
    ("XDG_MUSIC_DIR", "user_music_dir", "Music"),
    ("XDG_DESKTOP_DIR", "user_desktop_dir", "Desktop"),
    ("XDG_PROJECTS_DIR", "user_projects_dir", "Projects"),
    ("XDG_PUBLICSHARE_DIR", "user_publicshare_dir", "Public"),
    ("XDG_TEMPLATES_DIR", "user_templates_dir", "Templates"),
)


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
@pytest.mark.parametrize(("key", "prop", "default"), [pytest.param(*case, id=case[1]) for case in _MEDIA_DIR_CASES])
def test_ensure_exists_creates_configured_media_dir_only(  # ruff:ignore[too-many-arguments]  # parametrized case inputs
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
    user_dirs_file.write_text({"user-dirs": f'{key}="$HOME/parent/media"\n'}.get(source, ""), encoding="utf-8")
    if source == "env":  # simplint: ignore[conditional-in-test]  # env case sets the variable
        monkeypatch.setenv(key, f"{posix_tmp_path}/parent/media")
    result = Path(getattr(Unix(ensure_exists=ensure_exists), prop)).absolute()
    assert result == tmp_path / {"default": default}.get(source, "parent/media")
    made = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if ".config" not in path.parts)
    assert made == {True: ["parent", "parent/media"], False: []}[created]


@pytest.mark.parametrize("ensure_exists", [pytest.param(True, id="on"), pytest.param(False, id="off")])
@pytest.mark.parametrize("suffix", ["dir", "path"])
@pytest.mark.parametrize(("key", "prop"), [pytest.param(key, prop, id=prop) for key, prop, _ in _MEDIA_DIR_CASES])
def test_ensure_exists_reaches_the_media_function(  # ruff:ignore[too-many-arguments]  # parametrized case inputs
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    posix_tmp_path: str,
    key: str,
    prop: str,
    suffix: str,
    ensure_exists: bool,
) -> None:
    mocker.patch("platformdirs.PlatformDirs", Unix)
    monkeypatch.setenv(key, f"{posix_tmp_path}/parent/media")
    getattr(platformdirs, prop.removesuffix("dir") + suffix)(ensure_exists=ensure_exists)
    assert (tmp_path / "parent" / "media").is_dir() is ensure_exists


@pytest.mark.skipif(sys.platform == "win32", reason="creating symlinks needs elevated rights on Windows")
@pytest.mark.parametrize(
    ("key", "prop"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
    ],
)
@pytest.mark.parametrize("source", ["env", "user-dirs"])
def test_ensure_exists_returns_dangling_media_symlink(  # ruff:ignore[too-many-arguments]  # parametrized case inputs
    monkeypatch: pytest.MonkeyPatch, user_dirs_file: Path, tmp_path: Path, key: str, prop: str, source: str
) -> None:
    (link := tmp_path / "media").symlink_to(tmp_path / "unmounted")
    monkeypatch.delenv(key, raising=False)
    user_dirs_file.write_text({"user-dirs": f'{key}="$HOME/media"\n'}.get(source, ""), encoding="utf-8")
    if source == "env":  # simplint: ignore[conditional-in-test]  # env case sets the variable
        monkeypatch.setenv(key, str(link))
    assert getattr(Unix(ensure_exists=True), prop) == str(link)
    assert not link.exists()


@pytest.mark.skipif(sys.platform == "win32", reason="creating symlinks needs elevated rights on Windows")
@pytest.mark.parametrize(
    ("key", "prop"),
    [
        pytest.param("XDG_DOCUMENTS_DIR", "user_documents_dir", id="user_documents_dir"),
        pytest.param("XDG_MUSIC_DIR", "user_music_dir", id="user_music_dir"),
    ],
)
def test_ensure_exists_raises_on_user_dirs_media_file(
    monkeypatch: pytest.MonkeyPatch, user_dirs_file: Path, media_file: Path, key: str, prop: str
) -> None:
    monkeypatch.delenv(key, raising=False)
    user_dirs_file.write_text(f'{key}="{media_file}"\n', encoding="utf-8")
    with pytest.raises(FileExistsError):
        getattr(Unix(ensure_exists=True), prop)


@pytest.mark.skipif(sys.platform == "win32", reason="Windows reads media directories from Known Folders")
@pytest.mark.parametrize("suffix", ["dir", "path"])
def test_media_function_ensure_exists_raises_on_file(
    monkeypatch: pytest.MonkeyPatch, media_file: Path, suffix: str
) -> None:
    monkeypatch.setenv("XDG_DOCUMENTS_DIR", str(media_file))
    with pytest.raises(FileExistsError):
        getattr(platformdirs, f"user_documents_{suffix}")(ensure_exists=True)


@pytest.mark.skipif(sys.platform == "win32", reason="Windows reads media directories from Known Folders")
def test_ensure_exists_checks_user_media_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, user_dirs_file: Path
) -> None:
    (shared := tmp_path / "shared").mkdir()
    shared.chmod(0o1777)
    (foreign := shared / "foreign").mkdir()
    foreign.chmod(0o777)
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    user_dirs_file.write_text(f'XDG_DOCUMENTS_DIR="{foreign / "docs"}"\n', encoding="utf-8")
    with pytest.raises(PermissionError):
        _ = Unix(ensure_exists=True).user_documents_dir
    assert not (foreign / "docs").exists()


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
    ("prop", "env_var"),
    [
        pytest.param("site_data_dir", "XDG_DATA_DIRS", id="site_data_dir"),
        pytest.param("site_config_dir", "XDG_CONFIG_DIRS", id="site_config_dir"),
    ],
)
# parametrized case inputs
def test_site_dir_ensure_exists_creates_only_the_returned_entries(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str, prop: str, env_var: str, multipath: bool, created: set[str]
) -> None:
    monkeypatch.setenv(env_var, f"{posix_tmp_path}/first{os.pathsep}{posix_tmp_path}/second")
    getattr(Unix(appname="acme", multipath=multipath, ensure_exists=True), prop)
    assert {p.name for p in Path(posix_tmp_path).iterdir()} == created


@pytest.mark.parametrize(
    ("prop", "env_var"),
    [
        pytest.param("site_data_path", "XDG_DATA_DIRS", id="site_data_path"),
        pytest.param("site_config_path", "XDG_CONFIG_DIRS", id="site_config_path"),
    ],
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
    [
        pytest.param("iter_data_dirs", "XDG_DATA_HOME", "XDG_DATA_DIRS", id="iter_data_dirs"),
        pytest.param("iter_config_dirs", "XDG_CONFIG_HOME", "XDG_CONFIG_DIRS", id="iter_config_dirs"),
    ],
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
@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        pytest.param("XDG_DATA_DIRS", "site_data_dir", id="site_data_dir"),
        pytest.param("XDG_CONFIG_DIRS", "site_config_dir", id="site_config_dir"),
        pytest.param("XDG_DATA_DIRS", "site_applications_dir", id="site_applications_dir"),
    ],
)
def test_site_dirs_fall_back_when_xdg_var_has_no_absolute_paths(
    monkeypatch: pytest.MonkeyPatch, env_var: str, prop: str, value: str
) -> None:
    monkeypatch.setenv(env_var, value)
    expected = {
        # match host separators
        "site_data_dir": os.path.join("/usr/local/share", "foo"),  # ruff:ignore[os-path-join]
        "site_config_dir": os.path.join("/etc/xdg", "foo"),  # ruff:ignore[os-path-join]  # host separators
        "site_applications_dir": os.path.join("/usr/local/share", "applications"),  # ruff:ignore[os-path-join]  # host separators
    }[prop]
    assert getattr(Unix(appname="foo"), prop) == expected


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize(
    ("prop", "suffix"),
    [
        pytest.param("site_data_dir", "foo", id="data"),
        pytest.param("site_config_dir", "foo", id="config"),
        pytest.param("site_applications_dir", "applications", id="applications"),
    ],
)
def test_site_dirs_filter_relative_entries(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], prop: str, suffix: str
) -> None:
    value: typing.Final[str] = os.pathsep.join(("relative", "/custom/first", "", "~/relative", " /custom/second "))
    monkeypatch.setenv("XDG_DATA_DIRS", value)
    monkeypatch.setenv("XDG_CONFIG_DIRS", value)
    assert getattr(dirs_class(appname="foo", multipath=True), prop) == f"/custom/first{os.sep}{suffix}"


@pytest.mark.parametrize("dirs_class", [pytest.param(Unix, id="unix"), pytest.param(MacOS, id="macos")])
@pytest.mark.parametrize(
    "kind",
    [
        pytest.param("data", id="data"),
        pytest.param("config", id="config"),
    ],
)
@pytest.mark.parametrize("whitespace", [pytest.param(" ", id="space"), pytest.param("\t", id="tab")])
def test_xdg_site_preserves_trailing_whitespace(
    monkeypatch: pytest.MonkeyPatch, dirs_class: type[Unix | MacOS], kind: str, whitespace: str
) -> None:
    monkeypatch.setenv(f"XDG_{kind.upper()}_DIRS", f"/xdg-fixture/first{whitespace}{os.pathsep}/xdg-fixture/second")
    assert getattr(dirs_class(appname="demo", multipath=True), f"site_{kind}_dir") == (
        f"/xdg-fixture/first{whitespace}{os.sep}demo{os.pathsep}/xdg-fixture/second{os.sep}demo"
    )


def test_site_data_dir_multipath_falls_back_when_xdg_var_is_all_separators(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", os.pathsep)
    # match host separators
    dirs = [os.path.join("/usr/local/share", "foo"), os.path.join("/usr/share", "foo")]  # ruff:ignore[os-path-join]
    assert Unix(appname="foo", multipath=True).site_data_dir == os.pathsep.join(dirs)


@pytest.mark.usefixtures("_geteuid", "runtime_temp_dir")
@pytest.mark.parametrize(
    ("prop", "warns"),
    [
        pytest.param("user_runtime_dir", True, id="user"),
        pytest.param("site_runtime_dir", False, id="site"),
    ],
)
def test_runtime_dir_rejects_relative_value(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, prop: str, warns: bool
) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", "relative/runtime")
    mocker.patch("sys.platform", "linux")
    expected: typing.Final[Path] = {
        "user_runtime_dir": Path(gettempdir()) / "runtime-1234",
        "site_runtime_dir": Path("/run"),
    }[prop]
    with _fallback_warning(expected=warns):
        assert Path(getattr(Unix(), prop)) == expected


def test_site_applications_path_multipath_returns_first_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", f"/custom/first{os.pathsep}/custom/second")
    assert Unix(multipath=True).site_applications_path == Path("/custom/first/applications")


def test_user_media_dir_from_user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    (config_dir / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n')
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


@_POSIX_ONLY
def test_user_media_dir_from_symlinked_user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    config = tmp_path / "local.dirs"
    config.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n')
    (tmp_path / "user-dirs.dirs").symlink_to(config)
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


@_POSIX_ONLY
def test_user_media_dir_ignores_group_writable_config(tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    user_dirs_file.chmod(0o664)
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_ignores_foreign_config_parent(tmp_path: Path, user_dirs_file: Path, foreign: set[Path]) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    foreign.add(user_dirs_file.parent)
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_ignores_writable_config_parent(tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    user_dirs_file.parent.chmod(0o777)
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_accepts_group_writable_config_parent(tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    user_dirs_file.parent.chmod(0o775)
    user_dirs_file.chmod(0o600)
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


@_POSIX_ONLY
@pytest.mark.usefixtures("user_dirs_file")
def test_user_media_dir_ignores_file_config_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (file := tmp_path / "file").touch()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(file))
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_from_symlinked_config_parent(
    tmp_path: Path, user_dirs_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    (link := tmp_path / "config-link").symlink_to(user_dirs_file.parent, target_is_directory=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(link))
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


@_POSIX_ONLY
def test_user_media_dir_ignores_symlinked_foreign_target(
    tmp_path: Path, user_dirs_file: Path, foreign: set[Path]
) -> None:
    (target := tmp_path / "target").mkdir()
    (target / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    user_dirs_file.symlink_to(target / "user-dirs.dirs")
    foreign.add(target)
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
@pytest.mark.usefixtures("user_dirs_file")
def test_user_media_dir_ignores_config_parent_link_loop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (loop := tmp_path / "loop").symlink_to("loop")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(loop))
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_ignores_config_file_link_loop(tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.symlink_to("user-dirs.dirs")
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@_POSIX_ONLY
def test_user_media_dir_ignores_unreadable_config_parent(
    tmp_path: Path, user_dirs_file: Path, mocker: MockerFixture
) -> None:
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n', encoding="utf-8")
    parent = user_dirs_file.parent
    original_lstat = os.lstat

    def unreadable(path: str | os.PathLike[str]) -> os.stat_result:
        if Path(path) == parent:
            raise OSError(errno.EIO, os.strerror(errno.EIO), str(path))
        return original_lstat(path)

    mocker.patch.object(os, "lstat", autospec=True, side_effect=unreadable)
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


def test_user_media_dir_missing_key_in_user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    (config_dir / "user-dirs.dirs").write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
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
    custom_config: typing.Final[Path] = Path(posix_tmp_path) / "custom_config"
    custom_config.mkdir()
    (custom_config / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/CustomDocs"\n')
    monkeypatch.setenv("HOME", posix_tmp_path)
    monkeypatch.setenv("USERPROFILE", posix_tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", custom_config.as_posix())
    assert Unix().user_documents_path == Path(posix_tmp_path) / "CustomDocs"


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        pytest.param("$HOME/Docs", "/Docs", id="below-home"),
        pytest.param("$HOME", "/", id="home-itself"),
        pytest.param("$HOME/", "/", id="home-trailing-slash"),
    ],
)
def test_user_dirs_home_at_filesystem_root(
    entry: str, expected: str, posix_tmp_path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    (config := Path(posix_tmp_path) / "config").mkdir()
    (config / "user-dirs.dirs").write_text(f'XDG_DOCUMENTS_DIR="{entry}"\n', encoding="utf-8")
    monkeypatch.setenv("HOME", "/")
    monkeypatch.setenv("USERPROFILE", "/")
    monkeypatch.setenv("XDG_CONFIG_HOME", config.as_posix())
    assert Unix().user_documents_dir == expected


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


_SITE_REDIRECT_CASES: typing.Final[list[tuple[str, str]]] = [
    # match host separators
    ("user_data_dir", os.path.join("/usr/local/share", "foo")),  # ruff:ignore[os-path-join]
    ("user_config_dir", os.path.join("/etc/xdg", "foo")),  # ruff:ignore[os-path-join]  # match host separators
    ("user_cache_dir", os.path.join("/var/cache", "foo")),  # ruff:ignore[os-path-join]  # match host separators
    ("user_state_dir", os.path.join("/var/lib", "foo")),  # ruff:ignore[os-path-join]  # match host separators
    ("user_log_dir", os.path.join("/var/log", "foo")),  # ruff:ignore[os-path-join]  # match host separators
    (
        "user_runtime_dir",
        os.path.join(  # ruff:ignore[os-path-join]  # match host separators
            "/var/run" if sys.platform.startswith(("freebsd", "openbsd", "netbsd")) else "/run",
            "foo",
        ),
    ),
    ("user_bin_dir", "/usr/local/bin"),
    ("user_applications_dir", f"/usr/local/share{os.sep}applications"),
]
_SITE_RUNTIME_DIR: typing.Final[str] = dict(_SITE_REDIRECT_CASES)["user_runtime_dir"]


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_as_root(prop: str, expected: str) -> None:
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result == expected


@pytest.mark.usefixtures("_as_non_root", "_missing_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_as_non_root(prop: str, expected: str) -> None:
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result != expected


@pytest.fixture
def _credentials(request: pytest.FixtureRequest, mocker: MockerFixture) -> None:
    real, effective = typing.cast("tuple[int, int]", request.param)
    mocker.patch("os.getuid", return_value=real, autospec=True)
    mocker.patch("os.geteuid", return_value=effective, autospec=True)
    importlib.reload(sys.modules["platformdirs._runtime"])
    importlib.reload(unix)


@_POSIX_ONLY
@pytest.mark.usefixtures("_clear_xdg_env", "_credentials")
@pytest.mark.parametrize(
    ("_credentials", "expected"),
    [
        pytest.param((1000, 0), "/etc/xdg/foo", id="setuid-root"),
        pytest.param((0, 1000), "/home/alice/.config/foo", id="dropped-root"),
    ],
    indirect=["_credentials"],
)
def test_use_site_for_root_follows_effective_uid(monkeypatch: pytest.MonkeyPatch, expected: str) -> None:
    monkeypatch.setenv("HOME", "/home/alice")
    assert unix.Unix(appname="foo", use_site_for_root=True).user_config_dir == expected


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
    dirs: typing.Final[Unix] = Unix(appname="foo", use_site_for_root=not use_site_for_root)
    dirs.user_data_dir  # ruff:ignore[useless-expression]  # property access raises
    dirs.use_site_for_root = use_site_for_root
    assert dirs.user_data_dir == os.path.join(base, "foo")  # ruff:ignore[os-path-join]  # match host separators


@pytest.mark.usefixtures("_as_root", "_missing_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_disabled_as_root(prop: str, expected: str) -> None:
    result = getattr(Unix(appname="foo", use_site_for_root=False), prop)
    assert result != expected


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(
    ("xdg_var", "prop", "expected_site"),
    [
        pytest.param(
            "XDG_DATA_HOME",
            "user_data_dir",
            os.path.join("/usr/local/share", "foo"),  # ruff:ignore[os-path-join]  # match host separators
            id="user_data_dir",
        ),
        pytest.param(
            "XDG_CONFIG_HOME",
            "user_config_dir",
            os.path.join("/etc/xdg", "foo"),  # ruff:ignore[os-path-join]  # match host separators
            id="user_config_dir",
        ),
        pytest.param(
            "XDG_CACHE_HOME",
            "user_cache_dir",
            os.path.join("/var/cache", "foo"),  # ruff:ignore[os-path-join]  # match host separators
            id="user_cache_dir",
        ),
        pytest.param(
            "XDG_STATE_HOME",
            "user_state_dir",
            os.path.join("/var/lib", "foo"),  # ruff:ignore[os-path-join]  # match host separators
            id="user_state_dir",
        ),
        pytest.param(
            "XDG_STATE_HOME",
            "user_log_dir",
            os.path.join("/var/log", "foo"),  # ruff:ignore[os-path-join]  # match host separators
            id="user_log_dir",
        ),
        pytest.param("XDG_RUNTIME_DIR", "user_runtime_dir", _SITE_RUNTIME_DIR, id="XDG_RUNTIME_DIR-user_runtime_dir"),
    ],
)
def test_use_site_for_root_bypasses_xdg_user_vars(
    monkeypatch: pytest.MonkeyPatch, xdg_var: str, prop: str, expected_site: str
) -> None:
    monkeypatch.setenv(xdg_var, "/custom/xdg/path")
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result == expected_site


@pytest.fixture
def inherited_media_target(
    tmp_path: Path, posix_tmp_path: str, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    # The Unix class ignores an XDG path with a Windows drive, so inherit drive-less ones.
    target = Path(f"{posix_tmp_path}/inherited/media")
    if (key := request.param) == "user-dirs":
        (config := tmp_path / "inherited-config").mkdir()
        (config / "user-dirs.dirs").write_text(f'XDG_DOCUMENTS_DIR="{target.as_posix()}"\n', encoding="utf-8")
        monkeypatch.setenv("XDG_CONFIG_HOME", f"{posix_tmp_path}/inherited-config")
    else:
        monkeypatch.setenv(key, target.as_posix())
    return target


@pytest.mark.usefixtures("_as_root", "inherited_media_target")
@pytest.mark.parametrize(
    ("inherited_media_target", "prop", "default"),
    [
        pytest.param("user-dirs", "user_documents_dir", "Documents", id="user-dirs"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", "Downloads", id="XDG_DOWNLOAD_DIR"),
        pytest.param("XDG_DATA_HOME", "user_fonts_dir", ".local/share/fonts", id="XDG_DATA_HOME"),
    ],
    indirect=["inherited_media_target"],
)
def test_use_site_for_root_bypasses_xdg_media_vars(tmp_path: Path, prop: str, default: str) -> None:
    assert getattr(Unix(use_site_for_root=True), prop) == f"{tmp_path}/{default}"


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("inherited_media_target", "prop"),
    [
        pytest.param("user-dirs", "user_documents_dir", id="user-dirs"),
        pytest.param("XDG_DOWNLOAD_DIR", "user_downloads_dir", id="XDG_DOWNLOAD_DIR"),
    ],
    indirect=["inherited_media_target"],
)
def test_use_site_for_root_creates_no_inherited_media_dir(inherited_media_target: Path, prop: str) -> None:
    getattr(Unix(use_site_for_root=True, ensure_exists=True), prop)
    assert not inherited_media_target.parent.exists()


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize("suffix", ["dir", "path"])
@pytest.mark.parametrize(
    ("inherited_media_target", "prop", "default"),
    [
        *(pytest.param(*case, id=case[1]) for case in _MEDIA_DIR_CASES),
        pytest.param("XDG_DATA_HOME", "user_fonts_dir", ".local/share/fonts", id="user_fonts_dir"),
    ],
    indirect=["inherited_media_target"],
)
def test_use_site_for_root_reaches_the_media_function(
    mocker: MockerFixture, inherited_media_target: Path, prop: str, default: str, suffix: str
) -> None:
    mocker.patch("platformdirs.PlatformDirs", Unix)
    function = getattr(platformdirs, prop.removesuffix("dir") + suffix)
    assert Path(function()).is_relative_to(inherited_media_target)
    assert Path(function(use_site_for_root=True)) == Path.home() / default


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("xdg_var", "func"),
    [
        pytest.param("XDG_DATA_DIRS", Unix.iter_data_dirs, id="XDG_DATA_DIRS"),
        pytest.param("XDG_CONFIG_DIRS", Unix.iter_config_dirs, id="XDG_CONFIG_DIRS"),
    ],
)
def test_use_site_iter_dirs_no_duplicates(
    monkeypatch: pytest.MonkeyPatch,
    xdg_var: str,
    func: Callable[[Unix], Iterator[str]],
) -> None:
    monkeypatch.setenv(xdg_var, "/custom/xdg/path")
    result = func(Unix(appname="foo", use_site_for_root=True))
    # match host separators
    assert list(result) == [os.path.join("/custom/xdg/path", "foo")]  # ruff:ignore[os-path-join]


_SINGLE_SITE_ITER_CASES: typing.Final[list[tuple[Callable[[Unix], Iterator[str]], str]]] = [
    # match host separators
    (Unix.iter_cache_dirs, os.path.join("/var/cache", "foo")),  # ruff:ignore[os-path-join]
    (Unix.iter_state_dirs, os.path.join("/var/lib", "foo")),  # ruff:ignore[os-path-join]  # host separators
    (Unix.iter_log_dirs, os.path.join("/var/log", "foo")),  # ruff:ignore[os-path-join]  # match host separators
    (
        Unix.iter_runtime_dirs,
        os.path.join(  # ruff:ignore[os-path-join]  # match host separators
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


@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    ("environment", "directory", "suffix"),
    [
        pytest.param({}, "user_documents_path", "Documents", id="unset-home"),
        pytest.param({"HOME": "relative"}, "user_fonts_path", ".local/share/fonts", id="relative-home"),
    ],
)
def test_use_site_media_uses_root_password_entry(
    mocker: MockerFixture,
    root_password_home: Path,
    environment: dict[str, str],
    directory: str,
    suffix: str,
) -> None:
    mocker.patch.dict(os.environ, environment, clear=True)
    assert getattr(Unix(use_site_for_root=True), directory) == root_password_home / suffix


@pytest.fixture
def root_password_home(mocker: MockerFixture, pwd: ModuleType, tmp_path: Path) -> Path:
    mocker.patch("os.getuid", return_value=1000, autospec=True)
    mocker.patch.object(
        pwd,
        "getpwuid",
        autospec=True,
        side_effect=lambda uid: pwd.struct_passwd(("test", "x", uid, uid, "", str(tmp_path / str(uid)), "")),
    )
    return tmp_path / "0"


@pytest.mark.usefixtures("_as_root")
def test_use_site_media_rejects_empty_root_password_home(mocker: MockerFixture, pwd: ModuleType) -> None:
    mocker.patch.dict(os.environ, clear=True)
    mocker.patch.object(pwd, "getpwuid", autospec=True, return_value=pwd.struct_passwd(("root", "x", 0, 0, "", "", "")))
    with pytest.raises(RuntimeError, match="could not determine the home directory"):
        _ = Unix(use_site_for_root=True).user_documents_dir


@pytest.mark.usefixtures("_as_root", "_inherited_xdg_runtime_dir")
def test_use_site_keeps_xdg_runtime_dir_for_site_runtime_dir() -> None:
    # match host separators
    expected: typing.Final[str] = os.path.join("/run/user/1000", "foo")  # ruff:ignore[os-path-join]
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
        pytest.param("XDG_CONFIG_DIRS", Unix.iter_config_dirs, id="XDG_CONFIG_DIRS"),
        pytest.param("XDG_DATA_DIRS", Unix.iter_data_dirs, id="XDG_DATA_DIRS"),
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
    "case",
    [
        pytest.param(("user_data_path", "foo/1.0"), id="data"),
        pytest.param(("user_config_path", "foo/1.0"), id="config"),
        pytest.param(("user_preference_path", "foo/1.0"), id="preference"),
        pytest.param(("user_applications_path", "applications"), id="applications"),
    ],
)
def test_user_path_site_redirect(
    monkeypatch: pytest.MonkeyPatch,
    uid: int,
    use_site_for_root: bool,
    multipath: bool,
    case: tuple[str, str],
) -> None:
    prop, subdir = case
    monkeypatch.setenv("XDG_DATA_DIRS", f"/xdg/a{os.pathsep}/xdg/b")
    monkeypatch.setenv("XDG_CONFIG_DIRS", f"/xdg/a{os.pathsep}/xdg/b")
    monkeypatch.setenv("XDG_DATA_HOME", f"/user/with{os.pathsep}separator")
    monkeypatch.setenv("XDG_CONFIG_HOME", f"/user/with{os.pathsep}separator")
    dirs: typing.Final[Unix] = Unix(
        appname="foo", version="1.0", multipath=multipath, use_site_for_root=use_site_for_root
    )
    user_base: typing.Final[str] = f"/user/with{os.pathsep}separator"
    # Only the root row with site redirection reads from the site path.
    base = "/xdg/a" if uid == 0 and use_site_for_root else user_base  # simplint: ignore[conditional-in-test]  # root
    assert getattr(dirs, prop) == Path(base) / subdir


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.parametrize("uid", [pytest.param(0, id="root"), pytest.param(1000, id="user")], indirect=True)
@pytest.mark.parametrize("kind", ["config", "data"])
@pytest.mark.usefixtures("root_owned_paths")
def test_place_file_with_use_site_for_root_keeps_site_dir_readable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, uid: int, kind: str
) -> None:
    monkeypatch.setenv(f"XDG_{kind.upper()}_HOME", str(tmp_path / "user"))
    monkeypatch.setenv(f"XDG_{kind.upper()}_DIRS", str(tmp_path / "site"))
    getattr(Unix(appname="foo", use_site_for_root=True), f"place_{kind}_file")("sub/app.toml")
    (reference := tmp_path / "reference").mkdir(mode=0o755)
    expected: typing.Final[int] = {0: stat.S_IMODE(reference.stat().st_mode), 1000: 0o700}[uid]
    created: typing.Final[Iterator[Path]] = (tmp_path / {0: "site", 1000: "user"}[uid]).rglob("*")
    assert {path.name: oct(stat.S_IMODE(path.stat().st_mode)) for path in created} == dict.fromkeys(
        ["foo", "sub"], oct(expected)
    )


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
@pytest.mark.parametrize(
    ("mask", "expected"),
    [
        pytest.param(0o002, 0o755, id="group-write"),
        pytest.param(0o000, 0o755, id="no-mask"),
        pytest.param(0o077, 0o700, id="private"),
    ],
)
def test_root_site_modes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mask: int, expected: int) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path))
    previous = os.umask(mask)
    try:
        dirs = Unix("app", use_site_for_root=True)
        assert dirs.place_data_file("sub/state").parent == tmp_path / "app" / "sub"
        assert dirs.place_data_file("sub/again").parent == tmp_path / "app" / "sub"
    finally:
        os.umask(previous)
    assert stat.S_IMODE((tmp_path / "app").stat().st_mode) == expected
    assert stat.S_IMODE((tmp_path / "app" / "sub").stat().st_mode) == expected


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root")
@pytest.mark.parametrize(
    "use",
    [
        pytest.param(attrgetter("user_data_dir"), id="ensure_exists"),
        pytest.param(methodcaller("place_data_file", "file.txt"), id="place_file"),
    ],
)
def test_root_site_rejects_foreign_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, root_owned_paths: set[Path], use: Callable[[Unix], Path | str]
) -> None:
    (target := tmp_path / "target").mkdir()
    (site := tmp_path / "site").symlink_to(target, target_is_directory=True)
    root_owned_paths.add(site)
    monkeypatch.setenv("XDG_DATA_DIRS", str(site))
    with pytest.raises(PermissionError):
        use(Unix(appname="app", use_site_for_root=True, ensure_exists=True))
    assert not (target / "app").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
@pytest.mark.parametrize(
    "link_target",
    [pytest.param(lambda path: path, id="absolute"), pytest.param(attrgetter("name"), id="relative")],
)
def test_root_site_accepts_root_owned_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, link_target: Callable[[Path], Path | str]
) -> None:
    (target := tmp_path / "target").mkdir()
    (site := tmp_path / "site").symlink_to(link_target(target), target_is_directory=True)
    monkeypatch.setenv("XDG_DATA_DIRS", str(site))
    assert Unix(appname="app", use_site_for_root=True, ensure_exists=True).user_data_dir == str(site / "app")
    assert (target / "app").is_dir()


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
def test_root_site_with_group_writable_ancestor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tmp_path.chmod(0o775)
    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path))
    path = Unix("service", use_site_for_root=True).place_data_file("config")
    assert path == tmp_path / "service/config"
    assert path.parent.is_dir()


@_POSIX_ONLY
@pytest.mark.usefixtures("_as_root")
def test_existing_service_owned_site_directory(
    tmp_path: Path, root_owned_paths: set[Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    (service := tmp_path / "service").mkdir()
    root_owned_paths.add(service)
    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path))
    dirs = Unix("service", ensure_exists=True, use_site_for_root=True)
    assert dirs.site_data_path == service
    with pytest.raises(PermissionError, match="owned by uid"):
        dirs.place_data_file("config")
    with pytest.raises(PermissionError, match="owned by uid"):
        _ = Unix("service", version="2", ensure_exists=True).site_data_path
    assert list(service.iterdir()) == []


@_POSIX_ONLY
def test_root_with_user_owned_home(
    tmp_path: Path, root_owned_paths: set[Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    (home := tmp_path / "home").mkdir()
    root_owned_paths.add(home)
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert Unix("app", ensure_exists=True).user_cache_path == home / ".cache/app"
    assert (home / ".cache/app").is_dir()


@_POSIX_ONLY
def test_foreign_owned_sticky_data_parent(tmp_path: Path, foreign: set[Path], monkeypatch: pytest.MonkeyPatch) -> None:
    (base := tmp_path / "shared").mkdir()
    base.chmod(0o1777)
    foreign.add(base)
    monkeypatch.setenv("XDG_DATA_HOME", str(base))
    with pytest.raises(PermissionError, match="owned by uid"):
        _ = Unix("app", ensure_exists=True).user_data_path
    assert list(base.iterdir()) == []


@_POSIX_ONLY
def test_container_home_with_another_owner(tmp_path: Path, foreign: set[Path], monkeypatch: pytest.MonkeyPatch) -> None:
    (home := tmp_path / "home").mkdir()
    home.chmod(0o775)
    foreign.add(home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home))
    dirs = Unix("app", ensure_exists=True)
    assert dirs.user_config_path == home / "app"
    assert dirs.place_config_file("sub/settings").parent.is_dir()


@_POSIX_ONLY
@pytest.mark.parametrize(
    ("mask", "expected"), [pytest.param(0, 0o775, id="no-mask"), pytest.param(0o077, 0o700, id="private")]
)
def test_configured_media_creation_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mask: int, expected: int
) -> None:
    monkeypatch.setenv("XDG_MUSIC_DIR", str(music := tmp_path / "media/music"))
    previous = os.umask(mask)
    try:
        dirs = Unix(ensure_exists=True)
        assert (dirs.user_music_path, dirs.user_music_path) == (music, music)
    finally:
        os.umask(previous)
    assert (stat.S_IMODE(music.parent.stat().st_mode), stat.S_IMODE(music.stat().st_mode)) == (expected, expected)


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
def test_root_site_rejects_writable_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (site := tmp_path / "site").mkdir()
    site.chmod(0o777)
    monkeypatch.setenv("XDG_DATA_DIRS", str(site))
    with pytest.raises(PermissionError, match="writable by another user"):
        _ = Unix(appname="app", use_site_for_root=True, ensure_exists=True).user_data_dir
    assert not (site / "app").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
@pytest.mark.parametrize(
    ("code", "message"),
    [
        pytest.param(errno.ENOENT, "is missing", id="removed"),
        pytest.param(errno.EIO, "cannot be checked", id="io-error"),
    ],
)
def test_root_site_rejects_unreadable_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, code: int, message: str
) -> None:
    (site := tmp_path / "site").mkdir()
    monkeypatch.setenv("XDG_DATA_DIRS", str(site))
    original_lstat = os.lstat

    def lstat(path: str | os.PathLike[str]) -> os.stat_result:
        if Path(path) == site:
            raise OSError(code, os.strerror(code), str(site))
        return original_lstat(path)

    mocker.patch.object(os, "lstat", new=lstat)
    with pytest.raises(PermissionError, match=message):
        _ = Unix(appname="app", use_site_for_root=True, ensure_exists=True).user_data_dir
    assert not (site / "app").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root", "root_owned_paths")
def test_root_site_rejects_nondirectory_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    (site := tmp_path / "site").mkdir()
    monkeypatch.setenv("XDG_DATA_DIRS", str(site))
    original_lstat = os.lstat

    def lstat(path: str | os.PathLike[str]) -> os.stat_result:
        info = original_lstat(path)
        return os.stat_result((stat.S_IFREG | 0o644, *info[1:])) if Path(path) == site else info

    mocker.patch.object(os, "lstat", new=lstat)
    with pytest.raises(PermissionError, match="not a directory"):
        _ = Unix(appname="app", use_site_for_root=True, ensure_exists=True).user_data_dir
    assert not (site / "app").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix ownership only")
@pytest.mark.usefixtures("_as_root")
def test_root_site_creation_checks_new_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, root_owned_paths: set[Path], mocker: MockerFixture
) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path / "site"))
    original_mkdir = Path.mkdir

    def mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)
        if path == tmp_path / "site":
            root_owned_paths.add(path)

    mocker.patch.object(Path, "mkdir", autospec=True, side_effect=mkdir)
    with pytest.raises(PermissionError):
        _ = Unix(appname="app", use_site_for_root=True, ensure_exists=True).user_data_dir
    assert not (tmp_path / "site" / "app").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Windows reads media directories from Known Folders")
@pytest.mark.usefixtures("_as_root")
def test_root_user_media_uses_user_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DOCUMENTS_DIR", str(tmp_path / "docs"))
    assert Unix(ensure_exists=True).user_documents_dir == str(tmp_path / "docs")
    assert (tmp_path / "docs").is_dir()


@pytest.fixture
def uid(request: pytest.FixtureRequest, mocker: MockerFixture) -> int:
    value: typing.Final[int] = typing.cast("int", request.param)
    mocker.patch("platformdirs.unix.geteuid", return_value=value, autospec=True)
    mocker.patch("platformdirs._runtime.geteuid", return_value=value, autospec=True)
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
    assert Unix().user_documents_path == Path({"$HOME": tmp_path}.get(base, base)) / folder


@pytest.mark.parametrize(
    ("folder", "expected"),
    [
        pytest.param(r"a\q", r"a\q", id="ordinary-letter"),
        pytest.param(r"a\ b", r"a\ b", id="space"),
        pytest.param(r"a\-b", r"a\-b", id="hyphen"),
        pytest.param(r"a\nb", r"a\nb", id="literal-backslash-n"),
        pytest.param(r"a\'b", r"a\'b", id="single-quote"),
        pytest.param(r"a\\b", r"a\b", id="escaped-backslash"),
        pytest.param(r"a\$b", "a$b", id="escaped-dollar"),
        pytest.param(r"a\`b", "a`b", id="escaped-backtick"),
        pytest.param(r"a\"b", 'a"b', id="escaped-double-quote"),
        pytest.param(r"a\q\\b\$c", r"a\q\b$c", id="mixed-escapes"),
    ],
)
@pytest.mark.parametrize("base", ["$HOME", "/absolute"])
def test_user_dirs_double_quoted_backslashes(
    folder: str, expected: str, base: str, tmp_path: Path, user_dirs_file: Path
) -> None:
    user_dirs_file.write_text(f'XDG_DOCUMENTS_DIR="{base}/{folder}"\n', encoding="utf-8")
    assert Unix().user_documents_path == Path({"$HOME": tmp_path}.get(base, base)) / expected


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
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/My \t Docs  \n", "~/My \t Docs", id="unquoted-blanks-inside"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Reports\\ 2026\n", "~/Reports 2026", id="unquoted-escaped-blank"),
        pytest.param(
            "XDG_DOCUMENTS_DIR=$HOME/Reports\\ #2026\n", "~/Reports #2026", id="unquoted-escaped-blank-before-hash"
        ),
        pytest.param(
            "XDG_DOCUMENTS_DIR=$HOME/Reports\\ 2026 # moved\n",
            "~/Reports 2026",
            id="unquoted-escaped-blank-then-comment",
        ),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/a\\\\b\\#c\\$d\n", r"~/a\b#c$d", id="unquoted-escapes"),
        pytest.param(
            "XDG_DOCUMENTS_DIR=/srv/Reports\\ 2026\n", "/srv/Reports 2026", id="unquoted-absolute-escaped-blank"
        ),
        pytest.param(
            'XDG_DOCUMENTS_DIR="$HOME/Reports\\ #2026"\n', r"~/Reports\ #2026", id="quoted-keeps-backslash-blank"
        ),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs\\", "~/Docs\\", id="unquoted-backslash-ends-file"),
        pytest.param("XDG_DOCUMENTS_DIR=$HOME/Docs\\\n", "~/Docs", id="unquoted-backslash-newline-ends-file"),
    ],
)
def test_user_dirs_read_like_xdg_user_dir(content: str, expected: str, tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_text(content, encoding="utf-8")
    assert Unix().user_documents_dir == expected.replace("~", str(tmp_path), 1)


@pytest.mark.parametrize("blank", [pytest.param(" ", id="spaces"), pytest.param("\t", id="tabs")])
def test_user_dirs_long_unquoted_blank_run_reads_in_linear_time(blank: str, user_dirs_file: Path) -> None:
    user_dirs_file.write_text(f"XDG_DOCUMENTS_DIR=$HOME/Docs{blank * 40_000}x\n", encoding="utf-8")
    started = time.perf_counter()
    _ = Unix().user_documents_dir
    assert time.perf_counter() - started < 1


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


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        pytest.param(b'XDG_DOCUMENTS_DIR="$HOME/Docs\rArchive"\n', "~/Docs\rArchive", id="quoted-home"),
        pytest.param(b'XDG_DOCUMENTS_DIR="/srv/Docs\rArchive"\r\n', "/srv/Docs\rArchive", id="quoted-absolute"),
        pytest.param(b"XDG_DOCUMENTS_DIR=$HOME/Docs\r\n", "~/Docs", id="crlf-terminator"),
        pytest.param(b"XDG_DOCUMENTS_DIR=$HOME/Docs\r", "~/Docs", id="crlf-file-without-final-newline"),
    ],
)
def test_user_dirs_carriage_return(content: bytes, expected: str, tmp_path: Path, user_dirs_file: Path) -> None:
    user_dirs_file.write_bytes(content)
    assert Unix().user_documents_dir == expected.replace("~", str(tmp_path), 1)


def test_user_dirs_unreadable_file_uses_default(tmp_path: Path, user_dirs_file: Path) -> None:
    # a directory stands in for an unreadable file because root ignores a chmod 000
    user_dirs_file.mkdir()
    assert Unix().user_documents_dir == f"{tmp_path}/Documents"


@pytest.fixture
def user_dirs_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (config := tmp_path / ".config").mkdir()
    return config / "user-dirs.dirs"


_APP_COMPONENTS: typing.Final[list[str]] = ["home", "home/base", "home/base/app", "home/base/app/1.0"]


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
        pytest.param("site_runtime_dir", "XDG_RUNTIME_DIR", id="xdg-site-runtime"),
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
