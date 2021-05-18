import time
from multiprocessing import Process
from multiprocessing.context import AuthenticationError
from unittest import TestCase

from sockets_framework import BaseServer, Session


class Server(BaseServer):
    """Testing server

    Args:
        BaseServer ([type]): sockets_framework.core.BaseServer
    """

    arg3 = 0

    def get_sum(self, arg1: int, arg2: int) -> int:
        """Normal targeting method

        Args:
            arg1 (int): [description]
            arg2 (int): [description]

        Returns:
            int: [description]
        """
        return arg1 + arg2 + self.arg3

    def __str__(self) -> str:
        """Should not be exposed"""

    def no_args_action(self):
        return True


class TestClass01(TestCase):
    """The main test for the sockets_framework.core.BaseServer
    and the sockets_framework.core.Session"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.server_address = ("localhost", 4000)
        cls.server = Server(cls.server_address)
        cls.server_process = Process(target=cls.server.start)
        cls.server_process.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_process.terminate()

    def test_case01(self):
        "Server is running"
        self.assertTrue(self.server_process.is_alive())

    def test_case02(self):
        """Normal request"""
        with Session(self.server_address) as client:
            response = client.commit("get_sum", 1, 2)
        self.assertEqual(3, response)

    def test_case03(self):
        """Not implemented request"""
        with self.assertRaises(NotImplementedError):
            with Session(self.server_address) as client:
                client.commit("unimplemented_method")

    def test_case04(self):
        """Internal method request"""
        with self.assertRaises(ValueError):
            with Session(self.server_address) as client:
                client.commit("__str__")

    def test_case05(self):
        """Multiple requests per session"""
        with Session(self.server_address) as client:
            response = client.commit("get_sum", 2, 2)
            self.assertEqual(4, response)
            response = client.commit("get_sum", 12, response)
            self.assertEqual(16, response)

    def test_case06(self):
        """Querying function with no arguments"""
        with Session(self.server_address) as client:
            response = client.commit("no_args_action")
        self.assertTrue(response)


class TestClass02(TestCase):
    """Authentication facilities"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.authkey = b"dog"
        cls.server_address = ("localhost", 5000)
        cls.server = Server(cls.server_address, authkey=cls.authkey)
        cls.server_process = Process(target=cls.server.start)
        cls.server_process.start()

    def test_case01(self):
        self.assertTrue(self.server_process.is_alive())

    def test_case02(self):
        """Normal request"""
        with Session(self.server_address, authkey=self.authkey) as client:
            response = client.commit("get_sum", 1, 2)
        self.assertEqual(3, response)

    def test_case03(self):
        """Wrong authentication key"""
        with self.assertRaises(AuthenticationError):
            with Session(self.server_address, authkey=b"fish") as client:
                client.commit("get_sum", 1, 2)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_process.terminate()


class TestClass03(TestCase):
    """No server running"""

    def test_case01(self):
        with self.assertRaises(ConnectionRefusedError):
            with Session(("localhost", 3000)) as client:
                client.commit("none")
