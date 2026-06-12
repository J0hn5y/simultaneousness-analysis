import importlib


def test_main_is_not_exposed_from_package():
    package = importlib.import_module("simultaneousness_analysis")
    assert not hasattr(package, "main"), "Package should not expose 'main'"


def test_meta_is_exposed_from_package():
    package = importlib.import_module("simultaneousness_analysis")
    assert hasattr(package, "meta"), "Package should expose 'meta'"

    from simultaneousness_analysis import meta

    assert meta is package.meta


def test_retrieve_data_is_exposed_from_package():
    package = importlib.import_module("simultaneousness_analysis")
    assert hasattr(package, "retrieve_data"), "Package should expose 'retrieve_data'"

    from simultaneousness_analysis import retrieve_data

    assert callable(retrieve_data)
    assert retrieve_data is package.retrieve_data
