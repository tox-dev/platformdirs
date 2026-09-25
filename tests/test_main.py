from __future__ import annotations

import sys
from subprocess import check_output  # ruff:ignore[suspicious-subprocess-import]
from typing import TYPE_CHECKING, Final

from platformdirs import __version__
from platformdirs.__main__ import PROPS, main
from platformdirs.unix import Unix

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from pytest_mock import MockerFixture


def test_props_same_as_test(props: tuple[str, ...]) -> None:
    assert props == PROPS


def test_run_as_module() -> None:
    out = check_output([sys.executable, "-m", "platformdirs"], text=True)

    assert out.startswith(f"-- platformdirs {__version__} --")
    for prop in PROPS:
        assert prop in out


def test_run_prints_permission_error_and_continues(
    mocker: MockerFixture, runtime_temp_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mocker.patch("platformdirs.__main__.PlatformDirs", Unix)
    owner: Final = runtime_temp_dir.stat().st_uid
    (runtime_temp_dir / f"runtime-{owner + 1}").mkdir()
    mocker.patch("platformdirs.unix.getuid", return_value=owner + 1)
    main()
    error: Final = f"runtime directory {runtime_temp_dir}/runtime-{owner + 1} is owned by uid {owner}, not {owner + 1}"
    # every report section continues past the failing property
    assert capsys.readouterr().out.splitlines().count(f"user_runtime_dir: {error}; set XDG_RUNTIME_DIR instead") == 4
