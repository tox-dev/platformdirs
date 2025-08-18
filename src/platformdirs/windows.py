"""Windows."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import TYPE_CHECKING

from .api import PlatformDirsABC

if TYPE_CHECKING:
    from collections.abc import Callable

try:  # noqa: SIM105
    import ctypes
except ImportError:
    pass
try:  # noqa: SIM105
    import winreg
except ImportError:
    pass


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
        const = "FOLDERID_RoamingAppData" if self.roaming else "FOLDERID_LocalAppData"
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
        path = os.path.normpath(get_win_folder("FOLDERID_ProgramData"))
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
        path = os.path.normpath(get_win_folder("FOLDERID_LocalAppData"))
        return self._append_parts(path, opinion_value="Cache")

    @property
    def site_cache_dir(self) -> str:
        """:return: cache directory shared by users, e.g. ``C:\\ProgramData\\$appauthor\\$appname\\Cache\\$version``"""
        path = os.path.normpath(get_win_folder("FOLDERID_ProgramData"))
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
        return os.path.normpath(get_win_folder("FOLDERID_Documents"))

    @property
    def user_downloads_dir(self) -> str:
        """:return: downloads directory tied to the user e.g. ``%USERPROFILE%\\Downloads``"""
        return os.path.normpath(get_win_folder("FOLDERID_Downloads"))

    @property
    def user_pictures_dir(self) -> str:
        """:return: pictures directory tied to the user e.g. ``%USERPROFILE%\\Pictures``"""
        return os.path.normpath(get_win_folder("FOLDERID_Pictures"))

    @property
    def user_videos_dir(self) -> str:
        """:return: videos directory tied to the user e.g. ``%USERPROFILE%\\Videos``"""
        return os.path.normpath(get_win_folder("FOLDERID_Videos"))

    @property
    def user_music_dir(self) -> str:
        """:return: music directory tied to the user e.g. ``%USERPROFILE%\\Music``"""
        return os.path.normpath(get_win_folder("FOLDERID_Music"))

    @property
    def user_desktop_dir(self) -> str:
        """:return: desktop directory tied to the user, e.g. ``%USERPROFILE%\\Desktop``"""
        return os.path.normpath(get_win_folder("FOLDERID_Desktop"))

    @property
    def user_runtime_dir(self) -> str:
        """
        :return: runtime directory tied to the user, e.g.
         ``%USERPROFILE%\\AppData\\Local\\Temp\\$appauthor\\$appname``
        """
        path = os.path.normpath(os.path.join(get_win_folder("FOLDERID_LocalAppData"), "Temp"))  # noqa: PTH118
        return self._append_parts(path)

    @property
    def site_runtime_dir(self) -> str:
        """:return: runtime directory shared by users, same as `user_runtime_dir`"""
        return self.user_runtime_dir


def get_win_folder_from_env_vars(folderid_name: str) -> str:
    """Get folder from environment variables."""
    result = get_win_folder_if_folderid_name_not_env_var(folderid_name)
    if result is not None:
        return result

    env_var_name = {
        "FOLDERID_RoamingAppData": "APPDATA",
        "FOLDERID_ProgramData": "ALLUSERSPROFILE",
        "FOLDERID_LocalAppData": "LOCALAPPDATA",
    }.get(folderid_name)
    if env_var_name is None:
        msg = f"Unknown FOLDERID name: {folderid_name}"
        raise ValueError(msg)
    result = os.environ.get(env_var_name)
    if result is None:
        msg = f"Unset environment variable: {env_var_name}"
        raise ValueError(msg)
    return result


def get_win_folder_if_folderid_name_not_env_var(folderid_name: str) -> str | None:
    """Get a folder for a FOLDERID name that does not exist as an environment variable."""
    if folderid_name == "FOLDERID_Documents":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Documents")  # noqa: PTH118

    if folderid_name == "FOLDERID_Downloads":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Downloads")  # noqa: PTH118

    if folderid_name == "FOLDERID_Pictures":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Pictures")  # noqa: PTH118

    if folderid_name == "FOLDERID_Videos":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Videos")  # noqa: PTH118

    if folderid_name == "FOLDERID_Music":
        return os.path.join(os.path.normpath(os.environ["USERPROFILE"]), "Music")  # noqa: PTH118
    return None


FOLDERID_Downloads_guid_string = "374DE290-123F-4565-9164-39C4925E467B"

if "winreg" in globals():

    def get_win_folder_from_registry(folderid_name: str) -> str:
        """
        Get folder from the registry.

        This is a fallback technique at best. I'm not sure if using the registry for these guarantees us the correct
        answer for all FOLDERID_* names.

        """
        shell_folder_name = {
            "FOLDERID_RoamingAppData": "AppData",
            "FOLDERID_ProgramData": "Common AppData",
            "FOLDERID_LocalAppData": "Local AppData",
            "FOLDERID_Documents": "Personal",
            "FOLDERID_Downloads": "{" + FOLDERID_Downloads_guid_string + "}",
            "FOLDERID_Pictures": "My Pictures",
            "FOLDERID_Videos": "My Video",
            "FOLDERID_Music": "My Music",
        }.get(folderid_name)
        if shell_folder_name is None:
            msg = f"Unknown FOLDERID name: {folderid_name}"
            raise ValueError(msg)
        if sys.platform != "win32":  # only needed for mypy type checker to know that this code runs only on Windows
            raise NotImplementedError

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        directory, _ = winreg.QueryValueEx(key, shell_folder_name)
        return str(directory)


if "ctypes" in globals() and hasattr(ctypes, "windll"):

    class GUID(ctypes.Structure):
        """
        `
        The GUID structure from Windows's guiddef.h header
        <https://learn.microsoft.com/en-us/windows/win32/api/guiddef/ns-guiddef-guid>`_.
        """

        Data4Type = ctypes.c_ubyte * 8

        _fields_ = (
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", Data4Type),
        )

        def __init__(self, guid_string: str) -> None:
            digit_groups = guid_string.split("-")
            expected_digit_groups = 5
            if len(digit_groups) != expected_digit_groups:
                msg = f"The guid_string, {guid_string!r}, does not contain {expected_digit_groups} groups of digits."
                raise ValueError(msg)
            for digit_group, expected_length in zip(digit_groups, (8, 4, 4, 4, 12)):
                if len(digit_group) != expected_length:
                    msg = (
                        f"The digit group, {digit_group!r}, in the guid_string, {guid_string!r}, was the wrong length. "
                        f"It should have been {expected_length} digits long."
                    )
                    raise ValueError(msg)
            data_4_as_bytes = bytes.fromhex(digit_groups[3]) + bytes.fromhex(digit_groups[4])

            super().__init__(
                int(digit_groups[0], base=16),
                int(digit_groups[1], base=16),
                int(digit_groups[2], base=16),
                self.Data4Type(*(eight_bit_int for eight_bit_int in data_4_as_bytes)),
            )

        def __repr__(self) -> str:
            guid_string = f"{self.Data1:08X}-{self.Data2:04X}-{self.Data3:04X}-"
            for i in range(len(self.Data4)):
                guid_string += f"{self.Data4[i]:02X}"
                if i == 1:
                    guid_string += "-"
            return f"{type(self).__qualname__}({guid_string!r})"

    def get_win_folder_via_ctypes(folderid_name: str) -> str:  # noqa: C901, PLR0912
        """Get folder with ctypes."""
        # https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid
        if folderid_name == "FOLDERID_RoamingAppData":
            folderid_const = GUID("3EB685DB-65F9-4CF6-A03A-E3EF65729F3D")
        elif folderid_name == "FOLDERID_ProgramData":
            folderid_const = GUID("62AB5D82-FDC1-4DC3-A9DD-070D1D495D97")
        elif folderid_name == "FOLDERID_LocalAppData":
            folderid_const = GUID("F1B32785-6FBA-4FCF-9D55-7B8E7F157091")
        elif folderid_name == "FOLDERID_Documents":
            folderid_const = GUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7")
        elif folderid_name == "FOLDERID_Pictures":
            folderid_const = GUID("33E28130-4E1E-4676-835A-98395C3BC3BB")
        elif folderid_name == "FOLDERID_Videos":
            folderid_const = GUID("18989B1D-99B5-455B-841C-AB7C74E4DDFC")
        elif folderid_name == "FOLDERID_Music":
            folderid_const = GUID("4BD8D571-6D19-48D3-BE97-422220080E43")
        elif folderid_name == "FOLDERID_Downloads":
            folderid_const = GUID(FOLDERID_Downloads_guid_string)
        elif folderid_name == "FOLDERID_Desktop":
            folderid_const = GUID("B4BFCC3A-DB2C-424C-B029-7FE99A87C641")
        else:
            msg = f"Unknown FOLDERID name: {folderid_name}"
            raise ValueError(msg)
        # https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag
        kf_flag_default = 0
        # https://learn.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values
        s_ok = 0

        pointer_to_pointer_to_wchars = ctypes.pointer(ctypes.c_wchar_p())
        windll = getattr(ctypes, "windll")  # noqa: B009 # using getattr to avoid false positive with mypy type checker
        error_code = windll.shell32.SHGetKnownFolderPath(
            ctypes.pointer(folderid_const), kf_flag_default, None, pointer_to_pointer_to_wchars
        )
        return_value = pointer_to_pointer_to_wchars.contents.value
        # The documentation for SHGetKnownFolderPath() says that this needs to be freed using CoTaskMemFree():
        # https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath#parameters
        windll.ole32.CoTaskMemFree(pointer_to_pointer_to_wchars.contents)
        # Make sure that we don't accidentally use the memory now that we've freed it.
        del pointer_to_pointer_to_wchars
        if error_code != s_ok:
            # I'm using :08X as the format here because that's the format that the official documentation for HRESULT
            # uses: https://learn.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values
            msg = f"SHGetKnownFolderPath() failed with this error code: 0x{error_code:08X}"
            raise RuntimeError(msg)
        if return_value is None:
            msg = "SHGetKnownFolderPath() succeeded, but it gave us a null pointer. This should never happen."
            raise RuntimeError(msg)

        # Downgrade to short path name if it has high-bit chars.
        if any(ord(c) > 255 for c in return_value):  # noqa: PLR2004
            buf = ctypes.create_unicode_buffer(len(return_value))
            if windll.kernel32.GetShortPathNameW(return_value, buf, len(buf)):
                return_value = buf.value

        return return_value


def _pick_get_win_folder() -> Callable[[str], str]:
    if "get_win_folder_via_ctypes" in globals():
        return get_win_folder_via_ctypes
    if "get_win_folder_from_registry" in globals():
        return get_win_folder_from_registry
    return get_win_folder_from_env_vars


get_win_folder = lru_cache(maxsize=None)(_pick_get_win_folder())

__all__ = [
    "Windows",
]
