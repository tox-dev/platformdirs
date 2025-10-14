"""macOS."""

from __future__ import annotations

import os
import os.path
import sys
from typing import TYPE_CHECKING

from .api import PlatformDirsABC

if TYPE_CHECKING:
    from pathlib import Path


class MacOS(PlatformDirsABC):
    """
    Platform directories for the macOS operating system.

    Follows the guidance from
    `Apple documentation <https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html>`_.
    Makes use of the `appname <platformdirs.api.PlatformDirsABC.appname>`,
    `version <platformdirs.api.PlatformDirsABC.version>`,
    `ensure_exists <platformdirs.api.PlatformDirsABC.ensure_exists>`.

    Note: Also understands XDG_* environment variables similar to Unix; if these are set, they override the
    corresponding user directories.
    """

    @property
    def user_data_dir(self) -> str:
        """
        :return: data directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version`` or
        ``$XDG_DATA_HOME/$appname/$version`` if set
        """
        path = os.environ.get("XDG_DATA_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/Library/Application Support")  # noqa: PTH111
        return self._append_app_name_and_version(path)

    @property
    def site_data_dir(self) -> str:
        """
        :return: data directory shared by users, e.g. ``/Library/Application Support/$appname/$version``.
          If we're using a Python binary managed by `Homebrew <https://brew.sh>`_, the directory
          will be under the Homebrew prefix, e.g. ``$homebrew_prefix/share/$appname/$version``.
          If `multipath <platformdirs.api.PlatformDirsABC.multipath>` is enabled, and we're in Homebrew,
          the response is a multi-path string separated by ":", e.g.
          ``$homebrew_prefix/share/$appname/$version:/Library/Application Support/$appname/$version``
        """
        xdg_dirs = os.environ.get("XDG_DATA_DIRS", "").strip()
        if xdg_dirs:
            dirs = [self._append_app_name_and_version(p) for p in xdg_dirs.split(os.pathsep) if p]
            return os.pathsep.join(dirs) if self.multipath else dirs[0]
        is_homebrew = "/opt/python" in sys.prefix
        homebrew_prefix = sys.prefix.split("/opt/python")[0] if is_homebrew else ""
        path_list = [self._append_app_name_and_version(f"{homebrew_prefix}/share")] if is_homebrew else []
        path_list.append(self._append_app_name_and_version("/Library/Application Support"))
        if self.multipath:
            return os.pathsep.join(path_list)
        return path_list[0]

    @property
    def site_data_path(self) -> Path:
        """:return: data path shared by users. Only return the first item, even if ``multipath`` is set to ``True``"""
        return self._first_item_as_path_if_multipath(self.site_data_dir)

    @property
    def user_config_dir(self) -> str:
        """
        :return: config directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version`` or
        ``$XDG_CONFIG_HOME/$appname/$version`` if set. If ``XDG_CONFIG_HOME`` is not set, returns ``user_data_dir``.
        """
        path = os.environ.get("XDG_CONFIG_HOME", "").strip()
        if not path:
            return self.user_data_dir
        return self._append_app_name_and_version(path)

    @property
    def site_config_dir(self) -> str:
        """
        :return: config directory shared by the users.
        Honors ``XDG_CONFIG_DIRS`` if set (supports multipath), otherwise same as `site_data_dir`.
        """
        xdg_dirs = os.environ.get("XDG_CONFIG_DIRS", "").strip()
        if xdg_dirs:
            dirs = [self._append_app_name_and_version(p) for p in xdg_dirs.split(os.pathsep) if p]
            return os.pathsep.join(dirs) if self.multipath else dirs[0]
        return self.site_data_dir

    @property
    def user_cache_dir(self) -> str:
        """
        :return: cache directory tied to the user, e.g. ``~/Library/Caches/$appname/$version`` or
        ``$XDG_CACHE_HOME/$appname/$version`` if set
        """
        path = os.environ.get("XDG_CACHE_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/Library/Caches")  # noqa: PTH111
        return self._append_app_name_and_version(path)

    @property
    def site_cache_dir(self) -> str:
        """
        :return: cache directory shared by users, e.g. ``/Library/Caches/$appname/$version``.
          If we're using a Python binary managed by `Homebrew <https://brew.sh>`_, the directory
          will be under the Homebrew prefix, e.g. ``$homebrew_prefix/var/cache/$appname/$version``.
          If `multipath <platformdirs.api.PlatformDirsABC.multipath>` is enabled, and we're in Homebrew,
          the response is a multi-path string separated by ":", e.g.
          ``$homebrew_prefix/var/cache/$appname/$version:/Library/Caches/$appname/$version``
        """
        is_homebrew = "/opt/python" in sys.prefix
        homebrew_prefix = sys.prefix.split("/opt/python")[0] if is_homebrew else ""
        path_list = [self._append_app_name_and_version(f"{homebrew_prefix}/var/cache")] if is_homebrew else []
        path_list.append(self._append_app_name_and_version("/Library/Caches"))
        if self.multipath:
            return os.pathsep.join(path_list)
        return path_list[0]

    @property
    def site_cache_path(self) -> Path:
        """:return: cache path shared by users. Only return the first item, even if ``multipath`` is set to ``True``"""
        return self._first_item_as_path_if_multipath(self.site_cache_dir)

    @property
    def user_state_dir(self) -> str:
        """
        :return: state directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version`` or
        ``$XDG_STATE_HOME/$appname/$version`` if set. If ``XDG_STATE_HOME`` is not set, returns ``user_data_dir``.
        """
        path = os.environ.get("XDG_STATE_HOME", "").strip()
        if not path:
            return self.user_data_dir
        return self._append_app_name_and_version(path)

    @property
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user, e.g. ``~/Library/Logs/$appname/$version``"""
        return self._append_app_name_and_version(os.path.expanduser("~/Library/Logs"))  # noqa: PTH111

    @property
    def user_documents_dir(self) -> str:
        """:return: documents directory tied to the user, e.g. ``~/Documents``, or ``$XDG_DOCUMENTS_DIR`` if set"""
        env = os.environ.get("XDG_DOCUMENTS_DIR", "").strip()
        return os.path.expanduser(env or "~/Documents")  # noqa: PTH111

    @property
    def user_downloads_dir(self) -> str:
        """:return: downloads directory tied to the user, e.g. ``~/Downloads``, or ``$XDG_DOWNLOAD_DIR`` if set"""
        env = os.environ.get("XDG_DOWNLOAD_DIR", "").strip()
        return os.path.expanduser(env or "~/Downloads")  # noqa: PTH111

    @property
    def user_pictures_dir(self) -> str:
        """:return: pictures directory tied to the user, e.g. ``~/Pictures``, or ``$XDG_PICTURES_DIR`` if set"""
        env = os.environ.get("XDG_PICTURES_DIR", "").strip()
        return os.path.expanduser(env or "~/Pictures")  # noqa: PTH111

    @property
    def user_videos_dir(self) -> str:
        """:return: videos directory tied to the user, e.g. ``~/Movies``, or ``$XDG_VIDEOS_DIR`` if set"""
        env = os.environ.get("XDG_VIDEOS_DIR", "").strip()
        return os.path.expanduser(env or "~/Movies")  # noqa: PTH111

    @property
    def user_music_dir(self) -> str:
        """:return: music directory tied to the user, e.g. ``~/Music``, or ``$XDG_MUSIC_DIR`` if set"""
        env = os.environ.get("XDG_MUSIC_DIR", "").strip()
        return os.path.expanduser(env or "~/Music")  # noqa: PTH111

    @property
    def user_desktop_dir(self) -> str:
        """:return: desktop directory tied to the user, e.g. ``~/Desktop``, or ``$XDG_DESKTOP_DIR`` if set"""
        env = os.environ.get("XDG_DESKTOP_DIR", "").strip()
        return os.path.expanduser(env or "~/Desktop")  # noqa: PTH111

    @property
    def user_runtime_dir(self) -> str:
        """
        :return: runtime directory tied to the user, e.g. ``~/Library/Caches/TemporaryItems/$appname/$version`` or
        ``$XDG_RUNTIME_DIR/$appname/$version`` if set
        """
        path = os.environ.get("XDG_RUNTIME_DIR", "").strip()
        if not path:
            path = os.path.expanduser("~/Library/Caches/TemporaryItems")  # noqa: PTH111
        return self._append_app_name_and_version(path)

    @property
    def site_runtime_dir(self) -> str:
        """
        :return: runtime directory shared by users. Honors ``$XDG_RUNTIME_DIR`` if set, otherwise same as
        `user_runtime_dir`.
        """
        path = os.environ.get("XDG_RUNTIME_DIR", "").strip()
        if path:
            return self._append_app_name_and_version(path)
        return self.user_runtime_dir


__all__ = [
    "MacOS",
]
