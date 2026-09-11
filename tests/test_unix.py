from __future__ import annotations

import importlib
import inspect
import os
import sys
import typing
from pathlib import Path
from tempfile import gettempdir

import pytest

import platformdirs
from platformdirs import unix
from platformdirs.macos import MacOS
from platformdirs.unix import Unix

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _reload_after_test() -> typing.Iterator[None]:
    yield
    importlib.reload(unix)


@pytest.fixture
def _as_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=0)


@pytest.fixture
def _as_non_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=1000)


@pytest.fixture
def _writable_runtime_dir(mocker: MockerFixture) -> None:
    mocker.patch("os.access", return_value=True)


@pytest.fixture
def _no_xdg_runtime_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)


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
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_empty_value(monkeypatch: pytest.MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, "")
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)  # ruff:ignore[os-path-expanduser]


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


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize("platform", [pytest.param("freebsd", id="freebsd"), pytest.param("netbsd", id="netbsd")])
def test_freebsd_netbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    assert Unix().site_runtime_dir == "/var/run"


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize("platform", [pytest.param("freebsd", id="freebsd"), pytest.param("netbsd", id="netbsd")])
def test_freebsd_netbsd_user_runtime_dir_writable(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str
) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    mocker.patch("os.access", return_value=True)
    assert Unix().user_runtime_dir == "/var/run/user/1234"


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize("platform", [pytest.param("freebsd", id="freebsd"), pytest.param("netbsd", id="netbsd")])
def test_freebsd_netbsd_user_runtime_dir_not_writable(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str
) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    mocker.patch("os.access", return_value=False)
    mocker.patch("tempfile.tempdir", "/tmp")  # ruff:ignore[hardcoded-temp-file]
    assert Unix().user_runtime_dir == "/tmp/runtime-1234"  # ruff:ignore[hardcoded-temp-file]


@pytest.mark.usefixtures("_getuid")
def test_openbsd_site_runtime_dir(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "openbsd")
    assert Unix().site_runtime_dir == "/var/run"


@pytest.mark.usefixtures("_getuid")
def test_openbsd_user_runtime_dir_writable(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "openbsd")
    mocker.patch("os.access", return_value=True)
    assert Unix().user_runtime_dir == "/tmp/run/user/1234"  # ruff:ignore[hardcoded-temp-file]


@pytest.mark.usefixtures("_getuid")
def test_openbsd_user_runtime_dir_not_writable(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", "openbsd")
    mocker.patch("os.access", return_value=False)
    mocker.patch("tempfile.tempdir", "/tmp")  # ruff:ignore[hardcoded-temp-file]
    assert Unix().user_runtime_dir == "/tmp/runtime-1234"  # ruff:ignore[hardcoded-temp-file]


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


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize(
    ("platform", "default_dir"),
    [
        ("freebsd", "/var/run/user/1234"),
        ("linux", "/run/user/1234"),
    ],
)
def test_xdg_runtime_dir_unset_writable(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str, default_dir: str
) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    mocker.patch("os.access", return_value=True)

    assert Unix().user_runtime_dir == default_dir


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize(
    ("platform", "default_dir"),
    [
        ("freebsd", "/var/run/user/1234"),
        ("linux", "/run/user/1234"),
    ],
)
def test_xdg_runtime_dir_unset_not_writable(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, platform: str, default_dir: str
) -> None:
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    mocker.patch("sys.platform", platform)
    mocker.patch("os.access", return_value=False)
    mocker.patch("tempfile.tempdir", "/tmp")  # ruff:ignore[hardcoded-temp-file]

    result = Unix().user_runtime_dir
    assert not result.startswith(default_dir)
    assert result == "/tmp/runtime-1234"  # ruff:ignore[hardcoded-temp-file]


def test_ensure_exists_creates_folder(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=True).user_data_path == Path(posix_tmp_path) / "acme"
    assert (Path(posix_tmp_path) / "acme").is_dir()


def test_folder_not_created_without_ensure_exists(monkeypatch: pytest.MonkeyPatch, posix_tmp_path: str) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", posix_tmp_path)
    assert Unix(appname="acme", ensure_exists=False).user_data_path == Path(posix_tmp_path) / "acme"
    assert not (Path(posix_tmp_path) / "acme").exists()


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


@pytest.mark.usefixtures("_getuid")
@pytest.mark.parametrize("prop", ["user_runtime_dir", "site_runtime_dir"])
def test_runtime_dir_rejects_relative_value(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, prop: str) -> None:
    monkeypatch.setenv("XDG_RUNTIME_DIR", "relative/runtime")
    mocker.patch("sys.platform", "linux")
    mocker.patch("os.access", return_value=False)
    expected: typing.Final = Path(gettempdir()) / "runtime-1234" if prop == "user_runtime_dir" else Path("/run")
    assert Path(getattr(Unix(), prop)) == expected


def test_site_applications_path_multipath_returns_first_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_DIRS", f"/custom/first{os.pathsep}/custom/second")
    assert Unix(multipath=True).site_applications_path == Path("/custom/first/applications")


def test_user_media_dir_from_user_dirs_file(
    mocker: MockerFixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    user_dirs_file = config_dir / "user-dirs.dirs"
    user_dirs_file.write_text('XDG_DOCUMENTS_DIR="$HOME/MyDocs"\n')
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": ""})
    assert Unix().user_documents_dir == f"{tmp_path}/MyDocs"


def test_user_media_dir_missing_key_in_user_dirs_file(
    mocker: MockerFixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    user_dirs_file = config_dir / "user-dirs.dirs"
    user_dirs_file.write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": ""})
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


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir")
@pytest.mark.parametrize(("prop", "expected"), _SITE_REDIRECT_CASES)
def test_use_site_for_root_as_root(prop: str, expected: str) -> None:
    result = getattr(Unix(appname="foo", use_site_for_root=True), prop)
    assert result == expected


@pytest.mark.usefixtures("_as_non_root", "_no_xdg_runtime_dir", "_writable_runtime_dir")
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


@pytest.mark.usefixtures("_as_root", "_no_xdg_runtime_dir", "_writable_runtime_dir")
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


@pytest.mark.usefixtures("_as_non_root", "_no_xdg_runtime_dir", "_writable_runtime_dir")
@pytest.mark.parametrize(("func", "expected"), _SINGLE_SITE_ITER_CASES)
def test_iter_dirs_as_non_root_keeps_user_dir(func: Callable[[Unix], Iterator[str]], expected: str) -> None:
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
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/run/user/1000")
    # $XDG_RUNTIME_DIR backs both the user and the site runtime directory.
    assert list(Unix(appname="foo").iter_runtime_dirs()) == [os.path.join("/run/user/1000", "foo")]  # ruff:ignore[os-path-join]


@pytest.mark.parametrize(
    "folder",
    [
        pytest.param("100% complete", id="percent"),
        pytest.param("%(XDG_DESKTOP_DIR)s", id="interpolation-key"),
        pytest.param("100%%", id="double-percent"),
    ],
)
@pytest.mark.parametrize("base", [pytest.param("$HOME", id="home"), pytest.param("/absolute", id="absolute")])
def test_user_dirs_preserves_percent_signs(
    folder: str, base: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (tmp_path / ".config").mkdir()
    (tmp_path / ".config" / "user-dirs.dirs").write_text(
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
    ],
)
def test_user_dirs_read_like_xdg_user_dir(
    content: str, expected: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # user-dirs.dirs is shell, not INI: xdg-user-dir-lookup.c is the reference reader.
    monkeypatch.delenv("XDG_DOCUMENTS_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (tmp_path / ".config").mkdir()
    (tmp_path / ".config" / "user-dirs.dirs").write_text(content, encoding="utf-8")
    assert Unix().user_documents_dir == expected.replace("~", str(tmp_path), 1)
