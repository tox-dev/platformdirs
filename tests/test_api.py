import platformdirs


def test_package_metadata() -> None:
    assert hasattr(platformdirs, "__version__")
    assert hasattr(platformdirs, "__version_info__")


def test_method_result_is_str(func: str) -> None:
    method = getattr(platformdirs, func)
    result = method("MyApp", "MyCompany")
    assert isinstance(result, str)


def test_property_result_is_str(func: str) -> None:
    dirs = platformdirs.PlatformDirs("MyApp", "MyCompany", version="1.0")
    result = getattr(dirs, func)
    assert isinstance(result, str)
