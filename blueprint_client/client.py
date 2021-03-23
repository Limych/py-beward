"""Client."""

import datetime
import logging

from .const import VERSION

_LOGGER = logging.getLogger(__name__)


class Client:
    """Client class."""

    def __init__(self, username, password):
        """Init."""
        _LOGGER.info("Blueprint sample client. v%s", VERSION)

        self.username = username
        self.password = password
        self.something = None

    def get_data(self):
        """Return sample data."""
        data = {
            "username": self.username,
            "password": self.password,
            "data": {
                "time": datetime.time(),
                "static": "Some sample static text.",
                "bool_on": True,
                "bool_off": False,
                "none": None,
            },
        }
        return data

    async def async_get_data(self):
        """Return sample data."""
        return self.get_data()

    def change_something(self, something: bool = None):
        """Change something."""
        self.something = something

    async def async_change_something(self, something: bool = None):
        """Change something."""
        self.something = something
