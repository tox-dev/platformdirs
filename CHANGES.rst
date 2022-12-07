platformdirs Changelog
======================

platformdirs 2.6.0 (2022-12-06)
-------------------------------
- **BREAKING** Correct the log directory on Linux/Unix from
  XDG_CACHE_HOME to XDG_STATE_HOME per the XDG spec

platformdirs 2.5.4 (2022-11-12)
-------------------------------
- Fix licesing metadata

platformdirs 2.5.3 (2022-11-06)
-------------------------------
- Support 3.11
- Bump dependencies

platformdirs 2.5.2 (2022-04-18)
-------------------------------
- Move packaging to hatcling from setuptools
- Treat android shells as unix

platformdirs 2.5.2 (2022-04-18)
-------------------------------
- Move packaging to hatcling from setuptools
- Treat android shells as unix

platformdirs 2.5.1 (2022-02-19)
-------------------------------
- Add native support for nuitka

platformdirs 2.5.0 (2022-02-09)
-------------------------------
- Add support for Termux subsystems

platformdirs 2.4.1 (2021-12-26)
-------------------------------
- Drop python 3.6 support

platformdirs 2.4.0 (2021-09-25)
-------------------------------
- Add ``user_documents_dir``

platformdirs 2.3.0 (2021-08-31)
-------------------------------
- Add ``user_runtime_dir`` and its path-returning equivalent (#37)

platformdirs 2.2.0 (2021-07-29)
-------------------------------
- Unix: Fallback to default if XDG environment variable is empty

platformdirs 2.1.0 (2021-07-25)
-------------------------------
- Add ``readthedocs.org`` documentation via Sphinx
- Modernize project layout
- Drop Python 2.7 and 3.5 support
- Android support
- Add type annotations
- Reorganize project layout to platform specific classes, see
  :class:`PlatformDirsABC <platformdirs.api.PlatformDirsABC>` and it's implementations:
  :class:`Android <platformdirs.android.Android>`, :class:`MacOS <platformdirs.macos.MacOS>`,
  :class:`Unix <platformdirs.unix.Unix>` and :class:`Windows <platformdirs.windows.Windows>`
- Add ``*_path`` API, returning :class:`pathlib.Path <pathlib.Path>` objects instead of :class:`str`
  (``user_data_path``, ``user_config_path``, ``user_cache_path``, ``user_state_path``, ``user_log_path``,
  ``site_data_path``, ``site_config_path``) - by `@papr <https://github.com/papr/>`_

platformdirs 2.0.2 (2021-07-13)
-------------------------------
- Fix ``__version__`` and ``__version_info__``

platformdirs 2.0.1 (never released)
-----------------------------------
- Documentation fixes

platformdirs 2.0.0 (2021-07-12)
-------------------------------

- **BREAKING** Name change as part of the friendly fork
- **BREAKING** Remove support for end-of-life Pythons 2.6, 3.2, and 3.3
- **BREAKING** Correct the config directory on OSX/macOS
- Add Python 3.7, 3.8, and 3.9 support

appdirs 1.4.4 (2020-05-11)
--------------------------
- [PR #92] Don't import appdirs from setup.py which resolves issue #91

Project officially classified as Stable which is important
for inclusion in other distros such as ActivePython.

appdirs 1.4.3 (2017-03-07)
--------------------------
- [PR #76] Python 3.6 invalid escape sequence deprecation fixes
- Fix for Python 3.6 support

appdirs 1.4.2 (2017-02-24)
--------------------------
- [PR #84] Allow installing without setuptools
- [PR #86] Fix string delimiters in setup.py description
- Add Python 3.6 support

appdirs 1.4.1 (2017-02-23)
--------------------------
- [issue #38] Fix _winreg import on Windows Py3
- [issue #55] Make appname optional

appdirs 1.4.0 (2017-08-17)
--------------------------
- [PR #42] AppAuthor is now optional on Windows
- [issue 41] Support Jython on Windows, Mac, and Unix-like platforms. Windows
  support requires `JNA <https://github.com/twall/jna>`_.
- [PR #44] Fix incorrect behaviour of the site_config_dir method

appdirs 1.3.0 (2014-04-22)
--------------------------
- [Unix, issue 16] Conform to XDG standard, instead of breaking it for
  everybody
- [Unix] Removes gratuitous case mangling of the case, since \*nix-es are
  usually case sensitive, so mangling is not wise
- [Unix] Fixes the utterly wrong behaviour in ``site_data_dir``, return result
  based on XDG_DATA_DIRS and make room for respecting the standard which
  specifies XDG_DATA_DIRS is a multiple-value variable
- [Issue 6] Add ``*_config_dir`` which are distinct on nix-es, according to
  XDG specs; on Windows and Mac return the corresponding ``*_data_dir``

appdirs 1.2.0 (2011-01-26)
--------------------------

- [Unix] Put ``user_log_dir`` under the *cache* dir on Unix. Seems to be more
  typical.
- [issue 9] Make ``unicode`` work on py3k.

appdirs 1.1.0 (2010-09-02)
--------------------------

- [issue 4] Add ``AppDirs.user_log_dir``.
- [Unix, issue 2, issue 7] appdirs now conforms to `XDG base directory spec
  <https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_.
- [Mac, issue 5] Fix ``site_data_dir()`` on Mac.
- [Mac] Drop use of 'Carbon' module in favour of hardcoded paths; supports
  Python3 now.
- [Windows] Append "Cache" to ``user_cache_dir`` on Windows by default. Use
  ``opinion=False`` option to disable this.
- Add ``appdirs.AppDirs`` convenience class. Usage:

        >>> dirs = AppDirs("SuperApp", "Acme", version="1.0")
        >>> dirs.user_data_dir
        '/Users/trentm/Library/Application Support/SuperApp/1.0'

- [Windows] Cherry-pick Komodo's change to downgrade paths to the Windows short
  paths if there are high bit chars.
- [Linux] Change default ``user_cache_dir()`` on Linux to be singular, e.g.
  "~/.superapp/cache".
- [Windows] Add ``roaming`` option to ``user_data_dir()`` (for use on Windows only)
  and change the default ``user_data_dir`` behaviour to use a *non*-roaming
  profile dir (``CSIDL_LOCAL_APPDATA`` instead of ``CSIDL_APPDATA``). Why? Because
  a large roaming profile can cause login speed issues. The "only syncs on
  logout" behaviour can cause surprises in appdata info.


appdirs 1.0.1 (never released)
------------------------------

Started this changelog 27 July 2010. Before that this module originated in the
`Komodo <https://www.activestate.com/komodo-ide>`_ product as ``applib.py`` and then
as `applib/location.py
<https://github.com/ActiveState/applib/blob/master/applib/location.py>`_ (used by
`PyPM <https://code.activestate.com/pypm/>`_ in `ActivePython
<https://www.activestate.com/activepython>`_). This is basically a fork of
applib.py 1.0.1 and applib/location.py 1.0.1.
