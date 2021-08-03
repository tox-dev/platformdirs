import os
from pathlib import Path
from typing import Any, Dict, Tuple, cast

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
)


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
def mock_environ(mocker: MockerFixture) -> Dict[str, Any]:
    mocker.patch("os.environ", {})
    return os.environ


@pytest.fixture
def mock_homedir(
    mocker: MockerFixture,
    mock_environ: dict,
    tmp_path: Path,
) -> Path:
    def _expanduser(s: str) -> str:
        if s == "~":
            return str(tmp_path)
        if s.startswith("~/"):
            return str(tmp_path / s[2:])
        return s

    mocker.patch("os.path.expanduser", _expanduser)
    mock_environ["HOME"] = str(tmp_path)
    return tmp_path
