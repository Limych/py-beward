# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

from datetime import datetime
from unittest import TestCase

import requests_mock
from requests import ConnectTimeout

from beward import BewardCamera
from beward.const import ALARM_MOTION

from . import function_url, load_binary, load_fixture
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER


class TestBewardCamera(TestCase):
    """Test case for BewardCamera class."""

    def test___init__(self):
        """Initialize test."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertEqual(None, bwd.rtsp_port)
        self.assertEqual(0, bwd.stream)

        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, rtsp_port=123, stream=2)
        self.assertEqual(123, bwd.rtsp_port)
        self.assertEqual(2, bwd.stream)

    @requests_mock.Mocker()
    def test_obtain_uris(self, mock):
        """Test that obtain urls from device."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        self.assertIsNone(bwd._live_image_url)
        self.assertIsNone(bwd._rtsp_live_video_url)

        mock.register_uri("get", function_url("rtsp"), exc=ConnectTimeout)
        bwd.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":554/av0_0"
        )
        self.assertEqual(expect, bwd._rtsp_live_video_url)

        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, stream=1)
        mock.register_uri("get", function_url("rtsp"))
        bwd.obtain_uris()

        expect = (
            function_url("images", user=MOCK_USER, password=MOCK_PASS) + "?channel=0"
        )
        self.assertEqual(expect, bwd._live_image_url)

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":554/av0_1"
        )
        self.assertEqual(expect, bwd._rtsp_live_video_url)

        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))
        bwd.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":47456/av0_0"
        )
        self.assertEqual(expect, bwd._rtsp_live_video_url)

        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, rtsp_port=123, stream=2)
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))
        bwd.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":123/av0_2"
        )
        self.assertEqual(expect, bwd._rtsp_live_video_url)

    @requests_mock.Mocker()
    def test_live_image_url(self, mock):
        """Test that obtain live image url from device."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url("rtsp"))

        self.assertIsNone(bwd._live_image_url)

        expect = (
            function_url("images", user=MOCK_USER, password=MOCK_PASS) + "?channel=0"
        )
        self.assertEqual(expect, bwd.live_image_url)

    @requests_mock.Mocker()
    def test_rtsp_live_video_url(self, mock):
        """Test that obtain RTSP live video url from device."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))

        self.assertIsNone(bwd._rtsp_live_video_url)

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":47456/av0_0"
        )
        self.assertEqual(expect, bwd.rtsp_live_video_url)

    @requests_mock.Mocker()
    def test_live_image(self, mock):
        """Test that receive live image from device."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        image = load_binary("image.jpg")

        mock.register_uri("get", function_url("images"), content=image)
        res = bwd.live_image
        self.assertIsNone(res)

        mock.register_uri(
            "get",
            function_url("images"),
            content=image,
            headers={"Content-Type": "image/jpeg"},
        )
        res = bwd.live_image
        self.assertEqual(image, res)

    @requests_mock.Mocker()
    def test__handle_alarm(self, mock):
        """Test that handle alarms."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
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
        bwd._handle_alarm(ts1, ALARM_MOTION, True)
        self.assertEqual(ts1, bwd.last_motion_timestamp)
        self.assertEqual(image, bwd.last_motion_image)
