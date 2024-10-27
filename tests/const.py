# pylint: disable=protected-access,redefined-outer-name
"""Test constants."""

from datetime import UTC, datetime

MOCK_HOST = "192.168.0.2"
MOCK_USER = "user"
MOCK_PASS = "password"  # noqa: S105

local_tz = datetime.now(UTC).astimezone().tzinfo
