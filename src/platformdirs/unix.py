import os
from pathlib import Path
from configparser import ConfigParser
from typing import Optional

from .api import PlatformDirsABC


class Unix(PlatformDirsABC):
    """
    On Unix/Linux, we follow the
    `XDG Basedir Spec <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_. The spec allows
    overriding directories with environment variables. The examples show are the default values, alongside the name of
    the environment variable that overrides them. Makes use of the
    `appname <platformdirs.api.PlatformDirsABC.appname>`,
    `version <platformdirs.api.PlatformDirsABC.version>`,
    `multipath <platformdirs.api.PlatformDirsABC.multipath>`,
    `opinion <platformdirs.api.PlatformDirsABC.opinion>`.
    """

    @property
    def user_data_dir(self) -> str:
        """
        :return: data directory tied to the user, e.g. ``~/.local/share/$appname/$version`` or
         ``$XDG_DATA_HOME/$appname/$version``
        """
        path = os.environ.get("XDG_DATA_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/.local/share")
        return self._append_app_name_and_version(path)

    @property
    def site_data_dir(self) -> str:
        """
        :return: data directories shared by users (if `multipath <platformdirs.api.PlatformDirsABC.multipath>` is
         enabled and ``XDG_DATA_DIR`` is set and a multi path the response is also a multi path separated by the OS
         path separator), e.g. ``/usr/local/share/$appname/$version`` or ``/usr/share/$appname/$version``
        """
        # XDG default for $XDG_DATA_DIRS; only first, if multipath is False
        path = os.environ.get("XDG_DATA_DIRS", "")
        if not path.strip():
            path = f"/usr/local/share{os.pathsep}/usr/share"
        return self._with_multi_path(path)

    def _with_multi_path(self, path: str) -> str:
        path_list = path.split(os.pathsep)
        if not self.multipath:
            path_list = path_list[0:1]
        path_list = [self._append_app_name_and_version(os.path.expanduser(p)) for p in path_list]
        return os.pathsep.join(path_list)

    @property
    def user_config_dir(self) -> str:
        """
        :return: config directory tied to the user, e.g. ``~/.config/$appname/$version`` or
         ``$XDG_CONFIG_HOME/$appname/$version``
        """
        path = os.environ.get("XDG_CONFIG_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/.config")
        return self._append_app_name_and_version(path)

    @property
    def site_config_dir(self) -> str:
        """
        :return: config directories shared by users (if `multipath <platformdirs.api.PlatformDirsABC.multipath>`
         is enabled and ``XDG_DATA_DIR`` is set and a multi path the response is also a multi path separated by the OS
         path separator), e.g. ``/etc/xdg/$appname/$version``
        """
        # XDG default for $XDG_CONFIG_DIRS only first, if multipath is False
        path = os.environ.get("XDG_CONFIG_DIRS", "")
        if not path.strip():
            path = "/etc/xdg"
        return self._with_multi_path(path)

    @property
    def user_cache_dir(self) -> str:
        """
        :return: cache directory tied to the user, e.g. ``~/.cache/$appname/$version`` or
         ``~/$XDG_CACHE_HOME/$appname/$version``
        """
        path = os.environ.get("XDG_CACHE_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/.cache")
        return self._append_app_name_and_version(path)

    @property
    def user_state_dir(self) -> str:
        """
        :return: state directory tied to the user, e.g. ``~/.local/state/$appname/$version`` or
         ``$XDG_STATE_HOME/$appname/$version``
        """
        path = os.environ.get("XDG_STATE_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/.local/state")
        return self._append_app_name_and_version(path)

    @property
    def user_log_dir(self) -> str:
        """
        :return: log directory tied to the user, same as `user_data_dir` if not opinionated else ``log`` in it
        """
        path = self.user_cache_dir
        if self.opinion:
            path = os.path.join(path, "log")
        return path

    @property
    def user_documents_dir(self) -> str:
        """
        :return: documents directory tied to the user, e.g. ``~/Documents``
        """
        documents_dir = get_user_dirs_folder("XDG_DOCUMENTS_DIR")
        
        if documents_dir is None:
            documents_dir = os.environ.get("XDG_DOCUMENTS_DIR", "")
            if not documents_dir.strip():
                documents_dir = os.path.expanduser("~/Documents")
        
        return documents_dir

    @property
    def site_data_path(self) -> Path:
        """:return: data path shared by users. Only return first item, even if ``multipath`` is set to ``True``"""
        return self._first_item_as_path_if_multipath(self.site_data_dir)

    @property
    def site_config_path(self) -> Path:
        """:return: config path shared by the users. Only return first item, even if ``multipath`` is set to ``True``"""
        return self._first_item_as_path_if_multipath(self.site_config_dir)

    def _first_item_as_path_if_multipath(self, directory: str) -> Path:
        if self.multipath:
            # If multipath is True, the first path is returned.
            directory = directory.split(os.pathsep)[0]
        return Path(directory)

def get_user_dirs_folder(key: str) -> Optional[str]:
    """""Return """
    user_dirs_config_path = os.path.join(Unix().user_config_dir, "user-dirs.dirs")
    if not os.path.exists(user_dirs_config_path):
        return

    parser = ConfigParser()

    with open(user_dirs_config_path) as stream:
        # Add fake section header, so ConfigParser doesn't complain
        parser.read_string("[top]\n" + stream.read())

    if key not in parser["top"]:
        return
    
    path = parser["top"][key].strip('"')
    # Handle relative home paths
    path = path.replace("$HOME", os.path.expanduser("~"))
    return path

__all__ = [
    "Unix",
]
