from __future__ import annotations

import sys
from subprocess import check_output  # ruff:ignore[suspicious-subprocess-import]
from typing import TYPE_CHECKING

from platformdirs import PlatformDirs

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_platformdirs_isolated_yields_tmp_path(platformdirs_isolated: Path, tmp_path: Path) -> None:
    assert platformdirs_isolated == tmp_path


def test_platformdirs_isolated_redirects(platformdirs_isolated: Path) -> None:
    assert PlatformDirs("app").user_config_path == platformdirs_isolated / "user_config" / "app"


def test_platformdirs_isolated_is_opt_in(request: pytest.FixtureRequest) -> None:
    assert "platformdirs_isolated" not in request.fixturenames


def test_import_platformdirs_skips_pytest() -> None:
    code = "import sys, platformdirs, platformdirs.testing; print('pytest' in sys.modules)"
    assert check_output([sys.executable, "-c", code], text=True).strip() == "False"
