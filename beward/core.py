#  Copyright (c) 2019-2023, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""Beward devices controller core."""

from __future__ import annotations

import contextlib
import logging
import re
import socket
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from time import sleep
from typing import Any, Protocol

import requests
from requests import ConnectTimeout, PreparedRequest, RequestException, Response
from requests.auth import HTTPBasicAuth

import beward
from beward.util import is_valid_fqdn, normalize_fqdn

from .const import ALARM_ONLINE, BEWARD_MODELS, MSG_GENERIC_FAIL, TIMEOUT

_LOGGER = logging.getLogger(__name__)

local_tz = datetime.now(timezone.utc).astimezone().tzinfo  # noqa: UP017


class AlarmHandlerCallback(Protocol):
    """Protocol type for BewardGeneric alarm handler callback."""

    def __call__(
        self,
        device: BewardGeneric,
        timestamp: datetime,
        alarm: str,
        state: bool,  # noqa: FBT001
    ) -> None:
        """Define add_entities type."""


class BewardGeneric:
    """Generic Implementation for Beward device."""

    _class_group = "Beward"

    @staticmethod
    def get_device_type(model: str | None) -> str | None:
        """Detect device type for model."""
        if not model:
            return None

        model = re.sub(r"_rev.+$", "", model)

        for dev_type, models in BEWARD_MODELS.items():
            if model in models.split():
                return dev_type

        return None

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int | str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Initialize generic Beward device controller."""
        beward.init()

        self._sysinfo = None
        self._listen_alarms = False
        self._listener = None

        if port is None:
            with contextlib.suppress(IndexError):
                port = host.split(":")[1]
        host = normalize_fqdn(host)
        try:
            if not is_valid_fqdn(host):
                socket.inet_aton(host)
        except OSError as exc:
            msg = "Not a valid host address"
            raise ValueError(msg) from exc

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
        self._alarm_listeners = []

    def __del__(self) -> None:
        """Destructor."""
        self._listen_alarms = False

        if self._listener:
            self._listener.join()

    def get_url(
        self,
        function: str,
        extra_params: dict | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> str:
        """Get entry point for function."""
        url = "http://"
        if username:
            url += username
            if password:
                url += ":" + password
            url += "@"
        url += f"{self.host}:{self.port}/cgi-bin/{function}_cgi"
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

    # pylint: disable=unsubscriptable-object
    def query(self, function: str, extra_params: dict | None = None) -> Response | None:
        """Query data from Beward device."""
        url = self.get_url(function)
        _LOGGER.debug("Querying %s", beward.redact_auth_from_url(url))

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

        except Exception:
            _LOGGER.exception("Error!")
            raise

        if req.status_code in (200, 204):
            response = req

        if response is None:  # pragma: no cover
            _LOGGER.debug(MSG_GENERIC_FAIL)
        return response

    def add_alarms_handler(self, handler: AlarmHandlerCallback) -> BewardGeneric:
        """Add alarms handler."""
        self._alarm_handlers.add(handler)
        return self

    def remove_alarms_handler(self, handler: AlarmHandlerCallback) -> BewardGeneric:
        """Remove alarms handler."""
        if handler in self._alarm_handlers:
            self._alarm_handlers.remove(handler)
            self._listen_alarms = len(self._alarm_handlers) != 0
        return self

    def _handle_alarm(self, timestamp: datetime, alarm: str, state: bool) -> None:  # noqa: FBT001
        """Handle alarms from Beward device."""
        _LOGGER.debug("Handle alarm: %s; State: %s", alarm, state)

        self.last_activity = timestamp
        self.alarm_timestamp[alarm] = timestamp
        self.alarm_state[alarm] = state

        for handler in self._alarm_handlers:  # type: AlarmHandlerCallback
            handler(self, timestamp, alarm, state)

    def listen_alarms(self, channel: int = 0, alarms: Any = None) -> None:
        """Listen for alarms from Beward device."""
        if alarms is None:  # pragma: no cover
            alarms = {}

        url = self.get_url("alarmchangestate")
        _LOGGER.debug("Querying %s", beward.redact_auth_from_url(url))

        params = self.params.copy()
        params.update({"channel": channel, "parameter": ";".join(set(alarms))})
        auth = HTTPBasicAuth(self.username, self.password)

        self._listen_alarms = len(self._alarm_handlers) != 0

        self._listener = threading.Thread(
            target=self.__alarms_listener, args=(url, params, auth), daemon=True
        )
        self._listener.start()
        self._alarm_listeners.append(self._listener)

        _LOGGER.debug("Return from listen_alarms()")

    def __alarms_listener(self, url: str, params: Any, auth: Any) -> None:
        while self._listen_alarms:
            try:
                resp = requests.get(
                    url, params=params, auth=auth, stream=True, timeout=10
                )
            except RequestException:  # pragma: no cover
                break
            _LOGGER.debug("_query ret %s", resp.status_code)

            if not self._listen_alarms:  # pragma: no cover
                break

            if resp.status_code != HTTPStatus.OK:  # pragma: no cover
                sleep(TIMEOUT)
                continue

            self._handle_alarm(datetime.now(local_tz), ALARM_ONLINE, state=True)

            for line in resp.iter_lines(chunk_size=1, decode_unicode=True):
                if not self._listen_alarms:  # pragma: no cover
                    break

                if line:
                    _LOGGER.debug("Alarm: %s", line)

                    date, time, alert, state, _ = str(line).split(";", 5)
                    timestamp = datetime.strptime(
                        date + " " + time, "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=local_tz)
                    state = state != "0"

                    self._handle_alarm(timestamp, alert, state)

            self._handle_alarm(datetime.now(local_tz), ALARM_ONLINE, state=False)

        self._handle_alarm(
            datetime.now(local_tz), ALARM_ONLINE, state=False
        )  # pragma: no cover

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
        with contextlib.suppress(ConnectTimeout):
            self._sysinfo = self.get_info("systeminfo")

        return self._sysinfo

    @property
    # pylint: disable=unsubscriptable-object
    def device_type(self) -> str | None:
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
