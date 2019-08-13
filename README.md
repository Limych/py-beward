*Please :star: this repo if you find it useful*

# py-beward

[![Build Status](https://img.shields.io/travis/Limych/py-beward.svg?style=popout)](https://travis-ci.org/Limych/py-beward)
[![](https://img.shields.io/github/last-commit/Limych/py-beward.svg?style=popout)](https://github.com/Limych/py-beward/commits/master)
[![License](https://img.shields.io/badge/license-CC--by--ns--sa-green.svg?style=popout)](LICENSE.md)
[![Coverage Status](https://img.shields.io/coveralls/github/Limych/py-beward?style=popout)](https://coveralls.io/github/Limych/py-beward)
![Requires.io](https://img.shields.io/requires/github/Limych/py-beward)

![Project Maintenance](https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout)

[![](https://img.shields.io/github/issues/Limych/py-beward/bug.svg?colorB=red&label=bugs&style=popout)](https://github.com/Limych/py-beward/issues?q=is%3Aopen+is%3Aissue+label%3ABug)

Python API for Beward Cameras and Doorbells. This is used in [Home Assistant component](https://github.com/Limych/ha-beward/) but should be generic enough that can be used elsewhere.

## Installation

```bash
pip install beward
```

## Usage example

```python
import time

from beward import Beward
from beward.const import ALARM_ONLINE, ALARM_MOTION, ALARM_SENSOR


def handler(device, timestamp, alarm, state):
    print('Handling alarm "%s". State: %d' % (alarm, state))


DEVICE_HOST = '192.168.1.100'
DEVICE_USER = 'admin'
DEVICE_PASS = 'password'

bwd = Beward.factory(DEVICE_HOST, DEVICE_USER, DEVICE_PASS, stream=1)
bwd.add_alarms_handler(handler)
bwd.listen_alarms(alarms=(ALARM_ONLINE, ALARM_MOTION, ALARM_SENSOR))

print('Live image URL:', bwd.live_image_url)
print('RTSP live video URL:', bwd.rtsp_live_video_url)
print('Live image:', bwd.camera_image())

for decade in range(10):
    print('Time: %ds' % (decade * 10))
    time.sleep(10)
print('Bye')
```
