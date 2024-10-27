# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

from datetime import datetime

import requests_mock
from requests import ConnectTimeout

from beward import BewardCamera
from beward.const import ALARM_MOTION

from . import function_url, load_binary, load_fixture
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER, local_tz


def test___init__() -> None:
    """Initialize test."""
    beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
    assert beward.rtsp_port is None
    assert beward.stream == 0

    beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, rtsp_port=123, stream=2)
    assert beward.rtsp_port == 123
    assert beward.stream == 2


def test_obtain_uris() -> None:
    """Test that obtain urls from device."""
    with requests_mock.Mocker() as mock:
        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        assert beward._live_image_url is None
        assert beward._rtsp_live_video_url is None

        mock.register_uri("get", function_url("rtsp"), exc=ConnectTimeout)
        beward.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":554/av0_0"
        )
        assert beward._rtsp_live_video_url == expect

        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, stream=1)
        mock.register_uri("get", function_url("rtsp"))
        beward.obtain_uris()

        expect = (
            function_url("images", user=MOCK_USER, password=MOCK_PASS) + "?channel=0"
        )
        assert beward._live_image_url == expect

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":554/av0_1"
        )
        assert beward._rtsp_live_video_url == expect

        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))
        beward.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":47456/av0_0"
        )
        assert beward._rtsp_live_video_url == expect

        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS, rtsp_port=123, stream=2)
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))
        beward.obtain_uris()

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":123/av0_2"
        )
        assert beward._rtsp_live_video_url == expect


def test_live_image_url() -> None:
    """Test that obtain live image url from device."""
    with requests_mock.Mocker() as mock:
        mock.register_uri("get", function_url("rtsp"))
        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        assert beward._live_image_url is None

        expect = (
            function_url("images", user=MOCK_USER, password=MOCK_PASS) + "?channel=0"
        )
        assert beward.live_image_url == expect


def test_rtsp_live_video_url() -> None:
    """Test that obtain RTSP live video url from device."""
    with requests_mock.Mocker() as mock:
        mock.register_uri("get", function_url("rtsp"), text=load_fixture("rtsp.txt"))
        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        assert beward._rtsp_live_video_url is None

        expect = (
            "rtsp://" + MOCK_USER + ":" + MOCK_PASS + "@" + MOCK_HOST + ":47456/av0_0"
        )
        assert beward.rtsp_live_video_url == expect


def test_live_image() -> None:
    """Test that receive live image from device."""
    image = load_binary("image.jpg")

    with requests_mock.Mocker() as mock:
        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        mock.register_uri("get", function_url("images"), content=image)
        res = beward.live_image
        assert res is None

        mock.register_uri(
            "get",
            function_url("images"),
            content=image,
            headers={"Content-Type": "image/jpeg"},
        )
        res = beward.live_image
        assert res == image


def test__handle_alarm() -> None:
    """Test that handle alarms."""
    image = load_binary("image.jpg")

    with requests_mock.Mocker() as mock:
        beward = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

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
        beward._handle_alarm(ts1, ALARM_MOTION, state=True)
        assert beward.last_motion_timestamp == ts1
        assert beward.last_motion_image == image
