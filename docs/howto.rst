How-to guides
=============

This page provides recipes for common tasks and platform-specific guidance.

Common patterns
---------------

.. _creating-directories-safely:

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
   from pathlib import Path
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

.. _versioned-data-migration:

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

Platform-specific considerations
---------------------------------

Windows
~~~~~~~

Windows Store Python sandbox
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applications installed via the Microsoft Store run in a restricted sandbox environment.
``platformdirs`` handles this automatically, but be aware that:

- File system access is limited to specific directories.
- Some APIs may return sandbox-specific paths.
- Network access may require additional permissions.

Roaming vs local profiles
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``roaming=True`` for settings that should sync across domain-joined machines. Use local
(default) for machine-specific data like caches.

.. code-block:: python

   from platformdirs import user_config_path, user_cache_path

   # Synced across domain computers
   roaming_cfg = user_config_path("MyApp", roaming=True)

   # Local to this machine
   local_cache = user_cache_path("MyApp")

Environment variable overrides
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows supports environment variable overrides for certain directories:

- ``WIN_PD_OVERRIDE_*`` - Override specific directory types
- ``PLATFORMDIRS_*`` - Alternative override mechanism

See the source code for complete list of supported variables.

macOS
~~~~~

Data and config location
^^^^^^^^^^^^^^^^^^^^^^^^^

On macOS, ``user_data_dir`` and ``user_config_dir`` both return
``~/Library/Application Support/AppName`` by default. Use subdirectories to separate concerns:

.. code-block:: python

   from platformdirs import user_data_path

   app_dir = user_data_path("MyApp")
   config_dir = app_dir / "config"
   databases_dir = app_dir / "databases"

XDG support on macOS
^^^^^^^^^^^^^^^^^^^^

macOS now supports XDG environment variables. If ``XDG_DATA_HOME`` is set, ``platformdirs``
will honor it instead of using ``~/Library``:

.. code-block:: python

   import os
   from platformdirs import user_data_dir

   # Without XDG
   user_data_dir("MyApp")  # ~/Library/Application Support/MyApp

   # With XDG
   os.environ["XDG_DATA_HOME"] = os.path.expanduser("~/.local/share")
   user_data_dir("MyApp")  # ~/.local/share/MyApp

Linux/Unix
~~~~~~~~~~

Permission requirements
^^^^^^^^^^^^^^^^^^^^^^^^

Writing to ``site_*`` directories typically requires root privileges. Normal users can only
read from these locations:

.. code-block:: python

   from platformdirs import site_config_path, user_config_path
   import os

   site_cfg = site_config_path("MyApp") / "defaults.conf"

   # Check if we can write to site config
   if os.access(site_cfg.parent, os.W_OK):
       # Running as root or have special permissions
       site_cfg.write_text("[defaults]\n")
   else:
       # Normal user - use user config instead
       user_cfg = user_config_path("MyApp") / "config.conf"
       user_cfg.parent.mkdir(parents=True, exist_ok=True)
       user_cfg.write_text("[user_settings]\n")

XDG Base Directory Specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``platformdirs`` fully supports the XDG Base Directory Specification. Users can override
default paths by setting environment variables:

- ``XDG_DATA_HOME`` - defaults to ``~/.local/share``
- ``XDG_CONFIG_HOME`` - defaults to ``~/.config``
- ``XDG_CACHE_HOME`` - defaults to ``~/.cache``
- ``XDG_STATE_HOME`` - defaults to ``~/.local/state``
- ``XDG_RUNTIME_DIR`` - defaults to ``/run/user/$UID``
- ``XDG_DATA_DIRS`` - defaults to ``/usr/local/share:/usr/share``
- ``XDG_CONFIG_DIRS`` - defaults to ``/etc/xdg``

Running as root
^^^^^^^^^^^^^^^

When running as root (uid 0), ``user_*`` directories default to root's home directory
(``/root``). Use ``use_site_for_root=True`` to redirect to system directories instead:

.. code-block:: python

   from platformdirs import PlatformDirs
   import os

   # System service that should use /var/lib instead of /root
   if os.geteuid() == 0:
       dirs = PlatformDirs("myservice", use_site_for_root=True)
       # user_data_dir now returns /usr/local/share/myservice
   else:
       dirs = PlatformDirs("myservice")
       # user_data_dir returns ~/.local/share/myservice

Android
~~~~~~~

App-specific storage
^^^^^^^^^^^^^^^^^^^^

All directories are within your app's private storage (``/data/data/<package_name>/``).
Data is automatically removed when the app is uninstalled.

.. code-block:: python

   from platformdirs import user_data_path

   # Returns /data/data/com.example.myapp/files/MyApp
   data_dir = user_data_path("MyApp")

External storage not supported
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``platformdirs`` does not provide paths for external/shared storage (SD cards,
``/storage/emulated/0/``). Use Android-specific APIs for shared storage:

.. code-block:: python

   # For shared/external storage on Android, use Android APIs directly
   # platformdirs only handles app-private directories

Storage permissions
^^^^^^^^^^^^^^^^^^^

App-private directories provided by ``platformdirs`` don't require storage permissions.
For external storage access, your app needs appropriate Android permissions.
