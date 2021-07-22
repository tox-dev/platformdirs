from typing import Tuple, cast

import pytest
from _pytest.fixtures import SubRequest

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
)

PROPS_PATH = (
    "user_data_path",
    "user_config_path",
    "user_cache_path",
    "user_state_path",
    "user_log_path",
    "site_data_path",
    "site_config_path",
)


@pytest.fixture(params=PROPS)
def func(request: SubRequest) -> str:
    return cast(str, request.param)


@pytest.fixture(params=PROPS_PATH)
def func_path(request: SubRequest) -> str:
    return cast(str, request.param)


@pytest.fixture()
def props() -> Tuple[str, ...]:
    return PROPS
