from __future__ import annotations

import sys
from inspect import getmembers, isfunction
from typing import TypedDict

import appdirs
import pytest

import platformdirs


def test_has_backward_compatible_class() -> None:
    from platformdirs import AppDirs  # ruff:ignore[import-outside-top-level]  # the test checks this alias itself

    assert AppDirs is platformdirs.PlatformDirs


def test_has_all_functions() -> None:
    # Get all public function names from appdirs
    appdirs_function_names = [f[0] for f in getmembers(appdirs, isfunction) if not f[0].startswith("_")]

    # Exception will be raised if any appdirs functions aren't in platformdirs.
    for function_name in appdirs_function_names:
        getattr(platformdirs, function_name)


def test_has_all_properties() -> None:
    # Get names of all the properties of appdirs.AppDirs
    appdirs_property_names = [p[0] for p in getmembers(appdirs.AppDirs, lambda member: isinstance(member, property))]

    # Exception will be raised if any appdirs.AppDirs properties aren't in platformdirs.AppDirs
    for property_name in appdirs_property_names:
        getattr(platformdirs.AppDirs, property_name)


class AppParams(TypedDict, total=False):
    appname: str
    version: str
    appauthor: str


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
@pytest.mark.parametrize(
    "func",
    [
        pytest.param("site_config_dir", id="site_config_dir"),
        pytest.param("site_data_dir", id="site_data_dir"),
        pytest.param("user_cache_dir", id="user_cache_dir"),
        pytest.param("user_config_dir", id="user_config_dir"),
        pytest.param("user_data_dir", id="user_data_dir"),
        pytest.param(
            "user_log_dir",
            marks=pytest.mark.skipif(
                sys.platform != "win32",
                reason="appdirs.user_log_dir fails without an appname on macOS and uses XDG_STATE_DIR on Unix",
            ),
            id="user_log_dir",
        ),
        pytest.param("user_state_dir", id="user_state_dir"),
    ],
)
@pytest.mark.usefixtures("_clear_xdg_env")
def test_compatibility(params: AppParams, func: str, monkeypatch: pytest.MonkeyPatch) -> None:
    # Compare system defaults here; appdirs has no Homebrew-specific locations.
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    new = getattr(platformdirs, func)(*params)
    old = getattr(appdirs, func)(*params)

    assert new == old.rstrip("/")
