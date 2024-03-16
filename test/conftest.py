def pytest_configure(config):
    config.addinivalue_line(
        "markers", "learning: mark tests as learning exercises"
    )
    config.addinivalue_line(
        "markers", "slow: mark tests as slow running tests"
    )
