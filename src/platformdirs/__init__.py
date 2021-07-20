"""
Utilities for determining application-specific dirs. See <https://github.com/platformdirs/platformdirs> for details and
usage.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Optional, Type, Union

if TYPE_CHECKING:
    from typing_extensions import Literal  # pragma: no cover

from .api import PlatformDirsABC
from .version import __version__, __version_info__


def _set_platform_dir_class() -> Type[PlatformDirsABC]:
    for module, of_class in (  # only import as much as needed
        ("platformdirs.android", "Android"),
        ("platformdirs.windows", "Windows"),
        ("platformdirs.macos", "MacOS"),
        ("platformdirs.unix", "Unix"),
    ):
        impl = getattr(import_module(module), of_class)
        if impl.is_active():
            return impl
    raise RuntimeError("Unsupported platform, please report it at https://github.com/platformdirs/platformdirs")


PlatformDirs = _set_platform_dir_class()  #: Currently active platform
AppDirs = PlatformDirs  #: Backwards compatibility with appdirs


def user_data_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.version>`.
    :returns: data directory tied to the user
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, roaming=roaming).user_data_dir


def site_data_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    multipath: bool = False,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `roaming <platformdirs.api.PlatformDirsABC.multipath>`.
    :returns: data directory shared by users
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, multipath=multipath).site_data_dir


def user_config_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.version>`.
    :returns: config directory tied to the user
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, roaming=roaming).user_config_dir


def site_config_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    multipath: bool = False,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param multipath: See `roaming <platformdirs.api.PlatformDirsABC.multipath>`.
    :returns: config directory shared by the users
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, multipath=multipath).site_config_dir


def user_cache_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    opinion: bool = True,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `roaming <platformdirs.api.PlatformDirsABC.opinion>`.
    :returns: cache directory tied to the user
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, opinion=opinion).user_cache_dir


def user_state_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    roaming: bool = False,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param roaming: See `roaming <platformdirs.api.PlatformDirsABC.version>`.
    :returns: state directory tied to the user
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, roaming=roaming).user_state_dir


def user_log_dir(
    appname: Optional[str] = None,
    appauthor: Union[str, None, "Literal[False]"] = None,
    version: Optional[str] = None,
    opinion: bool = True,
) -> str:
    """
    :param appname: See `appname <platformdirs.api.PlatformDirsABC.appname>`.
    :param appauthor: See `appauthor <platformdirs.api.PlatformDirsABC.appauthor>`.
    :param version: See `version <platformdirs.api.PlatformDirsABC.version>`.
    :param opinion: See `roaming <platformdirs.api.PlatformDirsABC.opinion>`.
    :returns: log directory tied to the user
    """
    return PlatformDirs(appname=appname, appauthor=appauthor, version=version, opinion=opinion).user_log_dir


__all__ = [
    "__version__",
    "__version_info__",
    "PlatformDirs",
    "AppDirs",
    "PlatformDirsABC",
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
]
