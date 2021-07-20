import sys
from subprocess import check_output
from typing import Tuple

from platformdirs import __version__
from platformdirs.__main__ import PROPS


def test_props_same_as_test(props: Tuple[str, ...]) -> None:
    assert PROPS == props


def test_run_as_module() -> None:
    out = check_output([sys.executable, "-m", "platformdirs"], universal_newlines=True)

    assert out.startswith(f"-- platformdirs {__version__} --")
    for prop in PROPS:
        assert prop in out
