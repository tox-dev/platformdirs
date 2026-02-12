Platform details
================

``platformdirs`` auto-detects the current platform and returns the correct directory paths.
This page describes the default paths for each platform and any platform-specific behavior.

All examples below assume ``appname="SuperApp"`` and ``appauthor="Acme"`` unless stated otherwise.

Default paths
-------------

``user_data_dir``
~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.local/share/SuperApp``
   * - macOS
     - ``~/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/files/SuperApp``

``user_config_dir``
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.config/SuperApp``
   * - macOS
     - ``~/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/shared_prefs/SuperApp``

``user_cache_dir``
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.cache/SuperApp``
   * - macOS
     - ``~/Library/Caches/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Acme\SuperApp\Cache``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp``

``user_state_dir``
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.local/state/SuperApp``
   * - macOS
     - ``~/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/files/SuperApp``

``user_log_dir``
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.local/state/SuperApp/log``
   * - macOS
     - ``~/Library/Logs/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Acme\SuperApp\Logs``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp/log``

``user_runtime_dir``
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/run/user/<uid>/SuperApp``
   * - macOS
     - ``~/Library/Caches/TemporaryItems/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Temp\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp/tmp``

``site_data_dir``
~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/usr/local/share/SuperApp``
   * - macOS
     - ``/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\ProgramData\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/files/SuperApp``

``site_config_dir``
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/etc/xdg/SuperApp``
   * - macOS
     - ``/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\ProgramData\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/shared_prefs/SuperApp``

``site_cache_dir``
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/var/cache/SuperApp``
   * - macOS
     - ``/Library/Caches/SuperApp``
   * - Windows
     - ``C:\ProgramData\Acme\SuperApp\Cache``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp``

``site_runtime_dir``
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/run/SuperApp``
   * - macOS
     - ``~/Library/Caches/TemporaryItems/SuperApp``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Temp\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp/tmp``

``user_documents_dir``
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Documents``
   * - macOS
     - ``~/Documents``
   * - Windows
     - ``C:\Users\<User>\Documents``
   * - Android
     - ``/storage/emulated/0/Documents``

``user_downloads_dir``
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Downloads``
   * - macOS
     - ``~/Downloads``
   * - Windows
     - ``C:\Users\<User>\Downloads``
   * - Android
     - ``/storage/emulated/0/Downloads``

``user_pictures_dir``
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Pictures``
   * - macOS
     - ``~/Pictures``
   * - Windows
     - ``C:\Users\<User>\Pictures``
   * - Android
     - ``/storage/emulated/0/Pictures``

``user_videos_dir``
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Videos``
   * - macOS
     - ``~/Movies``
   * - Windows
     - ``C:\Users\<User>\Videos``
   * - Android
     - ``/storage/emulated/0/DCIM/Camera``

``user_music_dir``
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Music``
   * - macOS
     - ``~/Music``
   * - Windows
     - ``C:\Users\<User>\Music``
   * - Android
     - ``/storage/emulated/0/Music``

``user_desktop_dir``
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/Desktop``
   * - macOS
     - ``~/Desktop``
   * - Windows
     - ``C:\Users\<User>\Desktop``
   * - Android
     - ``/storage/emulated/0/Desktop``

macOS
-----

On macOS, ``platformdirs`` uses the standard Apple ``~/Library`` directories by default.
See `Apple's File System Programming Guide
<https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html>`_
for background.

XDG environment variables (``XDG_DATA_HOME``, ``XDG_CONFIG_HOME``, ``XDG_CACHE_HOME``, etc.)
are also supported and take precedence over the macOS defaults when set. This allows users who
prefer the XDG layout to override the default behavior.

When `Homebrew <https://brew.sh>`_ is installed, ``site_data_dir`` and ``site_cache_dir`` include
the Homebrew prefix as an additional path when ``multipath=True``.

.. autoclass:: platformdirs.macos.MacOS
   :members:
   :show-inheritance:
   :no-index:

Windows
-------

On Windows, ``platformdirs`` uses the Shell Folder APIs to resolve directories.
See `Microsoft's Known Folder documentation
<https://docs.microsoft.com/en-us/windows/win32/shell/known-folders>`_ for background.

Key behaviors:

- ``appauthor`` adds a parent directory: ``AppData\Local\<Author>\<App>``
- ``roaming=True`` switches from ``AppData\Local`` to ``AppData\Roaming``,
  which syncs across machines in a Windows domain
- **OPINION**: ``user_cache_dir`` appends ``\Cache``, ``user_log_dir`` appends ``\Logs``

.. autoclass:: platformdirs.windows.Windows
   :members:
   :show-inheritance:
   :no-index:

Linux / Unix
------------

On Linux and other Unix-like systems, ``platformdirs`` follows the
`XDG Base Directory Specification <https://specifications.freedesktop.org/basedir/latest/>`_.

XDG environment variables override the defaults:

- ``XDG_DATA_HOME`` (default ``~/.local/share``)
- ``XDG_CONFIG_HOME`` (default ``~/.config``)
- ``XDG_CACHE_HOME`` (default ``~/.cache``)
- ``XDG_STATE_HOME`` (default ``~/.local/state``)
- ``XDG_RUNTIME_DIR`` (default ``/run/user/<uid>``)
- ``XDG_DATA_DIRS`` (default ``/usr/local/share:/usr/share``)
- ``XDG_CONFIG_DIRS`` (default ``/etc/xdg``)

When ``multipath=True``, ``site_data_dir`` and ``site_config_dir`` return all paths from
the corresponding ``XDG_*_DIRS`` variable, joined by ``:``.

**FreeBSD / OpenBSD / NetBSD**: ``user_runtime_dir`` falls back to ``/var/run/user/<uid>`` or
``/tmp/runtime-<uid>`` when ``/run/user/<uid>`` does not exist.

.. autoclass:: platformdirs.unix.Unix
   :members:
   :show-inheritance:
   :no-index:

Android
-------

On Android, ``platformdirs`` uses the app's private storage directories. The app's package
folder (e.g. ``/data/data/com.example.app``) is detected via ``python-for-android`` or
``pyjnius``.

Media directories (documents, downloads, pictures, videos, music) point to shared external
storage under ``/storage/emulated/0/``.

**Shell environments**: Android apps like `Termux <https://termux.dev>`_ and Pydroid that
function as Linux shells are detected by the presence of the ``SHELL`` environment variable.
In these environments, ``platformdirs`` uses the Unix/XDG backend instead, including support
for ``XDG_*`` environment variables.

.. autoclass:: platformdirs.android.Android
   :members:
   :show-inheritance:
   :no-index:
