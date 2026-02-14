Parameter reference
===================

This page documents all parameters accepted by ``platformdirs`` functions and the
:class:`~platformdirs.PlatformDirs` class.

``appname``
-----------

The name of your application. Used as a subdirectory in all app-specific paths.
When ``None``, the base platform directory is returned without any app-specific subdirectory.

.. code-block:: pycon

   >>> from platformdirs import user_data_dir
   >>> user_data_dir("SuperApp")
   '/Users/trentm/Library/Application Support/SuperApp'
   >>> user_data_dir()
   '/Users/trentm/Library/Application Support'

**Type**: ``str | None``

**Default**: ``None``

``appauthor``
-------------

The app author or distributing organization. On Windows, this adds an additional parent directory:

.. code-block:: pycon

   >>> user_data_dir("SuperApp", "Acme")  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp'

Set to ``False`` to suppress the author directory even on Windows:

.. code-block:: pycon

   >>> user_data_dir("SuperApp", False)  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\SuperApp'

On non-Windows platforms, ``appauthor`` is ignored.

**Type**: ``str | Literal[False] | None``

**Default**: ``None``

``version``
-----------

Appends a version subdirectory. Useful for running multiple app versions side by side:

.. code-block:: pycon

   >>> from platformdirs import PlatformDirs
   >>> dirs = PlatformDirs("SuperApp", "Acme", version="1.0")
   >>> dirs.user_data_dir
   '/Users/trentm/Library/Application Support/SuperApp/1.0'
   >>> dirs.user_cache_dir
   '/Users/trentm/Library/Caches/SuperApp/1.0'

Be wary of using this for configuration files; you will need to handle migrating configuration
files between versions manually. See :ref:`versioned-data-migration` for guidance.

**Type**: ``str | None``

**Default**: ``None``

``roaming``
-----------

Windows-only. When ``True``, uses the roaming AppData directory (``CSIDL_APPDATA``) instead of
the local one (``CSIDL_LOCAL_APPDATA``). Roaming profiles sync across machines in a Windows domain.

.. code-block:: pycon

   >>> user_data_dir("SuperApp", "Acme", roaming=True)  # on Windows
   'C:\\Users\\trentm\\AppData\\Roaming\\Acme\\SuperApp'

On non-Windows platforms, this parameter is ignored.

**Type**: ``bool``

**Default**: ``False``

**Platform**: Windows only

``multipath``
-------------

Unix/macOS only. When ``True``, ``site_data_dir`` and ``site_config_dir`` return all directories
from ``XDG_DATA_DIRS`` / ``XDG_CONFIG_DIRS`` joined by ``os.pathsep`` (``:``) instead of just
the first one:

.. code-block:: pycon

   >>> from platformdirs import site_data_dir
   >>> site_data_dir("SuperApp", multipath=True)  # on Linux
   '/usr/local/share/SuperApp:/usr/share/SuperApp'

**Type**: ``bool``

**Default**: ``False``

**Platform**: Unix/macOS only

``opinion``
-----------

When ``True`` (the default), certain directories get an opinionated subdirectory. For example, on
Windows the cache directory includes a ``Cache`` subdirectory, and the log directory includes ``Logs``.
On Linux, the log directory appends ``/log``. Set to ``False`` to suppress this:

.. code-block:: pycon

   >>> user_cache_dir("SuperApp", "Acme")  # on Windows, opinion=True
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp\\Cache'
   >>> user_cache_dir("SuperApp", "Acme", opinion=False)  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp'

**Type**: ``bool``

**Default**: ``True``

``ensure_exists``
-----------------

When ``True``, the directory is created (including parents) when the property is accessed.
Defaults to ``False``.

.. code-block:: python

   from platformdirs import PlatformDirs

   dirs = PlatformDirs("SuperApp", "Acme", ensure_exists=True)
   dirs.user_cache_dir  # directory is created if it does not exist

**Type**: ``bool``

**Default**: ``False``

**See also**: :ref:`creating-directories-safely` for manual directory creation patterns.

``use_site_for_root``
---------------------

Unix-only. When ``True``, redirects ``user_*_dir`` calls to their ``site_*_dir`` equivalents when
running as root (uid 0). Defaults to ``False`` for backwards compatibility.

When enabled, XDG user environment variables (e.g., ``XDG_DATA_HOME``) are bypassed for the
redirected directories. This is useful for system services running as root that should use
system-wide directories rather than root's home directory.

.. code-block:: python

   from platformdirs import PlatformDirs

   dirs = PlatformDirs("SuperApp", use_site_for_root=True)
   # When running as root, user_data_dir returns the site_data_dir path
   dirs.user_data_dir  # Returns site directory instead of /root/.local/share/SuperApp

**Type**: ``bool``

**Default**: ``False``

**Platform**: Unix only

.. _xdg-env-vars:

XDG environment variables
--------------------------

On Linux, ``platformdirs`` follows the `XDG Base Directory Specification
<https://specifications.freedesktop.org/basedir/latest/>`_. Environment variables like
``XDG_DATA_HOME``, ``XDG_CONFIG_HOME``, ``XDG_CACHE_HOME``, and ``XDG_STATE_HOME`` override
the default directories when set.

On macOS, the same XDG environment variables are also supported and take precedence over the
default macOS directories:

.. code-block:: pycon

   >>> import os
   >>> os.environ["XDG_CONFIG_HOME"] = "/Users/trentm/.config"
   >>> user_config_dir("SuperApp")
   '/Users/trentm/.config/SuperApp'

Supported XDG variables:

- ``XDG_DATA_HOME`` - user data directory.
- ``XDG_CONFIG_HOME`` - user config directory.
- ``XDG_CACHE_HOME`` - user cache directory.
- ``XDG_STATE_HOME`` - user state directory.
- ``XDG_DATA_DIRS`` - system data directories (colon-separated).
- ``XDG_CONFIG_DIRS`` - system config directories (colon-separated).
- ``XDG_RUNTIME_DIR`` - user runtime directory.

**Windows environment variable overrides**: On Windows, ``WIN_PD_OVERRIDE_*`` environment
variables can override default paths. See the :ref:`platforms:Windows` section for details.

Directories not covered
------------------------

``platformdirs`` does not provide a property for the user's **home directory**. Use
:meth:`pathlib.Path.home` or :func:`os.path.expanduser` from the standard library instead:

.. code-block:: pycon

   >>> from pathlib import Path
   >>> Path.home()
   PosixPath('/Users/trentm')
