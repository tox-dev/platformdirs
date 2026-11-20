Use the same Unix site runtime fallback for lookup and creation when the XDG override fails validation. With root
redirection, ``site_runtime_dir`` creates a missing ``XDG_RUNTIME_DIR`` with mode ``0700`` when ``ensure_exists=True``.
Find runtime files in valid fallbacks and in directories selected by root redirection or test isolation.
