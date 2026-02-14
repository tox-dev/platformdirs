Usage guide
===========

Getting started
---------------

The simplest way to use ``platformdirs`` is through the convenience functions:

.. code-block:: pycon

   >>> from platformdirs import user_data_dir, user_config_dir, user_cache_dir
   >>> user_data_dir("SuperApp", "Acme")
   '/Users/trentm/Library/Application Support/SuperApp'
   >>> user_config_dir("SuperApp", "Acme")
   '/Users/trentm/Library/Application Support/SuperApp'
   >>> user_cache_dir("SuperApp", "Acme")
   '/Users/trentm/Library/Caches/SuperApp'

Each function returns a :class:`str`. For a :class:`~pathlib.Path`, use the ``_path`` variant:

.. code-block:: pycon

   >>> from platformdirs import user_data_path
   >>> user_data_path("SuperApp", "Acme")
   PosixPath('/Users/trentm/Library/Application Support/SuperApp')

Using the ``PlatformDirs`` class
--------------------------------

When you need multiple directories for the same application, instantiate
:data:`~platformdirs.PlatformDirs` once and access its properties:

.. code-block:: pycon

   >>> from platformdirs import PlatformDirs
   >>> dirs = PlatformDirs("SuperApp", "Acme")
   >>> dirs.user_data_dir
   '/Users/trentm/Library/Application Support/SuperApp'
   >>> dirs.user_cache_dir
   '/Users/trentm/Library/Caches/SuperApp'
   >>> dirs.user_log_dir
   '/Users/trentm/Library/Logs/SuperApp'

Each :class:`str` property has a corresponding ``_path`` property that returns a :class:`~pathlib.Path`:

.. code-block:: pycon

   >>> dirs.user_data_path
   PosixPath('/Users/trentm/Library/Application Support/SuperApp')

Parameters
----------

``appname``
~~~~~~~~~~~

The name of your application. Used as a subdirectory in all app-specific paths.
When ``None``, the base platform directory is returned without any app-specific subdirectory.

.. code-block:: pycon

   >>> user_data_dir("SuperApp")
   '/Users/trentm/Library/Application Support/SuperApp'
   >>> user_data_dir()
   '/Users/trentm/Library/Application Support'

``appauthor``
~~~~~~~~~~~~~

The app author or distributing organization. On Windows, this adds an additional parent directory:

.. code-block:: pycon

   >>> user_data_dir("SuperApp", "Acme")  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp'

Set to ``False`` to suppress the author directory even on Windows:

.. code-block:: pycon

   >>> user_data_dir("SuperApp", False)  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\SuperApp'

On non-Windows platforms, ``appauthor`` is ignored.

``version``
~~~~~~~~~~~

Appends a version subdirectory. Useful for running multiple app versions side by side:

.. code-block:: pycon

   >>> from platformdirs import PlatformDirs
   >>> dirs = PlatformDirs("SuperApp", "Acme", version="1.0")
   >>> dirs.user_data_dir
   '/Users/trentm/Library/Application Support/SuperApp/1.0'
   >>> dirs.user_cache_dir
   '/Users/trentm/Library/Caches/SuperApp/1.0'

Be wary of using this for configuration files; you will need to handle migrating configuration
files between versions manually.

``roaming``
~~~~~~~~~~~

Windows-only. When ``True``, uses the roaming AppData directory (``CSIDL_APPDATA``) instead of
the local one (``CSIDL_LOCAL_APPDATA``). Roaming profiles sync across machines in a Windows domain.

.. code-block:: pycon

   >>> user_data_dir("SuperApp", "Acme", roaming=True)  # on Windows
   'C:\\Users\\trentm\\AppData\\Roaming\\Acme\\SuperApp'

``multipath``
~~~~~~~~~~~~~

Unix/macOS only. When ``True``, ``site_data_dir`` and ``site_config_dir`` return all directories
from ``XDG_DATA_DIRS`` / ``XDG_CONFIG_DIRS`` joined by ``os.pathsep`` (``:``) instead of just
the first one:

.. code-block:: pycon

   >>> from platformdirs import site_data_dir
   >>> site_data_dir("SuperApp", multipath=True)  # on Linux
   '/usr/local/share/SuperApp:/usr/share/SuperApp'

``opinion``
~~~~~~~~~~~

When ``True`` (the default), certain directories get an opinionated subdirectory. For example, on
Windows the cache directory includes a ``Cache`` subdirectory, and the log directory includes ``Logs``.
On Linux, the log directory appends ``/log``. Set to ``False`` to suppress this:

.. code-block:: pycon

   >>> user_cache_dir("SuperApp", "Acme")  # on Windows, opinion=True
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp\\Cache'
   >>> user_cache_dir("SuperApp", "Acme", opinion=False)  # on Windows
   'C:\\Users\\trentm\\AppData\\Local\\Acme\\SuperApp'

``ensure_exists``
~~~~~~~~~~~~~~~~~

When ``True``, the directory is created (including parents) when the property is accessed.
Defaults to ``False``.

.. code-block:: python

   from platformdirs import PlatformDirs

   dirs = PlatformDirs("SuperApp", "Acme", ensure_exists=True)
   dirs.user_cache_dir  # directory is created if it does not exist

Directories not covered
-----------------------

``platformdirs`` does not provide a property for the user's **home directory**. Use
:meth:`pathlib.Path.home` or :func:`os.path.expanduser` from the standard library instead:

.. code-block:: pycon

   >>> from pathlib import Path
   >>> Path.home()
   PosixPath('/Users/trentm')

XDG environment variables
-------------------------

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
