Usage guide
===========

This guide shows you how to use ``platformdirs`` to find the correct directories for your
application's data, config, cache, logs, and state on any platform.

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

Using the PlatformDirs class
-----------------------------

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

Complete application example
-----------------------------

Here's a typical application setup using multiple directory types:

.. code-block:: python

   from platformdirs import PlatformDirs
   from pathlib import Path
   import json
   import logging

   class MyApp:
       def __init__(self):
           # Initialize all directories at once
           dirs = PlatformDirs("MyApp", "AcmeCompany", ensure_exists=True)

           # Persistent data (database, downloads)
           self.db_path = dirs.user_data_path / "app.db"

           # User configuration
           self.config_path = dirs.user_config_path / "settings.json"

           # Cache for performance
           self.cache_dir = dirs.user_cache_path

           # Application logs
           log_file = dirs.user_log_path / "app.log"
           logging.basicConfig(filename=log_file, level=logging.INFO)

           # Window state and UI preferences
           self.state_path = dirs.user_state_path / "window.json"

       def load_config(self):
           if self.config_path.exists():
               return json.loads(self.config_path.read_text())
           return {"theme": "light", "autosave": True}

Choosing the right directory
-----------------------------

``platformdirs`` provides different directory types for different kinds of data. Choose based on
the data's purpose and lifetime.

Data directories
~~~~~~~~~~~~~~~~

Use ``user_data_dir`` and ``site_data_dir`` for persistent application data that the user expects
to keep:

- SQLite databases, document stores.
- Downloaded files, media assets.
- User-created content.
- Application state that must survive app updates.

.. code-block:: python

   from platformdirs import user_data_path

   db_path = user_data_path("MyApp") / "app.db"
   downloads_dir = user_data_path("MyApp") / "downloads"

Config directories
~~~~~~~~~~~~~~~~~~

Use ``user_config_dir`` and ``site_config_dir`` for configuration files and user preferences:

- Settings files (JSON, TOML, INI, YAML).
- User preferences and options.
- Application themes, keybindings.
- Feature flags and toggles.

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

- API response caches.
- Thumbnail images, processed media.
- Compiled templates, bytecode.
- Downloaded package indexes.

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

- Window positions, sizes.
- Recently opened files, MRU lists.
- Undo/redo history.
- Search history, autocomplete data.

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

- Debug logs, error logs.
- Audit trails, access logs.
- Performance metrics.
- Crash reports.

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

- **Per-user**: Each user on the system has their own separate directory.
- **Writable**: Normal users can read and write without special permissions.
- **Isolated**: Changes by one user don't affect others.
- **Default choice**: Use these unless you specifically need system-wide access.

.. code-block:: python

   from platformdirs import user_config_path

   # Each user gets their own config
   config = user_config_path("MyApp") / "config.json"

Site directories
~~~~~~~~~~~~~~~~

Site directories (``site_data_dir``, ``site_config_dir``, etc.) are:

- **System-wide**: Shared across all users on the machine.
- **Read-only for users**: Typically require administrator/root privileges to write.
- **System defaults**: Store default configurations, shared resources.
- **Package managers**: Used by system package managers for application data.

.. code-block:: python

   from platformdirs import site_config_path, user_config_path

   # Check site config first (system defaults), then user config (overrides)
   site_cfg = site_config_path("MyApp") / "defaults.json"
   user_cfg = user_config_path("MyApp") / "config.json"

   if user_cfg.exists():
       config = user_cfg
   elif site_cfg.exists():
       config = site_cfg
   else:
       config = None

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

Next steps
----------

- See :doc:`parameters` for detailed parameter reference.
- See :doc:`howto` for common patterns and platform-specific guidance.
- See :doc:`api` for complete API documentation.
- See :doc:`platforms` for platform-specific path details.
