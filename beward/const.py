"""Constants."""

#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

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
    BEWARD_CAMERA: "",
    BEWARD_DOORBELL: "DK103M DS03M DS05M(P) DS06M DS06A(P) S06A S06M",
}
