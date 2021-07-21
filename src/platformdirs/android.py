import os
import re
import sys
from functools import lru_cache

from .api import PlatformDirsABC


class Android(PlatformDirsABC):
    """
    Follows the guidance `from here <https://android.stackexchange.com/a/216132>`_. Makes use of the
    `appname <platformdirs.api.PlatformDirsABC.appname>` and
    `version <platformdirs.api.PlatformDirsABC.version>`.
    """

    @property
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user, e.g. ``/data/user/<userid>/<packagename>/files/<AppName>``"""
        return self._path_with_app_name_version(_android_folder(), "files")

    @property
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    def user_config_dir(self) -> str:
        """
        :return: config directory tied to the user, e.g. ``/data/user/<userid>/<packagename>/shared_prefs/<AppName>``
        """
        return self._path_with_app_name_version(_android_folder(), "shared_prefs")

    @property
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, same as `user_config_dir`"""
        return self.user_config_dir

    @property
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user, e.g. e.g. ``/data/user/<userid>/<packagename>/cache/<AppName>``"""
        return self._path_with_app_name_version(_android_folder(), "cache")

    @property
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as `user_data_dir`"""
        return self.user_data_dir

    @property
    def user_log_dir(self) -> str:
        """
        :return: log directory tied to the user, same as `user_cache_dir` if not opinionated else ``log`` in it,
          e.g. ``/data/user/<userid>/<packagename>/cache/<AppName>/log``
        """
        path = self.user_cache_dir
        if self.opinion:
            path = os.path.join(path, "log")
        return path


@lru_cache(maxsize=1)
def _android_folder() -> str:
    """:return: base folder for the Android OS"""
    try:
        # First try to get path to android app via pyjnius
        from jnius import autoclass  # noqa: SC200

        Context = autoclass("android.content.Context")  # noqa: SC200
        result: str = Context.getFilesDir().getParentFile().getAbsolutePath()
    except Exception:
        # if fails find an android folder looking path on the sys.path
        pattern = re.compile(r"/data/(data|user/\d+)/(.+)/files")
        for path in sys.path:
            if pattern.match(path):
                result = path.split("/files")[0]
                break
        else:
            raise OSError("Cannot find path to android app folder")
    return result


__all__ = [
    "Android",
]
