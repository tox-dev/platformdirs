"""Unix."""

from __future__ import annotations

import os
import posixpath
import re
import stat
import sys
from contextlib import suppress
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Final

from ._runtime import RUNTIME_DIR_MODE as _RUNTIME_DIR_MODE
from ._runtime import geteuid
from ._runtime import runtime_dir_problem as _runtime_dir_problem
from ._runtime import warn_once as _warn_once
from ._xdg import XDGMixin, expand_user, xdg_dir
from .api import (
    PlatformDirsABC,
    RuntimeDirWarning,  # ruff:ignore[unused-import]  # retain module attribute
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class _UnixDefaults(PlatformDirsABC):  # ruff:ignore[too-many-public-methods]  # full directory API
    """Default directories for Unix/Linux without XDG environment variable overrides.

    The XDG env var handling is in :class:`~platformdirs._xdg.XDGMixin`.

    """

    @property
    def _use_site(self) -> bool:
        return self.use_site_for_root and geteuid() == 0

    @property
    def user_data_dir(self) -> str:
        """Data directory tied to the user.

        E.g. ``~/.local/share/$appname/$version`` or ``$XDG_DATA_HOME/$appname/$version``.

        """
        return self._append_app_name_and_version(expand_user("~/.local/share"), private=True)

    @property
    def _site_data_dirs(self) -> list[str]:
        return [self._join_app_name_and_version("/usr/local/share"), self._join_app_name_and_version("/usr/share")]

    @property
    def _site_config_dirs(self) -> list[str]:
        return [self._join_app_name_and_version("/etc/xdg")]

    @property
    def user_cache_dir(self) -> str:
        """Cache directory tied to the user.

        E.g. ``~/.cache/$appname/$version`` or ``$XDG_CACHE_HOME/$appname/$version``.

        """
        return self._append_app_name_and_version(expand_user("~/.cache"), private=True)

    @property
    def site_cache_dir(self) -> str:
        """Cache directory shared by users, e.g. ``/var/cache/$appname/$version``."""
        return self._append_app_name_and_version("/var/cache", private=False)

    @property
    def site_state_dir(self) -> str:
        """State directory shared by users, e.g. ``/var/lib/$appname/$version``."""
        return self._append_app_name_and_version("/var/lib", private=False)

    @property
    def user_log_dir(self) -> str:
        """Log directory tied to the user, same as `user_state_dir` if not opinionated else ``log`` in it."""
        path = self.user_state_dir
        if self.opinion:
            path = os.path.join(path, "log")  # ruff:ignore[os-path-join]  # preserve path separators
            self._optionally_create_directory(path, private=True)
        return path

    @property
    def user_state_dir(self) -> str:
        """State directory tied to the user.

        E.g. ``~/.local/state/$appname/$version`` or ``$XDG_STATE_HOME/$appname/$version``.

        """
        return self._append_app_name_and_version(expand_user("~/.local/state"), private=True)

    @property
    def site_log_dir(self) -> str:
        """Log directory shared by users, e.g. ``/var/log/$appname/$version``.

        Unlike `user_log_dir`, ``opinion`` has no effect since ``/var/log`` is inherently a log directory.

        """
        return self._append_app_name_and_version("/var/log", private=False)

    @property
    def user_documents_dir(self) -> str:
        """Documents directory tied to the user, e.g. ``~/Documents``."""
        return self._user_media_dir("XDG_DOCUMENTS_DIR", "~/Documents")

    def _user_media_dir(self, key: str, default: str) -> str:
        if path := _get_user_dirs_folder(key):
            self._optionally_create_media_directory(path)
            return path
        return expand_user(default)

    @property
    def user_downloads_dir(self) -> str:
        """Downloads directory tied to the user, e.g. ``~/Downloads``."""
        return self._user_media_dir("XDG_DOWNLOAD_DIR", "~/Downloads")

    @property
    def user_pictures_dir(self) -> str:
        """Pictures directory tied to the user, e.g. ``~/Pictures``."""
        return self._user_media_dir("XDG_PICTURES_DIR", "~/Pictures")

    @property
    def user_videos_dir(self) -> str:
        """Videos directory tied to the user, e.g. ``~/Videos``."""
        return self._user_media_dir("XDG_VIDEOS_DIR", "~/Videos")

    @property
    def user_music_dir(self) -> str:
        """Music directory tied to the user, e.g. ``~/Music``."""
        return self._user_media_dir("XDG_MUSIC_DIR", "~/Music")

    @property
    def user_desktop_dir(self) -> str:
        """Desktop directory tied to the user, e.g. ``~/Desktop``."""
        return self._user_media_dir("XDG_DESKTOP_DIR", "~/Desktop")

    @property
    def user_projects_dir(self) -> str:
        """Projects directory tied to the user, e.g. ``~/Projects``."""
        return self._user_media_dir("XDG_PROJECTS_DIR", "~/Projects")

    @property
    def user_publicshare_dir(self) -> str:
        """Public share directory tied to the user, e.g. ``~/Public``."""
        return self._user_media_dir("XDG_PUBLICSHARE_DIR", "~/Public")

    @property
    def user_templates_dir(self) -> str:
        """Templates directory tied to the user, e.g. ``~/Templates``."""
        return self._user_media_dir("XDG_TEMPLATES_DIR", "~/Templates")

    @property
    def user_fonts_dir(self) -> str:
        """Fonts directory tied to the user, e.g. ``~/.local/share/fonts``."""
        return f"{expand_user('~/.local/share')}/fonts"

    @property
    def user_preference_dir(self) -> str:
        """Preference directory tied to the user, same as ``user_config_dir``."""
        return self.user_config_dir

    @property
    def user_config_dir(self) -> str:
        """Config directory tied to the user.

        E.g. ``~/.config/$appname/$version`` or ``$XDG_CONFIG_HOME/$appname/$version``.

        """
        return self._append_app_name_and_version(expand_user("~/.config"), private=True)

    @property
    def user_bin_dir(self) -> str:
        """Bin directory tied to the user, e.g. ``~/.local/bin``."""
        return expand_user("~/.local/bin")

    @property
    def site_bin_dir(self) -> str:
        """Bin directory shared by users, e.g. ``/usr/local/bin``."""
        return "/usr/local/bin"

    @property
    def user_applications_dir(self) -> str:
        """Applications directory tied to the user, e.g. ``~/.local/share/applications``."""
        return f"{expand_user('~/.local/share')}{os.sep}applications"

    @property
    def _site_applications_dirs(self) -> list[str]:
        # preserve path separators
        return [os.path.join(p, "applications") for p in ["/usr/local/share", "/usr/share"]]  # ruff:ignore[os-path-join]

    @property
    def site_runtime_dir(self) -> str:
        """Runtime directory shared by users, e.g. ``/run/$appname/$version`` or ``$XDG_RUNTIME_DIR/$appname/$version``.

        Note that this behaves almost exactly like `user_runtime_dir` if ``$XDG_RUNTIME_DIR`` is set, but will fall back
        to paths associated to the root user instead of a regular logged-in user if it's not set.

        If you wish to ensure that a logged-in root user path is returned e.g. ``/run/user/0``, use `user_runtime_dir`
        instead.

        For FreeBSD/OpenBSD/NetBSD, it would return ``/var/run/$appname/$version`` if ``$XDG_RUNTIME_DIR`` is not set.

        """
        if sys.platform.startswith(("freebsd", "openbsd", "netbsd")):
            path = "/var/run"
        else:
            path = "/run"
        return self._append_app_name_and_version(path, private=False)

    def _default_runtime_dir(self) -> str:
        if sys.platform.startswith("openbsd"):
            path = f"/tmp/run/user/{geteuid()}"  # ruff:ignore[hardcoded-temp-file]  # fixed OpenBSD runtime directory
        elif sys.platform.startswith(("freebsd", "netbsd")):
            path = f"/var/run/user/{geteuid()}"
        else:
            path = f"/run/user/{geteuid()}"
        return self._temp_runtime_dir() if _runtime_dir_problem(path, missing_ok=False) else path

    def _temp_runtime_dir(self) -> str:
        # Another user can pre-create this predictable name, and XDG requires an owned runtime dir with mode 0700.
        path = _temp_runtime_fallback()
        with suppress(FileExistsError):
            self._optionally_create_directory(path, private=True)
        if problem := _runtime_dir_problem(path, missing_ok=not self.ensure_exists, check_mode=False):
            msg = f"runtime directory {problem}; set XDG_RUNTIME_DIR instead"
            raise PermissionError(msg)
        # Earlier releases created this directory with the default 0755.
        if self.ensure_exists:
            Path(path).chmod(_RUNTIME_DIR_MODE)
        return path


def _get_user_dirs_folder(key: str) -> str | None:
    # Return directory from user-dirs.dirs config file.
    #
    # ``xdg-user-dirs-update`` writes shell assignments, so match each line like ``xdg-user-dir`` does and keep the last
    # valid assignment to ``key``.
    #
    # See https://freedesktop.org/wiki/Software/xdg-user-dirs/.
    user_dirs_config_path = Path(xdg_dir("XDG_CONFIG_HOME") or expand_user("~/.config")) / "user-dirs.dirs"
    folder = None
    try:
        # the file holds raw path bytes, and surrogateescape round-trips undecodable ones like os.fsdecode
        with user_dirs_config_path.open(encoding=sys.getfilesystemencoding(), errors="surrogateescape") as stream:
            for line in stream:
                if (entry := _USER_DIRS_LINE.match(line)) and entry["key"] == key:
                    folder = _resolve_user_dirs_value(entry) or folder
    except OSError:  # a missing or unreadable file leaves the defaults in place
        return None
    return folder


def _resolve_user_dirs_value(entry: re.Match[str]) -> str | None:
    value = entry["bare"] if entry["quoted"] is None else entry["quoted"]
    if value == "$HOME" or value.startswith("$HOME/"):
        # A home of / would give "//Desktop", which pathlib keeps as a distinct root.
        prefix, value = expand_user("~").rstrip("/"), value.removeprefix("$HOME")
    elif value.startswith("/"):
        prefix = ""
    else:
        return None
    if entry["quoted"] is not None:
        # xdg-user-dirs-update backslash-escapes $, `, " and \ inside the quotes.
        value = _VALUE_PATTERN.sub(r"\1", value)
    return f"{prefix}{value}" or "/"


def _temp_runtime_fallback() -> str:
    # A temporary directory of / would give "//runtime-<uid>", which pathlib keeps as a distinct root.
    return posixpath.join(gettempdir(), f"runtime-{geteuid()}")


class Unix(XDGMixin, _UnixDefaults):
    """On Unix/Linux, we follow the `XDG Basedir Spec <https://specifications.freedesktop.org/basedir/latest/>`_.

    The spec allows overriding directories with environment variables. The examples shown are the default values,
    alongside the name of the environment variable that overrides them. Makes use of the `appname
    <platformdirs.api.PlatformDirsABC.appname>`, `version <platformdirs.api.PlatformDirsABC.version>`, `multipath
    <platformdirs.api.PlatformDirsABC.multipath>`, `opinion <platformdirs.api.PlatformDirsABC.opinion>`, `ensure_exists
    <platformdirs.api.PlatformDirsABC.ensure_exists>`.

    """

    @property
    def user_data_dir(self) -> str:
        """Data directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_data_dir if self._use_site else super().user_data_dir

    @property
    def user_config_dir(self) -> str:
        """Config directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_config_dir if self._use_site else super().user_config_dir

    @property
    def user_cache_dir(self) -> str:
        """Cache directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_cache_dir if self._use_site else super().user_cache_dir

    @property
    def user_state_dir(self) -> str:
        """State directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_state_dir if self._use_site else super().user_state_dir

    @property
    def user_log_dir(self) -> str:
        """Log directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_log_dir if self._use_site else super().user_log_dir

    @property
    def user_applications_dir(self) -> str:
        """Applications directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_applications_dir if self._use_site else super().user_applications_dir

    @property
    def user_runtime_dir(self) -> str:
        """Runtime directory tied to the user, e.g. ``$XDG_RUNTIME_DIR/$appname/$version``.

        Accepts ``$XDG_RUNTIME_DIR`` only as a directory, not a symlink, that the user owns with mode ``0700``, as the
        XDG spec requires, and only below parents no other user can replace. Creates a missing one that way under
        ``ensure_exists``. When the variable is unset or fails that check, emits one
        :class:`~platformdirs.RuntimeDirWarning` per cause and falls back to the platform default
        (``/tmp/run/user/<uid>`` on OpenBSD, ``/var/run/user/<uid>`` on FreeBSD/NetBSD, ``/run/user/<uid>`` elsewhere)
        if it passes the same check, else to ``runtime-<uid>`` in the temporary directory. Root with
        ``use_site_for_root`` gets the site equivalent.

        :raises PermissionError: if the temporary fallback is a symlink, not a directory, owned by another user, or
            missing right after its creation.

        """
        if self._use_site:
            # XDGMixin.site_runtime_dir reads $XDG_RUNTIME_DIR, which belongs to the user who started the root process.
            return super(XDGMixin, self).site_runtime_dir
        if not (path := xdg_dir("XDG_RUNTIME_DIR")):
            reason = "XDG_RUNTIME_DIR is not set"
        else:
            # Creating the missing levels follows whatever symlink sits at a parent, so check the parents first.
            if not (skipped := bool(_runtime_dir_parent_problem(path))):
                with suppress(OSError):
                    self._optionally_create_directory(path, private=True)
            # A leaf left missing because the parent check skipped creation is reported as that parent problem.
            if not (
                problem := _runtime_dir_problem(path, missing_ok=skipped or not self.ensure_exists)
                or _runtime_dir_parent_problem(path)
            ):
                return self._append_app_name_and_version(path, private=True)
            reason = f"XDG_RUNTIME_DIR {problem}"
        _warn_once(f"{reason}, falling back to {(fallback := self._default_runtime_dir())}")
        return self._append_app_name_and_version(fallback, private=True)

    @property
    def user_bin_dir(self) -> str:
        """Bin directory tied to the user, or site equivalent when root with ``use_site_for_root``."""
        return self.site_bin_dir if self._use_site else super().user_bin_dir

    @property
    def user_fonts_dir(self) -> str:
        """Fonts directory tied to the user, ignoring ``$XDG_DATA_HOME`` when root with ``use_site_for_root``."""
        return super(XDGMixin, self).user_fonts_dir if self._use_site else super().user_fonts_dir

    @property
    def user_data_path(self) -> Path:
        """Data path tied to the user, or the first site entry when root with ``use_site_for_root``."""
        return self.site_data_path if self._use_site else super().user_data_path

    @property
    def user_config_path(self) -> Path:
        """Config path tied to the user, or the first site entry when root with ``use_site_for_root``."""
        return self.site_config_path if self._use_site else super().user_config_path

    @property
    def user_preference_path(self) -> Path:
        """Preference path tied to the user, or the first site config entry when root with ``use_site_for_root``."""
        return self.site_config_path if self._use_site else super().user_preference_path

    @property
    def user_applications_path(self) -> Path:
        """Applications path tied to the user, or the first site entry when root with ``use_site_for_root``."""
        return self.site_applications_path if self._use_site else super().user_applications_path

    def place_runtime_file(self, name: str | os.PathLike[str]) -> Path:
        """Like :meth:`~platformdirs.api.PlatformDirsABC.place_runtime_file`.

        Creates the runtime directory before checking it, so another user cannot create it in between.

        :param name: see :meth:`~platformdirs.api.PlatformDirsABC.place_runtime_file`.

        :returns: the path of ``name`` under the user runtime directory.

        :raises PermissionError: if the temporary fallback is a symlink, not a directory, owned by another user, or
            missing right after its creation.

        """

        def created(lookup: PlatformDirsABC) -> Path:
            lookup.ensure_exists = True
            return lookup.user_runtime_path

        return self._place_file(created, name)

    def _find_runtime_files(self, name: str | os.PathLike[str]) -> Iterator[Path]:
        return filter(_in_own_runtime_dir, super()._find_runtime_files(name))

    def _xdg_media_dir(self, env_var: str) -> str | None:
        # The XDG_*_DIR variables and user-dirs.dirs belong to the user who started the root process.
        return None if self._use_site else super()._xdg_media_dir(env_var)

    def _user_media_dir(self, key: str, default: str) -> str:
        return expand_user(default) if self._use_site else super()._user_media_dir(key, default)


def _runtime_dir_parent_problem(path: str) -> str | None:
    if sys.platform == "win32":  # every directory reports as writable by everyone there
        return None
    in_shared_dir = False
    for parent in reversed(Path(path).parents):
        try:
            if in_shared_dir and (owner := os.lstat(parent).st_uid) not in {0, geteuid()}:
                return f"{path} is below {parent}, owned by uid {owner}"
            mode = parent.stat().st_mode  # a symlink that got past the owner check is judged by its target
        except OSError:
            return None  # the missing rest gets created, or _runtime_dir_problem reports the path itself
        if (in_shared_dir := bool(mode & stat.S_IWOTH)) and not mode & stat.S_ISVTX:
            return f"{path} is below {parent}, writable by every user"
    return None


def _in_own_runtime_dir(path: Path) -> bool:
    # The lookup let a missing runtime directory pass, so another user may have created it since. The fallback goes
    # first because a rejected XDG_RUNTIME_DIR, such as /tmp, contains it.
    for base in (_temp_runtime_fallback(), xdg_dir("XDG_RUNTIME_DIR")):
        if base and path.is_relative_to(base):
            return not _runtime_dir_problem(base, missing_ok=False, check_mode=False)
    return True


_USER_DIRS_LINE: Final[re.Pattern[str]] = re.compile(
    r"""
    [ \t]*(?P<key>\w+)[ \t]*=[ \t]*  # KEY=, blanks allowed around the key and after the =
    (?:
        "(?P<quoted>(?:[^"\\]|\\.)*)"  # a double-quoted value with backslash escapes, text after it ignored
        |(?P<bare>[^"\s](?:[^ \t\n]|[ \t]+[^ \t\n\#])*)  # or an unquoted value; blanks join it only before a word
                                                         # that starts no comment, and each run is matched once so
                                                         # long runs stay linear
    )
    """,
    re.VERBOSE,
)


_VALUE_PATTERN: Final[re.Pattern[str]] = re.compile(r'\\([$`"\\])')


__all__ = [
    "Unix",
]
