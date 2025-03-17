#  Copyright (c) 2025, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

# pylint: disable=protected-access,redefined-outer-name
"""Test constants."""

from datetime import datetime, timezone

MOCK_HOST = "192.168.0.2"
MOCK_USER = "user"
MOCK_PASS = "password"  # noqa: S105

local_tz = datetime.now(timezone.utc).astimezone().tzinfo
