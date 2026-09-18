from __future__ import annotations

import pytest

from platformdirs import PlatformDirs


@pytest.mark.parametrize("kwargs", [
    {"appname": "../evil"},
    {"appname": "safe", "version": "../evil"},
    {"appname": "safe", "appauthor": "acme/../evil"},
    {"appname": "foo/../../etc"},
])
def test_rejects_parent_directory_components(kwargs: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="parent-directory"):
        PlatformDirs(**kwargs)


def test_allows_nested_namespacing() -> None:
    dirs = PlatformDirs(appname="Company/App", version="1.0")
    assert "Company/App" in dirs.user_data_dir.replace("\\", "/")
    assert dirs.user_data_dir.endswith("1.0") or dirs.user_data_dir.replace("\\", "/").endswith("1.0")
