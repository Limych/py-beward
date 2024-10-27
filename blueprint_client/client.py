"""Client."""

import datetime
import logging

from .const import STARTUP_MESSAGE

_LOGGER = logging.getLogger(__name__)
#
_LOGGER.info(STARTUP_MESSAGE)


class Client:
    """Client class."""

    def __init__(self, username: str, password: str) -> None:
        """Init."""
        self.username = username
        self.password = password
        self.something = None

    def get_data(self) -> dict:
        """Return sample data."""
        return {
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

    async def async_get_data(self) -> dict:
        """Return sample data."""
        return self.get_data()

    def change_something(self, something: bool | None = None) -> None:
        """Change something."""
        self.something = something

    async def async_change_something(self, something: bool | None = None) -> None:
        """Change something."""
        self.something = something
