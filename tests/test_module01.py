from multiprocessing import Process
from unittest import TestCase

from anyd import Appd, ClientSession

ADDRESS = ("localhost", 5000)
appd = Appd(ADDRESS)


@appd.api
def get_sum(arg1: int, arg2: int) -> int:
    """Exposed method is available to client"""
    return arg1 + arg2


@appd.api
def no_args_action():
    return True


class TestClass01(TestCase):
    """The main test for the unix_daemon_framework.core.BaseServer
    and the unix_daemon_framework.core.ClientSession"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.process = Process(target=appd.start)
        cls.process.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.process.terminate()

    def test_case01(self):
        "Server is running"
        self.assertTrue(self.process.is_alive())

    def test_case02(self):
        """Normal request"""
        with ClientSession(ADDRESS) as client:
            response = client.commit("get_sum", 1, 2)
        self.assertEqual(3, response)

    # def test_case03(self):
    #     """Not exposed method request"""
    #     with self.assertRaises(NotImplementedError):
    #         with ClientSession(ADDRESS) as client:
    #             client.commit("helper")

    # def test_case04(self):
    #     """Internal method request"""
    #     with self.assertRaises(ValueError):
    #         with ClientSession(self.server_address) as client:
    #             client.commit("__str__")

    def test_case03(self):
        """Multiple requests per Clientsession"""
        with ClientSession(ADDRESS) as client:
            response = client.commit("get_sum", 2, 2)
            self.assertEqual(4, response)
            response = client.commit("get_sum", 12, response)
            self.assertEqual(16, response)

    def test_case04(self):
        """Querying function with no arguments"""
        with ClientSession(ADDRESS) as client:
            response = client.commit("no_args_action")
        self.assertTrue(response)
