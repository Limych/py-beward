# pylint: disable=protected-access,redefined-outer-name,no-value-for-parameter
"""Test to verify that Beward library works."""

import logging
from datetime import datetime
from time import sleep

import pytest
import requests
import requests_mock

from beward import BewardGeneric
from beward.const import (
    ALARM_MOTION,
    ALARM_ONLINE,
    ALARM_SENSOR,
    BEWARD_CAMERA,
    BEWARD_DOORBELL,
)

from . import function_url, load_fixture
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER, local_tz


@pytest.mark.parametrize("host", ["265.265.265.265", "-1.-1.-1.-1"])
def test___init__failing(host) -> None:
    """Test class initialization failing."""
    with pytest.raises(ValueError):  # noqa: PT011
        BewardGeneric(host, MOCK_USER, MOCK_PASS)


@pytest.mark.parametrize(
    ("host", "port", "host_exp", "port_exp"),
    [
        (MOCK_HOST, None, MOCK_HOST, 80),
        (MOCK_HOST + ":123", None, MOCK_HOST, 123),
        (MOCK_HOST, 456, MOCK_HOST, 456),
    ],
)
def test___init__(host: str, port, host_exp: str, port_exp: int) -> None:
    """Test class initialization."""
    bwd = BewardGeneric(host, MOCK_USER, MOCK_PASS, port=port)
    assert bwd.host == host_exp
    assert bwd.port == port_exp


@pytest.mark.parametrize(
    ("device", "dev_type"),
    [
        ("B102S", BEWARD_CAMERA),
        ("DS03M", BEWARD_DOORBELL),
        ("DS06M", BEWARD_DOORBELL),
        (None, None),
        ("NONEXISTENT", None),
    ],
)
def test_get_device_type(device: str, dev_type: str) -> None:
    """Test that correct device type detection."""
    assert BewardGeneric.get_device_type(device) == dev_type


def test_get_url(beward) -> None:
    """Test that correct URLs composing."""
    expect = f"http://{MOCK_HOST}:80/cgi-bin/systeminfo_cgi"
    res = beward.get_url("systeminfo")
    #
    assert res == expect

    expect = f"http://{MOCK_HOST}:80/cgi-bin/systeminfo_cgi?arg=123"
    res = beward.get_url("systeminfo", extra_params={"arg": "123"})
    #
    assert res == expect

    username = "user"
    expect = f"http://{username}@{MOCK_HOST}:80/cgi-bin/systeminfo_cgi"
    res = beward.get_url("systeminfo", username=username)
    #
    assert res == expect

    username = "user"
    password = "pass"  # noqa: S105
    expect = f"http://{username}:{password}@{MOCK_HOST}:80/cgi-bin/systeminfo_cgi"
    res = beward.get_url("systeminfo", username=username, password=password)
    #
    assert res == expect

    beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS, port=123)

    expect = f"http://{MOCK_HOST}:123/cgi-bin/systeminfo_cgi"
    res = beward.get_url("systeminfo")
    #
    assert res == expect

    username = "user"
    expect = f"http://{username}@{MOCK_HOST}:123/cgi-bin/systeminfo_cgi"
    res = beward.get_url("systeminfo", username=username)
    #
    assert res == expect


def test_add_url_param(beward) -> None:
    """Test that correct URLs parameters adding."""
    base_url = f"http://{MOCK_HOST}/cgi-bin/systeminfo_cgi"

    expect = base_url + "?arg=123"
    res = beward.add_url_params(base_url, {"arg": "123"})
    #
    assert res == expect


def test_query(caplog) -> None:
    """Test that send requests to device."""
    caplog.set_level(logging.DEBUG)
    function = "systeminfo"

    with requests_mock.Mocker() as mock:
        beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        caplog.clear()
        expect = load_fixture("systeminfo.txt")
        mock.register_uri("get", function_url(function), text=expect)

        res = beward.query(function)

        assert res.text == expect
        assert next((s for s in caplog.messages if MOCK_PASS in s), None) is None

        caplog.clear()
        expect = "test data"
        mock.register_uri("get", function_url(function) + "?extra=123", text=expect)

        res = beward.query(function, extra_params={"extra": 123})

        assert res.text == expect
        assert next((s for s in caplog.messages if MOCK_PASS in s), None) is None


def test_add_alarms_handler(beward) -> None:
    """Test that add alarm handlers."""
    # Check initial state
    assert beward._alarm_handlers == set()

    def logger1() -> None:
        pass

    def logger2() -> None:
        pass

    beward.add_alarms_handler(logger1)
    assert beward._alarm_handlers == {logger1}

    beward.add_alarms_handler(logger1)
    assert beward._alarm_handlers == {logger1}

    beward.add_alarms_handler(logger2)
    assert beward._alarm_handlers == {logger1, logger2}


def test_remove_alarms_handler(beward) -> None:
    """Test that remove alarm handlers."""

    def logger1() -> None:
        pass

    def logger2() -> None:
        pass

    beward.add_alarms_handler(logger1)
    beward.add_alarms_handler(logger2)
    assert beward._alarm_handlers == {logger1, logger2}

    beward.remove_alarms_handler(logger1)
    assert beward._alarm_handlers == {logger2}

    beward.remove_alarms_handler(logger1)
    assert beward._alarm_handlers == {logger2}

    beward.remove_alarms_handler(logger2)
    assert beward._alarm_handlers == set()


def test__handle_alarm(beward) -> None:
    """Test that handle alarms."""
    # Check initial state
    assert beward.alarm_state == {ALARM_ONLINE: False}
    assert beward.alarm_timestamp == {ALARM_ONLINE: datetime.min}

    ts1 = datetime.now(local_tz)
    beward._handle_alarm(ts1, ALARM_MOTION, state=True)
    assert beward.alarm_state == {ALARM_ONLINE: False, ALARM_MOTION: True}
    assert beward.alarm_timestamp == {ALARM_ONLINE: datetime.min, ALARM_MOTION: ts1}

    ts2 = datetime.now(local_tz)
    beward._handle_alarm(ts2, ALARM_SENSOR, state=True)
    assert beward.alarm_state == {
        ALARM_ONLINE: False,
        ALARM_MOTION: True,
        ALARM_SENSOR: True,
    }
    assert beward.alarm_timestamp == {
        ALARM_ONLINE: datetime.min,
        ALARM_MOTION: ts1,
        ALARM_SENSOR: ts2,
    }

    ts3 = datetime.now(local_tz)
    beward._handle_alarm(ts3, ALARM_MOTION, state=False)
    assert beward.alarm_state == {
        ALARM_ONLINE: False,
        ALARM_MOTION: False,
        ALARM_SENSOR: True,
    }
    assert beward.alarm_timestamp == {
        ALARM_ONLINE: datetime.min,
        ALARM_MOTION: ts3,
        ALARM_SENSOR: ts2,
    }


def _listen_alarms_tester(alarms, expected_log) -> None:
    with requests_mock.Mocker() as mock:
        beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)
        mock.register_uri(
            "get", function_url("alarmchangestate"), text="\n".join(alarms)
        )
        log = []
        logging = True

        def _alarms_logger(device, timestamp, alarm, state) -> None:
            nonlocal logging
            if not logging:
                return

            if alarm == ALARM_ONLINE:
                log.append(";".join((str(alarm), str(state))))
                logging = state
            else:
                log.append(";".join((str(timestamp), str(alarm), str(state))))

        # Check initial state
        assert beward.alarm_state == {ALARM_ONLINE: False}
        assert beward.alarm_timestamp == {ALARM_ONLINE: datetime.min}

        alarms2listen = [x.split(";")[2] for x in alarms]
        beward.add_alarms_handler(_alarms_logger)
        beward.listen_alarms(alarms=alarms2listen)
        sleep(0.1)
        beward.remove_alarms_handler(_alarms_logger)
        sleep(0.1)

        expect = [
            "DeviceOnline;True",
        ]
        expect.extend(expected_log)
        expect.append("DeviceOnline;False")
        assert log == expect


def test_listen_alarms():
    """Test that listen alarms."""
    local_tz_str = datetime.now(local_tz).isoformat(timespec="seconds")[19:]

    alarms = ["2019-07-28;00:57:27;MotionDetection;1;0"]
    ex_log = [f"2019-07-28 00:57:27{local_tz_str};MotionDetection;True"]
    _listen_alarms_tester(alarms, ex_log)

    alarms.append("2019-07-28;00:57:28;MotionDetection;0;0")
    ex_log.append(f"2019-07-28 00:57:28{local_tz_str};MotionDetection;False")
    _listen_alarms_tester(alarms, ex_log)

    alarms.append("2019-07-28;15:51:52;SensorAlarm;1;0")
    ex_log.append(f"2019-07-28 15:51:52{local_tz_str};SensorAlarm;True")
    _listen_alarms_tester(alarms, ex_log)

    alarms.append("2019-07-28;15:51:53;SensorAlarm;0;0")
    ex_log.append(f"2019-07-28 15:51:53{local_tz_str};SensorAlarm;False")
    _listen_alarms_tester(alarms, ex_log)


def test_system_info():
    """Test that get system info from device."""
    data = load_fixture("systeminfo.txt")

    with requests_mock.Mocker() as mock:
        mock.register_uri("get", function_url("systeminfo"), text=data)
        beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        expect = {}
        for env in data.splitlines():
            (k, val) = env.split("=", 2)
            expect[k] = val

        assert beward.system_info == expect

        mock.register_uri(
            "get", function_url("systeminfo"), exc=requests.exceptions.ConnectTimeout
        )

        assert beward.system_info == expect  # Check for caching

        beward._sysinfo = None

        assert beward.system_info == {}


def test_device_type():
    """Test that detect device type."""
    with requests_mock.Mocker() as mock:
        mock.register_uri(
            "get", function_url("systeminfo"), text=load_fixture("systeminfo.txt")
        )
        beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        assert beward.device_type == BEWARD_DOORBELL

        mock.register_uri("get", function_url("systeminfo"), text="DeviceModel=DS03M")
        beward._sysinfo = None

        assert beward.device_type == BEWARD_DOORBELL

        mock.register_uri(
            "get", function_url("systeminfo"), text="DeviceModel=NONEXISTENT"
        )
        beward._sysinfo = None

        assert beward.device_type is None

        mock.register_uri("get", function_url("systeminfo"), text="NonExistent=DS03M")
        beward._sysinfo = None

        assert beward.device_type is None


def test_is_online():
    """Test that detect device is online."""
    data = load_fixture("systeminfo.txt")

    with requests_mock.Mocker() as mock:
        mock.register_uri("get", function_url("systeminfo"), text=data)

        beward = BewardGeneric(MOCK_HOST, MOCK_USER, MOCK_PASS)

        assert beward.is_online is True
        assert beward.available is True

        mock.register_uri("get", function_url("systeminfo"))

        assert beward.is_online is True
        assert beward.available is True

        mock.register_uri(
            "get", function_url("systeminfo"), exc=requests.exceptions.ConnectTimeout
        )

        assert beward.is_online is False
        assert beward.available is False
