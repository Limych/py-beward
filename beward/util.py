# -*- coding: utf-8 -*-

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import re


def normalize_fqdn(dn) -> str:
    """Normalize full qualified domain name."""
    # Convert unicode hostname to punycode and
    # remove the port number from hostname
    dn = dn.encode("idna").decode().split(":")[0]

    # Strip exactly one dot from the right, if present
    if dn[-1] == ".":
        dn = dn[:-1]

    return dn


def is_valid_fqdn(dn) -> bool:
    """Validate full qualified domain name."""
    dn = normalize_fqdn(dn)
    if len(dn) < 1 or len(dn) > 253:
        return False
    dn_seq = dn.split('.')
    if re.match(r'[0-9]+$', dn_seq[-1]):
        return False
    ldh_re = re.compile(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
    return all(ldh_re.match(x) for x in dn_seq)
