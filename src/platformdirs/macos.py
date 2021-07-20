import os
import sys

from .api import PlatformDirsABC


class MacOS(PlatformDirsABC):
    """
    Platform directories for the macOS operating system. Follows the guidance from `Apple documentation
    <https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html>`_.
    Makes use of the `appname <platformdirs.api.PlatformDirsABC.appname>` and
    `version <platformdirs.api.PlatformDirsABC.version>`.
    """

    @classmethod
    def is_active(cls) -> bool:
        """:return: a check to detect if macOS platform is currently active"""
        return sys.platform == "darwin"

    @property
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version``"""
        return self._path_with_app_name_version("~/Library/Application Support/", expand=True)

    def _path_with_app_name_version(self, of: str, *, expand: bool = False) -> str:
        params = []
        if self.appname:
            params.append(self.appname)
            if self.version:
                params.append(self.version)
        base = os.path.expanduser(of) if expand else of
        return os.path.join(base, *params)

    @property
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, e.g. ``/Library/Application Support/$appname/$version``"""
        return self._path_with_app_name_version("/Library/Application Support")

    @property
    def user_config_dir(self) -> str:
        """:return: config directory tied to the user, e.g. ``~/Library/Preferences/$appname/$version``"""
        return self._path_with_app_name_version("~/Library/Preferences/", expand=True)

    @property
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, e.g. ``/Library/Preferences/$appname``"""
        """
        :return: same as `site_data_dir`.
        """
        return self._path_with_app_name_version("/Library/Preferences")

    @property
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user, e.g. ``~/Library/Caches/$appname/$version``"""
        return self._path_with_app_name_version("~/Library/Caches", expand=True)

    @property
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user, e.g. ``~/Library/Logs/$appname/$version``"""
        return self._path_with_app_name_version("~/Library/Logs", expand=True)


__all__ = [
    "MacOS",
]
