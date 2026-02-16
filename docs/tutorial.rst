##########
 Tutorial
##########

In this tutorial, we will set up ``platformdirs`` for a small application that stores user preferences, caches API
responses, and writes log files -- all to the correct platform-specific directories.

**************
 Installation
**************

Install ``platformdirs`` from PyPI:

.. code-block:: console

    $ pip install platformdirs

Verify the installation:

.. code-block:: pycon

    >>> import platformdirs
    >>> platformdirs.__version__
    '...'

******************************
 Finding your first directory
******************************

Let's find where our application should store its data. Open a Python shell and run:

.. code-block:: pycon

    >>> from platformdirs import user_data_dir
    >>> user_data_dir("MyApp", "AcmeCompany")
    '...'

The result depends on the platform you're running on:

.. tab-set::

    .. tab-item:: macOS
       :sync: macos

       .. code-block:: python

          '/Users/<you>/Library/Application Support/MyApp'

    .. tab-item:: Linux
       :sync: linux

       .. code-block:: python

          '/home/<you>/.local/share/MyApp'

    .. tab-item:: Windows
       :sync: windows

       .. code-block:: python

          'C:\\Users\\<you>\\AppData\\Local\\AcmeCompany\\MyApp'

Each function returns a :class:`str`. If we prefer a :class:`~pathlib.Path`, we use the ``_path`` variant:

.. code-block:: pycon

    >>> from platformdirs import user_data_path
    >>> user_data_path("MyApp", "AcmeCompany")
    PosixPath('...')

Now let's find the cache directory:

.. code-block:: pycon

    >>> from platformdirs import user_cache_dir
    >>> user_cache_dir("MyApp", "AcmeCompany")
    '...'

And the log directory:

.. code-block:: pycon

    >>> from platformdirs import user_log_dir
    >>> user_log_dir("MyApp", "AcmeCompany")
    '...'

Each directory type resolves to a different location, following the conventions of the current platform.

***********************************
 Working with multiple directories
***********************************

When we need several directories for the same application, importing individual functions becomes verbose. Instead, we
instantiate :class:`~platformdirs.PlatformDirs` once and access its properties:

.. code-block:: pycon

    >>> from platformdirs import PlatformDirs
    >>> dirs = PlatformDirs("MyApp", "AcmeCompany")
    >>> dirs.user_data_dir
    '...'
    >>> dirs.user_config_dir
    '...'
    >>> dirs.user_cache_dir
    '...'
    >>> dirs.user_log_dir
    '...'

Every :class:`str` property has a corresponding ``_path`` property:

.. code-block:: pycon

    >>> dirs.user_data_path
    PosixPath('...')
    >>> dirs.user_cache_path
    PosixPath('...')

We can also have ``platformdirs`` create the directories for us by setting ``ensure_exists=True``:

.. code-block:: pycon

    >>> dirs = PlatformDirs("MyApp", "AcmeCompany", ensure_exists=True)
    >>> dirs.user_data_dir  # directory is created if it doesn't exist
    '...'

******************
 Complete example
******************

Let's put it all together. We will build a small application class that uses config, cache, data, and log directories:

.. code-block:: python

    import json
    import logging
    from pathlib import Path

    from platformdirs import PlatformDirs


    class MyApp:
        def __init__(self) -> None:
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

        def load_config(self) -> dict:
            if self.config_path.exists():
                return json.loads(self.config_path.read_text())
            return {"theme": "light", "autosave": True}

We can verify that it works:

.. code-block:: pycon

    >>> app = MyApp()
    >>> app.config_path
    PosixPath('...')
    >>> app.db_path
    PosixPath('...')

Each directory is created automatically and follows the platform conventions.

*********************
 What you've learned
*********************

- ``platformdirs`` resolves the correct directory for each platform automatically.
- Standalone functions like ``user_data_dir`` return a single directory as a :class:`str`.
- The ``_path`` variants return :class:`~pathlib.Path` objects.
- The :class:`~platformdirs.PlatformDirs` class provides all directories from a single instance.
- ``ensure_exists=True`` creates directories on first access.

******************
 Where to go next
******************

- :doc:`howto` -- recipes for common tasks like error handling, cache cleanup, and testing.
- :doc:`explanation` -- understand why different directory types exist and how each platform works.
- :doc:`parameters` -- full reference for all parameters (``appname``, ``version``, ``roaming``, etc.).
- :doc:`api` -- complete API documentation.
- :doc:`platforms` -- exact paths for every directory on every platform.
