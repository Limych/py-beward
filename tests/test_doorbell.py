# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

from datetime import datetime
from unittest import TestCase

import requests_mock

from beward import BewardDoorbell
from beward.const import ALARM_SENSOR

from . import function_url, load_binary
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER


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
