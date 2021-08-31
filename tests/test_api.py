import inspect
from pathlib import Path
from typing import Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch

import platformdirs
from platformdirs.android import Android


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


@pytest.mark.parametrize("root", ["A", "/system", None])
@pytest.mark.parametrize("data", ["D", "/data", None])
def test_android_active(monkeypatch: MonkeyPatch, root: Optional[str], data: Optional[str]) -> None:
    for env_var, value in {"ANDROID_DATA": data, "ANDROID_ROOT": root}.items():
        if value is None:
            monkeypatch.delenv(env_var, raising=False)
        else:
            monkeypatch.setenv(env_var, value)

    expected = root == "/system" and data == "/data"
    if expected:
        assert platformdirs._set_platform_dir_class() is Android
    else:
        assert platformdirs._set_platform_dir_class() is not Android
