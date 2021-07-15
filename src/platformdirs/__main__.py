from platformdirs import PlatformDirs, __version__


def main() -> None:
    app_name = "MyApp"
    app_author = "MyCompany"

    props = (
        "user_data_dir",
        "user_config_dir",
        "user_cache_dir",
        "user_state_dir",
        "user_log_dir",
        "site_data_dir",
        "site_config_dir",
    )

    print(f"-- app dirs {__version__} --")

    print("-- app dirs (with optional 'version')")
    dirs = PlatformDirs(app_name, app_author, version="1.0")
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")

    print("\n-- app dirs (without optional 'version')")
    dirs = PlatformDirs(app_name, app_author)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")

    print("\n-- app dirs (without optional 'appauthor')")
    dirs = PlatformDirs(app_name)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")

    print("\n-- app dirs (with disabled 'appauthor')")
    dirs = PlatformDirs(app_name, appauthor=False)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")


if __name__ == "__main__":
    main()
