#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""Constants."""

from importlib import metadata

# Base library constants
VERSION = "1.1.14"

mdata = metadata.metadata(__package__)

URLS = dict(x.split(", ") for x in mdata.get_all("Project-URL"))

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{mdata["Summary"]}
Version: {mdata["Version"]}
If you have ANY issues with this you need to open an issue here:
{URLS["Issues"]}
-------------------------------------------------------------------
"""

TIMEOUT = 3

# Error strings
MSG_GENERIC_FAIL = "Sorry.. Something went wrong..."

# Alarms
ALARM_ONLINE = "DeviceOnline"
ALARM_MOTION = "MotionDetection"
ALARM_SENSOR = "SensorAlarm"
ALARM_SENSOR_OUT = "SensorOutAlarm"

# Device types
BEWARD_CAMERA = "camera"
BEWARD_DOORBELL = "doorbell"

# Beward models
BEWARD_MODELS = {
    BEWARD_CAMERA: "B102S",
    BEWARD_DOORBELL: "ALP-600 DC11EP DK103 DK103M DKS20210 DS03M DS05M(P) DS06 DS06M "
    "DS06A(P) DS07P-LP DSN06PS DSN23215PS S06A S06M",
}
