# pylint: disable=protected-access,redefined-outer-name
"""Test common fixtures."""

import threading

import pytest

from beward import BewardGeneric

from tests import MOCK_HOST
from tests.const import MOCK_PASS, MOCK_USER

INSTANCES = []


@pytest.fixture(autouse=True)
def verify_cleanup():
    """Verify that the test has cleaned up resources correctly."""
    threads_before = frozenset(threading.enumerate())

    yield

    if len(INSTANCES) >= 2:
        count = len(INSTANCES)
        for inst in INSTANCES:
            inst.stop()
        pytest.exit(f"Detected non stopped instances ({count}), aborting test run")

    threads = frozenset(threading.enumerate()) - threads_before
    assert not threads


@pytest.fixture
def beward() -> BewardGeneric:
    """Make test Beward instance."""
    return BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)
