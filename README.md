*Please :star: this repo if you find it useful*

# py-beward

[![PyPI version][pypi-shield]][pypi]
[![PyPI Python version][pypi-pyversion]][pypi]
[![Maintained][Maintained]](#)

[![Project Maintenance][maintainer-shield]][maintainer]

_Python API for Beward Cameras and Doorbells. This is used in [Home Assistant component](https://github.com/Limych/ha-beward/) but should be generic enough that can be used elsewhere._

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

We have set up a separate document containing our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this library is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

[contributors]: https://github.com/Limych/py-beward/graphs/contributors
[license]: https://github.com/Limych/ha-beward/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintained]: https://img.shields.io/maintenance/yes/2021.svg?style=popout
[maintainer]: https://github.com/Limych
[maintainer-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[pypi]: https://pypi.org/project/beward/
[pypi-pyversion]: https://img.shields.io/pypi/pyversions/beward.svg?style=popout
[pypi-shield]: https://img.shields.io/pypi/v/beward.svg?style=popout
