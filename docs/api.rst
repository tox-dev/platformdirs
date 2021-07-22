API
===

User directories
~~~~~~~~~~~~~~~~

These are user-specific (and, generally, user-writeable) directories.

User data directory
-------------------

.. autofunction:: platformdirs.user_data_dir

User config directory
---------------------

.. autofunction:: platformdirs.user_config_dir

Cache directory
-------------------

.. autofunction:: platformdirs.user_cache_dir

State directory
-------------------

.. autofunction:: platformdirs.user_state_dir

Logs directory
-------------------

.. autofunction:: platformdirs.user_log_dir

Shared directories
~~~~~~~~~~~~~~~~~~

These are system-wide (and, generally, read-only) directories.

Shared data directory
---------------------

.. autofunction:: platformdirs.site_data_dir

Shared config directory
-----------------------

.. autofunction:: platformdirs.site_config_dir

Platforms
~~~~~~~~~

ABC
---
.. autoclass:: platformdirs.api.PlatformDirsABC
   :members:
   :special-members: __init__

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
