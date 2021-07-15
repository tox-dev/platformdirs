import sys

import appdirs

import platformdirs


def test_metadata():
    assert hasattr(platformdirs, "__version__")
    assert hasattr(platformdirs, "__version_info__")


def test_helpers():
    assert isinstance(platformdirs.user_data_dir("MyApp", "MyCompany"), str)
    assert isinstance(platformdirs.site_data_dir("MyApp", "MyCompany"), str)
    assert isinstance(platformdirs.user_cache_dir("MyApp", "MyCompany"), str)
    assert isinstance(platformdirs.user_state_dir("MyApp", "MyCompany"), str)
    assert isinstance(platformdirs.user_log_dir("MyApp", "MyCompany"), str)


def test_dirs():
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    assert isinstance(dirs.user_data_dir, str)
    assert isinstance(dirs.site_data_dir, str)
    assert isinstance(dirs.user_cache_dir, str)
    assert isinstance(dirs.user_state_dir, str)
    assert isinstance(dirs.user_log_dir, str)


def test_backward_compatibility_basic():
    assert platformdirs.user_data_dir() == appdirs.user_data_dir()
    assert platformdirs.site_data_dir() == appdirs.site_data_dir()
    assert platformdirs.user_config_dir() == appdirs.user_config_dir()
    assert platformdirs.site_config_dir() == appdirs.site_config_dir()
    assert platformdirs.user_cache_dir() == appdirs.user_cache_dir()
    assert platformdirs.user_state_dir() == appdirs.user_state_dir()

    # Calling `appdirs.user_log_dir` without appname produces NoneType error on macOS
    if sys.platform == "darwin":
        assert isinstance(platformdirs.user_log_dir(), str)
    else:
        assert platformdirs.user_log_dir() == appdirs.user_log_dir()


def test_backward_compatibility_appname():
    kwargs = {"appname": "foo"}
    assert platformdirs.user_data_dir(**kwargs) == appdirs.user_data_dir(**kwargs)
    assert platformdirs.site_data_dir(**kwargs) == appdirs.site_data_dir(**kwargs)
    assert platformdirs.user_config_dir(**kwargs) == appdirs.user_config_dir(**kwargs)
    assert platformdirs.site_config_dir(**kwargs) == appdirs.site_config_dir(**kwargs)
    assert platformdirs.user_cache_dir(**kwargs) == appdirs.user_cache_dir(**kwargs)
    assert platformdirs.user_state_dir(**kwargs) == appdirs.user_state_dir(**kwargs)
    assert platformdirs.user_log_dir(**kwargs) == appdirs.user_log_dir(**kwargs)


def test_backward_compatibility_appname_appauthor():
    kwargs = {"appname": "foo", "appauthor": "bar"}
    assert platformdirs.user_data_dir(**kwargs) == appdirs.user_data_dir(**kwargs)
    assert platformdirs.site_data_dir(**kwargs) == appdirs.site_data_dir(**kwargs)
    assert platformdirs.user_config_dir(**kwargs) == appdirs.user_config_dir(**kwargs)
    assert platformdirs.site_config_dir(**kwargs) == appdirs.site_config_dir(**kwargs)
    assert platformdirs.user_cache_dir(**kwargs) == appdirs.user_cache_dir(**kwargs)
    assert platformdirs.user_state_dir(**kwargs) == appdirs.user_state_dir(**kwargs)
    assert platformdirs.user_log_dir(**kwargs) == appdirs.user_log_dir(**kwargs)


def test_backward_compatibility_appname_appauthor_version():
    kwargs = {"appname": "foo", "appauthor": "bar", "version": "v1.0"}
    assert platformdirs.user_data_dir(**kwargs) == appdirs.user_data_dir(**kwargs)
    assert platformdirs.site_data_dir(**kwargs) == appdirs.site_data_dir(**kwargs)
    assert platformdirs.user_config_dir(**kwargs) == appdirs.user_config_dir(**kwargs)
    assert platformdirs.site_config_dir(**kwargs) == appdirs.site_config_dir(**kwargs)
    assert platformdirs.user_cache_dir(**kwargs) == appdirs.user_cache_dir(**kwargs)
    assert platformdirs.user_state_dir(**kwargs) == appdirs.user_state_dir(**kwargs)
    assert platformdirs.user_log_dir(**kwargs) == appdirs.user_log_dir(**kwargs)
