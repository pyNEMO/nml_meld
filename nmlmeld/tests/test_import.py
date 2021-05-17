import pytest


def test_version():
    assert hasattr(pytest, "__version__")
