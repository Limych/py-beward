#!/usr/bin/env python
"""Library module setup."""

import re
from pathlib import Path

from setuptools import find_packages, setup


def load_requirements(fpath: str) -> list:
    """Load requirements from file."""
    with Path(fpath).open(encoding="utf8") as f_req:
        data = list(f_req)
    imp = re.compile(r"^(-r|--requirement)\s+(\S+)")
    reqs = []
    for i in data:
        # pylint: disable=invalid-name
        m = imp.match(i)
        if m:
            reqs.extend(load_requirements(m.group(2)))
        else:
            reqs.append(i)

    return reqs


PACKAGES = [x for x in find_packages() if x not in ["scripts", "tests"]]

with (Path(PACKAGES[0]) / "const.py").open(encoding="utf-8") as file:
    src = file.read()
metadata = dict(re.findall(r'([a-z]+) = "([^"]+)"', src, re.IGNORECASE))
metadata.update(dict(re.findall(r"([a-z]+) = '([^']+)'", src, re.IGNORECASE)))
docstrings = re.findall(r'"""(.*?)"""', src, re.MULTILINE | re.DOTALL)

VERSION = metadata["VERSION"]

REQUIREMENTS = load_requirements("requirements.txt")

setup(
    version=VERSION,
    packages=PACKAGES,
    install_requires=REQUIREMENTS,
)
