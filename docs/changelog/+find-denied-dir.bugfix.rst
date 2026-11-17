Make ``find_*_file`` and ``find_*_files`` skip a directory the user cannot search, and treat a name too long for the
file system as not found, instead of raising on Python 3.13 and older.
