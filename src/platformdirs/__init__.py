# Copyright (c) 2005-2010 ActiveState Software Inc.
# Copyright (c) 2013 Eddy Petrișor
"""Utilities for determining application-specific dirs.

See <https://github.com/platformdirs/platformdirs> for details and usage.
"""
# Dev Notes:
# - MSDN on where to store app data files:
#   http://support.microsoft.com/default.aspx?scid=kb;en-us;310294#XSLTH3194121123120121120120
# - macOS: http://developer.apple.com/documentation/MacOSX/Conceptual/BPFileSystem/index.html
# - XDG spec for Un*x: https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
import os
import sys
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from typing_extensions import Literal

from .version import __version__, __version_info__

# https://docs.python.org/dev/library/sys.html#sys.platform
if sys.platform == "win32":
    try:
        from ctypes import windll  # noqa: F401
    except ImportError:
        try:
            import winreg
        except ImportError:

            def _get_win_folder(csidl_name: str) -> str:
                """Get folder from environment variables."""
                if csidl_name == "CSIDL_APPDATA":
                    env_var_name = "APPDATA"
                elif csidl_name == "CSIDL_COMMON_APPDATA":
                    env_var_name = "ALLUSERSPROFILE"
                elif csidl_name == "CSIDL_LOCAL_APPDATA":
                    env_var_name = "LOCALAPPDATA"
                else:
                    raise ValueError(f"Unknown CSIDL name: {csidl_name}")

                if env_var_name in os.environ:
                    return os.environ[env_var_name]
                else:
                    raise ValueError(f"Unset environment variable: {env_var_name}")

        else:

            def _get_win_folder(csidl_name: str) -> str:
                """Get folder from the registry.

                This is a fallback technique at best. I'm not sure if using the
                registry for this guarantees us the correct answer for all CSIDL_*
                names.
                """
                if csidl_name == "CSIDL_APPDATA":
                    shell_folder_name = "AppData"
                elif csidl_name == "CSIDL_COMMON_APPDATA":
                    shell_folder_name = "Common AppData"
                elif csidl_name == "CSIDL_LOCAL_APPDATA":
                    shell_folder_name = "Local AppData"
                else:
                    raise ValueError(f"Unknown CSIDL name: {csidl_name}")

                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
                )
                directory, _ = winreg.QueryValueEx(key, shell_folder_name)
                return directory

    else:

        def _get_win_folder(csidl_name: str) -> str:
            """Get folder with ctypes."""
            import ctypes

            if csidl_name == "CSIDL_APPDATA":
                csidl_const = 26
            elif csidl_name == "CSIDL_COMMON_APPDATA":
                csidl_const = 35
            elif csidl_name == "CSIDL_LOCAL_APPDATA":
                csidl_const = 28
            else:
                raise ValueError(f"Unknown CSIDL name: {csidl_name}")

            buf = ctypes.create_unicode_buffer(1024)
            ctypes.windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

            # Downgrade to short path name if have highbit chars. See
            # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
            has_high_char = False
            for c in buf:
                if ord(c) > 255:
                    has_high_char = True
                    break
            if has_high_char:
                buf2 = ctypes.create_unicode_buffer(1024)
                if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
                    buf = buf2

            return buf.value

    def _user_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
    ) -> str:
        if appauthor is None:
            appauthor = appname

        const = "CSIDL_APPDATA" if roaming else "CSIDL_LOCAL_APPDATA"
        path = os.path.normpath(_get_win_folder(const))
        if appname:
            assert appname is not None
            assert appauthor is not None

            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)

            if version:
                path = os.path.join(path, version)

        return path

    def _site_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        multipath: bool = False,  # noqa: U100
    ) -> str:
        if appauthor is None:
            appauthor = appname

        path = os.path.normpath(_get_win_folder("CSIDL_COMMON_APPDATA"))
        if appname:
            assert appname is not None
            assert appauthor is not None

            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)

            if version:
                path = os.path.join(path, version)

        return path

    def _user_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
    ) -> str:
        return _user_data_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)

    def _site_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        multipath: bool = False,  # noqa: U100
    ) -> str:
        return _site_data_dir_impl(appname=appname, appauthor=appauthor, version=version)

    def _user_cache_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        opinion: bool = True,
    ) -> str:
        if appauthor is None:
            appauthor = appname

        path = os.path.normpath(_get_win_folder("CSIDL_LOCAL_APPDATA"))
        if appname:
            assert appname is not None
            assert appauthor is not None

            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)

            if opinion:
                path = os.path.join(path, "Cache")

            if version:
                path = os.path.join(path, version)

        return path

    def _user_state_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
    ) -> str:
        return _user_data_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)

    def _user_log_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        opinion: bool = True,
    ) -> str:
        path = _user_data_dir_impl(appname=appname, appauthor=appauthor, version=version)
        if opinion:
            path = os.path.join(path, "Logs")

        return path


elif sys.platform == "darwin":

    def _user_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        roaming: bool = False,  # noqa: U100
    ) -> str:
        path = os.path.expanduser("~/Library/Application Support/")
        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _site_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        multipath: bool = False,  # noqa: U100
    ) -> str:
        path = "/Library/Application Support"
        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _user_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        roaming: bool = False,  # noqa: U100
    ) -> str:
        path = os.path.expanduser("~/Library/Preferences/")
        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _site_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,  # noqa: U100
        multipath: bool = False,  # noqa: U100
    ) -> str:
        path = "/Library/Preferences"
        if appname:
            path = os.path.join(path, appname)

        return path

    def _user_cache_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        opinion: bool = True,  # noqa: U100
    ) -> str:
        path = os.path.expanduser("~/Library/Caches")
        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _user_state_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
    ) -> str:
        return _user_data_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)

    def _user_log_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        opinion: bool = True,  # noqa: U100
    ) -> str:
        path = os.path.expanduser("~/Library/Logs")
        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path


else:

    def _user_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        roaming: bool = False,  # noqa: U100
    ) -> str:
        if "XDG_DATA_HOME" in os.environ:
            path = os.environ["XDG_DATA_HOME"]
        else:
            path = os.path.expanduser("~/.local/share")

        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _site_data_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        multipath: bool = False,
    ) -> str:
        # XDG default for $XDG_DATA_DIRS
        # only first, if multipath is False
        if "XDG_DATA_DIRS" in os.environ:
            path = os.environ["XDG_DATA_DIRS"]
        else:
            path = f"/usr/local/share{os.pathsep}/usr/share"

        pathlist = [os.path.expanduser(x.rstrip(os.sep)) for x in path.split(os.pathsep)]
        if appname:
            if version:
                appname = os.path.join(appname, version)
            pathlist = [os.path.join(x, appname) for x in pathlist]

        if multipath:
            path = os.pathsep.join(pathlist)
        else:
            path = pathlist[0]

        return path

    def _user_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        roaming: bool = False,  # noqa: U100
    ) -> str:
        if "XDG_CONFIG_HOME" in os.environ:
            path = os.environ["XDG_CONFIG_HOME"]
        else:
            path = os.path.expanduser("~/.config")

        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _site_config_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        multipath: bool = False,
    ) -> str:
        # XDG default for $XDG_CONFIG_DIRS
        # only first, if multipath is False
        if "XDG_CONFIG_DIRS" in os.environ:
            path = os.environ["XDG_CONFIG_DIRS"]
        else:
            path = "/etc/xdg"

        pathlist = [os.path.expanduser(x.rstrip(os.sep)) for x in path.split(os.pathsep)]
        if appname:
            if version:
                appname = os.path.join(appname, version)
            pathlist = [os.path.join(x, appname) for x in pathlist]

        if multipath:
            path = os.pathsep.join(pathlist)
        else:
            path = pathlist[0]

        return path

    def _user_cache_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        opinion: bool = True,  # noqa: U100
    ) -> str:
        if "XDG_CACHE_HOME" in os.environ:
            path = os.environ["XDG_CACHE_HOME"]
        else:
            path = os.path.expanduser("~/.cache")

        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _user_state_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,  # noqa: U100
        version: Optional[str] = None,
        roaming: bool = False,  # noqa: U100
    ) -> str:
        if "XDG_STATE_HOME" in os.environ:
            path = os.environ["XDG_STATE_HOME"]
        else:
            path = os.path.expanduser("~/.local/state")

        if appname:
            path = os.path.join(path, appname)
            if version:
                path = os.path.join(path, version)

        return path

    def _user_log_dir_impl(
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        opinion: bool = True,
    ) -> str:
        path = _user_cache_dir_impl(appname=appname, appauthor=appauthor, version=version)
        if opinion:
            path = os.path.join(path, "log")

        return path


def user_data_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    r"""Return full path to the user-specific data dir for this application.

    :param appname: The name of application.
        If ``None``, just the system directory is returned.
    :param appauthor: (only used on Windows) The name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass ``False`` to disable it.
    :param version: An optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be ``<major>.<minor>``.

        Only applied when appname is present.
    :param roaming: Whether to use the roaming appdata directory on Windows. That means
        that for users on a Windows network setup for roaming profiles, this user data
        will be sync'd on login. See
        http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx for a discussion
        of issues.

    Typical user data directories are:

    | **macOS**:
    |   ``~/Library/Application Support/$appname``
    | **Unix / Linux**:
    |   ``~/.local/share/$appname`` (or ``$XDG_DATA_HOME/$appname``)
    | **Win XP (not roaming)**:
    |   ``%USERPROFILE%\Application Data\$appauthor\$appname``
    | **Win XP (roaming)**:
    |   ``%USERPROFILE%\Local Settings\Application Data\$appauthor\$appname``
    | **Win 7  (not roaming)**:
    |   ``%USERPROFILE%\AppData\Local\$appauthor\$appname``
    | **Win 7  (roaming)**:
    |   ``%USERPROFILE%\AppData\Roaming\$appauthor\$appname``

    For Unix, we follow the XDG basedir spec and support ``$XDG_DATA_HOME``.
    """
    return _user_data_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)


def site_data_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    multipath: bool = False,
) -> str:
    r"""Return full path to the user-shared data dir for this application.

    :param appname: The name of application.
        If ``None``, just the base directory is returned.
    :param appauthor: (only used on Windows) The name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass ``False`` to disable it.
    :param version: An optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param multipath: An optional parameter only applicable to \*nix
        which indicates that the entire list of data dirs should be
        returned. By default, the first item from ``XDG_DATA_DIRS`` is
        returned, or ``/usr/local/share/$appname`` if ``XDG_DATA_DIRS`` is not set

    Typical site data directories are:

    | **macOS**:
    |   ``/Library/Application Support/$appname``
    | **Unix / Linux**:
    |   ``/usr/local/share/$appname`` or ``/usr/share/$appname``
    | **Win XP**:
    |   ``%USERPROFILE%\Application Data\$appauthor\$appname``
    | **Win Vista**:
    |   Fails, ``C:\ProgramData`` is a hidden *system* directory
    | **Win 7**:
    |   ``C:\ProgramData\$appauthor\$appname``

    For Unix, this is using the ``$XDG_DATA_DIRS[0]`` default.

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    return _site_data_dir_impl(appname=appname, appauthor=appauthor, version=version, multipath=multipath)


def user_config_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    r"""Return full path to the user-specific config dir for this application.

    :param appname: The name of application.
        If None, just the system directory is returned.
    :param appauthor: (only used on Windows) The name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    :param version: An optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param roaming: Whether to use the Windows roaming appdata directory. That means
        that for users on a Windows network setup for roaming profiles, this user data
        will be sync'd on login.

        See http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx for a
        discussion of issues.

    Typical user config directories are:

    | **macOS**:
    |   ``~/Library/Preferences/$appname``
    | **Unix / Linux**:
    |   ``~/.config/$appname`` (or ``$XDG_CONFIG_HOME/$appname``)
    | **Win XP (not roaming)**:
    |   Same as :func:`~.user_data_dir`.

    For Unix, we follow the XDG basedir spec and use ``$XDG_CONFIG_HOME``.
    """
    return _user_config_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)


def site_config_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    multipath: bool = False,
) -> str:
    r"""Return full path to the user-shared data dir for this application.

    :param appname: is the name of application.
        If None, just the system directory is returned.
    :param appauthor: (only used on Windows) is the name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    :param version: is an optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param multipath: is an optional parameter only applicable to \*nix
        which indicates that the entire list of config dirs should be
        returned. By default, the first item from ``XDG_CONFIG_DIRS `` is
        returned, or '/etc/xdg/$appname', if ``XDG_CONFIG_DIRS`` is not set

    Typical site config directories are:

    | **macOS**:
    |   Same as :func:`~.site_data_dir`.
    | **Unix / Linux**:
    |   ``/etc/xdg/$appname`` (or ``$XDG_CONFIG_DIRS[0]/$appname``)
    | **Win Vista**:
    |   Fails, ``C:\ProgramData`` is a hidden *system* directory
    | **Win 7 and above**:
    |   Same as :func:`~.site_data_dir`.

    For Unix, the first directory in ``$XDG_CONFIG_DIRS`` is used, if
    ``multipath=False``.

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    return _site_config_dir_impl(appname=appname, appauthor=appauthor, version=version, multipath=multipath)


def user_cache_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    opinion: bool = True,
) -> str:
    r"""Return full path to the user-specific cache dir for this application.

    :param appname: The name of application.
        If None, just the system directory is returned.
    :param appauthor: (only used on Windows) The name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    :param version: An optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param opinion: (boolean) If ``False``, disable the appending of
        "Cache" to the base app data dir for Windows. See comments below.

    Typical user cache directories are:

    | **macOS**:
    |   ``~/Library/Caches/$appname``
    | **Unix / Linux**:
    |   ``~/.cache/$appname`` (or ``~/$XDG_CACHE_HOME/$appname``)
    | **Win XP**:
    |   ``%USERPROFILE%\Local Settings\Application Data\$appauthor\$appname\Cache``
    | **Win XP and above**:
    |   ``%USERPROFILE%\AppData\Local\$appauthor\$appname\Cache``

    On Windows the only suggestion in the MSDN docs is that local settings go in
    the ``CSIDL_LOCAL_APPDATA`` directory. This is identical to the non-roaming
    app data dir (the default returned by ``user_data_dir`` above). Apps typically
    put cache data somewhere *under* the given dir here. For example::

        ...\Mozilla\Firefox\Profiles\<ProfileName>\Cache
        ...\Acme\SuperApp\Cache\1.0

    OPINION: This function appends "Cache" to the ``CSIDL_LOCAL_APPDATA`` value.
    This can be disabled with the ``opinion=False`` option.
    """
    return _user_cache_dir_impl(appname=appname, appauthor=appauthor, version=version, opinion=opinion)


def user_state_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    r"""Return full path to the user-specific state dir for this application.

    :param appname: The name of application.
        If None, just the system directory is returned.
    :param appauthor: (only used on Windows) The name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    :param version: An optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param roaming: Whether to use the roaming appdata directory on Windows. That means
        that for users on a Windows network setup for roaming profiles, this user data
        will be sync'd on login. See
        http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx for a discussion
        of issues.

    Typical user state directories are:

    | **macOS**:
    |   Same as :func:`~.user_data_dir`.
    | **Unix / Linux**:
    |   ``~/.local/state/$appname`` (or ``$XDG_STATE_HOME/$appname``)
    | **Windows**:
    |   Same as :func:`~.user_data_dir`.

    For Unix, we follow the XDG basedir spec and use ``$XDG_STATE_HOME``.
    """
    return _user_state_dir_impl(appname=appname, appauthor=appauthor, version=version, roaming=roaming)


def user_log_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    opinion: bool = True,
) -> str:
    r"""Return full path to the user-specific log dir for this application.

    :param appname: is the name of application.
        If None, just the system directory is returned.
    :param appauthor: (only used on Windows) is the name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    :param version: is an optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    :param opinion: (boolean) can be False to disable the appending of
        "Logs" to the base app data dir for Windows, and "log" to the
        base cache dir for Unix. See discussion below.

    Typical user log directories are:

    | **macOS**:
    |   ``~/Library/Logs/$appname``
    | **Unix / Linux**:
    |   ``~/.cache/$appname/log`` (or ``$XDG_CACHE_HOME/$appname/log``)
    | **Win XP**:
    |  ``%USERPROFILE%\Local Settings\Application Data\$appauthor\$appname\Logs``
    | **Windows Vista or later**:
    |  ``%USERPROFILE%\AppData\Local\$appauthor\$appname\Logs``

    On Windows the only suggestion in the MSDN docs is that local settings
    go in the `CSIDL_LOCAL_APPDATA` directory. (Note: I'm interested in
    examples of what some windows apps use for a logs dir.)

    OPINION: This function appends ``Logs`` to the ``CSIDL_LOCAL_APPDATA``
    value for Windows and appends ``log`` to the user cache dir for Unix.
    This can be disabled with the `opinion=False` option.
    """
    return _user_log_dir_impl(appname=appname, appauthor=appauthor, version=version, opinion=opinion)


class PlatformDirs:
    """Convenience wrapper for getting application dirs."""

    def __init__(
        self,
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
        multipath: bool = False,
    ):
        self.appname = appname
        self.appauthor = appauthor
        self.version = version
        self.roaming = roaming
        self.multipath = multipath

    @property
    def user_data_dir(self) -> str:
        return user_data_dir(self.appname, self.appauthor, version=self.version, roaming=self.roaming)

    @property
    def site_data_dir(self) -> str:
        return site_data_dir(self.appname, self.appauthor, version=self.version, multipath=self.multipath)

    @property
    def user_config_dir(self) -> str:
        return user_config_dir(self.appname, self.appauthor, version=self.version, roaming=self.roaming)

    @property
    def site_config_dir(self) -> str:
        return site_config_dir(self.appname, self.appauthor, version=self.version, multipath=self.multipath)

    @property
    def user_cache_dir(self) -> str:
        return user_cache_dir(self.appname, self.appauthor, version=self.version)

    @property
    def user_state_dir(self) -> str:
        return user_state_dir(self.appname, self.appauthor, version=self.version)

    @property
    def user_log_dir(self) -> str:
        return user_log_dir(self.appname, self.appauthor, version=self.version)


# Backwards compatibility with appdirs
AppDirs = PlatformDirs
__all__ = [
    "__version__",
    "__version_info__",
    "PlatformDirs",
    "AppDirs",
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
]
