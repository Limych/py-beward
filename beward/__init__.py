# -*- coding: utf-8 -*-

"""Beward devices controller."""

import logging

from .core import BewardGeneric

# Will be parsed by setup.py to determine package metadata
__author__ = 'Andrey "Limych" Khrolenok <andrey@khrolenok.ru>'
# Please add the suffix "+" to the version after release, to make it
# possible infer whether in development code from the version string
__version__ = '0.0.1'
__website__ = 'https://github.com/Limych/python-beward'
__license__ = 'Creative Commons BY-NC-SA License'

# You really should not `import *` - it is poor practice
# but if you do, here is what you get:
__all__ = [
    'BewardGeneric',
]

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user

logging.getLogger(__name__).addHandler(logging.NullHandler())
