##############
 platformdirs
##############

``platformdirs`` is a Python library for determining platform-specific system directories. Whether you need user data,
configuration, cache, or log directories, ``platformdirs`` resolves the correct location for macOS, Windows, Linux/Unix,
and Android.

**********
 Features
**********

.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item-card:: Platform auto-detection
       :class-card: sd-border-0

       Works on macOS, Windows, Linux, FreeBSD, OpenBSD, and Android -- no configuration needed.

    .. grid-item-card:: Convention-compliant
       :class-card: sd-border-0

       XDG Base Directory Spec on Linux, ``~/Library`` on macOS, ``AppData`` on Windows.

    .. grid-item-card:: XDG variable support
       :class-card: sd-border-0

       Honors ``XDG_DATA_HOME``, ``XDG_CONFIG_HOME``, and friends on both Linux and macOS.

    .. grid-item-card:: :class:`str` or :class:`~pathlib.Path`
       :class-card: sd-border-0

       Every directory has a ``_dir`` (str) and ``_path`` (Path) variant.

    .. grid-item-card:: Auto-create directories
       :class-card: sd-border-0

       Set ``ensure_exists=True`` to create directories on first access.

    .. grid-item-card:: Version isolation
       :class-card: sd-border-0

       Keep multiple app versions side by side with the ``version`` parameter.

.. toctree::
    :maxdepth: 2
    :caption: Contents

    tutorial
    howto
    explanation
    parameters
    api
    platforms
    changelog

********************
 Indices and tables
********************

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`
