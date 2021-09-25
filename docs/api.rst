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
