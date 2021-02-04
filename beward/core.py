"""Beward devices controller core."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

from datetime import datetime
import logging
import socket
import threading
from time import sleep
from typing import Optional

from beward.util import is_valid_fqdn, normalize_fqdn
import requests
from requests import ConnectTimeout, PreparedRequest, RequestException, Response
from requests.auth import HTTPBasicAuth

from .const import ALARM_ONLINE, BEWARD_MODELS, MSG_GENERIC_FAIL, TIMEOUT

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class BewardGeneric:
    """Generic Implementation for Beward device."""

    _class_group = "Beward"

    @staticmethod
    def get_device_type(model: Optional[str]) -> Optional[str]:
        """Detect device type for model."""
        if not model:
            return None

        for dev_type, models in BEWARD_MODELS.items():
            if model in models.split():
                return dev_type

        return None

    # pylint: disable=unused-argument
    def __init__(self, host: str, username: str, password: str, port=None, **kwargs):
        """Initialize generic Beward device controller."""
        if port is None:
            try:
                port = host.split(":")[1]
            except IndexError:
                pass
        host = normalize_fqdn(host)
        try:
            if not is_valid_fqdn(host):
                socket.inet_aton(host)
        except OSError as exc:
            raise ValueError("Not a valid host address") from exc

        self.host = host
        self.port = int(port) if port else 80
        self.username = username
        self.password = password
        self.session = requests.session()
        self.params = {}

        self.last_activity = None
        self.alarm_state = {
            ALARM_ONLINE: False,
        }
        self.alarm_timestamp = {
            ALARM_ONLINE: datetime.min,
        }
        self._alarm_handlers = set()

        self._sysinfo = None
        self._listen_alarms = False

    def get_url(
        self, function: str, extra_params=None, username=None, password=None
    ) -> str:
        """Get entry point for function."""
        url = "http://"
        if username:
            url += username
            if password:
                url += ":" + password
            url += "@"
        url += "%s:%d/cgi-bin/%s_cgi" % (self.host, self.port, function)
        if extra_params:
            url = self.add_url_params(url, extra_params)
        return url

    def add_url_params(self, url: str, extra_params: dict) -> str:
        """Add params to URL."""
        params = self.params.copy()
        params.update(extra_params)

        req = PreparedRequest()
        req.prepare_url(url, params)

        return req.url

    def query(self, function: str, extra_params=None) -> Optional[Response]:
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
            req = self.session.get(url, params=params, auth=auth, timeout=TIMEOUT)
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
        """Add alarms handler."""
        self._alarm_handlers.add(handler)
        return self

    def remove_alarms_handler(self, handler: callable):
        """Remove alarms handler."""
        if handler in self._alarm_handlers:
            self._alarm_handlers.remove(handler)
            self._listen_alarms &= self._alarm_handlers == set()
        return self

    def _handle_alarm(self, timestamp: datetime, alarm: str, state: bool):
        """Handle alarms from Beward device."""
        _LOGGER.debug("Handle alarm: %s; State: %s", alarm, state)

        self.last_activity = timestamp
        self.alarm_timestamp[alarm] = timestamp
        self.alarm_state[alarm] = state

        for handler in self._alarm_handlers:
            handler(self, timestamp, alarm, state)

    def listen_alarms(self, channel: int = 0, alarms=None):
        """Listen for alarms from Beward device."""
        if alarms is None:  # pragma: no cover
            alarms = {}

        url = self.get_url("alarmchangestate")
        _LOGGER.debug("Querying %s", url)

        params = self.params.copy()
        params.update({"channel": channel, "parameter": ";".join(set(alarms))})
        auth = HTTPBasicAuth(self.username, self.password)

        self._listen_alarms = len(self._alarm_handlers) != 0

        thread = threading.Thread(
            target=self.__alarms_listener, args=(url, params, auth), daemon=True
        )
        thread.start()

        _LOGGER.debug("Return from listen_alarms()")

    def __alarms_listener(self, url: str, params, auth):
        while True:
            try:
                resp = requests.get(url, params=params, auth=auth, stream=True)
            except RequestException:  # pragma: no cover
                break
            _LOGGER.debug("_query ret %s", resp.status_code)

            if not self._listen_alarms:  # pragma: no cover
                break

            if resp.status_code != 200:  # pragma: no cover
                sleep(TIMEOUT)
                continue

            self._handle_alarm(datetime.now(), ALARM_ONLINE, True)

            for line in resp.iter_lines(chunk_size=1, decode_unicode=True):
                if line:
                    _LOGGER.debug("Alarm: %s", line)

                    date, time, alert, state, _ = str(line).split(";", 5)
                    timestamp = datetime.strptime(
                        date + " " + time, "%Y-%m-%d %H:%M:%S"
                    )
                    state = state != "0"

                    self._handle_alarm(timestamp, alert, state)

            self._handle_alarm(datetime.now(), ALARM_ONLINE, False)

        self._handle_alarm(datetime.now(), ALARM_ONLINE, False)  # pragma: no cover

    def get_info(self, function: str) -> dict:
        """Get info from Beward device."""
        info = {}
        data = self.query(function, extra_params={"action": "get"}).text
        for env in data.splitlines():
            (key, val) = env.split("=", 2)
            info[key] = val

        return info

    @property
    def system_info(self) -> dict:
        """Get system info from Beward device."""
        if self._sysinfo:
            return self._sysinfo

        self._sysinfo = {}
        try:
            self._sysinfo = self.get_info("systeminfo")
        except ConnectTimeout:
            pass

        return self._sysinfo

    @property
    def device_type(self) -> Optional[str]:
        """Detect device type."""
        return self.get_device_type(self.system_info.get("DeviceModel"))

    @property
    def is_online(self) -> bool:
        """Return True if entity is online."""
        try:
            self.query("systeminfo")
        except ConnectTimeout:
            return False

        return True

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.is_online
