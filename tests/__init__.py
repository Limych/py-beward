# pylint: disable=protected-access,redefined-outer-name
"""Unit tests package."""

from pathlib import Path

from .const import MOCK_HOST


def load_fixture(filename):
    """Load a fixture."""
    path = Path(__file__).parent / "fixtures" / filename
    with path.open(encoding="utf-8") as fptr:
        return fptr.read()


def load_binary(filename):
    """Load a binary data."""
    path = Path(__file__).parent / "binary" / filename
    with path.open("rb") as fptr:
        return fptr.read()


def function_url(function, host=MOCK_HOST, user=None, password=None):
    """Make function URL."""
    auth = ""
    if user:
        auth = user
        if password:
            auth += ":" + password
        auth += "@"
    return "http://" + auth + host + ":80/cgi-bin/" + function + "_cgi"
