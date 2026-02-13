API
===

User directories
~~~~~~~~~~~~~~~~

These are user-specific (and, generally, user-writeable) directories.

User data directory
-------------------

.. autofunction:: platformdirs.user_data_dir
.. autofunction:: platformdirs.user_data_path

User config directory
---------------------

.. autofunction:: platformdirs.user_config_dir
.. autofunction:: platformdirs.user_config_path

Cache directory
-------------------

.. autofunction:: platformdirs.user_cache_dir
.. autofunction:: platformdirs.user_cache_path

State directory
-------------------

.. autofunction:: platformdirs.user_state_dir
.. autofunction:: platformdirs.user_state_path

Logs directory
-------------------

.. autofunction:: platformdirs.user_log_dir
.. autofunction:: platformdirs.user_log_path

User documents directory
------------------------

.. autofunction:: platformdirs.user_documents_dir
.. autofunction:: platformdirs.user_documents_path

User downloads directory
------------------------

.. autofunction:: platformdirs.user_downloads_dir
.. autofunction:: platformdirs.user_downloads_path

User pictures directory
------------------------

.. autofunction:: platformdirs.user_pictures_dir
.. autofunction:: platformdirs.user_pictures_path

User videos directory
------------------------

.. autofunction:: platformdirs.user_videos_dir
.. autofunction:: platformdirs.user_videos_path

User music directory
------------------------

.. autofunction:: platformdirs.user_music_dir
.. autofunction:: platformdirs.user_music_path

User desktop directory
------------------------

.. autofunction:: platformdirs.user_desktop_dir
.. autofunction:: platformdirs.user_desktop_path

Runtime directory
-------------------

.. autofunction:: platformdirs.user_runtime_dir
.. autofunction:: platformdirs.user_runtime_path

Shared directories
~~~~~~~~~~~~~~~~~~

These are system-wide (and, generally, read-only) directories.

Shared data directory
---------------------

.. autofunction:: platformdirs.site_data_dir
.. autofunction:: platformdirs.site_data_path

Shared config directory
-----------------------

.. autofunction:: platformdirs.site_config_dir
.. autofunction:: platformdirs.site_config_path

Shared cache directory
----------------------

.. autofunction:: platformdirs.site_cache_dir
.. autofunction:: platformdirs.site_cache_path

Shared log directory
--------------------

.. autofunction:: platformdirs.site_log_dir
.. autofunction:: platformdirs.site_log_path

Shared runtime directory
------------------------

.. autofunction:: platformdirs.site_runtime_dir
.. autofunction:: platformdirs.site_runtime_path

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
