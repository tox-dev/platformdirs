platformdirs
============

``platformdirs`` is a Python library for determining platform-specific system directories.
Whether you need user data, configuration, cache, or log directories, ``platformdirs`` resolves the
correct location for macOS, Windows, Linux/Unix, and Android.

Features
--------

- **Auto-detects the current platform** -- works on macOS, Windows, Linux, FreeBSD, OpenBSD, and Android
- **Follows platform conventions** -- XDG Base Directory Spec on Linux, ``~/Library`` on macOS, ``AppData`` on Windows
- **XDG environment variable support** -- on both Linux and macOS
- **Returns** :class:`str` **or** :class:`~pathlib.Path` -- every directory has a ``_dir`` (str) and ``_path`` (Path) variant
- **Optional directory creation** -- set ``ensure_exists=True`` to create directories on access
- **Version isolation** -- keep multiple app versions side by side

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   api
   platforms

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
