API
===

.. note::
   On Unix / Linux, we follow the `XDG Basedir Spec`_. The spec allows overriding
   directories with environment variables. The examples show are the default
   values, alongside the name of the environment variable that overrides them.

   See the spec itself for further details on the topic.

.. _XDG Basedir Spec: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

User directories
~~~~~~~~~~~~~~~~

These are user-specific (and, generally, user-writeable) directories.

Data directory
-------------------

.. autofunction:: platformdirs.user_data_dir

Config directory
-------------------

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

Data directory
--------------

.. autofunction:: platformdirs.site_data_dir

Config directory
----------------

.. autofunction:: platformdirs.site_config_dir
