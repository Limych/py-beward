"""Constants."""

from importlib import metadata

# Base library constants
VERSION = "1.0.2.dev0"

mdata = metadata.metadata(__package__)

URLS = dict(x.split(", ") for x in mdata.get_all("Project-URL"))

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{mdata["Summary"]}
Version: {mdata["Version"]}
If you have ANY issues with this you need to open an issue here:
{URLS["Issues"]}
-------------------------------------------------------------------
"""
