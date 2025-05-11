def pytest_collection_modifyitems(session, config, items):
    # don't interpret `test_for_env_types()` from actual package's `util.py` as a test!
    # otherwise it screams about fixture not found or something
    items[:] = [item for item in items if item.name != "test_for_env_types"]
