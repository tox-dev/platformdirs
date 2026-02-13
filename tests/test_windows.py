from __future__ import annotations

import ctypes
import importlib
import os
import sys
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from platformdirs import windows
from platformdirs.windows import (
    _KF_FLAG_DONT_VERIFY,
    _KNOWN_FOLDER_GUIDS,
    Windows,
    get_win_folder_from_env_vars,
    get_win_folder_if_csidl_name_not_env_var,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_WIN_FOLDERS: dict[str, str] = {
    "CSIDL_APPDATA": r"C:\Users\Test\AppData\Roaming",
    "CSIDL_LOCAL_APPDATA": r"C:\Users\Test\AppData\Local",
    "CSIDL_COMMON_APPDATA": r"C:\ProgramData",
    "CSIDL_PERSONAL": r"C:\Users\Test\Documents",
    "CSIDL_DOWNLOADS": r"C:\Users\Test\Downloads",
    "CSIDL_MYPICTURES": r"C:\Users\Test\Pictures",
    "CSIDL_MYVIDEO": r"C:\Users\Test\Videos",
    "CSIDL_MYMUSIC": r"C:\Users\Test\Music",
    "CSIDL_DESKTOPDIRECTORY": r"C:\Users\Test\Desktop",
}

_LOCAL = os.path.normpath(_WIN_FOLDERS["CSIDL_LOCAL_APPDATA"])
_COMMON = os.path.normpath(_WIN_FOLDERS["CSIDL_COMMON_APPDATA"])


@pytest.fixture(autouse=True)
def _mock_get_win_folder(mocker: MockerFixture) -> None:
    mocker.patch("platformdirs.windows.get_win_folder", side_effect=lambda csidl: _WIN_FOLDERS[csidl])


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({}, id="no_args"),
        pytest.param({"appname": "foo"}, id="app_name"),
        pytest.param({"appname": "foo", "version": "v1.0"}, id="app_name_version"),
    ],
)
def test_windows(params: dict[str, Any], func: str) -> None:
    result = getattr(Windows(**params), func)

    suffix_parts = []
    if appname := params.get("appname"):
        suffix_parts.extend((appname, appname))
        if version := params.get("version"):
            suffix_parts.append(version)
    local = os.path.join(_LOCAL, *suffix_parts) if suffix_parts else _LOCAL  # noqa: PTH118
    common = os.path.join(_COMMON, *suffix_parts) if suffix_parts else _COMMON  # noqa: PTH118
    temp = os.path.join(_LOCAL, "Temp", *suffix_parts) if suffix_parts else os.path.join(_LOCAL, "Temp")  # noqa: PTH118
    cache_local = os.path.join(  # noqa: PTH118
        _LOCAL, *suffix_parts[:2], *(["Cache"] if suffix_parts else []), *suffix_parts[2:]
    )
    cache_common = os.path.join(  # noqa: PTH118
        _COMMON, *suffix_parts[:2], *(["Cache"] if suffix_parts else []), *suffix_parts[2:]
    )
    log = os.path.join(_LOCAL, *suffix_parts, "Logs")  # noqa: PTH118
    log_common = os.path.join(_COMMON, *suffix_parts, "Logs")  # noqa: PTH118

    expected_map = {
        "user_data_dir": local,
        "site_data_dir": common,
        "user_config_dir": local,
        "site_config_dir": common,
        "user_cache_dir": cache_local,
        "site_cache_dir": cache_common,
        "user_state_dir": local,
        "site_state_dir": common,
        "user_log_dir": log,
        "site_log_dir": log_common,
        "user_documents_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_PERSONAL"]),
        "user_downloads_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_DOWNLOADS"]),
        "user_pictures_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_MYPICTURES"]),
        "user_videos_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_MYVIDEO"]),
        "user_music_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_MYMUSIC"]),
        "user_desktop_dir": os.path.normpath(_WIN_FOLDERS["CSIDL_DESKTOPDIRECTORY"]),
        "user_runtime_dir": temp,
        "site_runtime_dir": temp,
    }
    assert result == expected_map[func]


def test_roaming_uses_appdata(mocker: MockerFixture) -> None:
    mock = mocker.patch("platformdirs.windows.get_win_folder", side_effect=lambda csidl: _WIN_FOLDERS[csidl])
    _result = Windows(appname="foo", roaming=True).user_data_dir
    mock.assert_called_with("CSIDL_APPDATA")


def test_non_roaming_uses_local_appdata(mocker: MockerFixture) -> None:
    mock = mocker.patch("platformdirs.windows.get_win_folder", side_effect=lambda csidl: _WIN_FOLDERS[csidl])
    _result = Windows(appname="foo", roaming=False).user_data_dir
    mock.assert_called_with("CSIDL_LOCAL_APPDATA")


def test_appauthor_false_skips_author() -> None:
    result = Windows(appname="foo", appauthor=False).user_data_dir
    assert result == os.path.join(_LOCAL, "foo")  # noqa: PTH118


def test_appauthor_explicit() -> None:
    result = Windows(appname="foo", appauthor="bar").user_data_dir
    assert result == os.path.join(_LOCAL, "bar", "foo")  # noqa: PTH118


@pytest.mark.parametrize(
    ("csidl_name", "env_var", "value"),
    [
        pytest.param("CSIDL_APPDATA", "APPDATA", r"C:\Users\Test\AppData\Roaming", id="appdata"),
        pytest.param("CSIDL_LOCAL_APPDATA", "LOCALAPPDATA", r"C:\Users\Test\AppData\Local", id="local_appdata"),
        pytest.param("CSIDL_COMMON_APPDATA", "ALLUSERSPROFILE", r"C:\ProgramData", id="common_appdata"),
    ],
)
def test_get_win_folder_from_env_vars_direct(
    monkeypatch: pytest.MonkeyPatch, csidl_name: str, env_var: str, value: str
) -> None:
    monkeypatch.setenv(env_var, value)
    assert get_win_folder_from_env_vars(csidl_name) == value


_USERPROFILE_CSIDL_PARAMS = [
    pytest.param("CSIDL_PERSONAL", "Documents", id="personal"),
    pytest.param("CSIDL_DOWNLOADS", "Downloads", id="downloads"),
    pytest.param("CSIDL_MYPICTURES", "Pictures", id="pictures"),
    pytest.param("CSIDL_MYVIDEO", "Videos", id="video"),
    pytest.param("CSIDL_MYMUSIC", "Music", id="music"),
]


@pytest.mark.parametrize(("csidl_name", "subfolder"), _USERPROFILE_CSIDL_PARAMS)
def test_get_win_folder_from_env_vars_user_folders(
    monkeypatch: pytest.MonkeyPatch, csidl_name: str, subfolder: str
) -> None:
    monkeypatch.setenv("USERPROFILE", r"C:\Users\Test")
    assert get_win_folder_from_env_vars(csidl_name).endswith(subfolder)


def test_get_win_folder_from_env_vars_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown CSIDL name"):
        get_win_folder_from_env_vars("CSIDL_BOGUS")


def test_get_win_folder_from_env_vars_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPDATA", raising=False)
    with pytest.raises(ValueError, match="Unset environment variable"):
        get_win_folder_from_env_vars("CSIDL_APPDATA")


def test_get_win_folder_if_csidl_name_not_env_var_returns_none() -> None:
    assert get_win_folder_if_csidl_name_not_env_var("CSIDL_APPDATA") is None


@pytest.mark.parametrize(("csidl_name", "subfolder"), _USERPROFILE_CSIDL_PARAMS)
def test_get_win_folder_if_csidl_name_not_env_var(
    monkeypatch: pytest.MonkeyPatch, csidl_name: str, subfolder: str
) -> None:
    monkeypatch.setenv("USERPROFILE", r"C:\Users\Test")
    result = get_win_folder_if_csidl_name_not_env_var(csidl_name)
    assert result is not None
    assert result.endswith(subfolder)


def _setup_ctypes_mocks(mocker: MockerFixture, *, win_dll: MagicMock | None = None) -> None:
    """Mock ctypes internals so get_win_folder_via_ctypes can be tested on non-Windows."""
    for attr in ("HRESULT", "WinDLL"):
        if not hasattr(ctypes, attr):
            setattr(ctypes, attr, MagicMock())
    if win_dll is not None:
        ctypes.WinDLL = win_dll  # type: ignore[attr-defined]
    mocker.patch("sys.platform", "win32")
    mocker.patch("ctypes.POINTER", return_value=MagicMock())


def _cleanup_ctypes_mocks() -> None:
    for attr in ("HRESULT", "WinDLL"):
        if isinstance(getattr(ctypes, attr, None), MagicMock):
            delattr(ctypes, attr)


@pytest.mark.skipif(sys.platform != "win32", reason="real ctypes test only runs on Windows")
@pytest.mark.parametrize("csidl_name", list(_KNOWN_FOLDER_GUIDS.keys()), ids=list(_KNOWN_FOLDER_GUIDS.keys()))
def test_get_win_folder_via_ctypes_real(csidl_name: str) -> None:
    importlib.reload(windows)
    from platformdirs.windows import get_win_folder_via_ctypes as fresh_fn  # noqa: PLC0415

    result = fresh_fn(csidl_name)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.skipif(sys.platform == "win32", reason="mock-based flag inspection only runs on non-Windows")
def test_get_win_folder_via_ctypes_passes_dont_verify_flag(mocker: MockerFixture) -> None:
    _setup_ctypes_mocks(mocker)

    mock_ole32 = MagicMock()
    mock_shell32 = MagicMock()
    mock_kernel32 = MagicMock()
    ctypes.WinDLL = MagicMock(  # type: ignore[attr-defined]
        side_effect=lambda name: {"ole32": mock_ole32, "shell32": mock_shell32, "kernel32": mock_kernel32}[name],
    )

    mocker.patch("ctypes.byref", side_effect=lambda x: x)

    mock_path_ptr = MagicMock()
    mock_path_ptr.value = r"C:\Users\Test\AppData\Local"
    mocker.patch("ctypes.wintypes.LPWSTR", return_value=mock_path_ptr)

    try:
        importlib.reload(windows)
        from platformdirs.windows import get_win_folder_via_ctypes as fresh_fn  # noqa: PLC0415

        result = fresh_fn("CSIDL_LOCAL_APPDATA")

        assert result == r"C:\Users\Test\AppData\Local"
        mock_shell32.SHGetKnownFolderPath.assert_called_once()
        flags_arg = mock_shell32.SHGetKnownFolderPath.call_args[0][1]
        assert flags_arg == _KF_FLAG_DONT_VERIFY
    finally:
        _cleanup_ctypes_mocks()


def test_get_win_folder_via_ctypes_unknown_csidl(mocker: MockerFixture) -> None:
    if sys.platform != "win32":
        _setup_ctypes_mocks(mocker, win_dll=MagicMock(side_effect=lambda _name: MagicMock()))

    try:
        importlib.reload(windows)
        from platformdirs.windows import get_win_folder_via_ctypes as fresh_fn  # noqa: PLC0415

        with pytest.raises(ValueError, match="Unknown CSIDL name"):
            fresh_fn("CSIDL_BOGUS")
    finally:
        if sys.platform != "win32":
            _cleanup_ctypes_mocks()


@pytest.mark.skipif(sys.platform == "win32", reason="cannot force NULL from real SHGetKnownFolderPath")
def test_get_win_folder_via_ctypes_null_result(mocker: MockerFixture) -> None:
    _setup_ctypes_mocks(mocker)

    mock_ole32 = MagicMock()
    mock_shell32 = MagicMock()
    mock_kernel32 = MagicMock()
    ctypes.WinDLL = MagicMock(  # type: ignore[attr-defined]
        side_effect=lambda name: {"ole32": mock_ole32, "shell32": mock_shell32, "kernel32": mock_kernel32}[name],
    )

    mocker.patch("ctypes.byref", side_effect=lambda x: x)

    mock_path_ptr = MagicMock()
    mock_path_ptr.value = None
    mocker.patch("ctypes.wintypes.LPWSTR", return_value=mock_path_ptr)

    try:
        importlib.reload(windows)
        from platformdirs.windows import get_win_folder_via_ctypes as fresh_fn  # noqa: PLC0415

        with pytest.raises(ValueError, match="SHGetKnownFolderPath returned NULL"):
            fresh_fn("CSIDL_LOCAL_APPDATA")
    finally:
        _cleanup_ctypes_mocks()


def test_known_folder_guids_has_all_csidl_names() -> None:
    expected = {
        "CSIDL_APPDATA",
        "CSIDL_COMMON_APPDATA",
        "CSIDL_LOCAL_APPDATA",
        "CSIDL_PERSONAL",
        "CSIDL_MYPICTURES",
        "CSIDL_MYVIDEO",
        "CSIDL_MYMUSIC",
        "CSIDL_DOWNLOADS",
        "CSIDL_DESKTOPDIRECTORY",
    }
    assert set(_KNOWN_FOLDER_GUIDS.keys()) == expected


def test_pick_get_win_folder_ctypes(mocker: MockerFixture) -> None:
    if sys.platform != "win32":
        _setup_ctypes_mocks(mocker, win_dll=MagicMock())

    try:
        importlib.reload(windows)
        assert windows._pick_get_win_folder() is windows.get_win_folder_via_ctypes  # noqa: SLF001
    finally:
        if sys.platform != "win32":
            _cleanup_ctypes_mocks()
