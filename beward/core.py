# -*- coding: utf-8 -*-

"""Beward devices controller core."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging
import socket
from datetime import datetime
from time import sleep

import requests
from requests import ConnectTimeout
from requests.auth import HTTPBasicAuth

from .const import MSG_GENERIC_FAIL, BEWARD_MODELS, TIMEOUT

try:
    from urllib.parse import urlencode
except ImportError:  # pragma: no cover
    from urllib import urlencode

_LOGGER = logging.getLogger(__name__)


# pylint: disable=R0902,R0904
class BewardGeneric(object):
    """Generic Implementation for Beward device.

    """

    _class_group = 'Beward'

    @staticmethod
    def get_device_type(model):
        """Detect device type for model."""

        if not model:
            return None

        for dev_type, models in BEWARD_MODELS.items():
            if model in models.split():
                return dev_type

        return None

    def __init__(self, host_ip, username, password, name=None, **kwargs):

        # Check if host_ip is a valid IPv4 representation.
        # This library does not (yet?) support IPv6
        try:
            socket.inet_aton(host_ip)
        except socket.error:
            raise ValueError("Not a valid IP address string")

        self.host = host_ip
        self.username = username
        self.password = password
        self.session = requests.session()
        self.params = {}

        self.last_activity = None
        self.alarm_timestamp = {}
        self.alarm_state = {}
        self._alarm_handlers = []

        self._sysinfo = None

    def get_url(self, function, extra_params=None, username=None,
                password=None):
        """Get entry point for function."""
        url = 'http://'
        if username:
            url += username
            if password:
                url += ':' + password
            url += '@'
        url += self.host + '/cgi-bin/' + function + '_cgi'
        if extra_params:
            url = self.add_url_params(url, extra_params)
        return url

    def add_url_params(self, url, extra_params):
        """Add params to URL."""
        from requests import PreparedRequest

        params = self.params.copy()
        params.update(extra_params)

        p = PreparedRequest()
        p.prepare_url(url, params)

        return p.url

    def query(self, function, method='GET', extra_params=None):
        """Query data from Beward device."""
        url = self.get_url(function)
        _LOGGER.debug("Querying %s", url)

        response = None

        # allow to override params when necessary
        # and update self.params globally for the next connection
        params = self.params.copy()
        if extra_params:
            params.update(extra_params)

        # Add authentication data
        auth = HTTPBasicAuth(self.username, self.password)

        try:
            if method == 'GET':
                req = self.session.get(url, params=params, auth=auth,
                                       timeout=TIMEOUT)
            # elif method == 'PUT':
            #     req = self.session.put(url, params=params, auth=auth,
            #                            timeout=TIMEOUT)
            # elif method == 'POST':
            #     req = self.session.post(url, params=params, auth=auth,
            #                             timeout=TIMEOUT, json=json)
            else:
                raise ValueError('Unknown method: %s' % method)

            _LOGGER.debug("_query ret %s", req.status_code)

        except Exception as err_msg:
            _LOGGER.error("Error! %s", err_msg)
            raise

        if req.status_code == 200 or req.status_code == 204:
            response = req

        if response is None:  # pragma: no cover
            _LOGGER.debug("%s", MSG_GENERIC_FAIL)
        return response

    def add_alarms_handler(self, handler: callable):
        self._alarm_handlers.append(handler)
        return self

    def remove_alarms_handler(self, handler: callable):
        self._alarm_handlers.remove(handler)
        return self

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""
        _LOGGER.debug("Handle alarm: %s; State: %s", alarm, state)

        self.last_activity = timestamp
        self.alarm_timestamp[alarm] = timestamp
        self.alarm_state[alarm] = state

        for handler in self._alarm_handlers:
            handler(self, timestamp, alarm, state)

    def listen_alarms(self, channel=0, alarms=None):
        """Listen for alarms from Beward device."""
        if alarms is None:  # pragma: no cover
            alarms = {}

        url = self.get_url('alarmchangestate')
        _LOGGER.debug("Querying %s", url)

        params = self.params.copy()
        params.update({
            'channel': channel,
            'parameter': ';'.join(alarms),
        })
        auth = HTTPBasicAuth(self.username, self.password)

        import threading
        thread = threading.Thread(
            target=self._alarms_listener, args=(url, params, auth),
            daemon=True)
        thread.start()

        _LOGGER.debug("Return from listen_alarms()")

    def _alarms_listener(self, url: str, params, auth):
        while True:
            resp = requests.get(url, params=params, auth=auth, stream=True)
            _LOGGER.debug("_query ret %s", resp.status_code)

            if resp.status_code != 200:
                sleep(TIMEOUT)
                continue

            for line in resp.iter_lines(chunk_size=1, decode_unicode=True):
                if line:
                    _LOGGER.debug("Alarm: %s", line)

                    date, time, alert, state, _ = str(line).split(';', 5)
                    timestamp = datetime.strptime(date + ' ' + time,
                                                  '%Y-%m-%d %H:%M:%S')
                    state = (state != '0')

                    self._handle_alarm(timestamp, alert, state)

    def get_info(self, function):
        """Get info from Beward device."""
        info = {}
        data = self.query(function, extra_params={
            'action': 'get',
        }).text
        for env in data.splitlines():
            (k, v) = env.split('=', 2)
            info[k] = v

        return info

    @property
    def system_info(self):
        """Get system info from Beward device."""
        if self._sysinfo:
            return self._sysinfo

        self._sysinfo = {}
        try:
            self._sysinfo = self.get_info('systeminfo')
        except ConnectTimeout:
            pass

        return self._sysinfo

    @property
    def device_type(self):
        """Detect device type."""
        return self.get_device_type(self.system_info.get('DeviceModel'))

    @property
    def ready(self):
        try:
            self.query('systeminfo')
        except ConnectTimeout:
            return False

        return True

    @property
    def is_online(self):
        return self.ready
