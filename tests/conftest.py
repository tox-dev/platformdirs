from __future__ import annotations

from typing import cast

import pytest
from _pytest.fixtures import SubRequest

PROPS = (
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "user_documents_dir",
    "user_runtime_dir",
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
def props() -> tuple[str, ...]:
    return PROPS
