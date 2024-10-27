"""Test test_client."""

import pytest

from blueprint_client.client import Client

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_get_data(test_client: Client, test_data):
    """Test get_data."""
    assert test_client.get_data() == test_data

    assert await test_client.async_get_data() == test_data


async def test_change_something(test_client: Client):
    """Test change_something."""
    assert test_client.something is None

    test_client.change_something(something=True)
    #
    assert test_client.something is True

    await test_client.async_change_something(something=False)
    #
    assert test_client.something is False
