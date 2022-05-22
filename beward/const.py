#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""Constants."""

# Base library constants
NAME = "Beward Client"
VERSION = "1.1.6"
AUTHOR = 'Andrey "Limych" Khrolenok <andrey@khrolenok.ru>'
LICENSE = "Creative Commons BY-NC-SA License"
WEBSITE = "https://github.com/Limych/py-beward"
ISSUE_URL = "https://github.com/Limych/py-beward/issues"
NEW_DEVICE_ISSUE_URL = "https://github.com/Limych/py-beward/issues/new?assignees=&labels=enhancement&template=new_device.md&title="

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
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
    BEWARD_DOORBELL: "ALP-600 DK103 DK103M DKS20210 DS03M DS05M(P) DS06M DS06A(P) "
    "DSN06PS S06A S06M",
}
