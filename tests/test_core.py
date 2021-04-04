# pylint: disable=protected-access,redefined-outer-name,no-value-for-parameter
"""Test to verify that Beward library works."""

from datetime import datetime
from time import sleep
from unittest import TestCase

import requests
import requests_mock

from beward import BewardGeneric
from beward.const import ALARM_MOTION, ALARM_ONLINE, ALARM_SENSOR, BEWARD_DOORBELL

from . import function_url, load_fixture
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER


class TestBewardGeneric(TestCase):
    """Test case for BewardGeneric class."""

    def test___init__(self):
        """Initialize test case."""
        try:
            BewardGeneric("265.265.265.265", MOCK_USER, MOCK_PASS)
            self.fail()  # pragma: no cover
        except ValueError:
            pass

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertEqual(MOCK_HOST, bwd.host)
        self.assertEqual(80, bwd.port)

        bwd = BewardGeneric(MOCK_HOST + ":123", MOCK_USER, MOCK_PASS)
        self.assertEqual(MOCK_HOST, bwd.host)
        self.assertEqual(123, bwd.port)

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS, port=456)
        self.assertEqual(MOCK_HOST, bwd.host)
        self.assertEqual(456, bwd.port)

    def test_get_device_type(self):
        """Test that correct device type detection."""
        self.assertEqual(BEWARD_DOORBELL, BewardGeneric.get_device_type("DS03M"))
        self.assertEqual(BEWARD_DOORBELL, BewardGeneric.get_device_type("DS06M"))

        self.assertIsNone(BewardGeneric.get_device_type(None))
        self.assertIsNone(BewardGeneric.get_device_type("NONEXISTENT"))

    def test_get_url(self):
        """Test that correct URLs composing."""
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        expect = "http://%s:80/cgi-bin/systeminfo_cgi" % MOCK_HOST
        res = bwd.get_url("systeminfo")
        #
        self.assertEqual(expect, res)

        expect = "http://%s:80/cgi-bin/systeminfo_cgi?arg=123" % MOCK_HOST
        res = bwd.get_url("systeminfo", extra_params={"arg": "123"})
        #
        self.assertEqual(expect, res)

        username = "user"
        expect = "http://{}@{}:80/cgi-bin/systeminfo_cgi".format(username, MOCK_HOST)
        res = bwd.get_url("systeminfo", username=username)
        #
        self.assertEqual(expect, res)

        username = "user"
        password = "pass"
        expect = "http://{}:{}@{}:80/cgi-bin/systeminfo_cgi".format(
            username, password, MOCK_HOST
        )
        res = bwd.get_url("systeminfo", username=username, password=password)
        #
        self.assertEqual(expect, res)

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS, port=123)

        expect = "http://%s:123/cgi-bin/systeminfo_cgi" % MOCK_HOST
        res = bwd.get_url("systeminfo")
        #
        self.assertEqual(expect, res)

        username = "user"
        expect = "http://{}@{}:123/cgi-bin/systeminfo_cgi".format(username, MOCK_HOST)
        res = bwd.get_url("systeminfo", username=username)
        #
        self.assertEqual(expect, res)

    def test_add_url_param(self):
        """Test that correct URLs parameters adding."""
        base_url = "http://%s/cgi-bin/systeminfo_cgi" % MOCK_HOST
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        expect = base_url + "?arg=123"
        res = bwd.add_url_params(base_url, {"arg": "123"})
        #
        self.assertEqual(expect, res)

    @requests_mock.Mocker()
    def test_query(self, mock):
        """Test that send requests to device."""
        function = "systeminfo"
        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", function_url(function), text=data)

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        res = bwd.query(function)
        self.assertEqual(data, res.text)

        data = "test data"
        mock.register_uri("get", function_url(function) + "?extra=123", text=data)

        res = bwd.query(function, extra_params={"extra": 123})
        self.assertEqual(data, res.text)

    def test_add_alarms_handler(self):
        """Test that add alarm handlers."""
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        self.assertEqual(set(), bwd._alarm_handlers)

        def logger1():
            pass

        def logger2():
            pass

        bwd.add_alarms_handler(logger1)
        self.assertEqual({logger1}, bwd._alarm_handlers)

        bwd.add_alarms_handler(logger1)
        self.assertEqual({logger1}, bwd._alarm_handlers)

        bwd.add_alarms_handler(logger2)
        self.assertEqual({logger1, logger2}, bwd._alarm_handlers)

    def test_remove_alarms_handler(self):
        """Test that remove alarm handlers."""
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        def logger1():
            pass

        def logger2():
            pass

        bwd.add_alarms_handler(logger1)
        bwd.add_alarms_handler(logger2)
        self.assertEqual({logger1, logger2}, bwd._alarm_handlers)

        bwd.remove_alarms_handler(logger1)
        self.assertEqual({logger2}, bwd._alarm_handlers)

        bwd.remove_alarms_handler(logger1)
        self.assertEqual({logger2}, bwd._alarm_handlers)

        bwd.remove_alarms_handler(logger2)
        self.assertEqual(set(), bwd._alarm_handlers)

    def test__handle_alarm(self):
        """Test that handle alarms."""
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # Check initial state
        self.assertEqual({ALARM_ONLINE: False}, bwd.alarm_state)
        self.assertEqual({ALARM_ONLINE: datetime.min}, bwd.alarm_timestamp)

        ts1 = datetime.now()
        bwd._handle_alarm(ts1, ALARM_MOTION, True)
        self.assertEqual({ALARM_ONLINE: False, ALARM_MOTION: True}, bwd.alarm_state)
        self.assertEqual(
            {ALARM_ONLINE: datetime.min, ALARM_MOTION: ts1}, bwd.alarm_timestamp
        )

        ts2 = datetime.now()
        bwd._handle_alarm(ts2, ALARM_SENSOR, True)
        self.assertEqual(
            {ALARM_ONLINE: False, ALARM_MOTION: True, ALARM_SENSOR: True},
            bwd.alarm_state,
        )
        self.assertEqual(
            {ALARM_ONLINE: datetime.min, ALARM_MOTION: ts1, ALARM_SENSOR: ts2},
            bwd.alarm_timestamp,
        )

        ts3 = datetime.now()
        bwd._handle_alarm(ts3, ALARM_MOTION, False)
        self.assertEqual(
            {ALARM_ONLINE: False, ALARM_MOTION: False, ALARM_SENSOR: True},
            bwd.alarm_state,
        )
        self.assertEqual(
            {ALARM_ONLINE: datetime.min, ALARM_MOTION: ts3, ALARM_SENSOR: ts2},
            bwd.alarm_timestamp,
        )

    @requests_mock.Mocker()
    def _listen_alarms_tester(self, alarms, expected_log, mock):
        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri(
            "get", function_url("alarmchangestate"), text="\n".join(alarms)
        )
        log = []
        logging = True

        def _alarms_logger(device, timestamp, alarm, state):
            nonlocal logging
            if not logging:
                return

            if alarm == ALARM_ONLINE:
                log.append(";".join((str(alarm), str(state))))
                logging = state
            else:
                log.append(";".join((str(timestamp), str(alarm), str(state))))

        # Check initial state
        self.assertEqual({ALARM_ONLINE: False}, bwd.alarm_state)
        self.assertEqual({ALARM_ONLINE: datetime.min}, bwd.alarm_timestamp)

        alarms2listen = []
        for alarm in alarms:
            alarms2listen.append(alarm.split(";")[2])
        bwd.add_alarms_handler(_alarms_logger)
        bwd.listen_alarms(alarms=alarms2listen)
        sleep(0.1)
        bwd.remove_alarms_handler(_alarms_logger)
        sleep(0.1)

        expect = [
            "DeviceOnline;True",
        ]
        expect.extend(expected_log)
        expect.append("DeviceOnline;False")
        self.assertEqual(expect, log)

    def test_listen_alarms(self):
        """Test that listen alarms."""
        alarms = ["2019-07-28;00:57:27;MotionDetection;1;0"]
        ex_log = ["2019-07-28 00:57:27;MotionDetection;True"]
        self._listen_alarms_tester(alarms, ex_log)

        alarms.append("2019-07-28;00:57:28;MotionDetection;0;0")
        ex_log.append("2019-07-28 00:57:28;MotionDetection;False")
        self._listen_alarms_tester(alarms, ex_log)

        alarms.append("2019-07-28;15:51:52;SensorAlarm;1;0")
        ex_log.append("2019-07-28 15:51:52;SensorAlarm;True")
        self._listen_alarms_tester(alarms, ex_log)

        alarms.append("2019-07-28;15:51:53;SensorAlarm;0;0")
        ex_log.append("2019-07-28 15:51:53;SensorAlarm;False")
        self._listen_alarms_tester(alarms, ex_log)

    @requests_mock.Mocker()
    def test_system_info(self, mock):
        """Test that get system info from device."""
        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", function_url("systeminfo"), text=data)

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        expect = {}
        for env in data.splitlines():
            (k, val) = env.split("=", 2)
            expect[k] = val

        self.assertEqual(expect, bwd.system_info)

        mock.register_uri(
            "get", function_url("systeminfo"), exc=requests.exceptions.ConnectTimeout
        )

        self.assertEqual(expect, bwd.system_info)  # Check for caching

        bwd._sysinfo = None

        self.assertEqual({}, bwd.system_info)

    @requests_mock.Mocker()
    def test_device_type(self, mock):
        """Test that detect device type."""
        mock.register_uri(
            "get", function_url("systeminfo"), text=load_fixture("systeminfo.txt")
        )

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        self.assertEqual(BEWARD_DOORBELL, bwd.device_type)

        mock.register_uri("get", function_url("systeminfo"), text="DeviceModel=DS03M")
        bwd._sysinfo = None

        self.assertEqual(BEWARD_DOORBELL, bwd.device_type)

        mock.register_uri(
            "get", function_url("systeminfo"), text="DeviceModel=NONEXISTENT"
        )
        bwd._sysinfo = None

        self.assertIsNone(bwd.device_type)

        mock.register_uri("get", function_url("systeminfo"), text="NonExistent=DS03M")
        bwd._sysinfo = None

        self.assertIsNone(bwd.device_type)

    @requests_mock.Mocker()
    def test_is_online(self, mock):
        """Test that detect device is online."""
        data = load_fixture("systeminfo.txt")
        mock.register_uri("get", function_url("systeminfo"), text=data)

        bwd = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        self.assertTrue(bwd.is_online)
        self.assertTrue(bwd.available)

        mock.register_uri("get", function_url("systeminfo"))

        self.assertTrue(bwd.is_online)
        self.assertTrue(bwd.available)

        mock.register_uri(
            "get", function_url("systeminfo"), exc=requests.exceptions.ConnectTimeout
        )

        self.assertFalse(bwd.is_online())
        self.assertFalse(bwd.available)
