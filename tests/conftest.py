import os
from pathlib import Path
from typing import Any, Dict, Tuple, cast

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture

from platformdirs.android import Android
from platformdirs.macos import MacOS
from platformdirs.unix import Unix
from platformdirs.windows import Windows

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
)

PARAMS = {
    "no_args": {},
    "app_name": {"appname": "foo"},
    "app_name_with_app_author": {"appname": "foo", "appauthor": "bar"},
    "app_name_author_version": {
        "appname": "foo",
        "appauthor": "bar",
        "version": "v1.0",
    },
    "app_name_author_version_false_opinion": {
        "appname": "foo",
        "appauthor": "bar",
        "version": "v1.0",
        "opinion": False,
    },
}


PLATFORMS = {
    "android": Android,
    "darwin": MacOS,
    "unix": Unix,
    "windows": Windows,
}


@pytest.fixture(params=PARAMS.values(), ids=PARAMS.keys())
def params(request: SubRequest) -> Dict[str, Any]:
    return cast(Dict[str, str], request.param)


@pytest.fixture(params=PROPS)
def func(request: SubRequest) -> str:
    return cast(str, request.param)


@pytest.fixture(params=PROPS)
def func_path(request: SubRequest) -> str:
    prop = cast(str, request.param)
    prop = prop.replace("_dir", "_path")
    return prop


@pytest.fixture()
def props() -> Tuple[str, ...]:
    return PROPS


@pytest.fixture
def mock_environ(
    mocker: MockerFixture,
    tmp_path: Path,
) -> Dict[str, Any]:
    mocker.patch("os.environ", {})
    home = str(tmp_path)

    def _expanduser(s: str) -> str:
        if s == "~":
            return home
        if s.startswith("~/"):
            return str(tmp_path / s[2:])
        return s

    mocker.patch("os.path.expanduser", _expanduser)
    os.environ["HOME"] = home

    return os.environ
