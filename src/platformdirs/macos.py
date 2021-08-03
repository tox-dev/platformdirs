import os
from functools import wraps
from typing import Callable

from .api import PlatformDirsABC
from .unix import SUPPORTS_XDG, Unix


def _xdg_fallback(func: Callable[[], str]) -> Callable[[], str]:
    if func.__name__ not in SUPPORTS_XDG:
        return func

    @wraps(func)
    def wrapper(self: PlatformDirsABC) -> str:
        if SUPPORTS_XDG.get(func.__name__) in os.environ:
            return getattr(super(MacOS, self), func.__name__)
        path = func.__get__(self, MacOS)()
        if os.path.exists(path):
            return path
        if self.xdg_fallback:
            return getattr(super(MacOS, self), func.__name__)
        return path

    return wrapper


class MacOS(Unix, PlatformDirsABC):
    """
    Platform directories for the macOS operating system. Follows the guidance from `Apple documentation
    <https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html>`_.
    Makes use of the `appname <platformdirs.api.PlatformDirsABC.appname>` and
    `version <platformdirs.api.PlatformDirsABC.version>`.
    """

    @property
    @_xdg_fallback
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Application Support/"))

    @property
    @_xdg_fallback
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, e.g. ``/Library/Application Support/$appname/$version``"""
        return self._append_app_name_and_version("/Library/Application Support")

    @property
    @_xdg_fallback
    def user_config_dir(self) -> str:
        """:return: config directory tied to the user, e.g. ``~/Library/Preferences/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Preferences/"))

    @property
    @_xdg_fallback
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, e.g. ``/Library/Preferences/$appname``"""
        return self._append_app_name_and_version("/Library/Preferences")

    @property
    @_xdg_fallback
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user, e.g. ``~/Library/Caches/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Caches"))

    @property
    @_xdg_fallback
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    @_xdg_fallback
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user, e.g. ``~/Library/Logs/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Logs"))


__all__ = [
    "MacOS",
]
