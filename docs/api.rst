API
===

User directories
~~~~~~~~~~~~~~~~

These are user-specific (and, generally, user-writeable) directories.

User data directory
-------------------

See also: :ref:`platforms:``user_data_dir```

.. autofunction:: platformdirs.user_data_dir
.. autofunction:: platformdirs.user_data_path

User config directory
---------------------

See also: :ref:`platforms:``user_config_dir```


.. autofunction:: platformdirs.user_config_dir
.. autofunction:: platformdirs.user_config_path

User cache directory
--------------------

See also: :ref:`platforms:``user_cache_dir```


.. autofunction:: platformdirs.user_cache_dir
.. autofunction:: platformdirs.user_cache_path

User state directory
--------------------

See also: :ref:`platforms:``user_state_dir```


.. autofunction:: platformdirs.user_state_dir
.. autofunction:: platformdirs.user_state_path

User log directory
------------------

See also: :ref:`platforms:``user_log_dir```


.. autofunction:: platformdirs.user_log_dir
.. autofunction:: platformdirs.user_log_path

User runtime directory
----------------------

See also: :ref:`platforms:``user_runtime_dir```


.. autofunction:: platformdirs.user_runtime_dir
.. autofunction:: platformdirs.user_runtime_path

User applications directory
----------------------------

See also: :ref:`platforms:``user_applications_dir```


Where application launchers and shortcuts are registered — ``.desktop`` files on Linux,
the per-user ``Applications`` folder on macOS, or Start Menu shortcuts on Windows.
These entries make applications discoverable in menus and app launchers.

.. autofunction:: platformdirs.user_applications_dir
.. autofunction:: platformdirs.user_applications_path

User binary directory
----------------------

See also: :ref:`platforms:``user_bin_dir```


Where user-installed executables and scripts are placed so they appear on ``$PATH`` —
``~/.local/bin`` on Linux/macOS or ``%LOCALAPPDATA%\Programs`` on Windows.

.. autofunction:: platformdirs.user_bin_dir
.. autofunction:: platformdirs.user_bin_path

User documents directory
------------------------

See also: :ref:`platforms:``user_documents_dir```


.. autofunction:: platformdirs.user_documents_dir
.. autofunction:: platformdirs.user_documents_path

User downloads directory
------------------------

See also: :ref:`platforms:``user_downloads_dir```


.. autofunction:: platformdirs.user_downloads_dir
.. autofunction:: platformdirs.user_downloads_path

User pictures directory
------------------------

See also: :ref:`platforms:``user_pictures_dir```


.. autofunction:: platformdirs.user_pictures_dir
.. autofunction:: platformdirs.user_pictures_path

User videos directory
------------------------

See also: :ref:`platforms:``user_videos_dir```


.. autofunction:: platformdirs.user_videos_dir
.. autofunction:: platformdirs.user_videos_path

User music directory
------------------------

See also: :ref:`platforms:``user_music_dir```


.. autofunction:: platformdirs.user_music_dir
.. autofunction:: platformdirs.user_music_path

User desktop directory
------------------------

See also: :ref:`platforms:``user_desktop_dir```


.. autofunction:: platformdirs.user_desktop_dir
.. autofunction:: platformdirs.user_desktop_path

Shared directories
~~~~~~~~~~~~~~~~~~

These are system-wide (and, generally, read-only) directories.

Shared data directory
---------------------

See also: :ref:`platforms:``site_data_dir```


.. autofunction:: platformdirs.site_data_dir
.. autofunction:: platformdirs.site_data_path

Shared config directory
-----------------------

See also: :ref:`platforms:``site_config_dir```


.. autofunction:: platformdirs.site_config_dir
.. autofunction:: platformdirs.site_config_path

Shared cache directory
----------------------

See also: :ref:`platforms:``site_cache_dir```


.. autofunction:: platformdirs.site_cache_dir
.. autofunction:: platformdirs.site_cache_path

Shared state directory
----------------------

See also: :ref:`platforms:``site_state_dir```


.. autofunction:: platformdirs.site_state_dir
.. autofunction:: platformdirs.site_state_path

Shared log directory
--------------------

See also: :ref:`platforms:``site_log_dir```


.. autofunction:: platformdirs.site_log_dir
.. autofunction:: platformdirs.site_log_path

Shared runtime directory
------------------------

See also: :ref:`platforms:``site_runtime_dir```


.. autofunction:: platformdirs.site_runtime_dir
.. autofunction:: platformdirs.site_runtime_path

Shared applications directory
------------------------------

See also: :ref:`platforms:``site_applications_dir```


Where application launchers and shortcuts are registered system-wide — ``.desktop`` files in
``/usr/share/applications`` on Linux, ``/Applications`` on macOS, or the All Users Start Menu
on Windows. Applications installed here are available to all users.

.. autofunction:: platformdirs.site_applications_dir
.. autofunction:: platformdirs.site_applications_path

Shared binary directory
------------------------

See also: :ref:`platforms:``site_bin_dir```


Where system-wide executables and scripts are placed — ``/usr/local/bin`` on Linux/macOS
or ``%ProgramData%\bin`` on Windows. Executables here are available to all users.

.. autofunction:: platformdirs.site_bin_dir
.. autofunction:: platformdirs.site_bin_path

Platforms
~~~~~~~~~

ABC
---
.. autoclass:: platformdirs.api.PlatformDirsABC
   :members:
   :special-members: __init__

PlatformDirs
------------

.. autoclass:: platformdirs.PlatformDirs
   :members:
   :show-inheritance:

Android
-------
.. autoclass:: platformdirs.android.Android
   :members:
   :show-inheritance:

macOS
-----
.. autoclass:: platformdirs.macos.MacOS
   :members:
   :show-inheritance:

Unix (Linux)
------------
.. autoclass:: platformdirs.unix.Unix
   :members:
   :show-inheritance:

Windows
-------
.. autoclass:: platformdirs.windows.Windows
   :members:
   :show-inheritance:
