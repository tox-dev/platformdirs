import pytest

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
def func(request):
    return request.param


@pytest.fixture()
def props():
    return PROPS
