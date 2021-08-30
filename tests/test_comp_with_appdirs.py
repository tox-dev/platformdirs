import sys
from typing import Any, Dict

import appdirs
import pytest

import platformdirs

NEW_IN_PLATFORMDIRS = {"user_runtime_dir"}


def test_has_backward_compatible_class() -> None:
    from platformdirs import AppDirs

    assert AppDirs is platformdirs.PlatformDirs


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"appname": "foo"},
        {"appname": "foo", "appauthor": "bar"},
        {"appname": "foo", "appauthor": "bar", "version": "v1.0"},
    ],
    ids=[
        "no_args",
        "app_name",
        "app_name_with_app_author",
        "app_name_author_version",
    ],
)
def test_compatibility(params: Dict[str, Any], func: str) -> None:
    if func in NEW_IN_PLATFORMDIRS:
        pytest.skip(f"`{func}` does not exist in `appdirs`")
    if sys.platform == "darwin":
        msg = {  # pragma: no cover
            "user_log_dir": "without appname produces NoneType error",
            "site_config_dir": "ignores the version argument",
            "user_config_dir": "uses Library/Preferences instead Application Support",
        }
        if func in msg:  # pragma: no cover
            pytest.skip(f"`appdirs.{func}` {msg[func]} on macOS")  # pragma: no cover

    new = getattr(platformdirs, func)(*params)
    old = getattr(appdirs, func)(*params)

    assert new == old
