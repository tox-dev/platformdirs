from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from multiprocessing import get_context
from pathlib import Path
from subprocess import check_output  # ruff:ignore[suspicious-subprocess-import]  # run checks in a fresh interpreter
from threading import Event
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

import pytest
from coverage import Coverage

import platformdirs
from platformdirs.android import Android
from platformdirs.testing import isolated_dirs
from platformdirs.unix import Unix

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from pytest_mock import MockerFixture

    from platformdirs.api import PlatformDirsABC


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
_ORIGINAL: Final[dict[str, list[str]]] = _resolve_all()
_ANDROID_ORIGINAL: Final[
    MappingProxyType[str, Any]  # simplint: ignore[imprecise-annotation]  # class attributes of mixed types
] = MappingProxyType(dict(vars(Android)))


def test_isolated_dirs_yields_root_as_path(tmp_path: Path) -> None:
    with isolated_dirs(str(tmp_path)) as root:
        assert root == tmp_path


@pytest.fixture(params=[pytest.param(".", id="dot"), pytest.param("isolated", id="named")])
def relative_root(request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    (start := tmp_path / "start").mkdir()
    monkeypatch.chdir(start)
    return request.param


def test_isolated_dirs_relative_root_yields_absolute(tmp_path: Path, relative_root: str) -> None:
    with isolated_dirs(relative_root) as root:
        assert root == tmp_path / "start" / relative_root


def test_isolated_dirs_relative_root_survives_chdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative_root: str
) -> None:
    with isolated_dirs(relative_root):
        monkeypatch.chdir(tmp_path)
        assert _outside(tmp_path / "start" / relative_root) == {}


def _outside(root: Path) -> dict[str, list[str]]:
    return {
        name: outside
        for name, values in _resolve_all().items()
        if (outside := [value for value in values if not Path(value).is_relative_to(root)])
    }


def test_isolated_dirs_redirects_every_accessor(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        assert _outside(tmp_path) == {}


@pytest.mark.skipif(sys.platform == "win32", reason="XDG runtime paths are POSIX paths")
def test_isolated_dirs_find_runtime_file_bypasses_xdg_runtime_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    mocker.patch("platformdirs.PlatformDirs", Unix)
    with isolated_dirs(tmp_path):
        dirs = platformdirs.PlatformDirs("app")
        marker = dirs.place_runtime_file("ready")
        marker.touch()
        monkeypatch.setenv("XDG_RUNTIME_DIR", str(marker))
        assert dirs.find_runtime_files("ready") == [marker]


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


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ignores POSIX mode bits")
@pytest.mark.usefixtures("_umask")
@pytest.mark.parametrize(
    ("kind", "mode"), [pytest.param("user_cache", 0o700, id="user"), pytest.param("site_cache", 0o755, id="site")]
)
def test_isolated_dirs_ensure_exists_mode(
    tmp_path: Path, modes: Callable[[Path], dict[str, int]], kind: str, mode: int
) -> None:
    with isolated_dirs(tmp_path):
        getattr(platformdirs.PlatformDirs("app", ensure_exists=True), f"{kind}_dir")
    assert modes(tmp_path) == {kind: mode, f"{kind}/app": mode}


def test_isolated_dirs_restores_on_exit(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        pass
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_restores_after_exception(tmp_path: Path) -> None:
    with pytest.raises(LookupError), isolated_dirs(tmp_path):
        raise LookupError
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_spawned_process(tmp_path: Path) -> None:
    # A real script makes the worker importable under spawn, including on Windows.
    script = tmp_path / "check_spawned_process.py"
    code = """
from multiprocessing import get_context
from pathlib import Path
from sys import argv

import platformdirs
from platformdirs.testing import isolated_dirs


def check_child(parent_root: Path, child_root: Path) -> None:
    dirs = platformdirs.PlatformDirs("app", version="1.0")
    original = dirs.user_config_path
    assert not original.is_relative_to(parent_root)
    assert not platformdirs.user_cache_path("app").is_relative_to(parent_root)
    with isolated_dirs(child_root):
        assert dirs.user_config_path == child_root / "user_config/app/1.0"
        assert platformdirs.user_cache_path("app") == child_root / "user_cache/app"
        dirs.place_config_file("settings.toml").write_text("enabled = true", encoding="utf-8")
    assert dirs.user_config_path == original


if __name__ == "__main__":
    parent_root, child_root = Path(argv[1]) / "parent", Path(argv[1]) / "child"
    original = platformdirs.user_config_path("app")
    with isolated_dirs(parent_root):
        process = get_context("spawn").Process(target=check_child, args=(parent_root, child_root))
        process.start()
        process.join(timeout=10)
        process.kill()
        process.join()
        assert process.exitcode == 0, process.exitcode
        assert platformdirs.user_config_path("app") == parent_root / "user_config/app"
        assert not parent_root.exists()
    assert platformdirs.user_config_path("app") == original
    assert (child_root / "user_config/app/1.0/settings.toml").read_text(encoding="utf-8") == "enabled = true"
    print("ok")
"""
    script.write_text(code, encoding="utf-8")
    assert check_output([sys.executable, str(script), str(tmp_path)], text=True, timeout=20).strip() == "ok"


def test_isolated_dirs_nested_restores_outer(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path / "outer"):
        with isolated_dirs(tmp_path / "inner"):
            pass
        assert platformdirs.user_data_path("app") == tmp_path / "outer" / "user_data" / "app"


def test_isolated_dirs_reentrant_exit(tmp_path: Path) -> None:
    code = """
from abc import ABCMeta
from contextlib import ExitStack
from pathlib import Path
from sys import argv
import platformdirs
from platformdirs.testing import isolated_dirs

with ExitStack() as older:
    class CloseOlder(ABCMeta):
        def __setattr__(cls, name: str, value: property) -> None:
            older.close()
            super().__setattr__(name, value)

    class Dirs(platformdirs.PlatformDirs, metaclass=CloseOlder):
        pass

    platformdirs.PlatformDirs = Dirs
    original = vars(Dirs).copy()
    older.enter_context(isolated_dirs(Path(argv[1]) / "older"))
    with isolated_dirs(Path(argv[1]) / "newer"):
        assert platformdirs.user_cache_path() == Path(argv[1]) / "newer/user_cache"
print(vars(Dirs) == original)
"""
    assert check_output([sys.executable, "-c", code, str(tmp_path)], text=True, timeout=10).strip() == "True"


def test_isolated_dirs_restores_intervening_patch(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path / "outer"), pytest.MonkeyPatch.context() as patch:
        patch.setattr(platformdirs.PlatformDirs, "user_cache_dir", property(lambda _: str(tmp_path)))
        with isolated_dirs(tmp_path / "inner"):
            assert platformdirs.user_cache_path() == tmp_path / "inner" / "user_cache"
        assert platformdirs.user_cache_path() == tmp_path
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_overlapping_restores_active_context(tmp_path: Path) -> None:
    with ExitStack() as first, ExitStack() as second:
        first.enter_context(isolated_dirs(tmp_path / "first"))
        second.enter_context(isolated_dirs(tmp_path / "second"))
        first.close()
        assert platformdirs.user_config_path("app") == tmp_path / "second" / "user_config" / "app"
    assert _resolve_all() == _ORIGINAL


def test_isolated_dirs_rolls_back_interrupted_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    interrupted = False

    def interrupt(cls: type[PlatformDirsABC], name: str, value: property) -> None:
        nonlocal interrupted
        setattr(cls, name, value)
        if not interrupted:
            interrupted = True
            raise KeyboardInterrupt

    monkeypatch.setattr("platformdirs.testing.setattr", interrupt, raising=False)
    with ExitStack() as scope, pytest.raises(KeyboardInterrupt):
        scope.enter_context(isolated_dirs(tmp_path / "interrupted"))
    assert _resolve_all() == _ORIGINAL
    with isolated_dirs(tmp_path / "active"):
        assert platformdirs.user_config_path("app") == tmp_path / "active" / "user_config" / "app"
    assert _resolve_all() == _ORIGINAL


if sys.platform != "win32":

    @pytest.mark.skipif(not hasattr(os, "fork"), reason="requires fork")
    @pytest.mark.filterwarnings("ignore:This process .* is multi-threaded.*:DeprecationWarning")
    def test_isolated_dirs_fork_inherits_thread_root(tmp_path: Path) -> None:
        installed, release = Event(), Event()

        def isolate_thread() -> None:
            with isolated_dirs(tmp_path / "worker"):
                installed.set()
                assert release.wait(10)

        with isolated_dirs(tmp_path / "parent"), ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(isolate_thread)
            try:
                assert installed.wait(10)
                assert _fork_check(tmp_path / "worker") == 0
            finally:
                release.set()
            pending.result(timeout=10)
            assert _outside(tmp_path / "parent") == {}

    def _enter_isolation(root: Path) -> None:
        with isolated_dirs(root):
            assert platformdirs.user_config_path("app") == root / "user_config" / "app"

    def _fork_check(root: Path) -> int | None:
        process = get_context("fork").Process(target=_check_child_root, args=(root,))
        process.start()
        try:
            process.join(timeout=5)
            return process.exitcode
        finally:
            process.kill()
            process.join()
            process.close()

    def _check_child_root(root: Path) -> None:
        assert platformdirs.user_config_path("app") == root / "user_config" / "app"
        _enter_isolation(root / "child")
        assert platformdirs.user_config_path("app") == root / "user_config" / "app"
        if (coverage := Coverage.current()) is not None:
            coverage.save()


@pytest.mark.usefixtures("_unix_root")
@pytest.mark.parametrize(
    ("kind", "suffix"),
    [
        pytest.param("user_data", "app/1.0", id="data"),
        pytest.param("user_config", "app/1.0", id="config"),
        pytest.param("user_preference", "app/1.0", id="preference"),
        pytest.param("user_applications", "", id="applications"),
    ],
)
@pytest.mark.parametrize("multipath", [pytest.param(False, id="single"), pytest.param(True, id="multiple")])
def test_isolated_dirs_root_paths_follow_redirected_dirs(
    tmp_path: Path, kind: str, suffix: str, multipath: bool
) -> None:
    dirs = Unix("app", version="1.0", multipath=multipath, use_site_for_root=True)
    expected = tmp_path / kind / suffix
    with isolated_dirs(tmp_path):
        assert getattr(dirs, f"{kind}_dir") == str(expected)
        assert getattr(dirs, f"{kind}_path") == expected


@pytest.mark.usefixtures("_unix_root")
def test_isolated_dirs_root_iter_config_paths(tmp_path: Path) -> None:
    with isolated_dirs(tmp_path):
        assert list(Unix("app", use_site_for_root=True).iter_config_paths()) == [
            tmp_path / "user_config/app",
            tmp_path / "site_config/app",
        ]


@pytest.mark.usefixtures("_unix_root")
def test_isolated_dirs_restores_root_redirection(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/user", "XDG_CONFIG_DIRS": "/site"})
    dirs = Unix("app", use_site_for_root=True)
    with isolated_dirs(tmp_path):
        pass
    assert dirs.user_config_dir == dirs.site_config_dir


@pytest.mark.usefixtures("_unix_root")
def test_isolated_dirs_nested_root_restores_after_exception(tmp_path: Path) -> None:
    dirs = Unix("app", use_site_for_root=True)
    with isolated_dirs(tmp_path):
        with pytest.raises(LookupError), isolated_dirs(tmp_path / "inner"):
            raise LookupError
        assert dirs.user_config_path == tmp_path / "user_config/app"


@pytest.fixture
def _unix_root(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.PlatformDirs", Unix)
    mocker.patch("platformdirs.unix.geteuid", return_value=0, autospec=True)
