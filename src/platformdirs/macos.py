import os

from .api import PlatformDirsABC
from .unix import Unix

XDG_SUPPORT = {
    "user_data_dir": "XDG_DATA_HOME",
    # "site_data_dir": "XDG_CONFIG_DIRS",  # Not supported
    "user_config_dir": "XDG_CONFIG_HOME",
    # "site_config_dir": "XDG_CONFIG_DIRS",  # Not supported
    "user_cache_dir": "XDG_CACHE_HOME",
    "user_state_dir": "XDG_STATE_HOME",
    # "user_log_dir": "XDG_CACHE_HOME",  # Not supported b/c Console
}


class MacOS(Unix, PlatformDirsABC):
    """
    Platform directories for the macOS operating system. Follows the guidance from `Apple documentation
    <https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html>`_.
    Makes use of the `appname <platformdirs.api.PlatformDirsABC.appname>` and
    `version <platformdirs.api.PlatformDirsABC.version>`.
    """

    @property
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version``"""
        old = self._append_app_name_and_version(os.path.expanduser("~/Library/Application Support/"))
        if "XDG_DATA_HOME" in os.environ or not os.path.exists(old) and self.xdg_fallback:
            return super().user_data_dir
        return old

    @property
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, e.g. ``/Library/Application Support/$appname/$version``"""
        return self._append_app_name_and_version("/Library/Application Support")

    @property
    def user_config_dir(self) -> str:
        """:return: config directory tied to the user, e.g. ``~/Library/Preferences/$appname/$version``"""
        old = self._append_app_name_and_version(os.path.expanduser("~/Library/Preferences/"))
        if "XDG_CONFIG_HOME" in os.environ or not os.path.exists(old) and self.xdg_fallback:
            return super().user_config_dir
        return old

    @property
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, e.g. ``/Library/Preferences/$appname``"""
        return self._append_app_name_and_version("/Library/Preferences")

    @property
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user, e.g. ``~/Library/Caches/$appname/$version``"""
        old = self._append_app_name_and_version(os.path.expanduser("~/Library/Caches"))
        if "XDG_CACHE_HOME" in os.environ or not os.path.exists(old) and self.xdg_fallback:
            return super().user_cache_dir
        return old

    @property
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as `user_data_dir`"""
        old = self.user_data_dir
        if "XDG_STATE_HOME" in os.environ or not os.path.exists(old) and self.xdg_fallback:
            return super().user_state_dir
        return old

    @property
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user, e.g. ``~/Library/Logs/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Logs"))


__all__ = [
    "MacOS",
]
