# -*- coding: utf-8 -*-

"""Beward devices controller core."""
import asyncio
import logging
import socket
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from .const import MSG_GENERIC_FAIL

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

    def __init__(self, host_ip, username, password, debug=False):

        # Check if ip_address is a valid IPv4 representation.
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

    def get_url(self, function):
        """Get entry point for function."""

        return 'http://' + self.host + '/cgi-bin/' + function + '_cgi'

    def query(self, url, method='GET', extra_params=None):
        """Query data from Beward device."""

        if self.debug:
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
                req = requests.get(url, params=urlencode(params),
                                   auth=auth)
            # elif method == 'PUT':
            #     req = requests.put(url, params=urlencode(params),
            #                        auth=auth)
            # elif method == 'POST':
            #     req = requests.post(url, params=urlencode(params),
            #                         auth=auth, json=json)
            else:
                raise ValueError('Unknown method: %s' % method)

            if self.debug:
                _LOG.debug("_query ret %s", req.status_code)

        except Exception as err_msg:
            _LOG.error("Error! %s", err_msg)
            raise

        if req.status_code == 200 or req.status_code == 204:
            # if raw, return session object otherwise return JSON
            response = req

        if self.debug and response is None:
            _LOG.debug("%s", MSG_GENERIC_FAIL)
        return response

    def handle_alerts(self, date_time, alert, status):
        """Handle alerts from Beward device."""

        if self.debug:
            _LOG.debug("Time: %s; Alert: %s; Status: %s", date_time, alert,
                       status)

    def listen_alerts(self, channel=0, alerts=None):
        """Listen for alerts from Beward device."""

        def listener():
            resp = requests.get(url, params=urlencode(params), auth=auth,
                                stream=True)
            if self.debug:
                _LOG.debug("_query ret %s", resp.status_code)

            if resp.status_code == 200:
                for line in resp.iter_lines(chunk_size=1, decode_unicode=True):
                    if line:
                        if self.debug:
                            _LOG.debug("Alert: %s", line)

                        # 2019-07-28;00:57:27;MotionDetection;1;0
                        # 2019-07-28;00:57:28;MotionDetection;0;0
                        date, time, alert, status, _ = str(line).split(';', 5)
                        date_time = datetime.strptime(date + ' ' + time,
                                                      '%Y-%m-%d %H:%M:%S')
                        status = int(status)

                        self.handle_alerts(date_time, alert, status)

        if alerts is None:
            alerts = {}

        url = self.get_url('alarmchangestate')

        if self.debug:
            _LOG.debug("Querying %s", url)

        params = self.params
        params.update({
            'channel': channel,
            'parameter': ';'.join(alerts),
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
            _LOG.debug("Return from listen_alerts()")
