# pylint: disable=protected-access,redefined-outer-name,no-value-for-parameter
"""Test to verify that Beward library works."""

from unittest import TestCase

import requests_mock

from beward import Beward, BewardDoorbell

from . import function_url
from .const import MOCK_HOST, MOCK_PASS, MOCK_USER


class TestBeward(TestCase):
    """Test case for Beward class."""

    @requests_mock.Mocker()
    def test_factory(self, mock):
        """Test that factory method works."""
        mock.register_uri(
            "get", function_url("systeminfo"), text="DeviceModel=NONEXISTENT"
        )

        try:
            Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
            self.fail()
        except ValueError:
            pass

        # TODO: BewardCamera; pylint: disable=fixme
        # mock.register_uri("get", function_url('systeminfo'),
        #                   text='DeviceModel=????')
        #
        # res = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        # self.assertTrue(isinstance(res, BewardCamera))

        mock.register_uri("get", function_url("systeminfo"), text="DeviceModel=DS06M")

        bwd = Beward.factory(MOCK_HOST, MOCK_USER, MOCK_PASS)
        self.assertTrue(isinstance(bwd, BewardDoorbell))
