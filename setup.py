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


with Path("beward/const.py").open(encoding="utf-8") as file:
    src = file.read()
metadata = dict(re.findall(r'([a-z]+) = "([^"]+)"', src, re.IGNORECASE))
metadata.update(dict(re.findall(r"([a-z]+) = '([^']+)'", src, re.IGNORECASE)))
docstrings = re.findall(r'"""(.*?)"""', src, re.MULTILINE | re.DOTALL)

NAME = "beward"

PACKAGES = [x for x in find_packages() if x not in ["scripts", "tests"]]

VERSION = metadata["VERSION"]
AUTHOR_EMAIL = metadata.get("AUTHOR", "Unknown <no@email.com>")
WEBSITE = metadata.get("WEBSITE", "")
LICENSE = metadata.get("LICENSE", "")
DESCRIPTION = docstrings[0]

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Home Automation",
    "Topic :: Security",
    "Topic :: Multimedia :: Video :: Capture",
]

with Path("README.md").open(encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()
    LONG_DESCRIPTION_TYPE = "text/markdown"

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r"(.*) <(.*)>", AUTHOR_EMAIL).groups()

REQUIREMENTS = load_requirements("requirements.txt")
TEST_REQUIREMENTS = load_requirements("requirements-test.txt")

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    license=LICENSE,
    url=WEBSITE,
    packages=PACKAGES,
    install_requires=REQUIREMENTS,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    classifiers=CLASSIFIERS,
)
