import sys
import unittest
import platformdirs
import appdirs

if sys.version_info[0] < 3:
    STRING_TYPE = basestring
else:
    STRING_TYPE = str


class Test_PlatformDirs(unittest.TestCase):
    def test_metadata(self):
        self.assertTrue(hasattr(platformdirs, "__version__"))
        self.assertTrue(hasattr(platformdirs, "__version_info__"))

    def test_helpers(self):
        self.assertIsInstance(
            platformdirs.user_data_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            platformdirs.site_data_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            platformdirs.user_cache_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            platformdirs.user_state_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            platformdirs.user_log_dir('MyApp', 'MyCompany'), STRING_TYPE)

    def test_dirs(self):
        dirs = platformdirs.PlatformDirs('MyApp', 'MyCompany', version='1.0')
        self.assertIsInstance(dirs.user_data_dir, STRING_TYPE)
        self.assertIsInstance(dirs.site_data_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_cache_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_state_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_log_dir, STRING_TYPE)

    def test_backward_compatibility_basic(self):
        self.assertEqual(platformdirs.user_data_dir(), appdirs.user_data_dir())
        self.assertEqual(platformdirs.site_data_dir(), appdirs.site_data_dir())
        self.assertEqual(platformdirs.user_config_dir(), appdirs.user_config_dir())
        self.assertEqual(platformdirs.site_config_dir(), appdirs.site_config_dir())
        self.assertEqual(platformdirs.user_cache_dir(), appdirs.user_cache_dir())
        self.assertEqual(platformdirs.user_state_dir(), appdirs.user_state_dir())

        # Calling `appdirs.user_log_dir` without appname produces NoneType error on macOS
        if sys.platform == 'darwin':
            self.assertTrue(isinstance(platformdirs.user_log_dir(), str))
        else:
            self.assertEqual(platformdirs.user_log_dir(), appdirs.user_log_dir())

    def test_backward_compatibility_appname(self):
        kwargs = {'appname': 'foo'}
        self.assertEqual(platformdirs.user_data_dir(**kwargs), appdirs.user_data_dir(**kwargs))
        self.assertEqual(platformdirs.site_data_dir(**kwargs), appdirs.site_data_dir(**kwargs))
        self.assertEqual(platformdirs.user_config_dir(**kwargs), appdirs.user_config_dir(**kwargs))
        self.assertEqual(platformdirs.site_config_dir(**kwargs), appdirs.site_config_dir(**kwargs))
        self.assertEqual(platformdirs.user_cache_dir(**kwargs), appdirs.user_cache_dir(**kwargs))
        self.assertEqual(platformdirs.user_state_dir(**kwargs), appdirs.user_state_dir(**kwargs))
        self.assertEqual(platformdirs.user_log_dir(**kwargs), appdirs.user_log_dir(**kwargs))

    def test_backward_compatibility_appname_appauthor(self):
        kwargs = {'appname': 'foo', 'appauthor': 'bar'}
        self.assertEqual(platformdirs.user_data_dir(**kwargs), appdirs.user_data_dir(**kwargs))
        self.assertEqual(platformdirs.site_data_dir(**kwargs), appdirs.site_data_dir(**kwargs))
        self.assertEqual(platformdirs.user_config_dir(**kwargs), appdirs.user_config_dir(**kwargs))
        self.assertEqual(platformdirs.site_config_dir(**kwargs), appdirs.site_config_dir(**kwargs))
        self.assertEqual(platformdirs.user_cache_dir(**kwargs), appdirs.user_cache_dir(**kwargs))
        self.assertEqual(platformdirs.user_state_dir(**kwargs), appdirs.user_state_dir(**kwargs))
        self.assertEqual(platformdirs.user_log_dir(**kwargs), appdirs.user_log_dir(**kwargs))

    def test_backward_compatibility_appname_appauthor_version(self):
        kwargs = {'appname': 'foo', 'appauthor': 'bar', 'version': 'v1.0'}
        self.assertEqual(platformdirs.user_data_dir(**kwargs), appdirs.user_data_dir(**kwargs))
        self.assertEqual(platformdirs.site_data_dir(**kwargs), appdirs.site_data_dir(**kwargs))
        self.assertEqual(platformdirs.user_config_dir(**kwargs), appdirs.user_config_dir(**kwargs))
        self.assertEqual(platformdirs.site_config_dir(**kwargs), appdirs.site_config_dir(**kwargs))
        self.assertEqual(platformdirs.user_cache_dir(**kwargs), appdirs.user_cache_dir(**kwargs))
        self.assertEqual(platformdirs.user_state_dir(**kwargs), appdirs.user_state_dir(**kwargs))
        self.assertEqual(platformdirs.user_log_dir(**kwargs), appdirs.user_log_dir(**kwargs))

if __name__ == "__main__":
    unittest.main()
