import os
import typing

import pytest
from _pytest.monkeypatch import MonkeyPatch

from platformdirs.unix import Unix


class XDGVariable(typing.NamedTuple):
    name: str
    default_value: str


def _func_to_path(func: str) -> XDGVariable:
    mapping = {
        "user_data_dir": XDGVariable("XDG_DATA_HOME", "~/.local/share"),
        "site_data_dir": XDGVariable("XDG_DATA_DIRS", f"/usr/local/share{os.pathsep}/usr/share"),
        "user_config_dir": XDGVariable("XDG_CONFIG_HOME", "~/.config"),
        "site_config_dir": XDGVariable("XDG_CONFIG_DIRS", "/etc/xdg"),
        "user_cache_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
        "user_state_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
        "user_log_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
    }
    return mapping[func]


@pytest.fixture()
def dirs_instance() -> Unix:
    return Unix(multipath=True, opinion=False)


def test_xdg_variable_not_set(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    monkeypatch.delenv(xdg_variable.name, raising=False)
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


def test_xdg_variable_empty_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    monkeypatch.setenv(xdg_variable.name, "")
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


def test_xdg_variable_custom_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    monkeypatch.setenv(xdg_variable.name, "/tmp/custom-dir")
    result = getattr(dirs_instance, func)
    assert result == "/tmp/custom-dir"
