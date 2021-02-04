"""Python API for Beward Cameras and Doorbells."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import logging

# Will be parsed by setup.py to determine package metadata
from beward.camera import BewardCamera
from beward.const import BEWARD_CAMERA, BEWARD_DOORBELL
from beward.core import BewardGeneric
from beward.doorbell import BewardDoorbell

__author__ = 'Andrey "Limych" Khrolenok <andrey@khrolenok.ru>'
# Please add the suffix "+" to the version after release, to make it
# possible infer whether in development code from the version string
__version__ = "1.0.12"
__website__ = "https://github.com/Limych/py-beward"
__license__ = "Creative Commons BY-NC-SA License"

VERSION = __version__

# You really should not `import *` - it is poor practice
# but if you do, here is what you get:
__all__ = [
    "Beward",
    "BewardGeneric",
    "BewardCamera",
    "BewardDoorbell",
]

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Beward:
    """Beward device factory class."""

    @staticmethod
    def factory(host_ip, username, password, **kwargs):
        """Return correct class for device."""
        bwd = BewardGeneric(host_ip, username, password)
        model = bwd.system_info.get("DeviceModel")
        dev_type = bwd.get_device_type(model)
        inst = None

        if dev_type is None:
            raise ValueError('Unknown device "%s"' % model)

        if dev_type == BEWARD_CAMERA:
            inst = BewardCamera(host_ip, username, password, **kwargs)

        if dev_type == BEWARD_DOORBELL:
            inst = BewardDoorbell(host_ip, username, password, **kwargs)

        _LOGGER.debug("Factory create instance of %s", inst.__class__)
        return inst
