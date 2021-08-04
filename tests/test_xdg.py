import os
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Tuple, Union

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture

from platformdirs.macos import XDG_SUPPORT as MAC_XDG_SUPPORT
from platformdirs.macos import MacOS
from platformdirs.unix import XDG_SUPPORT, Unix


@pytest.mark.parametrize("klass", (MacOS, Unix), ids=("darwin", "unix"))
@pytest.mark.parametrize(
    "case",
    XDG_SUPPORT.items(),
    ids=(s.lower() for s in XDG_SUPPORT.keys()),
)
def test_xdg_compliance(
    params: Dict[str, Any],
    klass: Union[MacOS, Unix],
    case: Tuple[str, str],
    mock_environ: Dict[str, str],
):
    func, key = case
    if klass == MacOS and func not in MAC_XDG_SUPPORT:
        pytest.skip(f"Platformdirs does not use XDG for {func} on MacOS")
    prefix = mock_environ[key] = os.path.expanduser(f"~/{func}")

    result: str = getattr(klass(**params), func)

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
