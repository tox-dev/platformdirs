Apply the ``XDG_RUNTIME_DIR`` check of the Unix :func:`~platformdirs.user_runtime_dir` to the macOS runtime directories
and to the Unix :func:`~platformdirs.site_runtime_dir`, so they no longer use a directory that is a symlink, owned by
another user or not mode ``0700``.
