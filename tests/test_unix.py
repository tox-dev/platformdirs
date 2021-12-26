from __future__ import annotations

import importlib
import os
import sys
import typing

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from platformdirs.unix import Unix


def test_user_documents_dir(mocker: MockerFixture) -> None:
    example_path = "/home/example/ExampleDocumentsFolder"
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = example_path
    assert Unix().user_documents_dir == example_path


def test_user_documents_dir_env_var(mocker: MockerFixture) -> None:
    # Mock documents dir not being in user-dirs.dirs file
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = None

    example_path = "/home/example/ExampleDocumentsFolder"
    mocker.patch.dict(os.environ, {"XDG_DOCUMENTS_DIR": example_path})

    assert Unix().user_documents_dir == example_path


def test_user_documents_dir_default(mocker: MockerFixture) -> None:
    # Mock documents dir not being in user-dirs.dirs file
    mock = mocker.patch("platformdirs.unix._get_user_dirs_folder")
    mock.return_value = None

    # Mock no XDG_DOCUMENTS_DIR env variable being set
    mocker.patch.dict(os.environ, {"XDG_DOCUMENTS_DIR": ""})

    # Mock home directory
    mocker.patch.dict(os.environ, {"HOME": "/home/example"})
    # Mock home directory for running the test on Windows
    mocker.patch.dict(os.environ, {"USERPROFILE": "/home/example"})

    assert Unix().user_documents_dir == "/home/example/Documents"


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
        "user_log_dir": XDGVariable("XDG_CACHE_HOME", "~/.cache"),
        "user_runtime_dir": XDGVariable("XDG_RUNTIME_DIR", "/run/user/1234"),
    }
    return mapping.get(func)


@pytest.fixture()
def dirs_instance() -> Unix:
    return Unix(multipath=True, opinion=False)


@pytest.fixture()
def _getuid(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.unix.getuid", return_value=1234)


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_not_set(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.delenv(xdg_variable.name, raising=False)
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_empty_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, "")
    result = getattr(dirs_instance, func)
    assert result == os.path.expanduser(xdg_variable.default_value)


@pytest.mark.usefixtures("_getuid")
def test_xdg_variable_custom_value(monkeypatch: MonkeyPatch, dirs_instance: Unix, func: str) -> None:
    xdg_variable = _func_to_path(func)
    if xdg_variable is None:
        return

    monkeypatch.setenv(xdg_variable.name, "/tmp/custom-dir")
    result = getattr(dirs_instance, func)
    assert result == "/tmp/custom-dir"


def test_platform_non_linux(monkeypatch: MonkeyPatch) -> None:
    from platformdirs import unix

    try:
        with monkeypatch.context() as context:
            context.setattr(sys, "platform", "magic")
            monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
            importlib.reload(unix)
        with pytest.raises(RuntimeError, match="should only be used on Linux"):
            unix.Unix().user_runtime_dir
    finally:
        importlib.reload(unix)
