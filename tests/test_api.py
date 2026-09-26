from __future__ import annotations

import builtins
import functools
import inspect
import os
import re
import stat
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import pytest

import platformdirs
from platformdirs.android import Android
from platformdirs.unix import Unix
from platformdirs.windows import Windows

builtin_import = builtins.__import__


if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from types import ModuleType

    from pytest_mock import MockerFixture


def test_package_metadata() -> None:
    assert hasattr(platformdirs, "__version__")
    assert hasattr(platformdirs, "__version_info__")


def test_method_result_is_str(func: str) -> None:
    method = getattr(platformdirs, func)
    result = method()
    assert isinstance(result, str)


def test_property_result_is_str(func: str) -> None:
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func)
    assert isinstance(result, str)


def test_method_result_is_path(func_path: str) -> None:
    method = getattr(platformdirs, func_path)
    result = method()
    assert isinstance(result, Path)


def test_property_result_is_path(func_path: str) -> None:
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func_path)
    assert isinstance(result, Path)


def test_function_interface_is_in_sync(func: str) -> None:
    function_dir = getattr(platformdirs, func)
    function_path = getattr(platformdirs, func.replace("_dir", "_path"))
    assert inspect.isfunction(function_dir)
    assert inspect.isfunction(function_path)
    function_dir_signature = inspect.Signature.from_callable(function_dir)
    function_path_signature = inspect.Signature.from_callable(function_path)
    assert function_dir_signature.parameters == function_path_signature.parameters


@pytest.mark.parametrize("func", ["user_applications_dir", "user_applications_path"])
def test_user_applications_function_boolean_options_are_keyword_only(func: str) -> None:
    # These options have not shipped yet, so they can be keyword-only without breaking any caller.
    parameters = inspect.Signature.from_callable(getattr(platformdirs, func)).parameters
    positional = [name for name, param in parameters.items() if param.kind is param.POSITIONAL_OR_KEYWORD]
    assert positional == ["appname", "appauthor", "version"]


@pytest.mark.parametrize("func", ["site_applications_dir", "site_applications_path"])
def test_site_applications_function_keeps_multipath_positional(func: str) -> None:
    # multipath has been the first positional argument since 4.9.0, so the app arguments are keyword-only.
    parameters = inspect.Signature.from_callable(getattr(platformdirs, func)).parameters
    positional = [name for name, param in parameters.items() if param.kind is param.POSITIONAL_OR_KEYWORD]
    assert positional == ["multipath", "ensure_exists"]


def test_function_matches_its_property_for_app_arguments(func: str) -> None:
    function = getattr(platformdirs, func)
    scoped = getattr(platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0"), func)
    if {"appname", "version"} <= inspect.Signature.from_callable(function).parameters.keys():
        assert function(appname="MyApp", appauthor="MyCompany", version="1.0") == scoped
    else:
        # A function without the app arguments can only ever return the unscoped base directory, so a property that
        # is app-scoped on any platform is out of its reach. Only one direction holds: a function may have to take
        # arguments this platform ignores because another platform scopes the same property.
        assert scoped == getattr(platformdirs.PlatformDirs(), func)


@pytest.mark.parametrize("root", ["A", "/system", None])
@pytest.mark.parametrize("data", ["D", "/data", None])
@pytest.mark.parametrize("path", ["/data/data/a/files", "/C"])
@pytest.mark.parametrize("shell", ["/data/data/com.app/files/usr/bin/sh", "/usr/bin/sh", None])
@pytest.mark.parametrize("prefix", ["/data/data/com.termux/files/usr", None])
def test_android_active(  # ruff:ignore[too-many-arguments]
    monkeypatch: pytest.MonkeyPatch,
    root: str | None,
    data: str | None,
    path: str,
    shell: str | None,
    prefix: str | None,
) -> None:
    for env_var, value in {"ANDROID_DATA": data, "ANDROID_ROOT": root, "SHELL": shell, "PREFIX": prefix}.items():
        if value is None:
            monkeypatch.delenv(env_var, raising=False)
        else:
            monkeypatch.setenv(env_var, value)

    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    _android_folder.cache_clear()
    monkeypatch.setattr(sys, "path", ["/A", "/B", path])

    expected = (
        root == "/system" and data == "/data" and shell is None and prefix is None and _android_folder() is not None
    )
    if expected:
        assert platformdirs._set_platform_dir_class() is Android  # ruff:ignore[private-member-access]
    else:
        assert platformdirs._set_platform_dir_class() is not Android  # ruff:ignore[private-member-access]


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        pytest.param(None, Android, id="cleared-environment"),
        pytest.param("/data/data/com.termux/files/usr", platformdirs._Result, id="termux"),  # ruff:ignore[private-member-access]
    ],
)
def test_android_build_detected_without_environment(
    monkeypatch: pytest.MonkeyPatch, prefix: str | None, expected: type[platformdirs.PlatformDirsABC]
) -> None:
    for env_var in ("ANDROID_DATA", "ANDROID_ROOT", "SHELL", "PREFIX"):
        monkeypatch.delenv(env_var, raising=False)
    if prefix is not None:
        monkeypatch.setenv("PREFIX", prefix)
    monkeypatch.setattr(sys, "getandroidapilevel", lambda: 34, raising=False)
    monkeypatch.setattr(sys, "path", ["/data/user/0/org.example.app/files/app"])
    from platformdirs.android import _android_folder  # ruff:ignore[import-outside-top-level]

    _android_folder.cache_clear()
    assert platformdirs._set_platform_dir_class() is expected  # ruff:ignore[private-member-access]


def _fake_import(
    name: str,
    globals: Mapping[str, object] | None = None,  # ruff:ignore[builtin-argument-shadowing]
    locals: Mapping[str, object] | None = None,  # ruff:ignore[builtin-argument-shadowing]
    fromlist: Sequence[str] | None = (),
    level: int = 0,
) -> ModuleType:
    if name == "ctypes":
        msg = f"No module named {name}"
        raise ModuleNotFoundError(msg)
    return builtin_import(name, globals, locals, fromlist, level)


def mock_import(func: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> None:  # ruff:ignore[any-type]
        platformdirs_module_items = [item for item in sys.modules.items() if item[0].startswith("platformdirs")]
        try:
            builtins.__import__ = _fake_import  # ty: ignore[invalid-assignment]
            for name, _ in platformdirs_module_items:
                del sys.modules[name]
            return func(*args, **kwargs)
        finally:
            # restore original modules
            builtins.__import__ = builtin_import
            for name, module in platformdirs_module_items:
                sys.modules[name] = module

    return wrap


@mock_import
def test_no_ctypes(func: str) -> None:
    import platformdirs  # ruff:ignore[import-outside-top-level]

    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func)
    assert isinstance(result, str)


def test_mypy_subclassing() -> None:
    # Ensure that PlatformDirs / AppDirs is seen as a valid superclass by mypy
    # This is a static type-checking test to ensure we work around
    # the following mypy issue: https://github.com/python/mypy/issues/10962
    class PlatformDirsSubclass(platformdirs.PlatformDirs): ...

    class AppDirsSubclass(platformdirs.AppDirs): ...


@pytest.mark.parametrize("kind", ["config", "data", "cache", "state", "log", "runtime"])
def test_iter_dirs_yields_user_before_site(kind: str) -> None:
    # docs/howto.rst merges config in reverse of this order so the user directory wins.
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    assert next(getattr(dirs, f"iter_{kind}_dirs")()) == getattr(dirs, f"user_{kind}_dir")


_APP_FIELDS: Final = [
    pytest.param("appname", id="appname"),
    pytest.param("appauthor", id="appauthor"),
    pytest.param("version", id="version"),
]
_ESCAPING_VALUES: Final = [
    pytest.param("../evil", id="parent"),
    pytest.param("nested/../../evil", id="nested-parent"),
    pytest.param("..\\evil", id="backslash-parent"),
    pytest.param("/evil", id="rooted"),
    pytest.param("\\evil", id="backslash-rooted"),
    pytest.param("//server/share/evil", id="unc"),
    pytest.param(
        "C:/evil",
        marks=pytest.mark.skipif(sys.platform != "win32", reason="drive letters only exist on Windows"),
        id="drive",
    ),
]


@pytest.mark.parametrize("field", _APP_FIELDS)
@pytest.mark.parametrize("value", _ESCAPING_VALUES)
def test_app_argument_escaping_base_is_rejected(field: str, value: str) -> None:
    args = {"appname": "app", "appauthor": "author", "version": "1.0"} | {field: value}
    with pytest.raises(
        ValueError, match=rf"^{field} must stay inside the base directory, got {re.escape(repr(value))}$"
    ):
        platformdirs.PlatformDirs(args["appname"], args["appauthor"], args["version"])


@pytest.mark.parametrize("field", _APP_FIELDS)
@pytest.mark.parametrize("value", _ESCAPING_VALUES)
def test_app_argument_escaping_base_is_rejected_on_assignment(field: str, value: str) -> None:
    dirs = platformdirs.PlatformDirs("app", "author", "1.0")
    with pytest.raises(
        ValueError, match=rf"^{field} must stay inside the base directory, got {re.escape(repr(value))}$"
    ):
        setattr(dirs, field, value)


@pytest.mark.parametrize(
    ("field", "value", "parts"),
    [
        pytest.param("appname", "other", ("author", "other", "1.0"), id="appname"),
        pytest.param("appname", None, (), id="appname-none"),
        pytest.param("appauthor", False, ("app", "1.0"), id="appauthor-false"),
        pytest.param("version", None, ("author", "app"), id="version-none"),
    ],
)
def test_app_argument_assignment_within_base_changes_the_path(
    mocker: MockerFixture, field: str, value: str | bool | None, parts: tuple[str, ...]
) -> None:
    # only Windows paths include appauthor
    mocker.patch("platformdirs.windows.get_win_folder", return_value="C:/Local")
    dirs = Windows("app", "author", "1.0")
    setattr(dirs, field, value)
    assert Path(dirs.user_data_dir) == Path(os.path.normpath("C:/Local"), *parts)


@pytest.mark.parametrize(
    "appname",
    [
        pytest.param("Company/App", id="nested"),
        pytest.param("..app", id="leading-dots"),
        pytest.param("app..", id="trailing-dots"),
    ],
)
def test_appname_within_base_is_accepted(appname: str) -> None:
    assert platformdirs.PlatformDirs(appname).user_data_dir.endswith(appname)


_KINDS: Final = [pytest.param(kind, id=kind) for kind in ("config", "data", "cache", "state", "log", "runtime")]
_POSIX_ONLY: Final = pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> Path:
    # XDG variables only take POSIX absolute paths, so drive the Unix defaults through the home directory instead.
    for var in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR"):
        monkeypatch.delenv(var, raising=False)
    for var in ("HOME", "USERPROFILE"):
        monkeypatch.setenv(var, str(tmp_path / "home"))
    mocker.patch("os.access", return_value=False)
    mocker.patch("tempfile.tempdir", str(tmp_path / "home" / "tmp"))
    return tmp_path / "home"


@pytest.fixture
def user_dirs(home: Path, mocker: MockerFixture) -> dict[str, Path]:
    mocker.patch("platformdirs.unix.getuid", return_value=(uid := home.parent.stat().st_uid))
    return {
        "config": home / ".config" / "app",
        "data": home / ".local" / "share" / "app",
        "cache": home / ".cache" / "app",
        "state": home / ".local" / "state" / "app",
        "log": home / ".local" / "state" / "app" / "log",
        "runtime": home / "tmp" / f"runtime-{uid}" / "app",
    }


def _place(kind: str, *, ensure_exists: bool = False) -> Callable[[str | Path], Path]:
    return getattr(Unix(appname="app", ensure_exists=ensure_exists), f"place_{kind}_file")


@pytest.mark.parametrize("kind", _KINDS)
def test_place_file_returns_path_under_user_dir(user_dirs: dict[str, Path], kind: str) -> None:
    assert _place(kind)("sub/app.toml") == user_dirs[kind] / "sub" / "app.toml"


@pytest.mark.parametrize("kind", _KINDS)
def test_place_file_creates_parent_directories(user_dirs: dict[str, Path], kind: str) -> None:
    _place(kind)("sub/deeper/app.toml")
    assert (user_dirs[kind] / "sub" / "deeper").is_dir()


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.usefixtures("user_dirs")
def test_place_file_does_not_create_the_file(kind: str) -> None:
    assert not _place(kind)("app.toml").exists()


@pytest.mark.usefixtures("home")
def test_place_file_accepts_path_like() -> None:
    assert _place("config")(Path("sub", "app.toml")).parent.is_dir()


@_POSIX_ONLY
@pytest.mark.parametrize("ensure_exists", [pytest.param(False, id="lookup"), pytest.param(True, id="ensure-exists")])
@pytest.mark.parametrize("kind", _KINDS)
def test_place_file_creates_directories_private(
    home: Path, user_dirs: dict[str, Path], kind: str, ensure_exists: bool
) -> None:
    _place(kind, ensure_exists=ensure_exists)("sub/app.toml")
    sub = user_dirs[kind] / "sub"
    created = [path for path in (sub, *sub.parents) if path.is_relative_to(home)]
    assert {path: oct(stat.S_IMODE(path.stat().st_mode)) for path in created} == dict.fromkeys(created, "0o700")


@_POSIX_ONLY
def test_place_file_keeps_mode_of_existing_directories(home: Path) -> None:
    home.mkdir()
    home.chmod(0o755)
    _place("config")("app.toml")
    assert stat.S_IMODE(home.stat().st_mode) == 0o755


_ESCAPING_NAMES: Final = [
    pytest.param("../evil", id="parent"),
    pytest.param("sub/../../evil", id="nested-parent"),
    pytest.param("..\\evil", id="backslash-parent"),
    pytest.param("/evil", id="rooted"),
    pytest.param("\\evil", id="backslash-rooted"),
    pytest.param("//server/share/evil", id="unc"),
    pytest.param(
        "C:/evil",
        marks=pytest.mark.skipif(sys.platform != "win32", reason="drive letters only exist on Windows"),
        id="drive",
    ),
    pytest.param(
        "C:evil",
        marks=pytest.mark.skipif(sys.platform != "win32", reason="drive letters only exist on Windows"),
        id="drive-relative",
    ),
]


@pytest.mark.parametrize("name", _ESCAPING_NAMES)
@pytest.mark.usefixtures("home")
def test_place_file_rejects_name_escaping_the_directory(name: str) -> None:
    with pytest.raises(ValueError, match=rf"^name must stay inside the base directory, got {re.escape(repr(name))}$"):
        _place("config")(name)


@pytest.mark.parametrize("name", [pytest.param("", id="empty"), pytest.param(".", id="dot")])
@pytest.mark.usefixtures("home")
def test_place_file_rejects_name_without_a_file(name: str) -> None:
    with pytest.raises(ValueError, match=rf"^name must point to a file, got {re.escape(repr(name))}$"):
        _place("config")(name)


def test_place_file_rejected_name_creates_nothing(home: Path) -> None:
    with pytest.raises(ValueError, match="must stay inside"):
        _place("config")("../evil")
    assert not home.exists()


_SUFFIXES: Final = [pytest.param("file", id="file"), pytest.param("files", id="files")]
_MISSING: Final = [pytest.param("file", None, id="file"), pytest.param("files", [], id="files")]


@pytest.fixture
def dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Unix:
    # XDG only accepts POSIX absolute paths, so Windows drops the drive and needs it as the current one.
    monkeypatch.chdir(tmp_path)
    root = tmp_path.as_posix().removeprefix(tmp_path.drive)
    for var in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR"):
        monkeypatch.setenv(var, f"{root}/user/{var}")
    for var in ("XDG_CONFIG_DIRS", "XDG_DATA_DIRS"):
        monkeypatch.setenv(var, os.pathsep.join(f"{root}/site/{var}/{index}" for index in (1, 2)))
    return Unix("find-files-test")


@pytest.fixture
def config_paths(dirs: Unix) -> list[Path]:
    return list(dirs.iter_config_paths())


@pytest.fixture
def user_file(dirs: Unix, kind: str) -> Path:
    return _touch(next(getattr(dirs, f"iter_{kind}_paths")()) / "app.toml")


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


@pytest.mark.parametrize("kind", _KINDS)
def test_find_file_returns_user_file(dirs: Unix, kind: str, user_file: Path) -> None:
    assert getattr(dirs, f"find_{kind}_file")("app.toml") == user_file


@pytest.mark.parametrize("kind", _KINDS)
def test_find_files_lists_user_file_once(dirs: Unix, kind: str, user_file: Path) -> None:
    assert getattr(dirs, f"find_{kind}_files")("app.toml") == [user_file]


@pytest.mark.parametrize(("suffix", "expected"), _MISSING)
@pytest.mark.parametrize("kind", _KINDS)
def test_find_missing_file(dirs: Unix, kind: str, suffix: str, expected: list[Path] | None) -> None:
    assert getattr(dirs, f"find_{kind}_{suffix}")("app.toml") == expected


@pytest.mark.parametrize(("suffix", "expected"), _MISSING)
def test_find_skips_directory_with_the_name(dirs: Unix, suffix: str, expected: list[Path] | None) -> None:
    (dirs.user_config_path / "app.toml").mkdir(parents=True)
    assert getattr(dirs, f"find_config_{suffix}")("app.toml") == expected


def test_find_config_file_prefers_user_over_site(dirs: Unix, config_paths: list[Path]) -> None:
    user = _touch(config_paths[0] / "app.toml")
    _touch(config_paths[2] / "app.toml")
    assert dirs.find_config_file("app.toml") == user


def test_find_config_file_falls_back_to_site(dirs: Unix, config_paths: list[Path]) -> None:
    site = _touch(config_paths[2] / "app.toml")
    assert dirs.find_config_file("app.toml") == site


def test_find_config_files_orders_user_before_site(dirs: Unix, config_paths: list[Path]) -> None:
    expected = [_touch(config_paths[index] / "app.toml") for index in (0, 2)]
    assert dirs.find_config_files("app.toml") == expected


def test_find_config_file_accepts_nested_path_like(dirs: Unix, config_paths: list[Path]) -> None:
    nested = _touch(config_paths[1] / "sub" / "app.toml")
    assert dirs.find_config_file(Path("sub", "app.toml")) == nested


@pytest.mark.parametrize("suffix", _SUFFIXES)
@pytest.mark.parametrize("kind", _KINDS)
def test_find_creates_no_directory_with_ensure_exists(dirs: Unix, tmp_path: Path, kind: str, suffix: str) -> None:
    dirs.ensure_exists = True
    getattr(dirs, f"find_{kind}_{suffix}")("app.toml")
    assert list(tmp_path.iterdir()) == []


def test_find_keeps_ensure_exists_on_the_instance(dirs: Unix) -> None:
    dirs.ensure_exists = True
    dirs.find_config_file("app.toml")
    assert dirs.ensure_exists is True


@pytest.mark.parametrize("suffix", _SUFFIXES)
@pytest.mark.parametrize(
    "name",
    [
        pytest.param("../evil", id="parent"),
        pytest.param("nested/../../evil", id="nested-parent"),
        pytest.param("..\\evil", id="backslash-parent"),
        pytest.param("/evil", id="rooted"),
        pytest.param("\\evil", id="backslash-rooted"),
        pytest.param("//server/share/evil", id="unc"),
        pytest.param(Path("..", "evil"), id="path-like-parent"),
        pytest.param(
            "C:/evil",
            marks=pytest.mark.skipif(sys.platform != "win32", reason="drive letters only exist on Windows"),
            id="drive",
        ),
    ],
)
def test_find_rejects_name_escaping_the_directory(dirs: Unix, name: str | Path, suffix: str) -> None:
    with pytest.raises(
        ValueError, match=rf"^name must stay inside the base directory, got {re.escape(repr(os.fspath(name)))}$"
    ):
        getattr(dirs, f"find_config_{suffix}")(name)
