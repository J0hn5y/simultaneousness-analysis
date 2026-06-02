import importlib


def test_main_is_exposed_from_package():
    package = importlib.import_module("simultaneousness_analysis")
    assert hasattr(package, "main"), "Package should expose 'main'"

    from simultaneousness_analysis import main
    assert main is package.main


def test_meta_is_exposed_from_package():
    package = importlib.import_module("simultaneousness_analysis")
    assert hasattr(package, "meta"), "Package should expose 'meta'"

    from simultaneousness_analysis import meta
    assert meta is package.meta
