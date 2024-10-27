# pylint: disable=protected-access,redefined-outer-name,no-value-for-parameter
"""Test to verify that Beward library works."""

import pytest
import requests_mock

from beward import Beward, BewardDoorbell

from . import function_url
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER


def test_factory():
    """Test that factory method works."""
    with requests_mock.Mocker() as mock:
        mock.register_uri(
            "get", function_url("systeminfo"), text="DeviceModel=NONEXISTENT"
        )

        with pytest.raises(ValueError):  # noqa: PT011
            Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)

        # ruff: noqa: ERA001, TD002
        # TODO: BewardCamera; pylint: disable=fixme
        # 123
        # mock.register_uri("get", function_url('systeminfo'),
        #                   text='DeviceModel=????')
        #
        # res = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        # assert isinstance(res, BewardCamera) is True

        mock.register_uri("get", function_url("systeminfo"), text="DeviceModel=DS06M")

        beward = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        assert isinstance(beward, BewardDoorbell) is True
