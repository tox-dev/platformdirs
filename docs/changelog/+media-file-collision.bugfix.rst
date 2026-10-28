Raise ``FileExistsError`` when ``ensure_exists`` encounters a regular file or a symlink to one at a configured media
directory, while continuing to return dangling media symlinks unchanged.
