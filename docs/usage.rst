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

``use_site_for_root``
~~~~~~~~~~~~~~~~~~~~~

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

Choosing the right directory
-----------------------------

``platformdirs`` provides different directory types for different kinds of data. Choose based on
the data's purpose and lifetime.

Data directories
~~~~~~~~~~~~~~~~

Use ``user_data_dir`` and ``site_data_dir`` for persistent application data that the user expects
to keep:

- SQLite databases, document stores
- Downloaded files, media assets
- User-created content
- Application state that must survive app updates

.. code-block:: python

   from pathlib import Path
   from platformdirs import user_data_path

   db_path = user_data_path("MyApp") / "app.db"
   downloads_dir = user_data_path("MyApp") / "downloads"

Config directories
~~~~~~~~~~~~~~~~~~

Use ``user_config_dir`` and ``site_config_dir`` for configuration files and user preferences:

- Settings files (JSON, TOML, INI, YAML)
- User preferences and options
- Application themes, keybindings
- Feature flags and toggles

.. code-block:: python

   from platformdirs import user_config_path
   import json

   config_file = user_config_path("MyApp") / "settings.json"
   config_file.parent.mkdir(parents=True, exist_ok=True)

   settings = {"theme": "dark", "auto_save": True}
   config_file.write_text(json.dumps(settings))

Cache directories
~~~~~~~~~~~~~~~~~

Use ``user_cache_dir`` and ``site_cache_dir`` for regenerable data that improves performance:

- API response caches
- Thumbnail images, processed media
- Compiled templates, bytecode
- Downloaded package indexes

Cached data can be safely deleted without losing functionality. Applications should gracefully
handle missing cache directories.

.. code-block:: python

   from platformdirs import user_cache_path

   cache_dir = user_cache_path("MyApp")
   thumbnail_cache = cache_dir / "thumbnails"
   api_cache = cache_dir / "api_responses"

State directories
~~~~~~~~~~~~~~~~~

Use ``user_state_dir`` and ``site_state_dir`` for non-critical runtime state:

- Window positions, sizes
- Recently opened files, MRU lists
- Undo/redo history
- Search history, autocomplete data

State persists between sessions but is less important than data or config. Loss of state is
inconvenient but not catastrophic.

.. code-block:: python

   from platformdirs import user_state_path
   import json

   state_file = user_state_path("MyApp") / "window_state.json"
   state = {"width": 1024, "height": 768, "maximized": False}
   state_file.parent.mkdir(parents=True, exist_ok=True)
   state_file.write_text(json.dumps(state))

Log directories
~~~~~~~~~~~~~~~

Use ``user_log_dir`` and ``site_log_dir`` for application logs:

- Debug logs, error logs
- Audit trails, access logs
- Performance metrics
- Crash reports

.. code-block:: python

   import logging
   from platformdirs import user_log_path

   log_file = user_log_path("MyApp") / "app.log"
   log_file.parent.mkdir(parents=True, exist_ok=True)

   logging.basicConfig(
       filename=log_file,
       level=logging.INFO,
       format="%(asctime)s - %(levelname)s - %(message)s"
   )

User vs site directories
------------------------

Each directory type has both ``user_*`` and ``site_*`` variants serving different purposes.

User directories
~~~~~~~~~~~~~~~~

User directories (``user_data_dir``, ``user_config_dir``, etc.) are:

- **Per-user**: Each user on the system has their own separate directory
- **Writable**: Normal users can read and write without special permissions
- **Isolated**: Changes by one user don't affect others
- **Default choice**: Use these unless you specifically need system-wide access

.. code-block:: python

   from platformdirs import user_config_path

   # Each user gets their own config
   config = user_config_path("MyApp") / "config.json"

Site directories
~~~~~~~~~~~~~~~~

Site directories (``site_data_dir``, ``site_config_dir``, etc.) are:

- **System-wide**: Shared across all users on the machine
- **Read-only for users**: Typically require administrator/root privileges to write
- **System defaults**: Store default configurations, shared resources
- **Package managers**: Used by system package managers for application data

.. code-block:: python

   from platformdirs import site_config_path, user_config_path
   from pathlib import Path

   # Check site config first (system defaults), then user config (overrides)
   site_cfg = site_config_path("MyApp") / "defaults.json"
   user_cfg = user_config_path("MyApp") / "config.json"

   if user_cfg.exists():
       config = user_cfg
   elif site_cfg.exists():
       config = site_cfg
   else:
       config = None

Common patterns
---------------

Creating directories safely
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always create parent directories before writing files:

.. code-block:: python

   from pathlib import Path
   from platformdirs import user_data_path

   data_dir = user_data_path("MyApp")
   db_file = data_dir / "data.db"

   # Create directory if it doesn't exist
   db_file.parent.mkdir(parents=True, exist_ok=True)

   # Now safe to write
   db_file.write_bytes(b"...")

Or use ``ensure_exists=True`` to create directories automatically:

.. code-block:: python

   from platformdirs import PlatformDirs

   dirs = PlatformDirs("MyApp", ensure_exists=True)
   db_file = dirs.user_data_path / "data.db"
   db_file.write_bytes(b"...")  # Directory already exists

Handling write errors
~~~~~~~~~~~~~~~~~~~~~

Directory paths may not be writable due to permissions or disk space:

.. code-block:: python

   from platformdirs import user_data_path
   import tempfile

   data_dir = user_data_path("MyApp")
   data_file = data_dir / "data.json"

   try:
       data_dir.mkdir(parents=True, exist_ok=True)
       data_file.write_text('{"key": "value"}')
   except (OSError, PermissionError) as e:
       # Fallback to temp directory
       temp_dir = Path(tempfile.gettempdir()) / "MyApp"
       temp_dir.mkdir(parents=True, exist_ok=True)
       data_file = temp_dir / "data.json"
       data_file.write_text('{"key": "value"}')

Checking directory writability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test if a directory is writable before using it:

.. code-block:: python

   from platformdirs import user_cache_path
   import os

   cache_dir = user_cache_path("MyApp")
   cache_dir.mkdir(parents=True, exist_ok=True)

   if os.access(cache_dir, os.W_OK):
       # Directory is writable
       cache_file = cache_dir / "cache.dat"
       cache_file.write_bytes(b"...")
   else:
       # Handle read-only directory
       print(f"Warning: {cache_dir} is not writable")

Cleaning up cache
~~~~~~~~~~~~~~~~~

Implement cache cleanup based on age or size:

.. code-block:: python

   from platformdirs import user_cache_path
   import time

   cache_dir = user_cache_path("MyApp")
   max_age_days = 30

   if cache_dir.exists():
       now = time.time()
       for item in cache_dir.rglob("*"):
           if item.is_file():
               age_days = (now - item.stat().st_mtime) / 86400
               if age_days > max_age_days:
                   item.unlink()

Versioned data migration
~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``version`` parameter, handle migration between versions:

.. code-block:: python

   from platformdirs import user_data_path
   import shutil

   current_version = "2.0"
   previous_version = "1.0"

   current_dir = user_data_path("MyApp", version=current_version)
   previous_dir = user_data_path("MyApp", version=previous_version)

   if not current_dir.exists() and previous_dir.exists():
       # Migrate data from previous version
       current_dir.mkdir(parents=True, exist_ok=True)
       for item in previous_dir.iterdir():
           shutil.copy2(item, current_dir / item.name)

Real-world examples
-------------------

These examples show how popular Python projects use ``platformdirs`` in production. Each example
is based on actual code with links to the source.

Black (code formatter)
~~~~~~~~~~~~~~~~~~~~~~

`Black <https://github.com/psf/black>`_ uses ``user_cache_path`` to cache formatted files,
speeding up repeat runs:

.. code-block:: python

   import os
   from pathlib import Path
   from platformdirs import user_cache_path

   def get_cache_dir() -> Path:
       # Allow customization via environment variable
       default_cache_dir = user_cache_path("black")
       cache_dir = Path(os.environ.get("BLACK_CACHE_DIR", default_cache_dir))
       return cache_dir / __version__

   CACHE_DIR = get_cache_dir()

See `black/cache.py <https://github.com/psf/black/blob/main/src/black/cache.py>`_ for the full
implementation.

virtualenv (environment manager)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`virtualenv <https://github.com/pypa/virtualenv>`_ uses ``user_data_dir`` to store application
data with fallback to temp directory if not writable:

.. code-block:: python

   import os
   from platformdirs import user_data_dir

   def get_app_data_dir(env):
       key = "VIRTUALENV_OVERRIDE_APP_DATA"
       if key in env:
           return env[key]
       return user_data_dir(appname="virtualenv", appauthor="pypa")

   folder = get_app_data_dir(os.environ)
   folder = os.path.abspath(folder)

   # Create directory and check writability
   os.makedirs(folder, exist_ok=True)
   if not os.access(folder, os.W_OK):
       # Fallback to temp directory
       folder = tempfile.gettempdir()

See `virtualenv/app_data/__init__.py <https://github.com/pypa/virtualenv/blob/main/src/virtualenv/app_data/__init__.py>`_
for the full implementation.

Poetry (dependency manager)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Poetry <https://github.com/python-poetry/poetry>`_ uses all three directory types with
environment variable overrides:

.. code-block:: python

   import os
   from pathlib import Path
   from platformdirs import user_cache_path, user_config_path, user_data_path

   APP_NAME = "pypoetry"

   # Cache directory for downloads and build artifacts
   DEFAULT_CACHE_DIR = user_cache_path(APP_NAME, appauthor=False)

   # Config directory with environment override and roaming enabled
   CONFIG_DIR = Path(
       os.getenv("POETRY_CONFIG_DIR")
       or user_config_path(APP_NAME, appauthor=False, roaming=True)
   )

   # Data directory with environment override
   def data_dir() -> Path:
       if poetry_home := os.getenv("POETRY_HOME"):
           return Path(poetry_home).expanduser()
       return user_data_path(APP_NAME, appauthor=False, roaming=True)

See `poetry/locations.py <https://github.com/python-poetry/poetry/blob/main/src/poetry/locations.py>`_
for the full implementation.

tox (testing tool)
~~~~~~~~~~~~~~~~~~

`tox <https://github.com/tox-dev/tox>`_ uses ``user_config_dir`` for user-level configuration:

.. code-block:: python

   from pathlib import Path
   from platformdirs import user_config_dir

   DEFAULT_CONFIG_FILE = Path(user_config_dir("tox")) / "config.ini"

   # Load config with environment variable override
   config_file = os.getenv("TOX_USER_CONFIG_FILE", DEFAULT_CONFIG_FILE)

See `tox/config/cli/ini.py <https://github.com/tox-dev/tox/blob/main/src/tox/config/cli/ini.py>`_
for the full implementation.

Platform-specific considerations
---------------------------------

Windows
~~~~~~~

**Store Python sandbox**: Applications installed via the Microsoft Store run in a restricted
sandbox environment. ``platformdirs`` handles this automatically, but be aware that:

- File system access is limited to specific directories
- Some APIs may return sandbox-specific paths
- Network access may require additional permissions

**Roaming vs local**: Use ``roaming=True`` for settings that should sync across domain-joined
machines. Use local (default) for machine-specific data like caches.

.. code-block:: python

   from platformdirs import user_config_path

   # Synced across domain computers
   roaming_cfg = user_config_path("MyApp", roaming=True)

   # Local to this machine
   local_cache = user_cache_path("MyApp")

macOS
~~~~~

**Data and config location**: On macOS, ``user_data_dir`` and ``user_config_dir`` both return
``~/Library/Application Support/AppName`` by default. Use subdirectories to separate concerns:

.. code-block:: python

   from platformdirs import user_data_path

   app_dir = user_data_path("MyApp")
   config_dir = app_dir / "config"
   databases_dir = app_dir / "databases"

**XDG support**: macOS now supports XDG environment variables. If ``XDG_DATA_HOME`` is set,
``platformdirs`` will honor it instead of using ``~/Library``.

Linux/Unix
~~~~~~~~~~

**Permissions**: Writing to ``site_*`` directories typically requires root privileges. Normal
users can only read from these locations.

**XDG environment variables**: ``platformdirs`` fully supports the XDG Base Directory Specification.
Users can override default paths by setting environment variables like ``XDG_DATA_HOME``,
``XDG_CONFIG_HOME``, etc.

**Running as root**: When running as root (uid 0), ``user_*`` directories default to root's home
directory (``/root``). Use ``use_site_for_root=True`` to redirect to system directories instead:

.. code-block:: python

   from platformdirs import PlatformDirs

   # System service that should use /var/lib instead of /root
   dirs = PlatformDirs("myservice", use_site_for_root=True)

Android
~~~~~~~

**App-specific paths**: All directories are within your app's private storage
(``/data/data/<package_name>/``). Data is automatically removed when the app is uninstalled.

**External storage**: ``platformdirs`` does not provide paths for external/shared storage
(SD cards, ``/storage/emulated/0/``). Use Android-specific APIs for shared storage.

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
