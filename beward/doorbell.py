# -*- coding: utf-8 -*-

"""Beward doorbell controller."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging
import warnings

from beward.const import ALARM_SENSOR
from .camera import BewardCamera

_LOGGER = logging.getLogger(__name__)


class BewardDoorbell(BewardCamera):
    """Beward doorbell controller class."""

    def __init__(self, host, username, password, **kwargs):
        super().__init__(host, username, password, **kwargs)

        self._ding_image = None

    def _handle_alarm(self, timestamp, alarm, state, channel=0):
        """Handle alarms from Beward device."""
        super()._handle_alarm(timestamp, alarm, state, channel)

        if alarm == ALARM_SENSOR and state:
            self._ding_image = self.live_image

    @property
    def ding(self):
        """Get ding alarm state"""
        return self.alarm_state.get(ALARM_SENSOR)

    @property
    def ding_timestamp(self):
        """Get last ding alarm timestamp"""
        return self.alarm_on_timestamp.get(ALARM_SENSOR)

    @property
    def last_ding_timestamp(self):  # pragma: no cover
        """Get last ding alarm timestamp"""
        warnings.warn('The "last_ding_timestamp" property was renamed '
                      'to "ding_timestamp"', DeprecationWarning)
        return self.ding_timestamp

    @property
    def ding_image(self):
        """Get last ding alarm image"""
        return self._ding_image

    @property
    def last_ding_image(self):  # pragma: no cover
        """Get last ding alarm image"""
        warnings.warn('The "last_ding_image" property was renamed '
                      'to "ding_image"', DeprecationWarning)
        return self.ding_image
