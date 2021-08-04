import os
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Tuple, Union

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture

from platformdirs.macos import XDG_SUPPORT, MacOS
from platformdirs.unix import XDG_DEFAULTS

# Mapping between function name and relevant XDG var
OLD = {
    "user_data_dir": "~/Library/Application Support",
    "site_data_dir": "/Library/Application Support",
    "user_config_dir": "~/Library/Preferences",
    "site_config_dir": "/Library/Preferences",
    "user_cache_dir": "~/Library/Caches",
    "user_state_dir": "~/Library/Application Support",
    "user_log_dir": "~/Library/Logs",
}


@pytest.mark.parametrize("func", OLD.keys())
@pytest.mark.parametrize("exists", (False, True), ids=("not_exists", "exists"))
@pytest.mark.parametrize(
    "xdg_fallback",
    (False, True),
    ids=("no_xdg_fallback", "xdg_fallback"),
)
def test_with_xdg_unset(
    mocker: MockerFixture,
    params: Dict[str, Any],
    func: str,
    exists: bool,
    xdg_fallback: bool,
    mock_environ: Dict[str, str],
):
    mocker.patch("os.path.exists", lambda _: exists)
    obj = MacOS(**params, xdg_fallback=xdg_fallback)
    result = getattr(obj, func)
    old = os.path.expanduser(OLD[func])

    if exists:
        prefix = old
    elif xdg_fallback and func in XDG_SUPPORT:
        prefix = os.path.expanduser(XDG_DEFAULTS[XDG_SUPPORT[func]])
    else:
        prefix = old

    if not result.startswith(prefix):  # pragma: no cover
        common = os.path.commonpath((result, prefix))
        result_unique = f"${{common}}{result[len(common) :]}"
        prefix_unique = f"${{common}}{prefix[len(common) :]}"
        common_msg = f'+ where common = {common.rstrip("/")}' if common != "/" else ""
        msg = dedent(
            f"""\
            Path $result does not start with $prefix
            + where result = {result_unique if common_msg else result}
            + where prefix = {prefix_unique if common_msg else prefix}
            {common_msg}
            """
        ).strip()
        assert False, msg
