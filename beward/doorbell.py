# -*- coding: utf-8 -*-

"""Beward doorbell controller."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging

from beward.const import ALARM_SENSOR
from .camera import BewardCamera

_LOG = logging.getLogger(__name__)


# pylint: disable=R0902,R0904
class BewardDoorbell(BewardCamera):
    """Beward doorbell controller class."""

    def __init__(self, host_ip, username, password, debug=False):
        super().__init__(host_ip, username, password, debug)

        self.last_ding_timestamp = None
        self.last_ding_image = None

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""

        super()._handle_alarm(timestamp, alarm, state)

        if alarm == ALARM_SENSOR and state == 1:
            self.last_ding_timestamp = timestamp
            self.last_ding_image = self.camera_image()
