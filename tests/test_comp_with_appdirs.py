import sys
from typing import Any, Dict

import appdirs
import pytest

import platformdirs


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
    if sys.platform == "darwin" and func == "user_log_dir":
        pytest.skip("`appdirs.user_log_dir` without appname produces NoneType error on macOS")  # pragma: no cover
    if sys.platform == "darwin" and func == "site_config_dir":
        pytest.skip("`appdirs.site_config_dir` ignores the version argument on macOS")  # pragma: no cover

    new = getattr(platformdirs, func)(*params)
    old = getattr(appdirs, func)(*params)

    assert new == old
