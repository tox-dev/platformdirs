import sys
from typing import Any, Dict

import appdirs
import pytest
from pytest_mock import MockerFixture

import platformdirs
from platformdirs.unix import SUPPORTS_XDG

from .common import OS


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
@pytest.mark.parametrize("system", ("darwin", "unix", "win32"))
def test_compatibility(
    mocker: MockerFixture,
    params: Dict[str, Any],
    system: str,
    func: str,
    mock_environ: Dict[str, str],
) -> None:
    if system == "darwin":
        msg = {  # pragma: no cover
            "user_log_dir": "without appname produces NoneType error",
            "site_config_dir": "ignores the version argument",
            "user_config_dir": "uses Library/Preferences instead of Application Support",
        }
        if func in msg:  # pragma: no cover
            pytest.skip(
                f"`appdirs.{func}` {msg[func]} on macOS"
            )  # pragma: no cover
        if SUPPORTS_XDG.get(func) in mock_environ:
            pytest.skip(
                f"`appdirs.{func}` ignores the XDG specification on macOS"
            )
    if system == "win32" and sys.platform != "win32":
        pytest.skip("Windows tests only work on win32")  # pragma: no cover

    mocker.patch("sys.platform", system)
    mocker.patch("appdirs.system", system)
    mocker.patch("platformdirs.PlatformDirs", OS[system])
    # ASSUMPTION: For checking compat, we only care about the old location if
    # it's on disk.
    mocker.patch("os.path.exists", lambda _: True)

    new = getattr(platformdirs, func)(*params)
    old = getattr(appdirs, func)(*params)

    assert new == old
