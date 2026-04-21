"""Shared fixtures for ops/ test suite."""

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Isolated ops/data/ for each test.

    Monkeypatches OPS_DATA_DIR so storage module reads from tmp dir.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("OPS_DATA_DIR", str(data_dir))
    yield data_dir
