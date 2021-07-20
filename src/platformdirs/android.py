import os
import re
import sys
from functools import lru_cache

from .api import PlatformDirsABC


class Android(PlatformDirsABC):
    """
    Follows the guidance `from here <https://android.stackexchange.com/a/216132>`_. Makes use of the
    :meth:`appname <platformdirs.api.PlatformDirsABC.appname>` and
    :meth:`version <platformdirs.api.PlatformDirsABC.version>`.
    """

    @classmethod
    def is_active(cls) -> bool:
        """:return: a check to detect if Android platform is currently active"""
        return os.getenv("ANDROID_DATA") == "/data" and os.getenv("ANDROID_ROOT") == "/system"

    @property
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user, e.g. ``/data/user/<userid>/<packagename>/files/<AppName>``"""
        return self._path_with_app_name_version(of="files")

    def _path_with_app_name_version(self, of: str) -> str:
        params = [of]
        if self.appname:
            params.append(self.appname)
            if self.version:
                params.append(self.version)
        path = os.path.join(_android_folder(), *params)
        return path

    @property
    def site_data_dir(self) -> str:
        """:return: data directory shared by users, same as :meth:`user_data_dir`"""
        return self.user_data_dir

    @property
    def user_config_dir(self) -> str:
        """
        :return: config directory tied to the user, e.g. ``/data/user/<userid>/<packagename>/shared_prefs/<AppName>``
        """
        return self._path_with_app_name_version(of="shared_prefs")

    @property
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users, same as :func:`user_config_dir`"""
        return self.user_config_dir

    @property
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user, e.g. e.g. ``/data/user/<userid>/<packagename>/cache/<AppName>``"""
        return self._path_with_app_name_version(of="cache")

    @property
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user, same as :func:`user_data_dir`"""
        return self.user_data_dir

    @property
    def user_log_dir(self) -> str:
        """
        :return: log directory tied to the user, same as :func:`user_cache_dir` if not opinionated else ``log`` in it,
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