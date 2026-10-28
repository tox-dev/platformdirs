Raise ``FileNotFoundError`` from the ``place_*_file`` methods when the user directory is on a missing Windows drive or
network share, rather than recursing until ``RecursionError``.
