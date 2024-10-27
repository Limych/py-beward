# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

from datetime import datetime

import requests_mock

from beward import BewardDoorbell
from beward.const import ALARM_SENSOR

from . import function_url, load_binary
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER, local_tz


def test__handle_alarm():
    """Test that handle alarms."""
    image = load_binary("image.jpg")

    with requests_mock.Mocker() as mock:
        beward = BewardDoorbell(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # Check initial state
        assert beward.last_motion_timestamp is None
        assert beward.last_motion_image is None

        ts1 = datetime.now(local_tz)
        mock.register_uri(
            "get",
            function_url("images"),
            content=image,
            headers={"Content-Type": "image/jpeg"},
        )
        beward._handle_alarm(ts1, ALARM_SENSOR, state=True)
        assert beward.last_ding_timestamp == ts1
        assert beward.last_ding_image == image
