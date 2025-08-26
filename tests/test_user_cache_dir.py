from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from platformdirs.api import TEMP_ENV_VARS

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
def test_user_cache_dir_linux_xdg_home_set(monkeypatch: MonkeyPatch, prop: str) -> None:
    """Test the user cache directory on Linux when XDG_CACHE_HOME is set."""
    monkeypatch.setattr(sys, "platform", "linux")
    from platformdirs.unix import Unix as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv("XDG_CACHE_HOME", "/home/user/.cache-xdg")
    monkeypatch.setenv("HOME", "/home/user")

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = getattr(dirs, prop)
    expected = Path("/home/user/.cache-xdg/MyApp")

    assert result == (str(expected) if prop == "user_cache_dir" else expected)


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
@pytest.mark.parametrize("env_var", TEMP_ENV_VARS)
def test_user_cache_dir_linux_tmp_set(monkeypatch: MonkeyPatch, prop: str, env_var: str) -> None:
    """Test the user cache directory on Linux when a temp env var is set."""
    monkeypatch.setattr(sys, "platform", "linux")
    from platformdirs.unix import Unix as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv(env_var, "/tmp/some-dir")  # noqa: S108
    monkeypatch.setenv("HOME", "/home/user")

    # Unset other temp vars to ensure priority is tested
    for var in set(TEMP_ENV_VARS) - {env_var}:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = getattr(dirs, prop)
    expected = Path("/tmp/some-dir/MyApp")  # noqa: S108

    assert result == (str(expected) if prop == "user_cache_dir" else expected)


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
def test_user_cache_dir_linux_fallback(monkeypatch: MonkeyPatch, prop: str) -> None:
    """Test the user cache directory on Linux as a fallback."""
    monkeypatch.setattr(sys, "platform", "linux")
    from platformdirs.unix import Unix as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv("HOME", "/home/user")
    for var in TEMP_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = getattr(dirs, prop)
    expected = Path("/home/user/.cache/MyApp")

    assert result == (str(expected) if prop == "user_cache_dir" else expected)


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
@pytest.mark.parametrize("env_var", TEMP_ENV_VARS)
def test_user_cache_dir_macos_tmp_set(monkeypatch: MonkeyPatch, prop: str, env_var: str) -> None:
    """Test the user cache directory on macOS when a temp env var is set."""
    monkeypatch.setattr(sys, "platform", "darwin")
    from platformdirs.macos import MacOS as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv(env_var, "/tmp/some-dir")  # noqa: S108
    monkeypatch.setenv("HOME", "/home/user")

    # Unset other temp vars to ensure priority is tested
    for var in set(TEMP_ENV_VARS) - {env_var}:
        monkeypatch.delenv(var, raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = getattr(dirs, prop)
    expected = Path("/tmp/some-dir/MyApp")  # noqa: S108

    assert result == (str(expected) if prop == "user_cache_dir" else expected)


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
def test_user_cache_dir_macos_fallback(monkeypatch: MonkeyPatch, prop: str) -> None:
    """Test the user cache directory on macOS as a fallback."""
    monkeypatch.setattr(sys, "platform", "darwin")
    from platformdirs.macos import MacOS as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv("HOME", "/home/user")
    for var in TEMP_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = getattr(dirs, prop)
    expected = Path("/home/user/Library/Caches/MyApp")

    assert result == (str(expected) if prop == "user_cache_dir" else expected)


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
@pytest.mark.parametrize("env_var", TEMP_ENV_VARS)
def test_user_cache_dir_windows_tmp_set(monkeypatch: MonkeyPatch, prop: str, env_var: str) -> None:
    """Test the user cache directory on Windows when a temp env var is set."""
    monkeypatch.setattr(sys, "platform", "win32")
    from platformdirs.windows import Windows as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv(env_var, "C:\\Temp\\some-dir")

    # Unset other temp vars to ensure priority is tested
    for var in set(TEMP_ENV_VARS) - {env_var}:
        monkeypatch.delenv(var, raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = str(getattr(dirs, prop))
    expected = str(Path("C:\\Temp\\some-dir\\MyCompany\\MyApp\\Cache"))

    assert result.replace("\\", "/") == expected.replace("\\", "/")


@pytest.mark.parametrize("prop", ["user_cache_dir", "user_cache_path"])
def test_user_cache_dir_windows_fallback(monkeypatch: MonkeyPatch, prop: str) -> None:
    """Test the user cache directory on Windows as a fallback."""
    monkeypatch.setattr(sys, "platform", "win32")
    from platformdirs.windows import Windows as PlatformDirs  # noqa: PLC0415

    monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\user\\AppData\\Local")
    for var in TEMP_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    dirs = PlatformDirs("MyApp", "MyCompany")
    result = str(getattr(dirs, prop))
    expected = str(Path("C:\\Users\\user\\AppData\\Local\\MyCompany\\MyApp\\Cache"))

    assert result.replace("\\", "/") == expected.replace("\\", "/")
