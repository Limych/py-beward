# -*- coding: utf-8 -*-

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import os
from datetime import datetime
from unittest import TestCase

import requests_mock

from beward import BewardDoorbell
from beward.const import ALARM_SENSOR

MOCK_HOST = '192.168.0.2'
MOCK_USER = 'user'
MOCK_PASS = 'pass'


def load_binary(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), 'binary', filename)
    with open(path, 'rb') as fptr:
        return fptr.read()


def function_url(function, host=MOCK_HOST):
    return 'http://' + host + ':80/cgi-bin/' + function + '_cgi'


class TestBewardDoorbell(TestCase):

    @requests_mock.Mocker()
    def test_ding(self, mock):
        bwd = BewardDoorbell(MOCK_HOST, MOCK_USER, MOCK_PASS)
        image = load_binary("image.jpg")
        mock.register_uri("get", function_url('images'), content=image,
                          headers={'Content-Type': 'image/jpeg'})

        # Check initial state
        self.assertIsNone(bwd.ding)
        self.assertIsNone(bwd.ding_timestamp)
        self.assertIsNone(bwd.ding_image)

        ts1 = datetime.now()
        bwd._handle_alarm(ts1, ALARM_SENSOR, True)
        self.assertEqual(True, bwd.ding)
        self.assertEqual(ts1, bwd.alarm_timestamp[ALARM_SENSOR])
        self.assertEqual(ts1, bwd.ding_timestamp)
        self.assertEqual(image, bwd.ding_image)

        ts2 = datetime.fromtimestamp(ts1.timestamp() + 1)
        bwd._handle_alarm(ts2, ALARM_SENSOR, False)
        self.assertEqual(False, bwd.ding)
        self.assertEqual(ts2, bwd.alarm_timestamp[ALARM_SENSOR])
        self.assertEqual(ts1, bwd.ding_timestamp)
        self.assertEqual(image, bwd.ding_image)
