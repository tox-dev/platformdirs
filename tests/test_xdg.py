import os
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture

from platformdirs.macos import MacOS
from platformdirs.unix import SUPPORTS_XDG, Unix

from .common import OS, PARAMS


@pytest.mark.parametrize("params", PARAMS.values(), ids=PARAMS.keys())
@pytest.mark.parametrize("klass", OS.values(), ids=OS.keys())
@pytest.mark.parametrize(
    "case",
    SUPPORTS_XDG.items(),
    ids=(s.lower() for s in SUPPORTS_XDG.keys()),
)
def test_xdg_compliance_on_unix(
    mocker: MockerFixture,
    params: Dict[str, Any],
    klass: Union[MacOS, Unix],
    case: Tuple[str, str],
    mock_environ: Dict[str, str],
    mock_homedir: Path,
):
    func, key = case
    prefix = mock_environ[key] = os.path.expanduser(f"~/{func}")

    result: str = getattr(klass(**params), func)

    assert result.startswith(prefix)
