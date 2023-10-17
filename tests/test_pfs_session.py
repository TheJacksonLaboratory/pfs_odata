from unittest import TestCase, mock
from unittest.mock import MagicMock
import sys
import os
import requests
from requests.exceptions import RequestException
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from pfs import pfs_session, pfs_exceptions, models


class Testpfs_session(TestCase):

    def setUp(self) -> None:
        self.pfs_session = pfs_session.pfs_session(
            hostname="jacksonlabstest.platformforscience.com",
            tenant="DEV_KOMP",
            username="svc-limsdb@jax.org",
            password="vA&ce3(ROzAL"
        )
        self.response = requests.Response()

    def test_good_send_request(self):
        self.response.status_code = 200
        self.response._content = "{}".encode()

        with mock.patch("requests.request", return_value=self.response):
            result = self.pfs_session.send_request(url="", http_method="GET", payload={})
            self.assertIsInstance(result, models.pfsHttpResult)

    """
    def test_authenticate(self):
        self.fail()

    def test_get_experiment(self):
        self.fail()

    def test_get_assay(self):
        self.fail()

    def test_get_meavals(self):
        self.fail()

    def test_get_meavals_by_expr(self):
        self.fail()

    def test_get_meavals_by_strain(self):
        self.fail()

    def test_get_sample_lot(self):
        self.fail()

    def test_get_strain(self):
        self.fail()
    
    """