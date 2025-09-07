"""Windows."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import TYPE_CHECKING

from .api import PlatformDirsABC

if TYPE_CHECKING:
    from collections.abc import Callable


class Windows(PlatformDirsABC):
    """
    `MSDN on where to store app data files <https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid>`_.

    Makes use of the `appname <platformdirs.api.PlatformDirsABC.appname>`, `appauthor
    <platformdirs.api.PlatformDirsABC.appauthor>`, `version <platformdirs.api.PlatformDirsABC.version>`, `roaming
    <platformdirs.api.PlatformDirsABC.roaming>`, `opinion <platformdirs.api.PlatformDirsABC.opinion>`, `ensure_exists
    <platformdirs.api.PlatformDirsABC.ensure_exists>`.

    """

    @property
    def user_data_dir(self) -> str:
        """
        :return: data directory tied to the user, e.g.
         ``%USERPROFILE%\\AppData\\Local\\$appauthor\\$appname`` (not roaming) or
         ``%USERPROFILE%\\AppData\\Roaming\\$appauthor\\$appname`` (roaming)
        """
        const = "CSIDL_APPDATA" if self.roaming else "CSIDL_LOCAL_APPDATA"
        path = os.path.normpath(get_win_folder(const))
        return self._append_parts(path)

    def _append_parts(self, path: str, *, opinion_value: str | None = None) -> str:
        params = []
        if self.appname:
            if self.appauthor is not False:
                author = self.appauthor or self.appname
                params.append(author)
            params.append(self.appname)
            if opinion_value is not None and self.opinion:
                params.append(opinion_value)
            if self.version:
                params.append(self.version)
        path = os.path.join(path, *params)  # noqa: PTH118
        self._optionally_create_directory(path)
        return path

    @property
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, e.g. ``C:\\ProgramData\\$appauthor\\$appname``"""
        path = os.path.normpath(get_win_folder("CSIDL_COMMON_APPDATA"))
        return self._append_parts(path)

    @property
    def user_config_dir(self) -> str:
        """:return: config directory tied to the user, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, same as `site_data_dir`"""
        return self.site_data_dir

    @property
    def user_cache_dir(self) -> str:
        """
        :return: cache directory tied to the user (if opinionated with ``Cache`` folder within ``$appname``) e.g.
         ``%USERPROFILE%\\AppData\\Local\\$appauthor\\$appname\\Cache\\$version``
        """
        path = os.path.normpath(get_win_folder("CSIDL_LOCAL_APPDATA"))
        return self._append_parts(path, opinion_value="Cache")

    @property
    def site_cache_dir(self) -> str:
        """:return: cache directory shared by users, e.g. ``C:\\ProgramData\\$appauthor\\$appname\\Cache\\$version``"""
        path = os.path.normpath(get_win_folder("CSIDL_COMMON_APPDATA"))
        return self._append_parts(path, opinion_value="Cache")

    @property
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user, same as `user_data_dir` if not opinionated else ``Logs`` in it"""
        path = self.user_data_dir
        if self.opinion:
            path = os.path.join(path, "Logs")  # noqa: PTH118
            self._optionally_create_directory(path)
        return path

    @property
    def user_documents_dir(self) -> str:
        """:return: documents directory tied to the user e.g. ``%USERPROFILE%\\Documents``"""
        return os.path.normpath(get_win_folder("CSIDL_PERSONAL"))

    @property
    def user_downloads_dir(self) -> str:
        """:return: downloads directory tied to the user e.g. ``%USERPROFILE%\\Downloads``"""
        return os.path.normpath(get_win_folder("CSIDL_DOWNLOADS"))

    @property
    def user_pictures_dir(self) -> str:
        """:return: pictures directory tied to the user e.g. ``%USERPROFILE%\\Pictures``"""
        return os.path.normpath(get_win_folder("CSIDL_MYPICTURES"))

    @property
    def user_videos_dir(self) -> str:
        """:return: videos directory tied to the user e.g. ``%USERPROFILE%\\Videos``"""
        return os.path.normpath(get_win_folder("CSIDL_MYVIDEO"))

    @property
    def user_music_dir(self) -> str:
        """:return: music directory tied to the user e.g. ``%USERPROFILE%\\Music``"""
        return os.path.normpath(get_win_folder("CSIDL_MYMUSIC"))

    @property
    def user_desktop_dir(self) -> str:
        """:return: desktop directory tied to the user, e.g. ``%USERPROFILE%\\Desktop``"""
        return os.path.normpath(get_win_folder("CSIDL_DESKTOPDIRECTORY"))

    @property
    def user_runtime_dir(self) -> str:
        """
        :return: runtime directory tied to the user, e.g.
         ``%USERPROFILE%\\AppData\\Local\\Temp\\$appauthor\\$appname``
        """
        path = os.path.normpath(os.path.join(get_win_folder("CSIDL_LOCAL_APPDATA"), "Temp"))  # noqa: PTH118
        return self._append_parts(path)

    @property
    def site_runtime_dir(self) -> str:
        """:return: runtime directory shared by users, same as `user_runtime_dir`"""
        return self.user_runtime_dir


def get_win_folder_from_env_vars(csidl_name: str) -> str:
    """Get folder from environment variables."""
    result = get_win_folder_if_csidl_name_not_env_var(csidl_name)
    if result is not None:
        return result

    env_var_name = {
        "CSIDL_APPDATA": "APPDATA",
        "CSIDL_COMMON_APPDATA": "ALLUSERSPROFILE",
        "CSIDL_LOCAL_APPDATA": "LOCALAPPDATA",
    }.get(csidl_name)
    if env_var_name is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)
    result = os.environ.get(env_var_name)
    if result is None:
        msg = f"Unset environment variable: {env_var_name}"
        raise ValueError(msg)
    return result


def get_win_folder_if_csidl_name_not_env_var(csidl_name: str) -> str | None:
    """Get a folder for a CSIDL name that does not exist as an environment variable."""
    if csidl_name == "CSIDL_PERSONAL":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Documents")  # noqa: PTH118

    if csidl_name == "CSIDL_DOWNLOADS":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Downloads")  # noqa: PTH118

    if csidl_name == "CSIDL_MYPICTURES":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Pictures")  # noqa: PTH118

    if csidl_name == "CSIDL_MYVIDEO":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Videos")  # noqa: PTH118

    if csidl_name == "CSIDL_MYMUSIC":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Music")  # noqa: PTH118
    return None


def get_win_folder_from_registry(csidl_name: str) -> str:
    """
    Get folder from the registry.

    This is a fallback technique at best. I'm not sure if using the registry for these guarantees us the correct answer
    for all CSIDL_* names.

    """
    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
        "CSIDL_PERSONAL": "Personal",
        "CSIDL_DOWNLOADS": "{374DE290-123F-4565-9164-39C4925E467B}",
        "CSIDL_MYPICTURES": "My Pictures",
        "CSIDL_MYVIDEO": "My Video",
        "CSIDL_MYMUSIC": "My Music",
    }.get(csidl_name)
    if shell_folder_name is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)
    if sys.platform != "win32":  # only needed for mypy type checker to know that this code runs only on Windows
        raise NotImplementedError
    import winreg  # noqa: PLC0415

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    directory, _ = winreg.QueryValueEx(key, shell_folder_name)
    return str(directory)


def get_win_folder_via_ctypes(csidl_name: str) -> str:  # noqa: PLR0914
    """Get folder with ctypes."""
    # There is no 'CSIDL_DOWNLOADS'.
    # Use 'CSIDL_PROFILE' (40) and append the default folder 'Downloads' instead.
    # https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid

    from ctypes import HRESULT, POINTER, Structure, WinDLL, byref, create_unicode_buffer, wintypes  # noqa: PLC0415

    class GUID(Structure):
        _fields_ = [  # noqa: RUF012
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8),
        ]

        @classmethod
        def from_uuid(cls, clsid: str) -> GUID:
            guid = GUID()
            CLSIDFromString(clsid, byref(guid))
            return guid

    LPCLSID = POINTER(GUID)  # noqa: N806

    ole32_dll = WinDLL("ole32")

    CLSIDFromString = ole32_dll.CLSIDFromString  # noqa: N806
    CLSIDFromString.restype = HRESULT
    CLSIDFromString.argtypes = [wintypes.LPCOLESTR, LPCLSID]

    CoTaskMemFree = ole32_dll.CoTaskMemFree  # noqa: N806
    CoTaskMemFree.restype = None
    CoTaskMemFree.argtypes = [wintypes.LPVOID]

    KNOWNFOLDERID = GUID  # noqa: N806
    REFKNOWNFOLDERID = POINTER(KNOWNFOLDERID)  # noqa: N806

    shell32_dll = WinDLL("shell32")
    SHGetKnownFolderPath = shell32_dll.SHGetKnownFolderPath  # noqa: N806
    SHGetKnownFolderPath.restype = HRESULT
    SHGetKnownFolderPath.argtypes = [REFKNOWNFOLDERID, wintypes.DWORD, wintypes.HANDLE, POINTER(wintypes.LPWSTR)]

    kernel32_dll = WinDLL("kernel32")
    GetShortPathNameW = kernel32_dll.GetShortPathNameW  # noqa: N806
    GetShortPathNameW.restype = wintypes.DWORD
    GetShortPathNameW.argtypes = [wintypes.LPWSTR, wintypes.LPWSTR, wintypes.DWORD]

    csidl_const = {
        "CSIDL_APPDATA": "{3EB685DB-65F9-4CF6-A03A-E3EF65729F3D}",
        "CSIDL_COMMON_APPDATA": "{62AB5D82-FDC1-4DC3-A9DD-070D1D495D97}",
        "CSIDL_LOCAL_APPDATA": "{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}",
        "CSIDL_PERSONAL": "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}",
        "CSIDL_MYPICTURES": "{33E28130-4E1E-4676-835A-98395C3BC3BB}",
        "CSIDL_MYVIDEO": "{18989B1D-99B5-455B-841C-AB7C74E4DDFC}",
        "CSIDL_MYMUSIC": "{4BD8D571-6D19-48D3-BE97-422220080E43}",
        "CSIDL_DOWNLOADS": "{374DE290-123F-4565-9164-39C4925E467B}",
        "CSIDL_DESKTOPDIRECTORY": "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}",
    }.get(csidl_name)
    if csidl_const is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)

    guid = GUID.from_uuid(csidl_const)
    path_buf = wintypes.LPWSTR()

    SHGetKnownFolderPath(byref(guid), 0, None, byref(path_buf))
    win_folder = path_buf.value

    CoTaskMemFree(path_buf)

    if win_folder is None:
        msg = "Unexpected, win_folder is None. This should never happen."
        raise ValueError(msg)

    # Downgrade to short path name if it has high-bit chars.
    if any(ord(c) > 255 for c in win_folder):  # noqa: PLR2004
        buf2 = create_unicode_buffer(1024)
        if GetShortPathNameW(win_folder, buf2, 1024):
            win_folder = buf2.value

    return win_folder


def _pick_get_win_folder() -> Callable[[str], str]:
    try:
        import ctypes  # noqa: PLC0415, F401
    except ImportError:
        pass
    else:
        try:
            from ctypes import WinDLL  # noqa: PLC0415, F401
        except ImportError:
            pass
        else:
            return get_win_folder_via_ctypes
    try:
        import winreg  # noqa: PLC0415, F401
    except ImportError:
        return get_win_folder_from_env_vars
    else:
        return get_win_folder_from_registry


get_win_folder = lru_cache(maxsize=None)(_pick_get_win_folder())

__all__ = [
    "Windows",
]
