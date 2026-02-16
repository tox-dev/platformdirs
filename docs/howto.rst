###############
 How-to guides
###############

Recipes for common tasks. For background on why directories differ across platforms, see :doc:`explanation`.

*****************
 Common patterns
*****************

.. _creating-directories-safely:

Creating directories safely
===========================

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
=====================

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
==============================

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
=================

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
========================

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

Merging config from multiple sources
====================================

Use :meth:`~platformdirs.api.PlatformDirsABC.iter_config_paths` to load site-wide defaults first, then overlay
user-specific overrides:

.. code-block:: python

    import json
    from platformdirs import PlatformDirs

    dirs = PlatformDirs("MyApp")
    config = {}

    # Iterate from least specific (site) to most specific (user)
    for config_dir in dirs.iter_config_paths():
        config_file = config_dir / "config.json"
        if config_file.exists():
            config.update(json.loads(config_file.read_text()))

The same pattern works with :meth:`~platformdirs.api.PlatformDirsABC.iter_data_paths` for data files and
:meth:`~platformdirs.api.PlatformDirsABC.iter_config_dirs` for string paths.

Testing code that uses platformdirs
===================================

Use ``monkeypatch`` or ``tmp_path`` to override directories in tests:

.. code-block:: python

    from platformdirs import PlatformDirs


    def my_app_init(dirs: PlatformDirs) -> dict:
        config_file = dirs.user_config_path / "config.json"
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {}

.. code-block:: python

    # test_my_app.py
    import json
    from unittest.mock import MagicMock


    def test_loads_config(tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text('{"theme": "dark"}')

        dirs = MagicMock()
        dirs.user_config_path = tmp_path

        result = my_app_init(dirs)
        assert result == {"theme": "dark"}

Alternatively, monkeypatch the standalone functions:

.. code-block:: python

    def test_data_dir(monkeypatch, tmp_path):
        monkeypatch.setattr("platformdirs.user_data_dir", lambda *a, **kw: str(tmp_path))

        from platformdirs import user_data_dir

        assert user_data_dir("MyApp") == str(tmp_path)

Overriding directories with environment variables
=================================================

On Linux/macOS, set XDG environment variables to redirect directories:

.. code-block:: console

    $ export XDG_CONFIG_HOME="$HOME/.myconfig"
    $ python -c "from platformdirs import user_config_dir; print(user_config_dir('MyApp'))"
    /home/user/.myconfig/MyApp

On Windows, use ``WIN_PD_OVERRIDE_*`` variables:

.. code-block:: console

    > set WIN_PD_OVERRIDE_LOCAL_APPDATA=X:\appdata
    > python -c "from platformdirs import user_cache_dir; print(user_cache_dir('MyApp', 'Acme'))"
    X:\appdata\Acme\MyApp\Cache

See :ref:`xdg-env-vars` for the full list of supported XDG variables, and the :ref:`explanation:Windows` section for all
``WIN_PD_OVERRIDE_*`` variables.

***************************
 Platform-specific recipes
***************************

Windows: roaming vs local profiles
==================================

Use ``roaming=True`` for settings that should sync across domain-joined machines:

.. code-block:: python

    from platformdirs import user_config_path, user_cache_path

    # Synced across domain computers
    roaming_cfg = user_config_path("MyApp", roaming=True)

    # Local to this machine
    local_cache = user_cache_path("MyApp")

macOS: separating data and config
=================================

On macOS, ``user_data_dir`` and ``user_config_dir`` both resolve to ``~/Library/Application Support/AppName``. Use
subdirectories to separate concerns:

.. code-block:: python

    from platformdirs import user_data_path

    app_dir = user_data_path("MyApp")
    config_dir = app_dir / "config"
    databases_dir = app_dir / "databases"

Linux: falling back from site to user config
============================================

Site directories require root privileges. Fall back to user directories for normal users:

.. code-block:: python

    from platformdirs import site_config_path, user_config_path
    import os

    site_cfg = site_config_path("MyApp") / "defaults.conf"

    if os.access(site_cfg.parent, os.W_OK):
        site_cfg.write_text("[defaults]\n")
    else:
        user_cfg = user_config_path("MyApp") / "config.conf"
        user_cfg.parent.mkdir(parents=True, exist_ok=True)
        user_cfg.write_text("[user_settings]\n")

Linux: redirecting user directories when running as root
========================================================

Use ``use_site_for_root=True`` so system services write to ``/usr/local/share`` instead of ``/root``:

.. code-block:: python

    from platformdirs import PlatformDirs
    import os

    if os.geteuid() == 0:
        dirs = PlatformDirs("myservice", use_site_for_root=True)
        # user_data_dir now returns /usr/local/share/myservice
    else:
        dirs = PlatformDirs("myservice")
        # user_data_dir returns ~/.local/share/myservice
