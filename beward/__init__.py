#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""Python API for Beward Cameras and Doorbells."""

import logging
import struct
from collections import namedtuple

import hexdump
from _socket import (
    AF_INET,
    SO_BROADCAST,
    SO_REUSEADDR,
    SOCK_DGRAM,
    SOL_SOCKET,
    inet_ntoa,
    socket,
    timeout,
)

# Will be parsed by setup.py to determine package metadata
from beward.camera import BewardCamera
from beward.const import BEWARD_CAMERA, BEWARD_DOORBELL, STARTUP_MESSAGE
from beward.core import BewardGeneric
from beward.doorbell import BewardDoorbell

# You really should not `import *` - it is poor practice
# but if you do, here is what you get:
__all__ = [
    "Beward",
    "BewardGeneric",
    "BewardCamera",
    "BewardDoorbell",
]

_LOGGER = logging.getLogger(__name__)
#
# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
_LOGGER.addHandler(logging.NullHandler())
#
_LOGGER.info(STARTUP_MESSAGE)


# pylint: disable=too-few-public-methods
class Beward:
    """Beward device factory class."""

    @staticmethod
    def discovery():  # pragma: no cover
        """Discover Beward devices in local network."""
        server = socket(AF_INET, SOCK_DGRAM)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        server.bind(("0.0.0.0", 0))
        server.settimeout(1)

        _LOGGER.debug("Start discovery")
        server.sendto(
            b"\x67\x45\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            ("255.255.255.255", 59123),
        )

        devices = {}
        while True:
            try:
                data = server.recvfrom(1024)
                _LOGGER.debug(
                    "Discovery response data:\n%s",
                    hexdump.hexdump(data[0][28:], result="return"),
                )

                (
                    # packet header (28 bytes):
                    # "\x67\x45\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x48\x02\x00\x00" (packet data length) = 584
                    # packet data (584 bytes):
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00"
                    device_id,  # "\x5f\x06\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03"
                    # "\x21\x00\x00"
                    name,  # "\x49\x50\x43\x31\x37\x32\x34\x00\x00\x00\x00..."
                    host_ip,  # "\x5a\x01\xa8\xc0"
                    mac,  # "\x00\x5a\x22\x30\x07\x5f"
                    http_port,  # "\x50\x00"
                    data_port,  # "\x88\x13"
                    # "\x00\x00"
                    net_mask,  # "\x00\xff\xff\xff"
                    gate_ip,  # "\x01\x01\xa8\xc0"
                    # "\x01\x08\x37\xe0"
                    # "\x01\x01\xa8\xc0" (gate_ip)
                    # "\x88\x13" (data_port)
                    # "\x00\x00\x01\x00\x00\x00"
                    # "\x5a\x01\xa8\xc0" (host_ip)
                    # "\x00\xff\xff\xff" "\x01\x01\xa8\xc0" (net_mask + gate_ip)
                    # "\x88\x13" "\x50\x00" (data_port + http_port)
                    # "\x01\x08\x37\xe0"
                    # "\x88\x13" (data_port)
                    # "\x00\x5a\x22\x30\x07\x5f" (mac)
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x02\x30\x75"
                    # "\x50\x00" "\x88\x13" (http_port + data_port)
                    # "\x00\x00"
                    # "\x01\x01\xa8\xc0" (gate_ip = dns1_ip?)
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x70\x17\x37\x01\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00"
                    # "\x08\x08\x08\x08" (dns2_ip)
                    # "\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00"
                    # "\x00\x00\x00\x00\x01\x00"
                    # "\xa0\x01\xa8\xc0" (ip?)
                    # "\x00\xff\xff\xff" "\x01\x01\xa8\xc0" (net_mask + gate_ip)
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    # "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x38\x71\x32\x4d"
                    # "\x75\x49\x62\x6d\x7a\x32\x67\x66\x4c\x5a\x35\x70\x6d\x42\x54\x51"
                    # "\x49\x69\x49\x77\x6f\x37\x63\x71\x6c\x4e\x64\x30"
                ) = struct.unpack("<45xL19x64sI6s2H2x2I", data[0][:156])
                name = name.replace(b"\x00", b"").decode("utf-8")

                def _unpack_ip(ip_addr):
                    return inet_ntoa(struct.pack(">I", ip_addr))

                (host_ip, net_mask, gate_ip) = (
                    _unpack_ip(host_ip),
                    _unpack_ip(net_mask),
                    _unpack_ip(gate_ip),
                )
                mac = ":".join("%02x" % i for i in mac)

                _LOGGER.info(
                    "Discovered %s (ID: %d) at http://%s:%d",
                    name,
                    device_id,
                    host_ip,
                    http_port,
                )

                if mac not in devices:
                    dev = {
                        "device_id": device_id,
                        "name": name,
                        "host_ip": host_ip,
                        "http_port": http_port,
                        "data_port": data_port,
                        "mac": mac,
                        "net_mask": net_mask,
                        "gate_ip": gate_ip,
                    }
                    devices[mac] = namedtuple("BewardDevice", dev.keys())(*dev.values())

            except Exception as err:  # pylint: disable=broad-except
                if not isinstance(err, timeout):
                    _LOGGER.debug(err)
                break

        _LOGGER.debug("Stop discovery")
        server.close()

        return devices

    @staticmethod
    def factory(host_ip: str, username: str, password: str, **kwargs):
        """Return correct class for device."""
        bwd = BewardGeneric(host_ip, username, password)
        model = bwd.system_info.get("DeviceModel")
        dev_type = bwd.get_device_type(model)

        if dev_type is None:
            raise ValueError('Unknown device "%s"' % model)

        inst = None

        if dev_type == BEWARD_CAMERA:
            inst = BewardCamera(host_ip, username, password, **kwargs)

        elif dev_type == BEWARD_DOORBELL:
            inst = BewardDoorbell(host_ip, username, password, **kwargs)

        _LOGGER.debug("Factory create instance of %s", inst.__class__)
        return inst
