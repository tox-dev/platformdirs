from __future__ import annotations

import os
from typing import Any

import pytest

from platformdirs.macos import MacOS


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"appname": "foo"},
        {"appname": "foo", "version": "v1.0"},
    ],
    ids=[
        "no_args",
        "app_name",
        "app_name_version",
    ],
)
def test_macos(params: dict[str, Any], func: str) -> None:
    result = getattr(MacOS(**params), func)

    home = os.path.expanduser("~")
    suffix_elements = []
    if "appname" in params:
        suffix_elements.append(params["appname"])
    if "version" in params:
        suffix_elements.append(params["version"])
    if suffix_elements:
        suffix_elements.insert(0, "")
    suffix = "/".join(suffix_elements)

    expected_map = {
        "user_data_dir": f"{home}/Library/Application Support{suffix}",
        "site_data_dir": f"/Library/Application Support{suffix}",
        # Please note that the config dirs are NOT */Library/Preferences!
        # For details see: https://github.com/platformdirs/platformdirs/issues/98
        "user_config_dir": f"{home}/Library/Application Support{suffix}",
        "site_config_dir": f"/Library/Application Support{suffix}",
        "user_cache_dir": f"{home}/Library/Caches{suffix}",
        "user_state_dir": f"{home}/Library/Application Support{suffix}",
        "user_log_dir": f"{home}/Library/Logs{suffix}",
        "user_documents_dir": f"{home}/Documents",
        "user_runtime_dir": f"{home}/Library/Caches/TemporaryItems{suffix}",
    }
    expected = expected_map[func]

    assert result == expected
