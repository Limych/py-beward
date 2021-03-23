# pylint: disable=protected-access,redefined-outer-name
"""Global fixtures for tests."""
# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)

import datetime
import json
import os

import pytest

from blueprint_client.client import Client

from tests.const import TEST_PASSWORD, TEST_USERNAME


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


def load_fixture_json(filename):
    """Load a fixture as JSON object."""
    return json.loads(load_fixture(filename))


@pytest.fixture()
def test_client():
    """Get test client fixture."""
    client = Client(TEST_USERNAME, TEST_PASSWORD)
    return client


@pytest.fixture()
def test_data():
    """Get test data fixture."""
    data = load_fixture_json("test_data.json")
    data["data"]["time"] = datetime.time()
    return data
