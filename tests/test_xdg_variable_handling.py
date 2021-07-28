import os
import platform
import typing

import pytest

import platformdirs


class XDGVariable(typing.NamedTuple):
    name: str
    default_value: str


DIR_CUSTOM = "/tmp/custom-dir"
MAP_XDG_DEFAULTS_WITH_MULTIPATH = {
    "user_data_dir": XDGVariable("XDG_DATA_HOME", "~/.local/share"),
    "site_data_dir": XDGVariable("XDG_DATA_DIRS", f"/usr/local/share{os.pathsep}/usr/share"),
    "user_config_dir": XDGVariable("XDG_CONFIG_HOME", "~/.config"),
    "site_config_dir": XDGVariable("XDG_CONFIG_DIRS", "/etc/xdg"),
    "user_cache_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
    "user_state_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
    "user_log_dir": XDGVariable("XDG_LOG_HOME", "~/.cache"),
}


@pytest.fixture()
def dirs_instance() -> platformdirs.PlatformDirs:
    return platformdirs.PlatformDirs(multipath=True, opinion=False)


@pytest.mark.skipif(platform.system() != "Linux", reason="requires Linux")
def test_xdg_variable_not_set(monkeypatch, dirs_instance: platformdirs.PlatformDirs, func: str) -> None:
    xdg_variable = MAP_XDG_DEFAULTS_WITH_MULTIPATH[func]
    monkeypatch.delenv(xdg_variable.name, raising=False)
    result = getattr(dirs_instance, func)
    assert result == xdg_variable.default_value


@pytest.mark.skipif(platform.system() != "Linux", reason="requires Linux")
def test_xdg_variable_empty_value(monkeypatch, dirs_instance: platformdirs.PlatformDirs, func: str) -> None:
    xdg_variable = MAP_XDG_DEFAULTS_WITH_MULTIPATH[func]
    monkeypatch.setenv(xdg_variable.name, "")
    result = getattr(dirs_instance, func)
    assert result == xdg_variable.default_value


@pytest.mark.skipif(platform.system() != "Linux", reason="requires Linux")
def test_xdg_variable_custom_value(monkeypatch, dirs_instance: platformdirs.PlatformDirs, func: str) -> None:
    xdg_variable = MAP_XDG_DEFAULTS_WITH_MULTIPATH[func]
    monkeypatch.setenv(xdg_variable.name, DIR_CUSTOM)
    result = getattr(dirs_instance, func)
    assert result == DIR_CUSTOM
