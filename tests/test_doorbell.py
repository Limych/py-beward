"""Test to verify that Beward library works."""

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

from datetime import datetime
import os
from unittest import TestCase

from beward import BewardDoorbell
from beward.const import ALARM_SENSOR
import requests_mock

MOCK_HOST = "192.168.0.2"
MOCK_USER = "user"
MOCK_PASS = "pass"


def load_binary(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), "binary", filename)
    with open(path, "rb") as fptr:
        return fptr.read()


def function_url(function, host=MOCK_HOST):
    """Make function URL."""
    return "http://" + host + ":80/cgi-bin/" + function + "_cgi"


class TestBewardDoorbell(TestCase):
    """Test case for BewardDoorbell class."""

    @requests_mock.Mocker()
    def test__handle_alarm(self, mock):
        """Test that handle alarms."""
        bwd = BewardDoorbell(MOCK_HOST, MOCK_USER, MOCK_PASS)
        image = load_binary("image.jpg")

        # Check initial state
        self.assertIsNone(bwd.last_motion_timestamp)
        self.assertIsNone(bwd.last_motion_image)

        ts1 = datetime.now()
        mock.register_uri(
            "get",
            function_url("images"),
            content=image,
            headers={"Content-Type": "image/jpeg"},
        )
        bwd._handle_alarm(ts1, ALARM_SENSOR, True)
        self.assertEqual(ts1, bwd.last_ding_timestamp)
        self.assertEqual(image, bwd.last_ding_image)
