# -*- coding: utf-8 -*-

"""Beward camera controller."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging

from beward.const import ALARM_MOTION
from .core import BewardGeneric

_LOGGER = logging.getLogger(__name__)


# pylint: disable=R0902,R0904
class BewardCamera(BewardGeneric):
    """Beward camera controller class."""

    def __init__(self, host_ip, username, password):
        super().__init__(host_ip, username, password)

        self.last_motion_timestamp = None
        self.last_motion_image = None

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""

        super()._handle_alarm(timestamp, alarm, state)

        if alarm == ALARM_MOTION and state == 1:
            self.last_motion_timestamp = timestamp
            self.last_motion_image = self.camera_image()

    def camera_image(self):
        """Return bytes of camera image."""

        res = self.query('images', extra_params={'channel': 0})

        if not res.headers.get('Content-Type') in ('image/jpeg', 'image/png'):
            return None

        return res.content
