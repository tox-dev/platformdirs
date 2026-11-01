"""Regression tests for platformdirs issue #678."""

from __future__ import annotations

import os

import pytest

from platformdirs._xdg import _xdg_dir, _xdg_dir_list
from platformdirs.unix import Unix


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        ("XDG_DATA_HOME", "user_data_dir"),
        ("XDG_CONFIG_HOME", "user_config_dir"),
        ("XDG_CACHE_HOME", "user_cache_dir"),
        ("XDG_STATE_HOME", "user_state_dir"),
    ],
)
@pytest.mark.parametrize("suffix", [" ", "\t"])
def test_xdg_home_preserves_whitespace(
    monkeypatch: pytest.MonkeyPatch,
    env_var: str,
    prop: str,
    suffix: str,
) -> None:
    base = "/xdg-fixture/xdg-home" + suffix
    monkeypatch.setenv(env_var, base)
    assert getattr(Unix(appname="demo"), prop) == base + "/demo"


@pytest.mark.parametrize(
    ("env_var", "prop"),
    [
        ("XDG_DATA_DIRS", "site_data_dir"),
        ("XDG_CONFIG_DIRS", "site_config_dir"),
    ],
)
def test_xdg_list_preserves_whitespace(
    monkeypatch: pytest.MonkeyPatch,
    env_var: str,
    prop: str,
) -> None:
    paths = [
        "/xdg-fixture/first ",
        " /xdg-fixture/invalid",
        "/xdg-fixture/second\t",
        "",
        "relative",
    ]
    monkeypatch.setenv(env_var, os.pathsep.join(paths))
    expected = os.pathsep.join([
        "/xdg-fixture/first /demo",
        "/xdg-fixture/second\t/demo",
    ])
    assert getattr(Unix(appname="demo", multipath=True), prop) == expected


def test_leading_whitespace_is_not_absolute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", " /xdg-fixture/invalid")
    monkeypatch.setenv("XDG_DATA_DIRS", os.pathsep.join([" /xdg-fixture/invalid", "/xdg-fixture/valid "]))

    assert _xdg_dir("XDG_DATA_HOME") is None
    assert _xdg_dir_list("XDG_DATA_DIRS") == ["/xdg-fixture/valid "]
