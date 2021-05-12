import sys
import unittest
import appdir

if sys.version_info[0] < 3:
    STRING_TYPE = basestring
else:
    STRING_TYPE = str


class Test_AppDir(unittest.TestCase):
    def test_metadata(self):
        self.assertTrue(hasattr(appdir, "__version__"))
        self.assertTrue(hasattr(appdir, "__version_info__"))

    def test_helpers(self):
        self.assertIsInstance(
            appdir.user_data_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            appdir.site_data_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            appdir.user_cache_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            appdir.user_state_dir('MyApp', 'MyCompany'), STRING_TYPE)
        self.assertIsInstance(
            appdir.user_log_dir('MyApp', 'MyCompany'), STRING_TYPE)

    def test_dirs(self):
        dirs = appdir.AppDirs('MyApp', 'MyCompany', version='1.0')
        self.assertIsInstance(dirs.user_data_dir, STRING_TYPE)
        self.assertIsInstance(dirs.site_data_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_cache_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_state_dir, STRING_TYPE)
        self.assertIsInstance(dirs.user_log_dir, STRING_TYPE)

if __name__ == "__main__":
    unittest.main()
