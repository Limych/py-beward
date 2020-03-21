*Please :star: this repo if you find it useful*

# py-beward

[![Build Status](https://img.shields.io/travis/Limych/py-beward.svg?style=popout)](https://travis-ci.org/Limych/py-beward)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Limych/py-beward.svg?style=popout)](https://github.com/Limych/py-beward/commits/master)
[![](https://img.shields.io/github/last-commit/Limych/py-beward.svg?style=popout)](https://github.com/Limych/py-beward/commits/master)
[![License](https://img.shields.io/pypi/l/beward?style=popout)](LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/beward?style=popout)](https://pypi.org/project/beward/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beward?style=popout)](https://pypi.org/project/beward/)
[![Coverage Status](https://img.shields.io/coveralls/github/Limych/py-beward?style=popout)](https://coveralls.io/github/Limych/py-beward)
![Requires.io](https://img.shields.io/requires/github/Limych/py-beward)

![Project Maintenance](https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout)

[![GitHub pull requests](https://img.shields.io/github/issues-pr/Limych/py-beward?style=popout)](https://github.com/Limych/py-beward/pulls)
[![Bugs](https://img.shields.io/github/issues/Limych/py-beward/bug.svg?colorB=red&label=bugs&style=popout)](https://github.com/Limych/py-beward/issues?q=is%3Aopen+is%3Aissue+label%3ABug)

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

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok][limych].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

[limych]: https://github.com/Limych
[contributors]: https://github.com/Limych/py-beward/graphs/contributors
