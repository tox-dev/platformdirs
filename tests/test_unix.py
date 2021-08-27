import os
import typing

import pytest
from _pytest.monkeypatch import MonkeyPatch

import platformdirs.unix
from platformdirs.unix import Unix


def test_user_documents_dir(monkeypatch: MonkeyPatch) -> None:
    example_path = "/home/example/ExampleDocumentsFolder"
    monkeypatch.setattr(platformdirs.unix, "get_user_dirs_folder", lambda key: example_path)
    assert Unix().user_documents_dir == example_path

def test_user_documents_dir_env_var(monkeypatch: MonkeyPatch) -> None:
    # Mock documents dir not being in user-dirs.dirs file
    monkeypatch.setattr(platformdirs.unix, "get_user_dirs_folder", lambda key: None)

    example_path = "/home/example/ExampleDocumentsFolder"
    monkeypatch.setenv("XDG_DOCUMENTS_DIR", example_path)

    assert Unix().user_documents_dir == example_path

def test_user_documents_dir_default(monkeypatch: MonkeyPatch) -> None:
    # Mock documents dir not being in user-dirs.dirs file
    monkeypatch.setattr(platformdirs.unix, "get_user_dirs_folder", lambda key: None)
    # Mock no XDG_DOCUMENTS_DIR env variable being set
    monkeypatch.setenv("XDG_DOCUMENTS_DIR", "")

    # Mock home directory
    monkeypatch.setenv("HOME", "/home/example")

    assert Unix().user_documents_dir == "/home/example/Documents"

class XDGVariable(typing.NamedTuple):
    name: str
    default_value: str


def _func_to_path(func: str) -> typing.Optional[XDGVariable]:
    mapping = {
        "user_data_dir": XDGVariable("XDG_DATA_HOME", "~/.local/share"),
        "site_data_dir": XDGVariable("XDG_DATA_DIRS", f"/usr/local/share{os.pathsep}/usr/share"),
        "user_config_dir": XDGVariable("XDG_CONFIG_HOME", "~/.config"),
        "site_config_dir": XDGVariable("XDG_CONFIG_DIRS", "/etc/xdg"),
        "user_cache_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
        "user_state_dir": XDGVariable("XDG_STATE_HOME", "~/.local/state"),
        "user_log_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
    }
    return mapping.get(func)


@pytest.fixture()
def dirs_instance() -> Unix:
    return Unix(multipath=True, opinion=False)


def test_xdg_variable_not_set(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return
    
    monkeypatch.delenv(xdg_variable.name, raising=False)
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


def test_xdg_variable_empty_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return
    
    monkeypatch.setenv(xdg_variable.name, "")
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


def test_xdg_variable_custom_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return
    
    monkeypatch.setenv(xdg_variable.name, "/tmp/custom-dir")
    result = getattr(dirs_instance, func)
    assert result == "/tmp/custom-dir"
