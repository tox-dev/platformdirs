from platformdirs.macos import MacOS
from platformdirs.unix import Unix

PARAMS = {
    "no_args": {},
    "app_name": {"appname": "foo"},
    "app_name_with_app_author": {"appname": "foo", "appauthor": "bar"},
    "app_name_author_version": {
        "appname": "foo",
        "appauthor": "bar",
        "version": "v1.0",
    },
    "app_name_author_version_false_opinion": {
        "appname": "foo",
        "appauthor": "bar",
        "version": "v1.0",
        "opinion": False,
    },
}

OS = {
    "darwin": MacOS,
    "unix": Unix,
}
