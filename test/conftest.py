def pytest_configure(config):
    config.addinivalue_line(
        "markers", "learning: mark tests as learning exercises"
    )
    config.addinivalue_line(
        "markers", "use_genuine_api: mark tests that use the genuine Notion API"
    )
