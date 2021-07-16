import importlib
import os
import sys

import pytest


@pytest.fixture()
def android_platformdirs(monkeypatch):
    import platformdirs

    # on Android just return what was resolved
    if os.environ.get("ANDROID_DATA") == "/data" and os.environ.get("ANDROID_ROOT") == "/system":
        return platformdirs
    # on non Android mock an Android environment
    with monkeypatch.context() as context:
        context.setenv("ANDROID_DATA", "/data")
        context.setenv("ANDROID_ROOT", "/system")
        context.syspath_prepend("/data/data/com.example/files")
        result = importlib.reload(platformdirs)
    if sys.platform == "win32":
        monkeypatch.setattr(platformdirs.os, "sep", "/")
    yield result
    importlib.reload(platformdirs)


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
def test_android(params, android_platformdirs, func):
    result = getattr(android_platformdirs, func)(**params)

    suffix_elements = []
    if "appname" in params:
        suffix_elements.append(params["appname"])
    if "version" in params:
        suffix_elements.append(params["version"])
    if suffix_elements:
        suffix_elements.insert(0, "")
    suffix = "/".join(suffix_elements)

    expected_map = {
        "user_data_dir": f"/data/data/com.example/files{suffix}",
        "site_data_dir": f"/data/data/com.example/files{suffix}",
        "user_config_dir": f"/data/data/com.example/shared_prefs{suffix}",
        "site_config_dir": f"/data/data/com.example/shared_prefs{suffix}",
        "user_cache_dir": f"/data/data/com.example/cache{suffix}",
        "user_state_dir": f"/data/data/com.example/files{suffix}",
        "user_log_dir": f"/data/data/com.example/cache{suffix}/log",
    }
    expected = expected_map[func]

    assert result == expected
