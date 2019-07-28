# -*- coding: utf-8 -*-

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import os
from datetime import datetime
from unittest import TestCase

import requests
import requests_mock

from beward import Beward, BewardDoorbell, BewardGeneric
from beward.const import ALARM_MOTION, ALARM_SENSOR, BEWARD_DOORBELL

MOCK_HOST = '192.168.0.2'
MOCK_USER = 'user'
MOCK_PASS = 'pass'


def load_fixture(filename):
    """Load a fixture."""

    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path) as fptr:
        return fptr.read()


class TestBeward(TestCase):

    @requests_mock.Mocker()
    def test_factory(self, mock):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text='DeviceModel=NONEXISTENT')

        res = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertTrue(isinstance(res, BewardGeneric))

        # TODO: BewardCamera
        # mock.register_uri("get", bw.get_url('systeminfo'),
        #                   text='DeviceModel=????')
        #
        # res = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        # self.assertTrue(isinstance(res, BewardCamera))

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text='DeviceModel=DS06M')

        res = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertTrue(isinstance(res, BewardDoorbell))


class TestBewardGeneric(TestCase):

    def test___init__(self):
        try:
            BewardGeneric('265.265.265.265', MOCK_USER, MOCK_PASS)
            self.fail()  # pragma: no cover
        except ValueError:
            pass

    def test_get_device_type(self):
        self.assertEqual(BewardGeneric.get_device_type('DS03M'),
                         BEWARD_DOORBELL)
        self.assertEqual(BewardGeneric.get_device_type('DS06M'),
                         BEWARD_DOORBELL)

        self.assertIsNone(BewardGeneric.get_device_type(None))
        self.assertIsNone(BewardGeneric.get_device_type('NONEXISTENT'))

    def test_get_url(self):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        expect = 'http://' + MOCK_HOST + '/cgi-bin/systeminfo_cgi'
        res = bw.get_url('systeminfo')

        self.assertEqual(res, expect)

    @requests_mock.Mocker()
    def test_query(self, mock):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        function = 'systeminfo'
        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", bw.get_url(function), text=data)

        res = bw.query(function)
        self.assertEqual(res.text, data)

        data = 'test data'
        mock.register_uri("get", bw.get_url(function) + '?extra=123',
                          text=data)

        res = bw.query(function, extra_params={'extra': 123})
        self.assertEqual(res.text, data)

        try:
            bw.query(function, method='UNEXISTENT')
            self.fail()  # pragma: no cover
        except ValueError:
            pass

    def test__handle_alarm(self):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # Check initial state
        self.assertEqual(bw.alarm_timestamp, {})
        self.assertEqual(bw.alarm_state, {})

        ts1 = datetime.now()
        bw._handle_alarm(ts1, ALARM_MOTION, 1)
        self.assertEqual(bw.alarm_timestamp, {
            ALARM_MOTION: ts1,
        })
        self.assertEqual(bw.alarm_state, {
            ALARM_MOTION: 1,
        })

        ts2 = datetime.now()
        bw._handle_alarm(ts2, ALARM_SENSOR, 1)
        self.assertEqual(bw.alarm_timestamp, {
            ALARM_MOTION: ts1,
            ALARM_SENSOR: ts2,
        })
        self.assertEqual(bw.alarm_state, {
            ALARM_MOTION: 1,
            ALARM_SENSOR: 1,
        })

        ts3 = datetime.now()
        bw._handle_alarm(ts3, ALARM_MOTION, 0)
        self.assertEqual(bw.alarm_timestamp, {
            ALARM_MOTION: ts3,
            ALARM_SENSOR: ts2,
        })
        self.assertEqual(bw.alarm_state, {
            ALARM_MOTION: 0,
            ALARM_SENSOR: 1,
        })

    # TODO: def test_listen_alarms()

    @requests_mock.Mocker()
    def test_system_info(self, mock):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", bw.get_url('systeminfo'),
                          text=data)

        expect = {}
        for env in data.splitlines():
            (k, v) = env.split('=', 2)
            expect[k] = v

        self.assertEqual(bw.system_info, expect)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          exc=requests.exceptions.ConnectTimeout)

        self.assertEqual(bw.system_info, {})

    @requests_mock.Mocker()
    def test_device_type(self, mock):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text=load_fixture("systeminfo.txt"))
        bw.sysinfo = None

        self.assertEqual(bw.device_type, BEWARD_DOORBELL)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text='DeviceModel=DS03M')
        bw.sysinfo = None

        self.assertEqual(bw.device_type, BEWARD_DOORBELL)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text='DeviceModel=NONEXISTENT')
        bw.sysinfo = None

        self.assertIsNone(bw.device_type)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          text='NonExistent=DS03M')
        bw.sysinfo = None

        self.assertIsNone(bw.device_type)

    @requests_mock.Mocker()
    def test_is_online(self, mock):
        bw = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", bw.get_url('systeminfo'),
                          text=data)

        self.assertTrue(bw.is_online)

        mock.register_uri("get", bw.get_url('systeminfo'))

        self.assertTrue(bw.is_online)

        mock.register_uri("get", bw.get_url('systeminfo'),
                          exc=requests.exceptions.ConnectTimeout)

        self.assertFalse(bw.is_online)
