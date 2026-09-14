from __future__ import annotations

import pytest

import platformdirs.unix
from platformdirs.unix import Unix


def test_user_log_dir_respects_opinion_when_use_site(monkeypatch: pytest.MonkeyPatch) -> None:
    """When opinion=False, user_log_dir should equal user_state_dir even when _use_site is True.

    This is a round-trip consistency bug:
    - Non-root, opinion=False: user_log_dir == user_state_dir
    - Root, opinion=False with use_site_for_root: user_log_dir should == site_state_dir
      (not site_log_dir)

    The implementation must respect opinion when _use_site is True.
    """
    # Simulate running as root by patching getuid BEFORE creating the object
    monkeypatch.setattr(platformdirs.unix, "getuid", lambda: 0)

    # Create instance with opinion=False
    p = Unix(appname="myapp", version="1.0", use_site_for_root=True, opinion=False, ensure_exists=False)

    # Clear the cached_property so it recomputes with our patched getuid
    if hasattr(p, "__dict__") and "_use_site" in p.__dict__:
        del p.__dict__["_use_site"]

    # When opinion=False, user_log_dir should equal user_state_dir
    # Since we're simulating root with use_site_for_root=True, user_state_dir returns site_state_dir
    # So user_log_dir should also return site_state_dir (not site_log_dir)
    user_state = p.user_state_dir
    user_log = p.user_log_dir

    # THE BUG: user_log_dir returns site_log_dir instead of site_state_dir when opinion=False
    # Expected: user_log_dir == site_state_dir (because opinion=False and _use_site=True)
    # Actual (before fix): user_log_dir == site_log_dir (opinion is ignored)

    # This assertion FAILS with current code (demonstrates the bug)
    assert user_log == user_state, (
        f"Round-trip defect: with opinion=False and use_site_for_root, "
        f"user_log_dir should equal user_state_dir, but got {user_log} != {user_state}"
    )
