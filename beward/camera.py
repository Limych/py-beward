"""Beward camera controller."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging
from typing import Optional

from beward.const import ALARM_MOTION
from requests import ConnectTimeout

from .core import BewardGeneric

_LOGGER = logging.getLogger(__name__)


class BewardCamera(BewardGeneric):
    """Beward camera controller class."""

    # pylint: disable=too-many-arguments
    def __init__(self, host, username, password, rtsp_port=None, stream=0, **kwargs):
        """Initialize Beward camera controller."""
        super().__init__(host, username, password, **kwargs)

        self.last_motion_timestamp = None
        self.last_motion_image = None

        self.rtsp_port = rtsp_port
        self.stream = stream

        self._live_image_url = None
        self._rtsp_live_video_url = None

    def obtain_uris(self):
        """Set the URIs for the camera."""

        self._live_image_url = self.get_url(
            "images",
            extra_params={"channel": 0},
            # Add authentication data
            username=self.username,
            password=self.password,
        )

        if not self.rtsp_port:
            try:
                info = self.get_info("rtsp")
                self.rtsp_port = info.get("RtspPort", 554)
            except ConnectTimeout:
                self.rtsp_port = 554

        url = "rtsp://%s:%s@%s:%s/av0_%d" % (
            self.username,
            self.password,
            self.host,
            self.rtsp_port,
            self.stream,
        )
        self._rtsp_live_video_url = url

    @property
    def live_image_url(self) -> str:
        """Return URL to get live photo from camera."""
        if not self._live_image_url:
            self.obtain_uris()
        return self._live_image_url

    @property
    def rtsp_live_video_url(self) -> str:
        """Return URL to get live video from camera via RTSP protocol."""
        if not self._live_image_url:
            self.obtain_uris()
        return self._rtsp_live_video_url

    @property
    def live_image(self) -> Optional[bytes]:
        """Return bytes of camera image."""
        res = self.query("images", extra_params={"channel": 0})

        if not res.headers.get("Content-Type") in ("image/jpeg", "image/png"):
            return None

        return res.content

    def _handle_alarm(self, timestamp, alarm, state):
        """Handle alarms from Beward device."""
        super()._handle_alarm(timestamp, alarm, state)

        if alarm == ALARM_MOTION and state:
            self.last_motion_timestamp = timestamp
            self.last_motion_image = self.live_image
