# -*- coding: utf-8 -*-

"""Beward camera controller."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging

from requests import ConnectTimeout

from beward.const import ALARM_MOTION
from .core import BewardGeneric

_LOGGER = logging.getLogger(__name__)


# pylint: disable=R0902,R0904
class BewardCamera(BewardGeneric):
    """Beward camera controller class."""

    def __init__(self, host_ip, username, password, stream=0, **kwargs):
        super().__init__(host_ip, username, password, **kwargs)

        self.last_motion_timestamp = None
        self.last_motion_image = None

        self._stream = stream
        self._live_image_url = None
        self._rtsp_live_video_url = None

    def obtain_uris(self):
        """Set the URIs for the camera."""

        self._live_image_url = self.get_url(
            'images',
            extra_params={
                'channel': 0,
            },
            # Add authentication data
            username=self.username,
            password=self.password,
        )

        try:
            info = self.get_info('rtsp')
            url = 'rtsp://%s:%s@%s:%s/av0_%d' % (
                self.username, self.password,
                self.host, info.get('RtspPort', 554),
                self._stream,
            )
            self._rtsp_live_video_url = url
        except ConnectTimeout:
            pass

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""

        super()._handle_alarm(timestamp, alarm, state)

        if alarm == ALARM_MOTION and state == 1:
            self.last_motion_timestamp = timestamp
            self.last_motion_image = self.live_image

    @property
    def live_image(self):
        """Return bytes of camera image."""

        res = self.query('images', extra_params={'channel': 0})

        if not res.headers.get('Content-Type') in ('image/jpeg', 'image/png'):
            return None

        return res.content

    @property
    def live_image_url(self):
        """Return URL to get live photo from camera."""

        if not self._live_image_url:
            self.obtain_uris()
        return self._live_image_url

    @property
    def rtsp_live_video_url(self):
        """Return URL to get live video from camera via RTSP protocol."""

        if not self._live_image_url:
            self.obtain_uris()
        return self._rtsp_live_video_url
