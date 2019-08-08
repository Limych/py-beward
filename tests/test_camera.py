# -*- coding: utf-8 -*-

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import os
from datetime import datetime
from unittest import TestCase

import requests_mock
from requests import ConnectTimeout

from beward import BewardCamera
from beward.const import ALARM_MOTION

MOCK_HOST = '192.168.0.2'
MOCK_USER = 'user'
MOCK_PASS = 'pass'


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path, encoding='utf-8') as fptr:
        return fptr.read()


def load_binary(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), 'binary', filename)
    with open(path, 'rb') as fptr:
        return fptr.read()


def function_url(function, host=MOCK_HOST, user=None, password=None):
    auth = ''
    if user:
        auth = user
        if password:
            auth += ':' + password
        auth += '@'
    return 'http://' + auth + host + '/cgi-bin/' + function + '_cgi'


class TestBewardCamera(TestCase):

    @requests_mock.Mocker()
    def test__obtain_uris(self, mock):
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)

        self.assertIsNone(bwd._live_image_url)
        self.assertIsNone(bwd._rtsp_live_video_url)

        mock.register_uri("get", function_url('rtsp'), exc=ConnectTimeout)
        bwd._obtain_uris()

        self.assertIsNone(bwd._rtsp_live_video_url)

        mock.register_uri("get", function_url('rtsp'))
        bwd._obtain_uris()

        expect = function_url('images', user=MOCK_USER,
                              password=MOCK_PASS) + '?channel=0'
        self.assertEqual(expect, bwd._live_image_url)

        expect = 'rtsp://' + MOCK_USER + ':' + MOCK_PASS + '@' + MOCK_HOST + \
                 ':554/av0_0'
        self.assertEqual(expect, bwd._rtsp_live_video_url)

        mock.register_uri("get", function_url('rtsp'),
                          text=load_fixture("rtsp.txt"))
        bwd._obtain_uris()

        expect = 'rtsp://' + MOCK_USER + ':' + MOCK_PASS + '@' + MOCK_HOST + \
                 ':47456/av0_0'
        self.assertEqual(expect, bwd._rtsp_live_video_url)

    @requests_mock.Mocker()
    def test_live_image_url(self, mock):
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url('rtsp'))

        self.assertIsNone(bwd._live_image_url)

        expect = function_url('images', user=MOCK_USER,
                              password=MOCK_PASS) + '?channel=0'
        self.assertEqual(expect, bwd.live_image_url)

    @requests_mock.Mocker()
    def test_rtsp_live_video_url(self, mock):
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri("get", function_url('rtsp'),
                          text=load_fixture("rtsp.txt"))

        self.assertIsNone(bwd._rtsp_live_video_url)

        expect = 'rtsp://' + MOCK_USER + ':' + MOCK_PASS + '@' + MOCK_HOST + \
                 ':47456/av0_0'
        self.assertEqual(expect, bwd.rtsp_live_video_url)

    @requests_mock.Mocker()
    def test_live_image(self, mock):
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        image = load_binary("image.jpg")

        mock.register_uri("get", function_url('images'), content=image)
        res = bwd.live_image
        self.assertIsNone(res)

        mock.register_uri("get", function_url('images'), content=image,
                          headers={'Content-Type': 'image/jpeg'})
        res = bwd.live_image
        self.assertEqual(image, res)

    @requests_mock.Mocker()
    def test__handle_alarm(self, mock):
        bwd = BewardCamera(MOCK_HOST, MOCK_USER, MOCK_PASS)
        image = load_binary("image.jpg")

        # Check initial state
        self.assertIsNone(bwd.last_motion_timestamp)
        self.assertIsNone(bwd.last_motion_image)

        ts1 = datetime.now()
        mock.register_uri("get", function_url('images'), content=image,
                          headers={'Content-Type': 'image/jpeg'})
        bwd._handle_alarm(ts1, ALARM_MOTION, True)
        self.assertEqual(ts1, bwd.last_motion_timestamp)
        self.assertEqual(image, bwd.last_motion_image)
