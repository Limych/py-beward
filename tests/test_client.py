"""Test test_client."""

from blueprint_client.client import Client


async def test_get_data(test_client: Client, test_data):
    """Test get_data."""
    assert test_client.get_data() == test_data

    assert await test_client.async_get_data() == test_data


async def test_change_something(test_client: Client):
    """Test change_something."""
    assert test_client.something is None

    test_client.change_something(True)
    #
    assert test_client.something is True

    await test_client.async_change_something(False)
    #
    assert test_client.something is False
