from multiprocessing import Process
from multiprocessing.context import AuthenticationError
from unittest import TestCase

from anyd import Appd, ClientSession

ADDRESS = ("localhost", 5001)
AUTHKEY = b"dog"
appd = Appd(ADDRESS, authkey=AUTHKEY)


@appd.api
def echo(arg1: str) -> str:
    """Exposed method is available to client"""
    return arg1


class TestClass01(TestCase):
    """Authentication facilities"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.process = Process(target=appd.start)
        cls.process.start()

    def test_case01(self):
        self.assertTrue(self.process.is_alive())

    def test_case02(self):
        """Normal request"""
        with ClientSession(ADDRESS, authkey=AUTHKEY) as client:
            response = client.commit("echo", "hello")
        self.assertEqual("hello", response)

    def test_case03(self):
        """Wrong authentication key"""
        with self.assertRaises(AuthenticationError):
            with ClientSession(ADDRESS, authkey=b"fish") as client:
                client.commit("echo", "hello")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.process.terminate()


class TestClass03(TestCase):
    """No server running"""

    def test_case01(self):
        with self.assertRaises(ConnectionRefusedError):
            with ClientSession(("localhost", 3000)) as client:
                client.commit("echo", "hello")
