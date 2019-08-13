# -*- coding: utf-8 -*-

"""Utilites."""

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import re


def normalize_fqdn(hostname) -> str:
    """Normalize full qualified domain name."""
    # Convert unicode hostname to punycode and
    # remove the port number from hostname
    hostname = hostname.encode("idna").decode().split(":")[0]

    # Strip exactly one dot from the right, if present
    if hostname[-1] == ".":
        hostname = hostname[:-1]

    return hostname


def is_valid_fqdn(hostname) -> bool:
    """Validate full qualified domain name."""
    hostname = normalize_fqdn(hostname)
    if not hostname or len(hostname) > 253:
        return False
    dn_seq = hostname.split('.')
    if re.match(r'[0-9]+$', dn_seq[-1]):
        return False
    ldh_re = re.compile(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
    return all(ldh_re.match(x) for x in dn_seq)
