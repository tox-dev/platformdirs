import sys
from abc import ABC, abstractmethod
from typing import Optional, Union

if sys.version_info >= (3, 8):  # pragma: no branch
    from typing import Literal  # pragma: no cover


class PlatformDirsABC(ABC):
    """
    Abstract base class for platform directories.
    """

    def __init__(
        self,
        appname: Optional[str] = None,
        appauthor: Union[str, None, "Literal[False]"] = None,
        version: Optional[str] = None,
        roaming: bool = False,
        multipath: bool = False,
        opinion: bool = True,
    ):
        """
        Create a new platform directory.

        :param appname: See `appname`.
        :param appauthor: See `appauthor`.
        :param version: See `version`.
        :param roaming: See `roaming`.
        :param multipath: See `multipath`.
        :param opinion: See `opinion`.
        """
        self.appname = appname  #: The name of application.
        self.appauthor = appauthor
        """
        The name of the app author or distributing body for this application. Typically, it is the owning company name.
        Defaults to `appname`. You may pass ``False`` to disable it.
        """
        self.version = version
        """
        An optional version path element to append to the path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this would typically be ``<major>.<minor>``.
        """
        self.roaming = roaming
        """
        Whether to use the roaming appdata directory on Windows. That means that for users on a Windows network setup
        for roaming profiles, this user data will be synced on login (see
        `here <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>`_).
        """
        self.multipath = multipath
        """
        An optional parameter only applicable to Unix/Linux which indicates that the entire list of data dirs should be
        returned. By default, the first item would only be returned.
        """
        self.opinion = opinion  #: A flag to indicating to use opinionated values.

    @property
    @abstractmethod
    def user_data_dir(self) -> str:
        """:return: data directory tied to the user"""
        raise NotImplementedError

    @property
    @abstractmethod
    def site_data_dir(self) -> str:
        """:return: data directory shared by users"""
        raise NotImplementedError

    @property
    @abstractmethod
    def user_config_dir(self) -> str:
        """:return: config directory tied to the user"""
        raise NotImplementedError

    @property
    @abstractmethod
    def site_config_dir(self) -> str:
        """:return: config directory shared by the users"""
        raise NotImplementedError

    @property
    @abstractmethod
    def user_cache_dir(self) -> str:
        """:return: cache directory tied to the user"""
        raise NotImplementedError

    @property
    @abstractmethod
    def user_state_dir(self) -> str:
        """:return: state directory tied to the user"""
        raise NotImplementedError

    @property
    @abstractmethod
    def user_log_dir(self) -> str:
        """:return: log directory tied to the user"""
        raise NotImplementedError
