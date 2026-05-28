##################
 Platform details
##################

``platformdirs`` auto-detects the current platform and returns the correct directory paths. This page describes the
default paths for each platform and any platform-specific behavior.

All examples below assume ``appname="SuperApp"`` and ``appauthor="Acme"`` unless stated otherwise.

******************
 User directories
******************

These are user-specific (and, generally, user-writeable) directories.

``user_data_dir``
=================

See also: :ref:`api:User data directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.local/share/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/files/SuperApp``

``user_config_dir``
===================

See also: :ref:`api:User config directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.config/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/shared_prefs/SuperApp``

``user_cache_dir``
==================

See also: :ref:`api:User cache directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.cache/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Caches/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Acme\SuperApp\Cache``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp``

``user_state_dir``
==================

See also: :ref:`api:User state directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.local/state/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/files/SuperApp``

``user_log_dir``
================

See also: :ref:`api:User log directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.local/state/SuperApp/log``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Logs/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Acme\SuperApp\Logs``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp/log``

``user_runtime_dir``
====================

See also: :ref:`api:User runtime directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/run/user/<uid>/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Caches/TemporaryItems/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Temp\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp/tmp``

``user_applications_dir``
=========================

See also: :ref:`api:User applications directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.local/share/applications``

    .. tab-item:: macOS
       :sync: macos

       ``~/Applications``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs``

    .. tab-item:: Android
       :sync: android

       Same as ``user_data_dir``

.. note::

    This property does not append ``appname`` or ``version``. It returns the shared applications directory where
    ``.desktop`` files (Linux), app bundles (macOS), or Start Menu shortcuts (Windows) are placed.

``user_bin_dir``
================

See also: :ref:`api:User binary directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/.local/bin``

    .. tab-item:: macOS
       :sync: macos

       ``~/.local/bin``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Programs``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/files/bin``

.. note::

    This property does not append ``appname`` or ``version``. It returns the directory where user-installed executables
    and scripts are placed.

``user_documents_dir``
======================

See also: :ref:`api:User documents directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Documents``

    .. tab-item:: macOS
       :sync: macos

       ``~/Documents``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Documents``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Documents``

``user_downloads_dir``
======================

See also: :ref:`api:User downloads directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Downloads``

    .. tab-item:: macOS
       :sync: macos

       ``~/Downloads``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Downloads``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Downloads``

``user_pictures_dir``
=====================

See also: :ref:`api:User pictures directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Pictures``

    .. tab-item:: macOS
       :sync: macos

       ``~/Pictures``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Pictures``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Pictures``

``user_videos_dir``
===================

See also: :ref:`api:User videos directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Videos``

    .. tab-item:: macOS
       :sync: macos

       ``~/Movies``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Videos``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/DCIM/Camera``

``user_music_dir``
==================

See also: :ref:`api:User music directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Music``

    .. tab-item:: macOS
       :sync: macos

       ``~/Music``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Music``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Music``

``user_desktop_dir``
====================

See also: :ref:`api:User desktop directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Desktop``

    .. tab-item:: macOS
       :sync: macos

       ``~/Desktop``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Desktop``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Desktop``

``user_projects_dir``
=====================

See also: :ref:`api:User projects directory`

Defined by `$XDG_PROJECTS_DIR
<https://gitlab.freedesktop.org/xdg/xdg-user-dirs/-/commit/217cae71c620ed2b3ed2936256ece68defccc6ab>`_ (recently added
to xdg-user-dirs).

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Projects`` (from ``$XDG_PROJECTS_DIR`` if set, else ``$XDG_PROJECTS_DIR`` entry in
       ``user-dirs.dirs``, else ``~/Projects``)

    .. tab-item:: macOS
       :sync: macos

       ``~/Projects``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\Projects``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Projects``

``user_publicshare_dir``
========================

See also: :ref:`api:User public share directory`

Defined by `$XDG_PUBLICSHARE_DIR <https://www.freedesktop.org/wiki/Software/xdg-user-dirs/>`_.

On Windows, this is the machine-wide ``C:\Users\Public`` (``%PUBLIC%``), shared across all local accounts — not a
per-user directory. See `FOLDERID_Public <https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid>`_.

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Public`` (from ``$XDG_PUBLICSHARE_DIR`` if set, else ``$XDG_PUBLICSHARE_DIR`` entry in
       ``user-dirs.dirs``, else ``~/Public``)

    .. tab-item:: macOS
       :sync: macos

       ``~/Public``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\Public`` (``%PUBLIC%``)

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Public``

``user_templates_dir``
======================

See also: :ref:`api:User templates directory`

Defined by `$XDG_TEMPLATES_DIR <https://www.freedesktop.org/wiki/Software/xdg-user-dirs/>`_. macOS has no
platform-defined templates directory; ``~/Templates`` is returned as a pragmatic fallback. On Windows, see
`FOLDERID_Templates <https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid>`_.

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``~/Templates`` (from ``$XDG_TEMPLATES_DIR`` if set, else ``$XDG_TEMPLATES_DIR`` entry in
       ``user-dirs.dirs``, else ``~/Templates``)

    .. tab-item:: macOS
       :sync: macos

       ``~/Templates`` (pragmatic fallback; macOS has no native templates directory)

    .. tab-item:: Windows
       :sync: windows

       ``%APPDATA%\Microsoft\Windows\Templates``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/Templates``

``user_fonts_dir``
==================

See also: :ref:`api:User fonts directory`

Derived from ``$XDG_DATA_HOME/fonts`` on Linux (no dedicated env var). See the `XDG Base Directory Specification
<https://specifications.freedesktop.org/basedir/latest/>`_. On Windows, uses the per-user font location added in Windows
10.

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``$XDG_DATA_HOME/fonts`` (default ``~/.local/share/fonts``)

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Fonts``

    .. tab-item:: Windows
       :sync: windows

       ``%LOCALAPPDATA%\Microsoft\Windows\Fonts``

    .. tab-item:: Android
       :sync: android

       ``/storage/emulated/0/fonts``

``user_preference_dir``
=======================

See also: :ref:`api:User preference directory`

On macOS, ``~/Library/Preferences`` is distinct from ``~/Library/Application Support`` (``user_config_dir``). See
`Apple's File System Programming Guide
<https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html>`_.
On all other platforms, this aliases ``user_config_dir``.

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       Same as ``user_config_dir`` (``$XDG_CONFIG_HOME`` or ``~/.config/AppName``)

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Preferences/AppName`` (distinct from ``~/Library/Application Support``)

    .. tab-item:: Windows
       :sync: windows

       Same as ``user_config_dir`` (``%APPDATA%\AppName``)

    .. tab-item:: Android
       :sync: android

       Same as ``user_config_dir``

********************
 Shared directories
********************

These are system-wide (and, generally, read-only) directories.

``site_data_dir``
=================

See also: :ref:`api:Shared data directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/usr/local/share/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/files/SuperApp``

``site_config_dir``
===================

See also: :ref:`api:Shared config directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/etc/xdg/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/shared_prefs/SuperApp``

``site_cache_dir``
==================

See also: :ref:`api:Shared cache directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/var/cache/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``/Library/Caches/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Acme\SuperApp\Cache``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp``

``site_state_dir``
==================

See also: :ref:`api:Shared state directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/var/lib/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``/Library/Application Support/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/files/SuperApp``

``site_log_dir``
================

See also: :ref:`api:Shared log directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/var/log/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``/Library/Logs/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Acme\SuperApp\Logs``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp/log``

``site_runtime_dir``
====================

See also: :ref:`api:Shared runtime directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/run/SuperApp``

    .. tab-item:: macOS
       :sync: macos

       ``~/Library/Caches/TemporaryItems/SuperApp``

    .. tab-item:: Windows
       :sync: windows

       ``C:\Users\<User>\AppData\Local\Temp\Acme\SuperApp``

    .. tab-item:: Android
       :sync: android

       ``/data/data/<pkg>/cache/SuperApp/tmp``

``site_applications_dir``
=========================

See also: :ref:`api:Shared applications directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/usr/share/applications``

    .. tab-item:: macOS
       :sync: macos

       ``/Applications``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\Microsoft\Windows\Start Menu\Programs``

    .. tab-item:: Android
       :sync: android

       Same as ``user_applications_dir``

.. note::

    This property does not append ``appname`` or ``version``. It returns the system-wide applications directory where
    ``.desktop`` files (Linux), app bundles (macOS), or Start Menu shortcuts (Windows) are installed for all users.

``site_bin_dir``
================

See also: :ref:`api:Shared binary directory`

.. tab-set::

    .. tab-item:: Linux
       :sync: linux

       ``/usr/local/bin``

    .. tab-item:: macOS
       :sync: macos

       ``/usr/local/bin``

    .. tab-item:: Windows
       :sync: windows

       ``C:\ProgramData\bin``

    .. tab-item:: Android
       :sync: android

       Same as ``user_bin_dir``

.. note::

    This property does not append ``appname`` or ``version``. It returns the directory where system-wide executables and
    scripts are placed. On Unix/Linux, this follows the `FHS 3.0
    <https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html>`_ standard for locally installed software. On Windows,
    it mirrors the ``site_data_dir`` pattern using ``%ProgramData%``, following the precedent set by `Chocolatey
    <https://docs.chocolatey.org/en-us/choco/setup>`_.

.. seealso::

    For platform-specific conventions and behavior details, see :doc:`explanation`.
