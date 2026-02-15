Platform details
================

``platformdirs`` auto-detects the current platform and returns the correct directory paths.
This page describes the default paths for each platform and any platform-specific behavior.

All examples below assume ``appname="SuperApp"`` and ``appauthor="Acme"`` unless stated otherwise.

User directories
~~~~~~~~~~~~~~~~

These are user-specific (and, generally, user-writeable) directories.

``user_data_dir``
^^^^^^^^^^^^^^^^^

See also: :ref:`api:User data directory`

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
^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User config directory`

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
^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User cache directory`

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
^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User state directory`

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
^^^^^^^^^^^^^^^^

See also: :ref:`api:User log directory`

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
^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User runtime directory`

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

``user_applications_dir``
^^^^^^^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User applications directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.local/share/applications``
   * - macOS
     - ``~/Applications``
   * - Windows
     - ``C:\Users\<User>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs``
   * - Android
     - same as ``user_data_dir``

.. note::

   This property does not append ``appname`` or ``version``. It returns the shared
   applications directory where ``.desktop`` files (Linux), app bundles (macOS), or
   Start Menu shortcuts (Windows) are placed.

``user_bin_dir``
^^^^^^^^^^^^^^^^

See also: :ref:`api:User binary directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``~/.local/bin``
   * - macOS
     - ``~/.local/bin``
   * - Windows
     - ``C:\Users\<User>\AppData\Local\Programs``
   * - Android
     - ``/data/data/<pkg>/files/bin``

.. note::

   This property does not append ``appname`` or ``version``. It returns the directory
   where user-installed executables and scripts are placed.

``user_documents_dir``
^^^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User documents directory`

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
^^^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User downloads directory`

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
^^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User pictures directory`

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
^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User videos directory`

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
^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User music directory`

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
^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:User desktop directory`

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

Shared directories
~~~~~~~~~~~~~~~~~~

These are system-wide (and, generally, read-only) directories.

``site_data_dir``
^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared data directory`

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
^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared config directory`

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
^^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared cache directory`

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

``site_state_dir``
^^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared state directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/var/lib/SuperApp``
   * - macOS
     - ``/Library/Application Support/SuperApp``
   * - Windows
     - ``C:\ProgramData\Acme\SuperApp``
   * - Android
     - ``/data/data/<pkg>/files/SuperApp``

``site_log_dir``
^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared log directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/var/log/SuperApp``
   * - macOS
     - ``/Library/Logs/SuperApp``
   * - Windows
     - ``C:\ProgramData\Acme\SuperApp\Logs``
   * - Android
     - ``/data/data/<pkg>/cache/SuperApp/log``

``site_runtime_dir``
^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared runtime directory`

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

``site_applications_dir``
^^^^^^^^^^^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared applications directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/usr/share/applications``
   * - macOS
     - ``/Applications``
   * - Windows
     - ``C:\ProgramData\Microsoft\Windows\Start Menu\Programs``
   * - Android
     - same as ``user_applications_dir``

.. note::

   This property does not append ``appname`` or ``version``. It returns the system-wide
   applications directory where ``.desktop`` files (Linux), app bundles (macOS), or
   Start Menu shortcuts (Windows) are installed for all users.

``site_bin_dir``
^^^^^^^^^^^^^^^^

See also: :ref:`api:Shared binary directory`

.. list-table::
   :widths: 20 80

   * - Linux
     - ``/usr/local/bin``
   * - macOS
     - ``/usr/local/bin``
   * - Windows
     - ``C:\ProgramData\bin``
   * - Android
     - Same as ``user_bin_dir``

.. note::

   This property does not append ``appname`` or ``version``. It returns the directory
   where system-wide executables and scripts are placed. On Unix/Linux, this follows
   the `FHS 3.0 <https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html>`_
   standard for locally installed software. On Windows, it mirrors the ``site_data_dir``
   pattern using ``%ProgramData%``, following the precedent set by
   `Chocolatey <https://docs.chocolatey.org/en-us/choco/setup>`_.

macOS
~~~~~

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
~~~~~~~

On Windows, ``platformdirs`` uses the Shell Folder APIs to resolve directories.
See `Microsoft's Known Folder documentation
<https://docs.microsoft.com/en-us/windows/win32/shell/known-folders>`_ for background.

Key behaviors:

- ``appauthor`` adds a parent directory: ``AppData\Local\<Author>\<App>``
- ``roaming=True`` switches from ``AppData\Local`` to ``AppData\Roaming``,
  which syncs across machines in a Windows domain
- **OPINION**: ``user_cache_dir`` appends ``\Cache``, ``user_log_dir`` appends ``\Logs``

Unlike Linux/macOS where ``XDG_*`` variables are a platform standard, Windows has no built-in
convention for overriding folder locations at the application level. To fill this gap,
``platformdirs`` checks ``WIN_PD_OVERRIDE_*`` environment variables before querying the Shell
Folder APIs. This is useful when large data (ML models, package caches) should live on a different
drive without changing the system-wide ``APPDATA`` / ``LOCALAPPDATA`` variables that other
applications rely on.

The override variable name is ``WIN_PD_OVERRIDE_`` followed by the CSIDL suffix:

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Environment variable
     - Overrides
   * - ``WIN_PD_OVERRIDE_APPDATA``
     - Roaming user data (``AppData\Roaming``)
   * - ``WIN_PD_OVERRIDE_LOCAL_APPDATA``
     - Local user data, config, cache, state (``AppData\Local``)
   * - ``WIN_PD_OVERRIDE_COMMON_APPDATA``
     - Site-wide data, config, cache, state (``ProgramData``)
   * - ``WIN_PD_OVERRIDE_PERSONAL``
     - Documents
   * - ``WIN_PD_OVERRIDE_DOWNLOADS``
     - Downloads
   * - ``WIN_PD_OVERRIDE_MYPICTURES``
     - Pictures
   * - ``WIN_PD_OVERRIDE_MYVIDEO``
     - Videos
   * - ``WIN_PD_OVERRIDE_MYMUSIC``
     - Music
   * - ``WIN_PD_OVERRIDE_DESKTOPDIRECTORY``
     - Desktop
   * - ``WIN_PD_OVERRIDE_PROGRAMS``
     - Applications (Start Menu Programs)

Example — redirect cache to a separate drive:

.. code-block:: python

   import os
   os.environ["WIN_PD_OVERRIDE_LOCAL_APPDATA"] = r"X:\appdata"

   import platformdirs
   print(platformdirs.user_cache_dir("MyApp", "Acme"))
   # X:\appdata\Acme\MyApp\Cache

Empty or whitespace-only values are ignored and the normal resolution applies.

.. note:: **Windows Store Python (MSIX)**

   Python installed from the Microsoft Store runs in a sandboxed (AppContainer) environment.
   Windows silently redirects writes under ``AppData`` to a per-package private location, e.g.
   ``AppData\Local\Packages\PythonSoftwareFoundation.Python.3.X_<hash>\LocalCache\Local\...``.

   ``platformdirs`` returns the logical ``AppData`` path, which is correct for code running inside
   the same sandbox. However, if you pass these paths to external processes (subprocesses, other
   applications), those processes may not see files created at the logical path because they run
   outside the sandbox.

   To obtain the real on-disk path for sharing with external processes, call
   :func:`os.path.realpath` on the path **after** the file or directory has been created:

   .. code-block:: python

      import os
      import platformdirs

      data_dir = platformdirs.user_data_dir(appname="MyApp", appauthor="Acme", ensure_exists=True)
      real_dir = os.path.realpath(data_dir)

   This is a Windows design limitation, not a ``platformdirs`` bug. See `Microsoft's MSIX
   documentation
   <https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes>`_
   for details on filesystem virtualization.

.. autoclass:: platformdirs.windows.Windows
   :members:
   :show-inheritance:
   :no-index:

Linux / Unix
~~~~~~~~~~~~

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

.. note:: **Running as root**

   When ``use_site_for_root=True`` is passed and the process is running as root (uid 0),
   ``user_*_dir`` calls are redirected to their ``site_*_dir`` equivalents. This is useful for
   system daemons and installers that should write to system-wide directories rather than
   ``/root/.local/...``. XDG user environment variables (e.g. ``XDG_DATA_HOME``) are bypassed
   when the redirect is active, since they are typically inherited from the calling user via
   ``sudo`` and would defeat the purpose. The parameter is accepted on all platforms but only
   has an effect on Unix.

.. autoclass:: platformdirs.unix.Unix
   :members:
   :show-inheritance:
   :no-index:

Android
~~~~~~~

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
