from __future__ import annotations

import sys
from subprocess import check_output  # ruff:ignore[suspicious-subprocess-import]
from typing import TYPE_CHECKING, Final

import pytest

from platformdirs import PlatformDirs

if TYPE_CHECKING:
    from pathlib import Path


def test_platformdirs_isolated_yields_tmp_path(platformdirs_isolated: Path, tmp_path: Path) -> None:
    assert platformdirs_isolated == tmp_path


def test_platformdirs_isolated_redirects(platformdirs_isolated: Path) -> None:
    assert PlatformDirs("app").user_config_path == platformdirs_isolated / "user_config" / "app"


def test_platformdirs_isolated_is_opt_in(request: pytest.FixtureRequest) -> None:
    assert "platformdirs_isolated" not in request.fixturenames


def test_import_platformdirs_skips_pytest() -> None:
    code = "import sys, platformdirs, platformdirs.testing; print('pytest' in sys.modules)"
    assert check_output([sys.executable, "-c", code], text=True).strip() == "False"


@pytest.mark.parametrize(
    "invocation",
    [
        pytest.param("pytest.main(args)", id="main-thread"),
        pytest.param("executor.submit(pytest.main, args).result()", id="worker-thread"),
    ],
)
def test_import_before_pytest_main(tmp_path: Path, invocation: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    (tmp_path / "test_example.py").write_text(
        "from pathlib import Path\n"
        "from platformdirs import PlatformDirs\n\n"
        "def test_isolation(platformdirs_isolated: Path) -> None:\n"
        "    assert PlatformDirs('app').user_config_path == platformdirs_isolated / 'user_config' / 'app'\n",
        encoding="utf-8",
    )
    code: Final = (
        "import platformdirs\n"
        "import pytest\n"
        "from concurrent.futures import ThreadPoolExecutor\n"
        "args = ['-q', '-Werror']\n"
        "with ThreadPoolExecutor(max_workers=1) as executor:\n"
        f"    raise SystemExit({invocation})\n"
    )
    assert "1 passed" in check_output([sys.executable, "-Werror", "-c", code], cwd=tmp_path, text=True)
