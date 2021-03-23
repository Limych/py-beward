# pylint: disable=protected-access,redefined-outer-name
"""Unit tests package."""

import os

from .const import MOCK_HOST


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


def load_binary(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), "binary", filename)
    with open(path, "rb") as fptr:
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
