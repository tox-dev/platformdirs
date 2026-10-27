Accept ``ensure_exists`` in :func:`~platformdirs.user_documents_dir`, :func:`~platformdirs.user_documents_path` and
the other media directory functions, so they create a media directory set through ``XDG_*_DIR`` or ``user-dirs.dirs``
the way :class:`~platformdirs.PlatformDirs` with ``ensure_exists=True`` does.
