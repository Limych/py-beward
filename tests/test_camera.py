"""Test to verify that Beward library works."""

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

from datetime import datetime
import os
from unittest import TestCase

from beward import BewardCamera
from beward.const import ALARM_MOTION, ALARM_SENSOR_OUT
from requests import ConnectTimeout
import requests_mock

MOCK_HOST = "192.168.0.2"
MOCK_USER = "user"
MOCK_PASS = "pass"


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


class TestBewardCamera(TestCase):
    """Test case for BewardCamera class."""

    @requests_mock.Mocker()
    def test___init__(self, mock):
        """Initialize test."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertEqual(None, bwd.rtsp_port)
        self.assertEqual(0, bwd.stream)

        mock.register_uri(
            "get", function_url("controller"), text=load_fixture("controller.txt")
        )
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, rtsp_port=123, stream=2)
        self.assertEqual(123, bwd.rtsp_port)
        self.assertEqual(2, bwd.stream)
        self.assertEqual(1, bwd._outputs_num)

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
        self.assertEqual(True, bwd.motion)
        self.assertEqual(ts1, bwd.alarm_timestamp[ALARM_MOTION])
        self.assertEqual(ts1, bwd.motion_timestamp)
        self.assertEqual(image, bwd.motion_image)

        ts2 = datetime.fromtimestamp(ts1.timestamp() + 1)
        bwd._handle_alarm(ts2, ALARM_MOTION, False)
        self.assertEqual(False, bwd.motion)
        self.assertEqual(ts2, bwd.alarm_timestamp[ALARM_MOTION])
        self.assertEqual(ts1, bwd.motion_timestamp)
        self.assertEqual(image, bwd.motion_image)

    @requests_mock.Mocker()
    def test_output1(self, mock):
        """Test that handle output 1 alarms."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # Check initial state
        self.assertIsNone(bwd.output1)
        self.assertIsNone(bwd.output1_timestamp)

        ts1 = datetime.now()
        bwd._handle_alarm(ts1, ALARM_SENSOR_OUT, True)
        self.assertEqual(True, bwd.output1)
        self.assertEqual(ts1, bwd.alarm_timestamp[ALARM_SENSOR_OUT])
        self.assertEqual(ts1, bwd.output1_timestamp)

        ts2 = datetime.fromtimestamp(ts1.timestamp() + 1)
        bwd._handle_alarm(ts2, ALARM_SENSOR_OUT, False)
        self.assertEqual(False, bwd.output1)
        self.assertEqual(ts2, bwd.alarm_timestamp[ALARM_SENSOR_OUT])
        self.assertEqual(ts1, bwd.output1_timestamp)

    @requests_mock.Mocker()
    def test_output1_set(self, mock):
        """Test that switch output 1."""
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # Check initial state
        self.assertIsNone(bwd.output1)
        self.assertIsNone(bwd.output1_timestamp)

        # TODO

    # TODO: Multiple Sensor outs
