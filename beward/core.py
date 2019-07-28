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

import requests
from requests import ConnectTimeout
from requests.auth import HTTPBasicAuth

from .const import MSG_GENERIC_FAIL, BEWARD_MODELS, TIMEOUT

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

_LOG = logging.getLogger(__name__)


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

    def __init__(self, host_ip, username, password, debug=False):

        # Check if host_ip is a valid IPv4 representation.
        # This library does not (yet?) support IPv6
        try:
            socket.inet_aton(host_ip)
        except socket.error:
            raise ValueError("Not a valid IP address string")

        self.params = {}

        self.debug = debug
        self.host = host_ip
        self.username = username
        self.password = password
        self.session = requests.session()

        self.last_activity = None
        self.alarm_timestamp = {}
        self.alarm_state = {}

    def get_url(self, function):
        """Get entry point for function."""

        return 'http://' + self.host + '/cgi-bin/' + function + '_cgi'

    def query(self, function, method='GET', extra_params=None):
        """Query data from Beward device."""

        url = self.get_url(function)
        if self.debug:  # pragma: no cover
            _LOG.debug("Querying %s", url)

        response = None

        # allow to override params when necessary
        # and update self.params globally for the next connection
        if extra_params:
            params = self.params
            params.update(extra_params)
        else:
            params = self.params

        # Add authentication data
        params.update({
            'user': self.username,
            'pwd': self.password,
        })
        auth = HTTPBasicAuth(self.username, self.password)

        try:
            if method == 'GET':
                req = self.session.get(url, params=urlencode(params),
                                       auth=auth, timeout=TIMEOUT)
            # elif method == 'PUT':
            #     req = self.session.put(url, params=urlencode(params),
            #                            auth=auth, timeout=TIMEOUT)
            # elif method == 'POST':
            #     req = self.session.post(url, params=urlencode(params),
            #                             auth=auth, timeout=TIMEOUT, json=json)
            else:
                raise ValueError('Unknown method: %s' % method)

            if self.debug:  # pragma: no cover
                _LOG.debug("_query ret %s", req.status_code)

        except Exception as err_msg:
            _LOG.error("Error! %s", err_msg)
            raise

        if req.status_code == 200 or req.status_code == 204:
            response = req

        if self.debug and response is None:  # pragma: no cover
            _LOG.debug("%s", MSG_GENERIC_FAIL)
        return response

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""

        if self.debug:  # pragma: no cover
            _LOG.debug("Time: %s; Alert: %s; Status: %s", timestamp, alarm,
                       state)

        self.last_activity = timestamp
        self.alarm_timestamp[alarm] = timestamp
        self.alarm_state[alarm] = state

    def listen_alarms(self, channel=0, alarms=None):
        """Listen for alarms from Beward device."""

        def listener():
            resp = requests.get(url, params=urlencode(params), auth=auth,
                                timeout=TIMEOUT, stream=True)
            if self.debug:
                _LOG.debug("_query ret %s", resp.status_code)

            if resp.status_code == 200:
                for line in resp.iter_lines(chunk_size=1, decode_unicode=True):
                    if line:
                        if self.debug:
                            _LOG.debug("Alarm: %s", line)

                        date, time, alert, state, _ = str(line).split(';', 5)
                        timestamp = datetime.strptime(date + ' ' + time,
                                                      '%Y-%m-%d %H:%M:%S')
                        state = int(state)

                        self._handle_alarm(timestamp, alert, state)

        if alarms is None:
            alarms = {}

        url = self.get_url('alarmchangestate')

        if self.debug:
            _LOG.debug("Querying %s", url)

        params = self.params
        params.update({
            'channel': channel,
            'parameter': ';'.join(alarms),
        })

        # Add authentication data
        params.update({
            'user': self.username,
            'pwd': self.password,
        })
        auth = HTTPBasicAuth(self.username, self.password)

        import threading
        thread = threading.Thread(target=listener)
        thread.start()

        if self.debug:
            _LOG.debug("Return from listen_alarms()")

    @property
    def system_info(self):
        """Get system info from Beward device."""

        sysinfo = {}

        try:
            data = self.query('systeminfo').text
            for env in data.splitlines():
                (k, v) = env.split('=', 2)
                sysinfo[k] = v
        except ConnectTimeout:
            pass

        return sysinfo

    @property
    def device_type(self):
        """Detect device type."""

        return self.get_device_type(self.system_info.get('DeviceModel'))

    @property
    def is_online(self):
        try:
            self.query('systeminfo')
        except ConnectTimeout:
            return False

        return True
